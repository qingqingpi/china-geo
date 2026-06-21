"""真实站点案例研究模板 docs/case-study/TEMPLATE.md：

loop 只备**结构**（固定字段 / 采集 schema / 步骤是确定性的）；真实数据（站点/分数/引用率）
⏳ 由人填——需真站 + 真 key + 时间，绝不编造。
"""
import json
import os
import re

_TEMPLATE = os.path.join(os.path.dirname(__file__), os.pardir, "docs", "case-study", "TEMPLATE.md")


def _read() -> str:
    with open(_TEMPLATE, encoding="utf-8") as f:
        return f.read()


def test_template_exists():
    assert os.path.exists(_TEMPLATE), "缺 docs/case-study/TEMPLATE.md"


def test_template_has_required_fields_and_human_fill():
    t = _read()
    for field in ("站点", "总分", "引用率", "SoV"):
        assert field in t, f"案例模板应含字段：{field}"
    assert "⏳" in t                          # 真实数据留人填、不编造
    assert "chinese-geo audit" in t           # 体检前后用 audit
    assert "chinese-geo monitor" in t         # 引用率前后用 monitor


def test_template_has_parseable_collection_schema():
    t = _read()
    block = re.search(r"```json\n(.*?)\n```", t, re.S).group(1)
    schema = json.loads(block)                # 采集 schema 必须是合法 JSON
    assert "audit_before" in schema and "audit_after" in schema
    assert "monitor_before" in schema and "monitor_after" in schema


def test_template_terminology_neutral():
    t = _read()
    assert chr(0x4e2d) + chr(0x56fd) not in t  # 不含"中国"
    assert chr(0x897f) + chr(0x65b9) not in t  # 不含"西方"
