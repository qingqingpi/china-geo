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


def audit_url(url: str) -> AuditResult:
    origin = origin_of(url)
    html, html_error = fetch_text(origin)  # 保留首页抓取错误，别让"抓不到"被当成"空页面"假打分
    robots_txt, robots_error = fetch_text(origin + "/robots.txt")
    llms_txt, _ = fetch_text(origin + "/llms.txt")
    sitemap_xml, _ = fetch_text(origin + "/sitemap.xml")

    bytespider_blocked = None
    if robots_txt and classify_bot("Bytespider", robots_txt).status == "blocked":
        bytespider_blocked = probe_bytespider_blocked(origin)

    ctx = AuditContext(url=origin, html=html or "", html_error=html_error,
                       robots_txt=robots_txt, robots_error=robots_error,
                       llms_txt=llms_txt, sitemap_xml=sitemap_xml,
                       bytespider_blocked=bytespider_blocked)
    return run_audit(ctx)
