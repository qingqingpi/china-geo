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
