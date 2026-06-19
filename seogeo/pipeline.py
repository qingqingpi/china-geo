"""审计管线：跑全部已注册规则 → 打分 → 优先级建议 → AuditResult。

控制流移植自 Auriti `core/audit.py:run_full_audit`（抓取在 CLI 侧完成、这里只编排检查与汇总）。
"""
from __future__ import annotations

import time

import seogeo.rules  # noqa: F401  触发规则自注册到全局 REGISTRY
from seogeo.dom import scan
from seogeo.report import AuditResult, build_recommendations
from seogeo.rules.base import REGISTRY, AuditContext, CheckOutcome
from seogeo.scoring import score_audit


def run_audit(ctx: AuditContext) -> AuditResult:
    t0 = time.perf_counter()
    if ctx.dom is None and ctx.html:
        ctx.dom = scan(ctx.html)  # 一次解析，所有 HTML 检查复用
    outcomes = []
    for rule in REGISTRY.all():
        try:
            oc = rule.run(ctx)
        except Exception as e:  # noqa: BLE001 — 单条检查崩溃不应中断整次审计
            oc = CheckOutcome(id=rule.id, status="fail",
                              message=f"检查执行异常：{e}", score=0, max_score=rule.weight)
        oc.category = rule.category  # 从 registry 标注类目，供打分分组
        outcomes.append(oc)

    sr = score_audit(outcomes)
    return AuditResult(
        url=ctx.url, score=sr.total, band=sr.band, breakdown=sr.breakdown,
        outcomes=outcomes, recommendations=build_recommendations(outcomes),
        duration_ms=int((time.perf_counter() - t0) * 1000),
    )
