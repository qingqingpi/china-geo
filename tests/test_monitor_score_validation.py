"""回归：monitor score 对畸形 answers（值非字符串列表）须报错而非崩栈。

Bug：score_answers 直接 t.strip()，喂 {"豆包": [123]} 在 CLI 与 MCP 两条路径都抛
AttributeError。修复＝score_answers 校验形状抛 ValueError（允许 None＝未答），
CLI 返 2、MCP 返 {error}。
"""
from __future__ import annotations

import json

import pytest

from seogeo.cli import main
from seogeo.mcp_server import monitor_score
from seogeo.monitor import score_answers


def test_score_answers_rejects_non_string_item():
    with pytest.raises(ValueError):
        score_answers({"豆包": [123, 456]}, brand="X", brand_aliases=[], competitors={})


def test_score_answers_rejects_non_list_value():
    with pytest.raises(ValueError):
        score_answers({"豆包": "not a list"}, brand="X", brand_aliases=[], competitors={})


def test_score_answers_rejects_non_dict():
    with pytest.raises(ValueError):
        score_answers([1, 2], brand="X", brand_aliases=[], competitors={})


def test_score_answers_allows_none_items():
    # null = 未答该题，应优雅跳过、不报错（保留既有行为）
    r = score_answers({"e": [None, "X 很好"]}, brand="X", brand_aliases=[], competitors={})
    assert r["e"]["answered"] == 1


def test_cli_monitor_score_bad_item_returns_2_not_crash(tmp_path):
    p = tmp_path / "a.json"
    p.write_text(json.dumps({"豆包": [123, 456]}), encoding="utf-8")
    assert main(["monitor", "score", "--answers", str(p), "--brand", "X"]) == 2


def test_mcp_monitor_score_bad_item_returns_error_not_crash():
    r = monitor_score(json.dumps({"豆包": [123]}), "X")
    assert "error" in r


def test_mcp_monitor_score_json_array_returns_error_not_crash():
    r = monitor_score(json.dumps([1, 2]), "X")
    assert "error" in r
