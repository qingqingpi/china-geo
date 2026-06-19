"""discovery 类检查：AI 可发现性基础。

v0 只查 sitemap.xml（利于百度/搜狗等发现页面）。llms.txt 国内基本无效（CLAUDE.md），
只作信息项记录、不参与成败判定。
"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "discovery-sitemap"
WEIGHT = 8
_LLMS_NOTE = "（注：llms.txt 国内基本无效，仅对部分海外引擎有用）"


@register(id=RULE_ID, category="discovery", weight=WEIGHT)
def check_sitemap(ctx: AuditContext) -> CheckOutcome:
    has_sitemap = bool(ctx.sitemap_xml and ctx.sitemap_xml.strip())
    has_llms = bool(ctx.llms_txt and ctx.llms_txt.strip())
    evidence = {"sitemap": has_sitemap, "llms_txt": has_llms}
    if has_sitemap:
        return outcome(RULE_ID, WEIGHT, "pass",
                       f"已提供 sitemap.xml，利于百度/搜狗等发现页面（llms.txt：{'有' if has_llms else '无'}）",
                       evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "fail",
                   "未发现 sitemap.xml —— 爬虫更难发现你的全部页面",
                   recommendation="生成 sitemap.xml，并在百度搜索资源平台 / 搜狗站长提交" + _LLMS_NOTE,
                   evidence=evidence)
