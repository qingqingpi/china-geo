"""discovery 类检查：sitemap.xml 可发现性（利于百度/搜狗抓取）。

llms.txt 国内基本无效（CLAUDE.md），故只作信息项记录、不参与成败判定。
"""
from seogeo.rules.base import AuditContext
from seogeo.rules.discovery import check_sitemap


def _ctx(**kw):
    return AuditContext(url="https://example.com", **kw)


def test_sitemap_present_passes():
    out = check_sitemap(_ctx(sitemap_xml="<urlset>...</urlset>"))
    assert out.status == "pass"


def test_sitemap_absent_fails():
    out = check_sitemap(_ctx())
    assert out.status == "fail"
    assert "sitemap" in out.recommendation.lower()


def test_llms_recorded_as_info_only():
    # 有 llms 无 sitemap → 仍 fail（llms 不参与判定），但 evidence 记录 llms 状态
    out = check_sitemap(_ctx(llms_txt="# Site"))
    assert out.status == "fail"
    assert out.evidence["llms_txt"] is True


def test_outcome_id():
    assert check_sitemap(_ctx()).id == "discovery-sitemap"
