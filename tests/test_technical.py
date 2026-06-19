"""technical 类：<html lang> 声明。"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.technical import check_lang


def _ctx(html):
    return AuditContext(url="https://x.com", html=html, dom=scan(html))


def test_lang_present_passes():
    assert check_lang(_ctx('<html lang="zh-CN"></html>')).status == "pass"


def test_lang_missing_warns():
    out = check_lang(_ctx("<html></html>"))
    assert out.status == "warn"
    assert "lang" in out.recommendation.lower()


def test_id():
    assert check_lang(_ctx("")).id == "technical-lang"
