"""人工验证清单 docs/verify/VERIFY-<name>.md：

loop 只备**模板**（确定性落点已自动填），真 agent 里的实跑结果（transcript/截图）⏳ 由人补。
- 8 家都有；接入落点与 build_agent_bundle 一致（防漂移——别让人去核对错的文件）；
- 含 ⏳ 待人工填 + 勾选框 + chinese-geo 命令；术语中性。
"""
import os

import pytest

from seogeo.generate import build_agent_bundle

_VERIFY = os.path.join(os.path.dirname(__file__), os.pardir, "docs", "verify")
_AGENTS = ["claude", "codex", "codebuddy", "kimi", "opencode", "qoder", "trae", "lingma"]


def _doc(name: str) -> str:
    with open(os.path.join(_VERIFY, f"VERIFY-{name}.md"), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("agent", _AGENTS)
def test_verify_checklist_exists(agent):
    assert os.path.exists(os.path.join(_VERIFY, f"VERIFY-{agent}.md")), f"缺 docs/verify/VERIFY-{agent}.md"


@pytest.mark.parametrize("agent", _AGENTS)
def test_verify_lists_real_landing_files(agent):
    # 验证清单里的接入落点必须与 build_agent_bundle 一致（别让人去核对错的文件）
    doc = _doc(agent)
    for fname in build_agent_bundle(agent):
        assert fname in doc, f"{agent} 验证清单应列出落点 {fname}"


@pytest.mark.parametrize("agent", _AGENTS)
def test_verify_has_human_fill_and_checkboxes(agent):
    doc = _doc(agent)
    assert "⏳" in doc                              # 实跑结果留给人填，不编造
    assert "- [ ]" in doc                           # 可勾选清单
    assert f"init --agent {agent}" in doc           # 指明用哪条命令接入
    assert "chinese-geo audit" in doc               # 必过的 CLI 直调验证


@pytest.mark.parametrize("agent", _AGENTS)
def test_verify_terminology_neutral(agent):
    doc = _doc(agent)
    assert chr(0x4e2d) + chr(0x56fd) not in doc  # 不含"中国"
    assert chr(0x897f) + chr(0x65b9) not in doc  # 不含"西方"
