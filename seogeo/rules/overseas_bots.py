"""海外主流 AI 爬虫准入检查（与国内爬虫并列）。

判定：任一海外 AI 爬虫被显式封禁 → fail；否则 pass。
与国内爬虫不同：海外爬虫遵守 `*` 通配，仅靠通配放行也算 OK（无"各家单独成块"警告）。
"""
from __future__ import annotations

from seogeo.data.overseas_bots import OVERSEAS_BOTS
from seogeo.robots import classify_bot
from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "overseas-bot-access"
WEIGHT = 12


@register(id=RULE_ID, category="overseas", weight=WEIGHT)
def check_overseas_bots(ctx: AuditContext) -> CheckOutcome:
    if ctx.robots_error:
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"无法获取 robots.txt（{ctx.robots_error}）—— 无法判定海外 AI 爬虫准入",
                       recommendation="确认 robots.txt 可公开访问",
                       evidence={"robots_error": ctx.robots_error})
    if not ctx.robots_txt:
        return outcome(RULE_ID, WEIGHT, "pass",
                       "未发现 robots.txt —— 海外 AI 爬虫默认可抓全站",
                       evidence={"robots": False})

    blocked, allowed = [], []
    for bot in OVERSEAS_BOTS:
        c = classify_bot(bot, ctx.robots_txt)
        if c.status == "blocked":
            blocked.append(bot)
        else:
            allowed.append(bot)  # allowed（含仅通配）或 missing → OK
    evidence = {"blocked": blocked, "allowed": allowed}

    if blocked:
        return outcome(RULE_ID, WEIGHT, "fail",
                       f"robots.txt 挡住了海外 AI 爬虫：{', '.join(blocked)}",
                       recommendation=(
                           f"若想被 ChatGPT / Claude / Perplexity / Google AI 引用，"
                           f"移除对 {', '.join(blocked)} 的 Disallow"),
                       evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "pass",
                   f"海外 AI 爬虫均可正常抓取（{len(allowed)} 个）",
                   evidence=evidence)
