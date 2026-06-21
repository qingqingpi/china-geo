"""HTTP 抓取层（stdlib 零依赖）+ SSRF 防护。

CLI 会抓任意用户给的 URL，所以抓之前必须挡掉私网 / 回环 / 云元数据地址
（169.254.169.254 等）。SSRF 判断是纯逻辑、可单测；真正的 urllib 抓取是薄胶水。
"""
from __future__ import annotations

import gzip
import ipaddress
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse

USER_AGENT = "seogeo/0.1 (+https://github.com/seogeo/seogeo)"
TIMEOUT = 10
MAX_BYTES = 10 * 1024 * 1024


def _ip_is_blocked(ip_str: str) -> bool:
    """私网/回环/链路本地/保留/多播/未指定地址一律拦截；无法解析则保守拦截。"""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return (ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_reserved or ip.is_multicast or ip.is_unspecified)


def is_safe_url(url: str) -> bool:
    """只允许 http/https，且解析出的所有 IP 都不在黑名单内。

    已知限制：getaddrinfo 无超时、慢 DNS 可能阻塞；包成服务端时需线程化限时。
    """
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        return False
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror:
        return False
    return all(not _ip_is_blocked(info[4][0]) for info in infos)


def _decode_body(raw: bytes, headers, charset: str = "utf-8") -> tuple[str | None, str | None]:
    """根据 Content-Encoding 决定是否先解压；返回 (text | None, err | None)。

    部分 CDN / Nginx 无视请求头、强制返回 Content-Encoding: gzip，
    直接 decode 会得到乱码。此处统一处理，解压失败返回 (None, 'gzip 解压失败')。
    """
    encoding = headers.get("content-encoding", "") or ""
    if "gzip" in encoding.lower():
        try:
            raw = gzip.decompress(raw)
        except Exception:  # noqa: BLE001
            return None, "gzip 解压失败"
    return raw.decode(charset, "replace"), None


def fetch(url: str, ua: str = USER_AGENT, timeout: int = TIMEOUT):
    """返回 (resp_dict | None, err | None)。resp_dict = {status, text, headers, url}。
    4xx/5xx 仍算"成功拿到响应"（status 非 200）；网络错误返回 (None, err)。"""
    if not is_safe_url(url):
        return None, "blocked or unresolvable host (SSRF guard)"
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                return None, f"response too large (>{MAX_BYTES} bytes)"
            charset = r.headers.get_content_charset() or "utf-8"
            resp_headers = {k.lower(): v for k, v in r.headers.items()}
            text, err = _decode_body(raw, resp_headers, charset)
            if err:
                return None, err
            return {
                "status": r.status,
                "text": text,
                "headers": resp_headers,
                "url": r.geturl(),
            }, None
    except urllib.error.HTTPError as e:
        raw = e.read(MAX_BYTES)
        err_headers = {k.lower(): v for k, v in e.headers.items()}
        text, decode_err = _decode_body(raw, err_headers, "utf-8")
        if decode_err:
            return None, decode_err
        return {"status": e.code, "text": text,
                "headers": err_headers, "url": url}, None
    except Exception as e:  # noqa: BLE001 — 抓取层把一切网络异常收敛成 err 字符串
        return None, str(e)
