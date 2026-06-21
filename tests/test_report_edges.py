"""报告渲染 + 优先级矩阵 + 打分分档边界——补 test_report.py / test_scoring.py 盲区。

聚焦：gap 阈值端点（>=8 Critical / >=3 High / 其余 Quick Win）、warn-无建议被排除、
render_markdown 空建议走"🎉"分支不带验证脚注、未知 category 的引擎注释退化、
分档区间端点。均为 characterization（绿）。
"""
from seogeo.report import (
    AuditResult,
    build_recommendations,
    render_json,
    render_markdown,
)
from seogeo.rules.base import CheckOutcome
from seogeo.scoring import get_band


def _oc(rid, cat, status, score, mx, rec="改它"):
    return CheckOutcome(id=rid, status=status, message="m", recommendation=rec,
                        score=score, max_score=mx, category=cat)


# ---- gap 阈值端点（非 domestic 路径）----

def test_gap_8_is_critical_boundary():
    # gap 恰为 8 → Critical（>=8 边界）
    assert build_recommendations([_oc("x", "technical", "warn", 2, 10)])[0]["priority"] == "Critical"


def test_gap_7_is_high():
    assert build_recommendations([_oc("x", "technical", "warn", 3, 10)])[0]["priority"] == "High"


def test_gap_3_is_high_boundary():
    # gap 恰为 3 → High（>=3 边界）
    assert build_recommendations([_oc("x", "technical", "warn", 2, 5)])[0]["priority"] == "High"


def test_gap_2_is_quick_win():
    assert build_recommendations([_oc("x", "technical", "warn", 3, 5)])[0]["priority"] == "Quick Win"


# ---- domestic warn（非 fail）走通用 gap 逻辑，不强制 Critical ----

def test_domestic_warn_not_forced_critical():
    # 仅 domestic + fail 才强制 Critical；domestic warn 按 gap 走（gap2 → Quick Win）
    r = build_recommendations([_oc("d", "domestic", "warn", 18, 20)])
    assert r[0]["priority"] == "Quick Win"


def test_overseas_fail_uses_gap_not_forced_critical():
    # overseas fail（非 domestic）gap=12 → Critical（因 gap>=8，而非 domestic 强制）
    r = build_recommendations([_oc("o", "overseas", "fail", 0, 12)])
    assert r[0]["priority"] == "Critical"


# ---- pass / 无建议被排除 ----

def test_pass_outcome_excluded():
    assert build_recommendations([_oc("x", "technical", "pass", 5, 5)]) == []


def test_warn_without_recommendation_excluded():
    assert build_recommendations([_oc("x", "technical", "warn", 3, 10, rec="")]) == []


# ---- 未知 category 的引擎注释退化为空串 ----

def test_unknown_category_has_empty_engines_note():
    r = build_recommendations([_oc("x", "mystery", "fail", 0, 10)])
    assert r[0]["engines"] == ""


# ---- render_markdown 空建议：🎉 分支、无验证脚注 ----

def test_markdown_no_recommendations_celebrates():
    res = AuditResult(url="https://x.com", score=100, band="excellent",
                      breakdown={"technical": {"earned": 10, "max": 10}},
                      outcomes=[], recommendations=[])
    md = render_markdown(res)
    assert "🎉" in md
    assert "monitor" not in md  # 无修复项时不渲染验证闭环脚注
    assert "100/100" in md


def test_markdown_renders_breakdown_rows_with_cn_labels():
    res = AuditResult(url="https://x.com", score=50, band="foundation",
                      breakdown={"domestic": {"earned": 10, "max": 20}},
                      outcomes=[], recommendations=[])
    md = render_markdown(res)
    assert "国内 AI 爬虫准入" in md   # _CAT_CN 标签
    assert "10/20" in md


# ---- render_json 形状（含空 outcomes）----

def test_render_json_empty_outcomes_valid():
    import json
    res = AuditResult(url="https://x.com", score=0, band="critical",
                      breakdown={}, outcomes=[], recommendations=[], duration_ms=7)
    data = json.loads(render_json(res))
    assert data["checks"] == []
    assert data["duration_ms"] == 7
    assert data["band"] == "critical"


# ---- scoring 分档区间端点 ----

def test_band_interval_endpoints():
    assert get_band(86) == "excellent"   # 下端点
    assert get_band(100) == "excellent"  # 上端点
    assert get_band(85) == "good"
    assert get_band(68) == "good"
    assert get_band(67) == "foundation"
    assert get_band(36) == "foundation"
    assert get_band(35) == "critical"
    assert get_band(0) == "critical"


def test_band_out_of_range_falls_to_critical():
    # 兜底：区间外（如负数 / >100）→ critical
    assert get_band(-1) == "critical"
    assert get_band(101) == "critical"
