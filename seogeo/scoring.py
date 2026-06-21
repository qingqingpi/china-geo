"""打分与分档。

范式 A（绝对加权）+ 对"已实现检查"做百分比归一化：total = round(100 * Σ得分 / Σ满分)。
这样开发期部分实现也能给出诚实总分（"在我们检查的项里你得几分"）。
分档阈值移植自 Auriti `config.py` SCORE_BANDS。
"""
from __future__ import annotations

from dataclasses import dataclass

SCORE_BANDS = {
    "excellent": (86, 100),
    "good": (68, 85),
    "foundation": (36, 67),
    "critical": (0, 35),
}


def get_band(score: int) -> str:
    for name, (lo, hi) in SCORE_BANDS.items():
        if lo <= score <= hi:
            return name
    return "critical"


@dataclass
class ScoreResult:
    total: int
    band: str
    breakdown: dict  # {category: {"earned": int, "max": int}}


def score_audit(outcomes) -> ScoreResult:
    breakdown: dict = {}
    for o in outcomes:
        cat = o.category or "uncategorized"
        b = breakdown.setdefault(cat, {"earned": 0, "max": 0})
        b["earned"] += o.score
        b["max"] += o.max_score
    tot_e = sum(b["earned"] for b in breakdown.values())
    tot_m = sum(b["max"] for b in breakdown.values())
    total = round(100 * tot_e / tot_m) if tot_m else 0
    total = max(0, min(100, total))
    return ScoreResult(total=total, band=get_band(total), breakdown=breakdown)
