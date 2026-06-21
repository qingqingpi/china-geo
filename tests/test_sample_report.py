"""真实样例 audit 报告 examples/sample-report.md：由 `chinese-geo audit` 实跑落盘（真实输出、非手写）。"""
import os

_REPORT = os.path.join(os.path.dirname(__file__), os.pardir, "examples", "sample-report.md")


def _read() -> str:
    with open(_REPORT, encoding="utf-8") as f:
        return f.read()


def test_sample_report_exists():
    assert os.path.exists(_REPORT), "缺 examples/sample-report.md"


def test_sample_report_is_real_audit_output():
    r = _read()
    assert "chinese-geo 体检报告" in r        # render_markdown 的真实标题
    assert "总分" in r and "/100" in r          # 真实分数
    assert "优先级修复清单" in r                 # 真实清单结构
    assert "https://example.com" in r           # 被审计的真实公开站


def test_sample_report_terminology_neutral():
    r = _read()
    assert chr(0x4e2d) + chr(0x56fd) not in r  # 不含"中国"
    assert chr(0x897f) + chr(0x65b9) not in r  # 不含"西方"
