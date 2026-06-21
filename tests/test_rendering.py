"""rendering 类：JS 渲染可见性（raw HTML 启发式检测 CSR 空壳）。

补"web_fetch 看不到 JS 注入内容"的坑。Playwright 真渲染对比是可选层（后续）。
"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.rendering import check_js_visibility


def _ctx(html, rendered=None):
    return AuditContext(url="https://x.com", html=html, dom=scan(html), rendered_html=rendered)


def test_ssr_content_passes():
    html = "<html><body><h1>标题</h1><p>" + "实质内容" * 100 + "</p></body></html>"
    assert check_js_visibility(_ctx(html)).status == "pass"


# —— D4：有 playwright 真渲染对比时，用确定证据替代启发式（注入、零网络） ——

def test_rendered_confirms_js_shell_fails():
    # raw 空壳但渲染后有实质内容 → 确定 CSR 空壳（比启发式更硬）
    rendered = "<h1>标题</h1><p>" + "渲染后才出现的内容。" * 30 + "</p>"
    out = check_js_visibility(_ctx('<div id="root"></div>', rendered))
    assert out.status == "fail"
    assert out.evidence["rendered_text_length"] >= 100
    assert "确认" in out.message


def test_rendered_both_thin_warns():
    # raw 薄 + 渲染后仍薄 → 真的内容稀薄（warn，不武断判空壳）
    out = check_js_visibility(_ctx('<div id="root"></div>', "<div></div>"))
    assert out.status == "warn"


def test_no_rendered_html_keeps_heuristic():
    # rendered_html=None（默认）→ 原启发式不变：SSR 有内容 → pass
    out = check_js_visibility(_ctx("<h1>t</h1><p>" + "字" * 200 + "</p>"))
    assert out.status == "pass"
    assert "rendered_text_length" not in out.evidence


def test_empty_spa_shell_fails():
    html = '<html><body><div id="root"></div></body></html>'
    out = check_js_visibility(_ctx(html))
    assert out.status == "fail"
    assert out.evidence["spa_root"] is True


def test_id():
    assert check_js_visibility(_ctx("<p>x</p>")).id == "rendering-js-visibility"


# ── Group D 修复：rendered_html="" 空串不应被当"有渲染数据" ──

def test_empty_string_rendered_html_uses_heuristic():
    """rendered_html="" 应走启发式分支（与 None 行为一致），不触发 playwright 对比路径。"""
    # 充足内容 → 启发式判 pass，证明走的是启发式而非 playwright 路径
    html = "<h1>标题</h1><p>" + "内容" * 100 + "</p>"
    out = check_js_visibility(_ctx(html, rendered=""))
    assert out.status == "pass"
    assert "rendered_text_length" not in out.evidence


def test_empty_string_rendered_spa_shell_heuristic_fail():
    """rendered_html="" 且 raw 是 SPA 空壳 → 启发式 fail（与 rendered=None 行为一致）。"""
    html = '<html><body><div id="root"></div></body></html>'
    out = check_js_visibility(_ctx(html, rendered=""))
    assert out.status == "fail"
    assert "rendered_text_length" not in out.evidence
