"""版本号工具 + 一键发版编排（被 .github/workflows/publish.yml 的按钮路径调用，也可本地跑）。

单一事实源 = pyproject.toml 的 version；bump 时把 4 个 manifest 一起改齐，
配合 tests/test_version_sync.py 护栏杜绝漂移。

纯函数（bump / current_version / set_version / format_release_notes）可单测；
main() 是薄胶水：实际读写文件 + 跑 git log 取更新日志。仅用标准库。

用法：
  python -m seogeo.versioning bump <major|minor|patch>   # 改 4 处版本号，打印新版本
  python -m seogeo.versioning notes <vX.Y.Z>             # 打印自上个 tag 以来的更新日志
"""
from __future__ import annotations

import re
import subprocess
import sys

_LEVELS = ("major", "minor", "patch")

# 改动版本号的 4 个文件（相对仓库根；发版工作流在仓库根运行）
_MANIFESTS = (
    "pyproject.toml",
    "seogeo/__init__.py",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
)

# 三种写法各一条正则；对任一文件只有匹配的那条会命中，其余 no-op
_VERSION_PATTERNS = (
    re.compile(r'(__version__\s*=\s*)"[^"]*"'),      # seogeo/__init__.py
    re.compile(r'(?m)(^version\s*=\s*)"[^"]*"'),     # pyproject.toml
    re.compile(r'("version"\s*:\s*)"[^"]*"'),        # *.json（含多处则全改，保持同步）
)


def bump(version: str, level: str) -> str:
    """语义化递增：major 进位清零次/修订，minor 进位清零修订，patch +1。"""
    if level not in _LEVELS:
        raise ValueError(f"未知递增级别：{level}（应为 {' / '.join(_LEVELS)}）")
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if not m:
        raise ValueError(f"版本号格式应为 X.Y.Z：{version!r}")
    major, minor, patch = (int(x) for x in m.groups())
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def current_version(pyproject_text: str) -> str:
    """从 pyproject.toml 文本里读当前版本（单一事实源）。"""
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject_text)
    if not m:
        raise ValueError("pyproject.toml 里找不到 version")
    return m.group(1)


def set_version(text: str, new_version: str) -> str:
    """把文本里的版本号改成 new_version（toml / python / json 通吃）。"""
    for pat in _VERSION_PATTERNS:
        text = pat.sub(rf'\g<1>"{new_version}"', text)
    return text


def format_release_notes(tag: str, commit_subjects: list) -> str:
    """把"自上个 tag 以来的提交标题"排成 Markdown 更新日志。"""
    lines = [f"## Chinese-Geo {tag}", ""]
    cleaned = [s for s in commit_subjects if s and not s.startswith("chore: release ")]
    lines += [f"- {s}" for s in cleaned] if cleaned else ["- 维护性更新"]
    lines += ["", "**安装**：`pip install chinese-geo`（命令 `seogeo`）"]
    return "\n".join(lines)


# ---- 薄胶水（文件 I/O + git）----

def _apply_bump(level: str) -> str:
    with open("pyproject.toml", encoding="utf-8") as f:
        new_version = bump(current_version(f.read()), level)
    for path in _MANIFESTS:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(set_version(text, new_version))
    return new_version


def _git_subjects_since_last_tag() -> list:
    last = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True,
    ).stdout.strip()
    rng = [f"{last}..HEAD"] if last else []
    out = subprocess.run(
        ["git", "log", *rng, "--no-merges", "--pretty=%s"],
        capture_output=True, text=True,
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) == 2 and argv[0] == "bump":
        print(_apply_bump(argv[1]))
        return 0
    if len(argv) == 2 and argv[0] == "notes":
        print(format_release_notes(argv[1], _git_subjects_since_last_tag()))
        return 0
    print("用法：python -m seogeo.versioning bump <major|minor|patch> | notes <vX.Y.Z>",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
