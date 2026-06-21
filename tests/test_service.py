"""service.audit_url 网络编排：首页抓取失败不该被当成"页面质量差"误打分（零网络，monkeypatch fetch_text）。"""
import seogeo.service as svc


def test_audit_url_homepage_fetch_failure_warns_not_fail(monkeypatch):
    # 模拟首页抓取失败（DNS/网络/SSRF guard），robots 正常放行
    def fake_fetch_text(url):
        if url == "https://example.com":          # 首页：抓取失败
            return None, "DNS resolution failed"
        if url.endswith("/robots.txt"):
            return "User-agent: *\nAllow: /", None
        return None, None                          # llms / sitemap：当作不存在
    monkeypatch.setattr(svc, "fetch_text", fake_fetch_text)

    by_id = {o.id: o for o in svc.audit_url("https://example.com").outcomes}
    # 内容/结构/渲染等不能 fail 成"没内容"，应 warn"无法获取 HTML"
    for rid in ("content-structure", "structure-jsonld", "rendering-js-visibility"):
        assert by_id[rid].status == "warn", rid
        assert "无法获取首页 HTML" in by_id[rid].message, rid


def test_audit_url_homepage_404_warns_not_fail(monkeypatch):
    # 首页本身 404：fetch_text 把 404 映射成 (None, None)，html_error 为 None。
    # 不该让守卫漏判 → 把空首页误当"页面质量差"而 fail，应当作"抓不到首页"warn。
    def fake_fetch_text(url):
        if url == "https://example.com":
            return None, None                      # 首页 404
        if url.endswith("/robots.txt"):
            return "User-agent: *\nAllow: /", None
        return None, None
    monkeypatch.setattr(svc, "fetch_text", fake_fetch_text)

    by_id = {o.id: o for o in svc.audit_url("https://example.com").outcomes}
    for rid in ("content-structure", "structure-jsonld"):
        assert by_id[rid].status == "warn", rid
        assert "无法获取首页 HTML" in by_id[rid].message, rid


def test_audit_url_homepage_ok_judges_normally(monkeypatch):
    # 边界：首页抓得到（含足量内容）时正常判定，不被守卫误伤
    good = (
        '<html lang="zh-CN"><head><title>X</title></head>'
        "<body><h1>标题</h1><h2>节</h2><p>" + "实质内容。" * 80 + "</p>"
        "<ul><li>一</li></ul></body></html>"
    )

    def fake_fetch_text(url):
        if url == "https://example.com":
            return good, None
        return None, None
    monkeypatch.setattr(svc, "fetch_text", fake_fetch_text)

    by_id = {o.id: o for o in svc.audit_url("https://example.com").outcomes}
    assert by_id["content-structure"].status == "pass"
