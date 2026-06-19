"""structure 类：JSON-LD 结构化数据存在性 + 合法性。"""
from __future__ import annotations

import json

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "structure-jsonld"
WEIGHT = 16


@register(id=RULE_ID, category="structure", weight=WEIGHT)
def check_jsonld(ctx: AuditContext) -> CheckOutcome:
    blocks = ctx.dom.jsonld_blocks if ctx.dom else []
    types: list = []
    parse_errors = 0
    for b in blocks:
        try:
            data = json.loads(b)
        except (json.JSONDecodeError, TypeError):
            parse_errors += 1
            continue
        for item in (data if isinstance(data, list) else [data]):
            t = item.get("@type") if isinstance(item, dict) else None
            if t:
                types += t if isinstance(t, list) else [t]
    evidence = {"blocks": len(blocks), "types": sorted(set(types)), "parse_errors": parse_errors}

    if not blocks:
        return outcome(RULE_ID, WEIGHT, "fail",
                       "未发现 JSON-LD 结构化数据 —— AI 更难理解你的实体与内容",
                       recommendation="添加 Organization / Article / FAQPage 等 JSON-LD（schema.org）",
                       evidence=evidence)
    if not types and parse_errors:
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"发现 {len(blocks)} 个 JSON-LD 块但解析失败（{parse_errors} 个）",
                       recommendation="修正 JSON-LD 语法错误，确保是合法 JSON",
                       evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "pass",
                   f"已提供 JSON-LD（类型：{', '.join(evidence['types']) or '未识别'}）",
                   evidence=evidence)
