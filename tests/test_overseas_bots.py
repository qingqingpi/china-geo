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


# ---- Bingbot 描述不再把 Bing 与 Copilot 简单并列 ----

def test_bingbot_description_not_simple_copilot_pairing():
    """Bingbot 描述不得再是 'Microsoft Bing / Copilot' 这类简单并列，
    因为 Copilot 用独立 UA，不走 Bingbot。新描述须明确说明 Copilot 不走此 UA。"""
    from seogeo.data.overseas_bots import OVERSEAS_BOTS
    desc = OVERSEAS_BOTS["Bingbot"]
    # 旧的简单并列串
    assert desc != "Microsoft Bing / Copilot", "旧的简单并列描述未修改"
    # 新描述必须提及 Copilot 不走此 UA
    assert "Copilot" in desc and "不走" in desc, \
        f"新描述应说明 Copilot 不走 Bingbot UA，实际: {desc!r}"
