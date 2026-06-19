"""国内主流 AI 爬虫准入检查——seogeo 最差异化的一条规则。

判定：
- 任一国内爬虫被封禁 → fail（最高优先修复）。
- 仅靠 `*` 通配放行 → warn（百度/字节倾向只读精确匹配自己 UA 的块，通配段可能被忽略）。
- 显式放行、或 robots 对它无任何约束 → pass。
"""
from __future__ import annotations

from seogeo.data.domestic_bots import DOMESTIC_BOTS
from seogeo.robots import classify_bot
from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "domestic-bot-access"
WEIGHT = 20


@register(id=RULE_ID, category="domestic", weight=WEIGHT)
def check_domestic_bots(ctx: AuditContext) -> CheckOutcome:
    if ctx.robots_error:
        # 抓取失败/403 ≠ 无 robots。诚实报"无法判定"，不能假装放行。
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"无法获取 robots.txt（{ctx.robots_error}）—— 无法判定国内 AI 爬虫准入",
                       recommendation="确认 robots.txt 可公开访问；若站点对默认 UA 反爬，AI 爬虫可能同样受阻。可换 www 域名或人工核实",
                       evidence={"robots_error": ctx.robots_error})
    if not ctx.robots_txt:
        return outcome(RULE_ID, WEIGHT, "pass",
                       "未发现 robots.txt —— 国内 AI 爬虫默认可抓全站",
                       evidence={"robots": False})

    blocked, wildcard_only, explicit_ok = [], [], []
    for bot in DOMESTIC_BOTS:
        c = classify_bot(bot, ctx.robots_txt)
        if c.status == "blocked":
            blocked.append(bot)
        elif c.status == "allowed" and c.via_wildcard:
            wildcard_only.append(bot)
        elif c.status == "allowed":
            explicit_ok.append(bot)
        # status == "missing"：robots 对它无约束 → 可抓，不计入问题

    evidence = {"blocked": blocked, "wildcard_only": wildcard_only, "explicit_ok": explicit_ok}

    if blocked:
        return outcome(RULE_ID, WEIGHT, "fail",
                       f"robots.txt 挡住了国内 AI 爬虫：{', '.join(blocked)}",
                       recommendation=(
                           f"为 {', '.join(blocked)} 各自单独写 User-agent 块并 Allow: /"
                           "（合并进 * 通配段会被忽略）"),
                       evidence=evidence)
    if wildcard_only:
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"以下国内 AI 爬虫仅靠通配 * 放行，可能被忽略：{', '.join(wildcard_only)}",
                       recommendation="百度/字节倾向只读精确匹配自己 UA 的块；建议为每家单独成块并 Allow: /",
                       evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "pass",
                   f"国内 AI 爬虫均可正常抓取（显式放行：{', '.join(explicit_ok) or '无显式块且无封禁'}）",
                   evidence=evidence)
