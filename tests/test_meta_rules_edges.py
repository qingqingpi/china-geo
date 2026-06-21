"""技术 / 元信息规则的防御分支与状态细分——补 test_meta_rules.py / test_technical.py 盲区。

聚焦：dom=None 防御（`ctx.dom else` 分支）、html_error→warn 退化、
OpenGraph 部分缺失 warn、freshness 多种日期来源、各规则 id。
均为 characterization（绿）。
"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.freshness import check_freshness
from seogeo.rules.opengraph import check_og
from seogeo.rules.technical import check_lang
from seogeo.rules.viewport import check_viewport


def _ctx(html="", **kw):
    return AuditContext(url="https://x.com", html=html, dom=scan(html), **kw)


# ============ dom=None 防御分支（不带 html_error）============
# 这些规则用 `ctx.X if ctx.dom else 默认`——dom 缺失也不该崩，按"缺该信号"判 warn。

def test_lang_dom_none_warns_not_crash():
    out = check_lang(AuditContext(url="https://x.com", dom=None))
    assert out.status == "warn"
    assert out.evidence["lang"] == ""


def test_viewport_dom_none_warns_not_crash():
    out = check_viewport(AuditContext(url="https://x.com", dom=None))
    assert out.status == "warn"


def test_og_dom_none_warns_not_crash():
    out = check_og(AuditContext(url="https://x.com", dom=None))
    assert out.status == "warn"
    assert out.evidence["og"] == []


def test_freshness_dom_none_warns_not_crash():
    out = check_freshness(AuditContext(url="https://x.com", dom=None))
    assert out.status == "warn"
    assert out.evidence["has_date"] is False


# ============ html_error 优先：返回"无法获取 HTML"warn ============

def test_lang_html_error_unavailable_warn():
    out = check_lang(AuditContext(url="https://x.com", html_error="timeout"))
    assert out.status == "warn"
    assert out.evidence.get("html_unavailable") is True


def test_og_html_error_unavailable_warn():
    out = check_og(AuditContext(url="https://x.com", html_error="403"))
    assert out.evidence.get("html_unavailable") is True


def test_viewport_html_error_unavailable_warn():
    out = check_viewport(AuditContext(url="https://x.com", html_error="dns"))
    assert out.evidence.get("html_unavailable") is True


def test_freshness_html_error_unavailable_warn():
    out = check_freshness(AuditContext(url="https://x.com", html_error="net"))
    assert out.evidence.get("html_unavailable") is True


# ============ OpenGraph 状态细分 ============

def test_og_partial_only_image_warns_incomplete():
    # 仅 og:image（缺 title/description）→ warn "不全"
    out = check_og(_ctx('<meta property="og:image" content="https://x.com/i.png">'))
    assert out.status == "warn"
    assert out.evidence["og"] == ["og:image"]


def test_og_title_only_warns_incomplete():
    # 只有 og:title，缺 description → 不满足 {title,description} 子集 → warn
    out = check_og(_ctx('<meta property="og:title" content="T">'))
    assert out.status == "warn"


def test_og_all_three_passes():
    html = ('<meta property="og:title" content="T">'
            '<meta property="og:description" content="D">'
            '<meta property="og:image" content="https://x.com/i.png">')
    out = check_og(_ctx(html))
    assert out.status == "pass"
    assert set(out.evidence["og"]) == {"og:title", "og:description", "og:image"}


# ============ freshness 多日期来源 ============

def test_freshness_via_date_meta_passes():
    out = check_freshness(_ctx('<meta name="date" content="2026-01-01">'))
    assert out.status == "pass"
    assert out.evidence["has_date"] is True


def test_freshness_via_jsonld_datemodified_passes():
    out = check_freshness(_ctx('<script type="application/ld+json">{"dateModified":"2026-06-01"}</script>'))
    assert out.status == "pass"


def test_freshness_via_modified_time_meta_passes():
    out = check_freshness(_ctx('<meta property="article:modified_time" content="2026-06-01">'))
    assert out.status == "pass"


# ============ id 锚定 ============

def test_rule_ids_stable():
    assert check_lang(_ctx("")).id == "technical-lang"
    assert check_viewport(_ctx("")).id == "technical-viewport"
    assert check_og(_ctx("")).id == "structure-opengraph"
    assert check_freshness(_ctx("")).id == "content-freshness"
