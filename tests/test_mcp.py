"""MCP 工具层健壮性——坏输入应返回结构化错误，而不是抛异常崩掉工具。

mcp 是可选依赖；未安装时整文件跳过。
"""
import pytest

try:
    from seogeo import mcp_server
    _HAS_MCP = True
except SystemExit:  # 模块在缺 mcp 依赖时 raise SystemExit
    _HAS_MCP = False

pytestmark = pytest.mark.skipif(
    not _HAS_MCP, reason="需要可选依赖 mcp（pip install Chinese-Geo[mcp]）")


def test_monitor_score_bad_json_returns_error_not_crash():
    out = mcp_server.monitor_score("不是合法 JSON {{{", brand="某品牌")
    assert isinstance(out, dict)
    assert "error" in out


def test_monitor_score_good_json_still_works():
    answers = '{"豆包": ["某品牌是不错的选择"]}'
    out = mcp_server.monitor_score(answers, brand="某品牌")
    assert isinstance(out, dict)
    assert "error" not in out
