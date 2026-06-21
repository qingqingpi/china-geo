"""可选 JS 真渲染模块（D4）：未装 playwright（[render] extra）时优雅降级返回 None，不崩。"""
import pytest

from seogeo import render


def test_available_returns_bool():
    assert isinstance(render.available(), bool)


def test_render_degrades_to_none_without_playwright():
    if render.available():
        pytest.skip("已装 playwright，跳过降级路径（避免真起浏览器 / 联网）")
    # 未装时：立即返回 None（ImportError 在任何网络动作前发生）→ 零网络
    assert render.render_html("https://example.com") is None


# ---------------------------------------------------------------------------
# render_html SSRF 防护测试
# 强制模拟 playwright 已安装（_AVAILABLE=True）且 sync_playwright 可正常调用，
# 确保测的是 SSRF 守卫逻辑而非"playwright 缺失导致的降级"：
# 即使浏览器"可用"，私网地址也必须在 playwright 启动前被 is_safe_url 拦截。
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock, patch


def _make_mock_playwright():
    """构造一个能正常运行的假 playwright 上下文管理器（但不应被调到）。"""
    page = MagicMock()
    page.content.return_value = "<html>pwned</html>"
    browser = MagicMock()
    browser.new_page.return_value = page
    pw = MagicMock()
    pw.chromium.launch.return_value = browser
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=pw)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


def test_render_html_blocks_loopback():
    """render_html 在 playwright 可用时，应在浏览器启动前拦截回环地址，返回 None。"""
    with patch.object(render, "_AVAILABLE", True), \
         patch("seogeo.render.sync_playwright", return_value=_make_mock_playwright(), create=True):
        result = render.render_html("http://127.0.0.1/")
    assert result is None


def test_render_html_blocks_link_local():
    """render_html 在 playwright 可用时，应拦截云元数据链路本地地址（169.254.169.254），返回 None。"""
    with patch.object(render, "_AVAILABLE", True), \
         patch("seogeo.render.sync_playwright", return_value=_make_mock_playwright(), create=True):
        result = render.render_html("http://169.254.169.254/")
    assert result is None


def test_render_html_blocks_private_network():
    """render_html 在 playwright 可用时，应拦截内网地址，返回 None。"""
    with patch.object(render, "_AVAILABLE", True), \
         patch("seogeo.render.sync_playwright", return_value=_make_mock_playwright(), create=True):
        result = render.render_html("http://192.168.1.1/")
    assert result is None
