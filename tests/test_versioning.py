"""版本号工具纯函数（被一键发版工作流调用）——TDD 先行。"""
import pytest

from seogeo.versioning import bump, current_version, format_release_notes, set_version


# ---- bump：语义化递增 ----

def test_bump_patch():
    assert bump("0.1.1", "patch") == "0.1.2"


def test_bump_minor_resets_patch():
    assert bump("0.1.9", "minor") == "0.2.0"


def test_bump_major_resets_minor_and_patch():
    assert bump("1.2.3", "major") == "2.0.0"


def test_bump_rejects_unknown_level():
    with pytest.raises(ValueError):
        bump("0.1.1", "huge")


def test_bump_rejects_malformed_version():
    with pytest.raises(ValueError):
        bump("1.2", "patch")


# ---- current_version：从 pyproject 文本读 ----

def test_current_version_from_pyproject_text():
    text = '[project]\nname = "x"\nversion = "3.4.5"\n'
    assert current_version(text) == "3.4.5"


# ---- set_version：按文件格式改写（toml / python / json 同一函数搞定）----

def test_set_version_in_toml():
    assert 'version = "0.2.0"' in set_version('version = "0.1.1"\n', "0.2.0")


def test_set_version_in_python_dunder():
    assert set_version('__version__ = "0.1.1"\n', "0.2.0") == '__version__ = "0.2.0"\n'


def test_set_version_in_json():
    assert '"version": "0.2.0"' in set_version('  "version": "0.1.1",\n', "0.2.0")


def test_set_version_leaves_unrelated_numbers_untouched():
    text = 'requires-python = ">=3.9"\nversion = "0.1.1"\n'
    out = set_version(text, "0.2.0")
    assert '">=3.9"' in out           # 没误伤其它带引号的数字
    assert 'version = "0.2.0"' in out


# ---- format_release_notes：自动更新日志 ----

def test_release_notes_include_version_and_commits():
    notes = format_release_notes("v0.2.0", ["feat: 加表格检测", "fix: 修空壳判断"])
    assert "0.2.0" in notes
    assert "加表格检测" in notes
    assert "修空壳判断" in notes


def test_release_notes_skip_release_chore_commits():
    notes = format_release_notes("v0.2.0", ["chore: release v0.1.9", "feat: 真功能"])
    assert "真功能" in notes
    assert "release v0.1.9" not in notes      # 发版提交自身不进日志


def test_release_notes_handle_no_commits():
    notes = format_release_notes("v0.2.0", [])
    assert "0.2.0" in notes                    # 没新提交也不崩，仍有标题
