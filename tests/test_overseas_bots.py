"""海外主流 AI 爬虫准入检查。

与国内爬虫的关键区别：海外爬虫（GPTBot/ClaudeBot/PerplexityBot…）遵守 `*` 通配，
所以仅靠通配放行 = pass（无"必须各家单独成块"警告）；只有显式封禁才 fail。
"""
from seogeo.rules.base import AuditContext
from seogeo.rules.overseas_bots import check_overseas_bots


def _ctx(robots=None, robots_error=None):
    return AuditContext(url="https://x.com", robots_txt=robots, robots_error=robots_error)


def test_no_robots_passes():
    assert check_overseas_bots(_ctx()).status == "pass"


def test_blocked_overseas_bot_fails():
    out = check_overseas_bots(_ctx("User-agent: GPTBot\nDisallow: /"))
    assert out.status == "fail"
    assert "GPTBot" in out.evidence["blocked"]
    assert out.recommendation


def test_wildcard_allow_is_pass_not_warn():
    # 海外爬虫遵守 *，仅靠通配放行也 OK（与国内爬虫不同）
    assert check_overseas_bots(_ctx("User-agent: *\nDisallow:")).status == "pass"


def test_wildcard_block_fails():
    out = check_overseas_bots(_ctx("User-agent: *\nDisallow: /"))
    assert out.status == "fail"


def test_robots_error_warns():
    out = check_overseas_bots(_ctx(robots_error="HTTP 403"))
    assert out.status == "warn"
    assert out.evidence["robots_error"] == "HTTP 403"


def test_id():
    assert check_overseas_bots(_ctx()).id == "overseas-bot-access"
