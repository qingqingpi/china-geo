"""打分：范式A 思路，但对"已实现的检查"做百分比归一化（开发期部分实现也给出诚实总分）。

total = round(100 * Σ得分 / Σ满分)。breakdown 按类目分组展示。
分档移植自 Auriti `config.py` SCORE_BANDS。
"""
from seogeo.rules.base import CheckOutcome
from seogeo.scoring import get_band, score_audit


def _oc(cat, status, score, mx):
    return CheckOutcome(id=f"{cat}-x", status=status, message="",
                        score=score, max_score=mx, category=cat)


def test_all_pass_is_100_excellent():
    r = score_audit([_oc("domestic", "pass", 20, 20), _oc("discovery", "pass", 8, 8)])
    assert r.total == 100
    assert r.band == "excellent"


def test_all_fail_is_0_critical():
    r = score_audit([_oc("domestic", "fail", 0, 20)])
    assert r.total == 0
    assert r.band == "critical"


def test_partial_normalizes_to_percent():
    r = score_audit([_oc("domestic", "warn", 10, 20)])  # 10/20 = 50%
    assert r.total == 50


def test_breakdown_groups_by_category():
    r = score_audit([_oc("domestic", "pass", 20, 20), _oc("discovery", "fail", 0, 8)])
    assert r.breakdown["domestic"] == {"earned": 20, "max": 20}
    assert r.breakdown["discovery"] == {"earned": 0, "max": 8}


def test_empty_outcomes_is_zero():
    assert score_audit([]).total == 0


def test_band_thresholds():
    assert get_band(90) == "excellent"
    assert get_band(75) == "good"
    assert get_band(50) == "foundation"
    assert get_band(10) == "critical"
