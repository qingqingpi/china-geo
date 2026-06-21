"""抓取层补充边界——补 test_fetch.py 盲区（零网络，mock urlopen）。

聚焦：is_safe_url 退化输入、_decode_body 的 encoding 子串判定、MAX_BYTES 上限、
HTTPError 路径 status 透传、通用网络异常收敛成 err 串。
"""
from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

from seogeo.fetch import MAX_BYTES, _decode_body, fetch, is_safe_url


# ---- is_safe_url 退化 / 大小写 ----

def test_safe_url_empty_string_rejected():
    assert is_safe_url("") is False


def test_safe_url_no_hostname_rejected():
    assert is_safe_url("http://") is False


def test_safe_url_scheme_case_insensitive():
    # urlparse 归一化 scheme 为小写 → HTTP:// 仍按 http 放行（IP 字面量公网）
    assert is_safe_url("HTTP://8.8.8.8/") is True


def test_safe_url_https_public_ip_literal_ok():
    assert is_safe_url("https://1.1.1.1/") is True


def test_safe_url_data_scheme_rejected():
    assert is_safe_url("data:text/html,hi") is False


# ---- _decode_body：content-encoding 子串判定 ----

def test_decode_body_gzip_substring_in_encoding_triggers_decompress():
    # "br, gzip" 含 'gzip' 子串 → 走解压路径；非法压缩字节 → 报错
    text, err = _decode_body(b"not-gzip", {"content-encoding": "br, gzip"})
    assert text is None
    assert err == "gzip 解压失败"


def test_decode_body_no_encoding_plain_decode():
    text, err = _decode_body("你好".encode("utf-8"), {})
    assert err is None
    assert text == "你好"


def test_decode_body_invalid_utf8_replaced_not_crash():
    # 非法 UTF-8 字节用 'replace' 兜底，不抛异常
    text, err = _decode_body(b"\xff\xfe abc", {})
    assert err is None
    assert "abc" in text


def test_decode_body_plain_dict_headers_no_encoding():
    # headers 是普通 dict、无 content-encoding —— 原样解码返回
    text, err = _decode_body(b"x", {})
    assert err is None and text == "x"


# ---- MAX_BYTES 上限 ----

def _fake_resp(body: bytes, status: int = 200):
    headers = MagicMock()
    headers.get_content_charset.return_value = "utf-8"
    headers.items.return_value = [("content-type", "text/html")]
    headers.get = lambda k, default=None: default
    resp = MagicMock()
    resp.status = status
    resp.headers = headers
    resp.read = lambda n=None: body  # fetch 调 r.read(MAX_BYTES+1)
    resp.geturl.return_value = "http://8.8.8.8/"
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_fetch_response_too_large_rejected():
    big = b"x" * (MAX_BYTES + 1)  # 超过上限 1 字节
    with patch("urllib.request.urlopen", return_value=_fake_resp(big)):
        resp, err = fetch("http://8.8.8.8/")
    assert resp is None
    assert "too large" in err


def test_fetch_exactly_max_bytes_ok():
    body = b"x" * MAX_BYTES  # 恰好上限 → 通过
    with patch("urllib.request.urlopen", return_value=_fake_resp(body)):
        resp, err = fetch("http://8.8.8.8/")
    assert err is None
    assert resp is not None and resp["status"] == 200


# ---- SSRF 守卫优先于发起请求 ----

def test_fetch_blocks_private_before_request():
    # 私网地址应在 urlopen 前被拦，返回 SSRF 提示，且 urlopen 不被调用
    with patch("urllib.request.urlopen") as mock_open:
        resp, err = fetch("http://127.0.0.1/")
    assert resp is None
    assert "SSRF" in err
    mock_open.assert_not_called()


# ---- HTTPError 路径：status 透传，4xx 仍算"拿到响应" ----

def test_fetch_http_404_returns_response_not_error():
    import urllib.error
    err_headers = MagicMock()
    err_headers.items.return_value = [("content-type", "text/html")]
    err_headers.get = lambda k, default=None: default
    http_err = urllib.error.HTTPError(
        url="http://8.8.8.8/", code=404, msg="Not Found",
        hdrs=err_headers, fp=io.BytesIO(b"<html>404</html>"),
    )
    http_err.read = MagicMock(return_value=b"<html>404</html>")
    http_err.headers = err_headers
    with patch("urllib.request.urlopen", side_effect=http_err):
        resp, err = fetch("http://8.8.8.8/")
    assert err is None
    assert resp["status"] == 404
    assert "404" in resp["text"]


# ---- 通用网络异常收敛成 err 串（不抛）----

def test_fetch_generic_exception_becomes_error_string():
    with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
        resp, err = fetch("http://8.8.8.8/")
    assert resp is None
    assert "timed out" in err
