"""抓取层的 SSRF 防护——CLI 会抓任意用户给的 URL，必须挡掉私网/云元数据地址。

参考 Auriti `validators.py` 的 _BLOCKED_NETWORKS 思路，用 stdlib `ipaddress` 复刻。
"""
from __future__ import annotations

import gzip
import io
from unittest.mock import MagicMock, patch

from seogeo.fetch import _ip_is_blocked, fetch, is_safe_url


def test_loopback_ip_blocked():
    assert _ip_is_blocked("127.0.0.1") is True


def test_cloud_metadata_ip_blocked():
    # 169.254.169.254 是云厂商元数据端点（link-local），SSRF 头号目标
    assert _ip_is_blocked("169.254.169.254") is True


def test_private_ips_blocked():
    for ip in ["10.0.0.5", "192.168.1.1", "172.16.0.1"]:
        assert _ip_is_blocked(ip) is True


def test_public_ip_not_blocked():
    assert _ip_is_blocked("8.8.8.8") is False


def test_ipv6_loopback_blocked():
    assert _ip_is_blocked("::1") is True


def test_unparseable_ip_blocked_conservatively():
    assert _ip_is_blocked("not-an-ip") is True


def test_non_http_scheme_rejected():
    assert is_safe_url("ftp://example.com/x") is False
    assert is_safe_url("file:///etc/passwd") is False


def test_safe_url_blocks_localhost():
    assert is_safe_url("http://127.0.0.1/") is False


def test_safe_url_allows_public_ip_literal():
    # 8.8.8.8 是 IP 字面量，getaddrinfo 直接返回、无需真实 DNS
    assert is_safe_url("http://8.8.8.8/") is True


# ---------------------------------------------------------------------------
# gzip 解压修复测试
# ---------------------------------------------------------------------------

def _make_fake_response(body_bytes: bytes, content_encoding: str | None = None,
                        content_type: str = "text/html; charset=utf-8",
                        status: int = 200, url: str = "http://8.8.8.8/"):
    """构造一个假 urlopen 返回值，模拟服务端强制 gzip 或普通响应。"""
    headers = MagicMock()
    headers.get_content_charset.return_value = "utf-8"
    # headers.items() 用于构建 resp["headers"]
    items = [("content-type", content_type)]
    if content_encoding:
        items.append(("content-encoding", content_encoding))
    headers.items.return_value = items
    # headers.get(key) 风格——fetch 里用 r.headers.get_content_charset()，
    # 以及下方新增的 r.headers.get("content-encoding") 或类似访问
    headers.get = lambda key, default=None: (
        content_encoding if key.lower() == "content-encoding" and content_encoding else default
    )

    resp = MagicMock()
    resp.status = status
    resp.headers = headers
    resp.read.return_value = body_bytes
    resp.geturl.return_value = url
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_fetch_gzip_response_decompressed():
    """服务端强制返回 Content-Encoding: gzip 时，fetch 应正确解压出原始 HTML 文本。"""
    original_html = "<html><body>国内 AI 可见性优化</body></html>".encode("utf-8")
    compressed = gzip.compress(original_html)

    fake_resp = _make_fake_response(
        body_bytes=compressed,
        content_encoding="gzip",
    )

    with patch("urllib.request.urlopen", return_value=fake_resp):
        resp, err = fetch("http://8.8.8.8/")

    assert err is None
    assert resp is not None
    assert "国内 AI 可见性优化" in resp["text"]


def test_fetch_no_content_encoding_decoded_as_is():
    """无 Content-Encoding 头时，fetch 应原样解码，不做 gzip 处理。"""
    original_html = b"<html><body>plain response</body></html>"

    fake_resp = _make_fake_response(
        body_bytes=original_html,
        content_encoding=None,
    )

    with patch("urllib.request.urlopen", return_value=fake_resp):
        resp, err = fetch("http://8.8.8.8/")

    assert err is None
    assert resp is not None
    assert "plain response" in resp["text"]


def test_fetch_gzip_decompress_failure_returns_error():
    """gzip 头存在但内容非法压缩字节时，fetch 应返回 (None, 'gzip 解压失败')。"""
    bad_bytes = b"this is not gzip data at all"

    fake_resp = _make_fake_response(
        body_bytes=bad_bytes,
        content_encoding="gzip",
    )

    with patch("urllib.request.urlopen", return_value=fake_resp):
        resp, err = fetch("http://8.8.8.8/")

    assert resp is None
    assert err == "gzip 解压失败"


def test_fetch_http_error_with_gzip_body_decompressed():
    """HTTPError 路径：若响应体也被 gzip 压缩，应正确解压。"""
    import urllib.error

    original_html = b"<html>404 page</html>"
    compressed = gzip.compress(original_html)

    error_headers = MagicMock()
    error_headers.items.return_value = [("content-encoding", "gzip")]
    error_headers.get = lambda key, default=None: (
        "gzip" if key.lower() == "content-encoding" else default
    )

    http_err = urllib.error.HTTPError(
        url="http://8.8.8.8/", code=404, msg="Not Found",
        hdrs=error_headers, fp=io.BytesIO(compressed),
    )
    http_err.read = MagicMock(return_value=compressed)
    http_err.headers = error_headers

    with patch("urllib.request.urlopen", side_effect=http_err):
        resp, err = fetch("http://8.8.8.8/")

    assert err is None
    assert resp is not None
    assert resp["status"] == 404
    assert "404 page" in resp["text"]
