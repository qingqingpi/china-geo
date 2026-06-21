"""structure 类：JSON-LD 结构化数据存在性 + 合法性。"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.structure import check_jsonld


def _ctx(html):
    return AuditContext(url="https://x.com", html=html, dom=scan(html))


def test_no_jsonld_fails():
    assert check_jsonld(_ctx("<html><body>无结构化</body></html>")).status == "fail"


def test_valid_jsonld_passes():
    out = check_jsonld(_ctx('<script type="application/ld+json">{"@type":"Organization","name":"x"}</script>'))
    assert out.status == "pass"
    assert "Organization" in out.evidence["types"]


def test_invalid_jsonld_warns():
    out = check_jsonld(_ctx('<script type="application/ld+json">{bad json</script>'))
    assert out.status == "warn"
    assert out.evidence["parse_errors"] == 1


def test_id():
    assert check_jsonld(_ctx("")).id == "structure-jsonld"


# ── Group D 修复：合法 JSON-LD 但无 @type 应 warn，不应 pass ──

def test_valid_jsonld_without_type_warns():
    """合法 JSON-LD 但无 @type → warn（AI/搜索无法识别结构意图）。"""
    out = check_jsonld(_ctx('<script type="application/ld+json">{"name":"无类型实体"}</script>'))
    assert out.status == "warn", f"期望 warn，实际 {out.status}"


def test_valid_jsonld_with_type_still_passes():
    """有 @type 的 JSON-LD 仍应 pass（回归测试，确保修复不破坏正常路径）。"""
    out = check_jsonld(_ctx('<script type="application/ld+json">{"@type":"Article","name":"x"}</script>'))
    assert out.status == "pass"
