"""护栏：4 个 manifest 的版本号必须始终一致——杜绝漏改漂移。

一键发版用 seogeo.versioning 同时改这 4 处；万一手动只改了部分，这个测试会红。
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _toml_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return re.search(r'(?m)^version\s*=\s*"([^"]+)"', text).group(1)


def _dunder_version() -> str:
    text = (ROOT / "seogeo" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__\s*=\s*"([^"]+)"', text).group(1)


def _plugin_version() -> str:
    return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def _marketplace_version() -> str:
    data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    return data["plugins"][0]["version"]


def test_all_four_manifests_share_one_version():
    versions = {
        "pyproject.toml": _toml_version(),
        "seogeo/__init__.py": _dunder_version(),
        ".claude-plugin/plugin.json": _plugin_version(),
        ".claude-plugin/marketplace.json": _marketplace_version(),
    }
    assert len(set(versions.values())) == 1, f"版本号漂移：{versions}"
