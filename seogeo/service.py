"""audit 的网络编排：抓取 + Bytespider 探测 + 跑管线 → AuditResult。

抽出来给 CLI 和 MCP server 共用（确定性打分逻辑在 pipeline，这里只做 I/O 编排）。
"""
from __future__ import annotations

from urllib.parse import urlparse

from seogeo.botverify import probe_bytespider_blocked
from seogeo.fetch import fetch
from seogeo.pipeline import run_audit
from seogeo.report import AuditResult
from seogeo.robots import classify_bot
from seogeo.rules.base import AuditContext


def origin_of(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def fetch_text(url: str):
    """返回 (text | None, error | None)。200→text；404→(None,None)；其它→(None,'HTTP xxx')。"""
    resp, err = fetch(url)
    if err:
        return None, err
    if resp["status"] == 200:
        return resp["text"], None
    if resp["status"] == 404:
        return None, None
    return None, f"HTTP {resp['status']}"


def audit_url(url: str, render: bool = False) -> AuditResult:
    origin = origin_of(url)
    html, html_error = fetch_text(origin)  # 保留首页抓取错误，别让"抓不到"被当成"空页面"假打分
    if html is None and html_error is None:  # 首页 404：fetch_text 把 404 映射成 (None, None)；
        html_error = "首页返回 404 或无内容"  # 对首页而言这是"抓不到"，不是"页面真空白"，须让守卫生效
    robots_txt, robots_error = fetch_text(origin + "/robots.txt")
    llms_txt, _ = fetch_text(origin + "/llms.txt")
    sitemap_xml, _ = fetch_text(origin + "/sitemap.xml")

    rendered_html = None
    if render:  # 可选：装了 [render] extra 才会真渲染；否则降级 None，rendering 规则退回启发式
        from seogeo import render as render_mod
        rendered_html = render_mod.render_html(origin)

    bytespider_blocked = None
    if robots_txt and classify_bot("Bytespider", robots_txt).status == "blocked":
        bytespider_blocked = probe_bytespider_blocked(origin)

    ctx = AuditContext(url=origin, html=html or "", html_error=html_error,
                       robots_txt=robots_txt, robots_error=robots_error,
                       llms_txt=llms_txt, sitemap_xml=sitemap_xml,
                       rendered_html=rendered_html,
                       bytespider_blocked=bytespider_blocked)
    return run_audit(ctx)
