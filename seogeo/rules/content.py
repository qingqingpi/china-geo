"""content 类：内容可引用性结构（唯一H1 / H2切分 / 正文足量 / 列表表格）。

正文足量按字符数判定（中文无空格，词数失真）。4 项信号 → pass / warn / fail。
"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, html_unavailable, outcome, register

RULE_ID = "content-structure"
WEIGHT = 16
MIN_CHARS = 300


@register(id=RULE_ID, category="content", weight=WEIGHT)
def check_content_structure(ctx: AuditContext) -> CheckOutcome:
    if ctx.html_error:
        return html_unavailable(RULE_ID, WEIGHT, "内容结构")
    if ctx.dom is None and not ctx.html_error:
        return html_unavailable(RULE_ID, WEIGHT, "内容结构")
    d = ctx.dom
    signals = {
        "single_h1": bool(d) and d.headings["h1"] == 1,
        "has_subheadings": bool(d) and d.headings["h2"] > 0,
        "enough_text": bool(d) and d.text_length >= MIN_CHARS,
        "has_list_or_table": bool(d) and (d.has_list or d.has_table),
    }
    n = sum(signals.values())
    evidence = {**signals, "text_length": d.text_length if d else 0, "signals_met": n}

    if n >= 4:
        return outcome(RULE_ID, WEIGHT, "pass", f"内容结构良好（{n}/4 项可引用性信号）", evidence=evidence)

    missing = []
    if not signals["single_h1"]:
        missing.append("唯一 H1 主标题")
    if not signals["has_subheadings"]:
        missing.append("H2 小节切分")
    if not signals["enough_text"]:
        missing.append(f"正文≥{MIN_CHARS}字")
    if not signals["has_list_or_table"]:
        missing.append("列表/表格（利于被 AI 抽取引用）")
    status = "warn" if n >= 2 else "fail"
    return outcome(RULE_ID, WEIGHT, status,
                   f"内容结构待改进（{n}/4 项信号）",
                   recommendation="补强：" + "、".join(missing),
                   evidence=evidence)
