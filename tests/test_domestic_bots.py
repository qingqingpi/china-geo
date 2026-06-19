"""国内主流 AI 爬虫准入检查——seogeo 最差异化的一条规则。

语义：
- 封禁国内爬虫 → fail（最高优先修复）。
- 仅靠 `*` 通配放行 → warn（百度/字节可能忽略通配段，建议各自单独成块）。
- 显式放行或无任何封禁 → pass。
"""
from seogeo.rules.base import AuditContext
from seogeo.rules.domestic_bots import check_domestic_bots


def _ctx(robots):
    return AuditContext(url="https://example.com", robots_txt=robots)


def test_no_robots_passes():
    out = check_domestic_bots(_ctx(None))
    assert out.status == "pass"


def test_blocked_domestic_bot_fails_and_lists_it():
    robots = "User-agent: Bytespider\nDisallow: /\n"
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "fail"
    assert "Bytespider" in out.evidence["blocked"]
    assert out.recommendation


def test_wildcard_only_allow_warns():
    robots = "User-agent: *\nDisallow:\n"
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "warn"
    assert "Baiduspider" in out.evidence["wildcard_only"]


def test_all_explicitly_allowed_passes():
    robots = "\n\n".join(
        f"User-agent: {b}\nDisallow:"
        for b in ["Baiduspider", "Bytespider", "PetalBot", "Sogou web spider", "YisouSpider"]
    )
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "pass"


def test_blocked_takes_precedence_over_wildcard_warn():
    robots = "User-agent: *\nDisallow:\n\nUser-agent: Bytespider\nDisallow: /\n"
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "fail"
    assert "Bytespider" in out.evidence["blocked"]


def test_outcome_carries_rule_id():
    assert check_domestic_bots(_ctx(None)).id == "domestic-bot-access"


def test_robots_fetch_error_warns_not_false_pass():
    ctx = AuditContext(url="https://example.com", robots_txt=None, robots_error="HTTP 403")
    out = check_domestic_bots(ctx)
    assert out.status == "warn"
    assert "403" in out.message
    assert out.evidence.get("robots_error") == "HTTP 403"
