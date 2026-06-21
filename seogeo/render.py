"""可选 JS 真渲染（`[render]` extra = playwright）。

未装 playwright 则优雅降级返回 None，调用方退回 raw HTML 启发式——保持"运行时零依赖"。
"""
from __future__ import annotations

try:
    from playwright.sync_api import sync_playwright
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def available() -> bool:
    """playwright 是否就绪（装了 `pip install Chinese-Geo[render]` 才为 True）。"""
    return _AVAILABLE


def render_html(url: str, timeout_ms: int = 15000) -> str | None:
    """取 JS 渲染后的 HTML；未装 playwright 或渲染失败 → None（调用方降级到 raw 启发式）。"""
    if not _AVAILABLE:
        return None
    try:  # pragma: no cover  （需真浏览器 + 联网，单测不覆盖；只测降级路径）
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(url, timeout=timeout_ms, wait_until="networkidle")
                return page.content()
            finally:
                browser.close()
    except Exception:
        return None
