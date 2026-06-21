"""杂项边界加固：generate / botverify / versioning / offsite / CLI 退化路径。

均为零网络、对当前行为为绿的 characterization + 边界。
"""
from __future__ import annotations

import json

import pytest

from seogeo.botverify import looks_blocked, verify_bot_ip
from seogeo.cli import main
from seogeo.data.domestic_bots import DOMESTIC_BOT_RDNS
from seogeo.generate import (
    build_agent_bundle,
    generate_llms,
    generate_robots,
)
from seogeo.offsite import recommend
from seogeo.versioning import bump, current_version, set_version


# ============ generate_robots ============

def test_robots_no_overseas_omits_overseas_bots():
    out = generate_robots(allow_overseas=False)
    assert "GPTBot" not in out
    assert "PerplexityBot" not in out
    assert "Baiduspider" in out  # 国内仍在


def test_robots_both_disabled_still_has_wildcard():
    out = generate_robots(allow_domestic=False, allow_overseas=False)
    assert "User-agent: *" in out
    assert "Baiduspider" not in out and "GPTBot" not in out


def test_robots_sitemap_http_allowed():
    assert "Sitemap: http://x.com/s.xml" in generate_robots(sitemap_url="http://x.com/s.xml")


def test_robots_sitemap_whitespace_only_ignored():
    out = generate_robots(sitemap_url="   ")
    assert "Sitemap:" not in out


def test_robots_ends_with_single_newline():
    # 输出规整：rstrip 后补一个换行
    out = generate_robots()
    assert out.endswith("\n") and not out.endswith("\n\n")


# ============ generate_llms ============

def test_llms_renders_multiple_links():
    out = generate_llms("站", links=[
        ("页1", "https://x.com/1", "讲1"),
        ("页2", "https://x.com/2"),  # 无描述（2 元组）
    ])
    assert "[页1](https://x.com/1): 讲1" in out
    # 第二条是 2 元组无描述 → 渲染成裸链接行，结尾无 ": 描述"
    assert "- [页2](https://x.com/2)\n" in out


def test_llms_default_summary_placeholder_when_none():
    out = generate_llms("站")
    assert "<一句话介绍" in out  # 未给 summary → 占位符


# ============ build_agent_bundle（补 generic / 落点）============

def test_agent_bundle_generic_uses_agents_md_and_standard_mcp():
    b = build_agent_bundle("generic")
    assert "AGENTS.md" in b
    assert ".mcp.json" in b
    assert "chinese-geo" in json.loads(b[".mcp.json"])["mcpServers"]


def test_agent_bundle_codex_uses_agents_md():
    b = build_agent_bundle("codex")
    assert "AGENTS.md" in b and ".mcp.json" in b


def test_agent_bundle_case_insensitive_agent_name():
    # build_agent_bundle 入口 .lower() → 大写也认
    assert "CLAUDE.md" in build_agent_bundle("CLAUDE")


# ============ botverify.looks_blocked 边界 ============

def test_looks_blocked_exactly_30pct_not_blocked():
    # botlen == 0.3 * blen 恰好不触发（严格小于才算被截断）
    assert looks_blocked({"status": 200, "text": "x" * 1000},
                         {"status": 200, "text": "x" * 300}) is False


def test_looks_blocked_just_under_30pct_blocked():
    assert looks_blocked({"status": 200, "text": "x" * 1000},
                         {"status": 200, "text": "x" * 299}) is True


def test_looks_blocked_both_empty_not_blocked():
    # 两边都空（blen=0）→ 短内容判据不成立 → False
    assert looks_blocked({"status": 200, "text": ""},
                         {"status": 200, "text": ""}) is False


def test_looks_blocked_all_block_statuses():
    for code in (403, 429, 451, 503):
        assert looks_blocked({"status": 200, "text": "x" * 100},
                             {"status": code, "text": "denied"}) is True


def test_looks_blocked_captcha_challenge_detected():
    assert looks_blocked({"status": 200, "text": "x" * 1000},
                         {"status": 200, "text": "请完成 CAPTCHA 验证"}) is True


# ============ verify_bot_ip：每个有 rDNS 落点的爬虫 ============

@pytest.mark.parametrize("bot,suffix", list(DOMESTIC_BOT_RDNS.items()))
def test_verify_genuine_for_each_known_bot(bot, suffix):
    host = "node" + suffix  # 以官方后缀结尾的反向解析
    assert verify_bot_ip("203.0.113.7", bot,
                         reverse=lambda ip: host,
                         forward=lambda h: ["203.0.113.7"]) is True


def test_verify_forward_mismatch_is_false():
    bot, suffix = next(iter(DOMESTIC_BOT_RDNS.items()))
    assert verify_bot_ip("203.0.113.7", bot,
                         reverse=lambda ip: "node" + suffix,
                         forward=lambda h: ["8.8.8.8"]) is False


def test_verify_unknown_bot_returns_false_without_dns():
    # 未知爬虫（无 rDNS 后缀）直接 False，不调用 resolver
    called = {"reverse": False}

    def reverse(ip):
        called["reverse"] = True
        return "x"

    assert verify_bot_ip("1.2.3.4", "无此爬虫", reverse=reverse, forward=lambda h: []) is False
    assert called["reverse"] is False  # 提前短路，未做 DNS


# ============ versioning 边界 ============

def test_bump_strips_surrounding_whitespace():
    assert bump("  1.2.3  ", "patch") == "1.2.4"


def test_bump_multi_digit_components():
    assert bump("10.20.30", "minor") == "10.21.0"
    assert bump("10.20.30", "major") == "11.0.0"


def test_set_version_no_version_line_unchanged():
    text = 'name = "x"\ndescription = "y"\n'
    assert set_version(text, "9.9.9") == text


def test_current_version_missing_raises():
    with pytest.raises(ValueError):
        current_version("no version anywhere")


def test_set_version_json_multiple_occurrences_all_updated():
    # *.json 里多处 "version" 应全部同步
    text = '{"version": "0.1.0", "deps": {"version": "0.1.0"}}'
    out = set_version(text, "0.2.0")
    assert out.count('"0.2.0"') == 2
    assert "0.1.0" not in out


# ============ offsite / CLI 退化 ============

def test_offsite_recommend_empty_on_bogus_engine():
    assert recommend(engine="不存在的引擎") == []


def test_offsite_recommend_empty_on_bogus_audience():
    assert recommend(audience="nobody") == []


def test_cli_offsite_no_match_exits_zero_with_hint(capsys):
    # 无匹配平台 → 退出 0 + 友好提示（不崩、不空白）
    assert main(["offsite", "--engine", "不存在的引擎"]) == 0
    out = capsys.readouterr().out
    assert "没有匹配平台" in out


def test_cli_offsite_filter_by_engine_lists_platforms(capsys):
    assert main(["offsite", "--engine", "元宝"]) == 0
    out = capsys.readouterr().out
    assert "公众号" in out  # 元宝主力平台


def test_cli_monitor_run_no_key_exits_2(capsys, monkeypatch):
    # 无任何 API key → run 提示配 key 并退出 2（不发任何网络请求）
    monkeypatch.setattr("seogeo.cli.available_engines", lambda: [])
    code = main(["monitor", "run", "--industry", "智能客服", "--brand", "X"])
    assert code == 2
    assert "API key" in capsys.readouterr().out


def test_cli_monitor_score_missing_brand_exits_2(capsys):
    assert main(["monitor", "score", "--answers", "x.json"]) == 2
    assert "brand" in capsys.readouterr().out.lower()
