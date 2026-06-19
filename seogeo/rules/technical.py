"""technical 类：<html lang> 语言声明。"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "technical-lang"
WEIGHT = 8


@register(id=RULE_ID, category="technical", weight=WEIGHT)
def check_lang(ctx: AuditContext) -> CheckOutcome:
    lang = ctx.dom.lang if ctx.dom else ""
    if lang:
        return outcome(RULE_ID, WEIGHT, "pass", f'已声明语言：lang="{lang}"', evidence={"lang": lang})
    return outcome(RULE_ID, WEIGHT, "warn",
                   "未声明 <html lang> —— 影响搜索引擎/AI 判断语言与地区",
                   recommendation='为 <html> 添加 lang 属性（中文站用 lang="zh-CN"）',
                   evidence={"lang": ""})
