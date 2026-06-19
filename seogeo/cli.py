"""seogeo CLI 入口。

v0：`seogeo audit <url> [--format md|json]` —— 抓 robots/llms/sitemap → 跑全部已注册检查
→ 打分 → 输出中文报告（默认）或 JSON（给 skill/CI）。退出码：有 Critical 问题 → 1，否则 0，用法错 → 2。
"""
from __future__ import annotations

import sys
from urllib.parse import urlparse

from seogeo.fetch import fetch
from seogeo.pipeline import run_audit
from seogeo.report import render_json, render_markdown
from seogeo.rules.base import AuditContext


def _origin(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _fetch_text(url: str):
    """返回 (text | None, error | None)。200→text；404→(None,None) 真不存在；其它→(None,'HTTP xxx')。"""
    resp, err = fetch(url)
    if err:
        return None, err
    if resp["status"] == 200:
        return resp["text"], None
    if resp["status"] == 404:
        return None, None
    return None, f"HTTP {resp['status']}"


def main(argv: list | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2 or argv[0] != "audit":
        print("用法：seogeo audit <域名或URL> [--format md|json]")
        return 2

    fmt = "md"
    if "--format" in argv:
        i = argv.index("--format")
        if i + 1 < len(argv):
            fmt = argv[i + 1]

    origin = _origin(argv[1])
    html, html_err = _fetch_text(origin)
    if html_err:
        print(f"⚠️  无法抓取首页 HTML（{html_err}）—— 结构/内容/渲染类检查将基于空内容",
              file=sys.stderr)
    robots_txt, robots_error = _fetch_text(origin + "/robots.txt")
    llms_txt, _ = _fetch_text(origin + "/llms.txt")
    sitemap_xml, _ = _fetch_text(origin + "/sitemap.xml")

    ctx = AuditContext(url=origin, html=html or "",
                       robots_txt=robots_txt, robots_error=robots_error,
                       llms_txt=llms_txt, sitemap_xml=sitemap_xml)
    result = run_audit(ctx)

    print(render_json(result) if fmt == "json" else render_markdown(result))
    return 1 if any(r["priority"] == "Critical" for r in result.recommendations) else 0


if __name__ == "__main__":
    sys.exit(main())
