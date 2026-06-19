"""rendering 类：JS 渲染可见性（raw HTML 启发式检测 CSR 空壳）。

补"web_fetch 看不到 JS 注入内容"的坑。Playwright 真渲染对比是可选层（后续）。
"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.rendering import check_js_visibility


def _ctx(html):
    return AuditContext(url="https://x.com", html=html, dom=scan(html))


def test_ssr_content_passes():
    html = "<html><body><h1>标题</h1><p>" + "实质内容" * 100 + "</p></body></html>"
    assert check_js_visibility(_ctx(html)).status == "pass"


def test_empty_spa_shell_fails():
    html = '<html><body><div id="root"></div></body></html>'
    out = check_js_visibility(_ctx(html))
    assert out.status == "fail"
    assert out.evidence["spa_root"] is True


def test_id():
    assert check_js_visibility(_ctx("<p>x</p>")).id == "rendering-js-visibility"
