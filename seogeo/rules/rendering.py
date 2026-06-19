"""rendering 类：JS 渲染可见性（raw HTML 启发式，检测 CSR 空壳）。

补"web_fetch 看不到 JS 注入内容"的坑。判据移植自 Auriti `audit_js.py` + geo-aeo `route.ts`。
Playwright 真渲染对比是可选层（后续）。
"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "rendering-js-visibility"
WEIGHT = 14
MIN_VISIBLE_CHARS = 100
_SPA_ROOTS = ['id="root"', 'id="app"', 'id="__next"', 'id="__nuxt"', 'data-reactroot']
_SSR_MARKERS = ["__next_data__", "data-reactroot"]


@register(id=RULE_ID, category="rendering", weight=WEIGHT)
def check_js_visibility(ctx: AuditContext) -> CheckOutcome:
    d = ctx.dom
    html_low = (ctx.html or "")[:20000].lower()
    text_len = d.text_length if d else 0
    heads = sum(d.headings.values()) if d else 0
    has_spa_root = any(m.lower() in html_low for m in _SPA_ROOTS)
    has_ssr_marker = any(m in html_low for m in _SSR_MARKERS)
    evidence = {"text_length": text_len, "headings": heads, "spa_root": has_spa_root}

    if text_len < MIN_VISIBLE_CHARS and heads == 0 and has_spa_root and not has_ssr_marker:
        return outcome(RULE_ID, WEIGHT, "fail",
                       "页面疑似 JS 渲染空壳（raw HTML 几乎无内容）—— AI 爬虫可能只看到空白",
                       recommendation="改用 SSR/SSG 或预渲染，让 AI 爬虫无需执行 JS 即可读到内容",
                       evidence=evidence)
    if text_len < MIN_VISIBLE_CHARS:
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"raw HTML 可见文本很少（{text_len} 字）—— 确认 AI 爬虫能看到主要内容",
                       recommendation="确保核心内容在初始 HTML 中（非纯前端渲染）",
                       evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "pass",
                   f"raw HTML 含 {text_len} 字可见内容，无需执行 JS 即可读取",
                   evidence=evidence)
