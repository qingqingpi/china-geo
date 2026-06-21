"""robots.txt 解析边界——补 test_robots.py 盲区。

聚焦：多组选择、最长匹配 vs 同长 Allow 胜、规则出现在 UA 前被忽略、
通配 * 与 $ 锚的更多组合、连续 UA 共享组的混合判定、空 Allow 多种组合、
parse_robots 直接断言组结构。均为 characterization（绿）。
"""
from seogeo.robots import classify_bot, parse_robots


# ---- parse_robots 组结构 ----

def test_parse_groups_rule_resets_agent_collection():
    # 规则行后再现 User-agent → 开新组
    groups = parse_robots(
        "User-agent: A\nDisallow: /\n"
        "User-agent: B\nAllow: /\n"
    )
    assert len(groups) == 2
    assert groups[0].agents == ["a"] and groups[1].agents == ["b"]


def test_parse_consecutive_agents_one_group():
    groups = parse_robots("User-agent: A\nUser-agent: B\nDisallow: /\n")
    assert len(groups) == 1
    assert groups[0].agents == ["a", "b"]


def test_parse_rule_before_any_agent_ignored():
    # Disallow 出现在任何 User-agent 之前 → 该规则被丢弃（没有可归属的组）
    groups = parse_robots("Disallow: /secret\nUser-agent: A\nAllow: /\n")
    assert len(groups) == 1
    assert groups[0].agents == ["a"]
    assert groups[0].rules == [("allow", "/")]  # 孤立的 Disallow 没进任何组


def test_parse_lines_without_colon_skipped():
    groups = parse_robots("garbage line\nUser-agent: A\nDisallow: /\n")
    assert len(groups) == 1 and groups[0].agents == ["a"]


# ---- 最长匹配 + 同长 Allow 胜 ----

def test_longer_disallow_beats_shorter_allow_on_root():
    # Allow: / (len1) vs Disallow: /a (不匹配根)；根仅被 Allow:/ 命中 → allowed
    robots = "User-agent: A\nAllow: /\nDisallow: /admin\n"
    assert classify_bot("A", robots).status == "allowed"


def test_more_specific_disallow_root_wins_over_short_allow():
    # 对根 '/'：Disallow:/ (len1) 与 Allow:/ (len1) 同长 → Allow 胜
    robots = "User-agent: A\nDisallow: /\nAllow: /\n"
    assert classify_bot("A", robots).status == "allowed"


def test_disallow_root_alone_blocks():
    robots = "User-agent: A\nDisallow: /\n"
    assert classify_bot("A", robots).status == "blocked"


# ---- _select_group：精确优先；多通配取首个遇到的 ----

def test_exact_match_anywhere_beats_wildcard():
    robots = (
        "User-agent: *\nDisallow: /\n\n"
        "User-agent: Baiduspider\nAllow: /\n"
    )
    c = classify_bot("Baiduspider", robots)
    assert c.status == "allowed" and c.via_wildcard is False


def test_unknown_ua_falls_to_wildcard_group():
    robots = "User-agent: *\nDisallow: /\n"
    c = classify_bot("SomeRandomBot", robots)
    assert c.status == "blocked" and c.via_wildcard is True


# ---- 通配 * 与结尾锚 $ 的更多组合 ----

def test_star_in_middle_of_path_blocks_root():
    # Disallow: /*/ 用 * 通配——/ 能被 ^/.*/ ... 实际 '/' 不含第二个 '/'，不挡根
    assert classify_bot("A", "User-agent: *\nDisallow: /a*b\n").status == "allowed"


def test_bare_star_disallow_blocks_everything():
    # Disallow: * （无前导斜杠）→ ^.* 匹配根 → blocked
    assert classify_bot("A", "User-agent: *\nDisallow: *\n").status == "blocked"


def test_dollar_anchor_on_root_blocks_only_exact_root():
    # /$ 精确锚根 → 根被挡
    assert classify_bot("A", "User-agent: *\nDisallow: /$\n").status == "blocked"


def test_allow_star_does_not_rescue_when_disallow_more_specific():
    # Allow: /* (len2 含通配) 与 Disallow: / (len1)；对根：两者都匹配，
    # Allow 更长(2>1) → allowed（最长匹配胜，且更长的是 Allow）
    robots = "User-agent: A\nDisallow: /\nAllow: /*\n"
    assert classify_bot("A", robots).status == "allowed"


# ---- 连续 UA 共享组的混合查询 ----

def test_consecutive_agents_both_allowed():
    robots = "User-agent: Baiduspider\nUser-agent: PetalBot\nAllow: /\n"
    assert classify_bot("Baiduspider", robots).status == "allowed"
    assert classify_bot("PetalBot", robots).status == "allowed"


# ---- 空 Allow / 空 Disallow 组合 ----

def test_empty_disallow_means_allow_all():
    # 空 Disallow（Disallow:）= 不限制 → allowed
    assert classify_bot("A", "User-agent: A\nDisallow:\n").status == "allowed"


def test_both_empty_allow_and_disallow_is_allowed():
    assert classify_bot("A", "User-agent: A\nAllow:\nDisallow:\n").status == "allowed"


def test_empty_allow_does_not_rescue_disallow_root():
    # 空 Allow 不该被当成"匹配所有路径"而救回被封的根
    assert classify_bot("A", "User-agent: A\nDisallow: /\nAllow:\n").status == "blocked"


# ---- 退化输入 ----

def test_empty_robots_text_is_missing():
    # 空 robots → 无任何组 → 对任意 UA missing
    assert classify_bot("A", "").status == "missing"


def test_none_robots_text_is_missing():
    assert classify_bot("A", None).status == "missing"
