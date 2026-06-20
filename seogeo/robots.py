"""robots.txt 解析与按 User-agent 分类。

纯 stdlib、零依赖。语义移植自 Auriti `utils/robots_parser.py`（RFC 9309 子集）：
- 连续的 `User-agent:` 行共享同一组规则；规则行出现后，下一个 `User-agent:` 开启新组。
- `classify_bot` 既判 allowed/blocked，也分辨命中的是"显式 UA 块"还是"仅靠 * 通配"
  （via_wildcard）——Bytespider / 搜狗 对仅靠 * 覆盖的合规度有争议（站长报告、非官方），
  上层规则据此决定是否提醒；其余爬虫按 RFC 9309 遵守 *。

路径匹配：前缀语义 + RFC 9309 的 `*` 通配与结尾 `$` 锚（见 `_pattern_to_regex`），
足够回答"根路径能否被抓"。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Classification:
    status: str  # "allowed" | "blocked" | "missing"
    via_wildcard: bool = False


@dataclass
class _Group:
    agents: list = field(default_factory=list)  # 小写化的 UA token
    rules: list = field(default_factory=list)   # [(kind, path)]，kind ∈ {"allow","disallow"}


def _strip_comment(line: str) -> str:
    i = line.find("#")
    if i != -1:
        line = line[:i]
    return line.strip()


def parse_robots(text: str) -> list:
    """把 robots.txt 文本解析成规则组列表。"""
    groups: list = []
    cur: _Group | None = None
    expecting_agent = False  # 是否处于"连续 User-agent 收集"状态
    for raw in (text or "").splitlines():
        line = _strip_comment(raw)
        if not line or ":" not in line:
            continue
        name, _, value = line.partition(":")
        name = name.strip().lower()
        value = value.strip()
        if name == "user-agent":
            if cur is None or not expecting_agent:
                cur = _Group()
                groups.append(cur)
            cur.agents.append(value.lower())
            expecting_agent = True
        elif name in ("allow", "disallow"):
            if cur is None:
                continue  # 规则出现在任何 UA 之前 → 忽略
            cur.rules.append((name, value))
            expecting_agent = False
    return groups


def _select_group(ua: str, groups: list):
    """返回 (适用组, via_wildcard)。精确匹配优先于 * 通配。"""
    ua_l = ua.lower()
    wildcard = None
    for g in groups:
        if ua_l in g.agents:
            return g, False
        if "*" in g.agents:
            wildcard = g
    if wildcard is not None:
        return wildcard, True
    return None, False


def _pattern_to_regex(pattern: str):
    """robots 路径模式 → 正则。RFC 9309：`*` 匹配任意序列、结尾 `$` 锚定路径末尾；
    其余按前缀语义（不锚结尾，所以 `/admin` 命中 `/admin/x`）。"""
    anchored = pattern.endswith("$")
    core = pattern[:-1] if anchored else pattern
    body = "".join(".*" if ch == "*" else re.escape(ch) for ch in core)
    return re.compile("^" + body + ("$" if anchored else ""))


def _matches(pattern: str, path: str) -> bool:
    return _pattern_to_regex(pattern).match(path) is not None


def _is_root_allowed(group: _Group) -> bool:
    """对路径 '/' 做最长匹配；Allow 与 Disallow 同长度时 Allow 胜（最不受限）。"""
    best_len = -1
    best_kind = None
    for kind, path in group.rules:
        if path == "":  # 空 Disallow = 允许全部，不约束 '/'
            continue
        if _matches(path, "/"):
            plen = len(path)
            if plen > best_len or (plen == best_len and kind == "allow"):
                best_len = plen
                best_kind = kind
    if best_kind is None:
        return True
    return best_kind == "allow"


def classify_bot(ua: str, robots_text: str) -> Classification:
    """判断某 UA 在给定 robots.txt 下能否抓取站点根路径。"""
    groups = parse_robots(robots_text)
    group, via_wildcard = _select_group(ua, groups)
    if group is None:
        return Classification(status="missing", via_wildcard=False)
    allowed = _is_root_allowed(group)
    return Classification(status="allowed" if allowed else "blocked", via_wildcard=via_wildcard)
