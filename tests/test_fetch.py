"""抓取层的 SSRF 防护——CLI 会抓任意用户给的 URL，必须挡掉私网/云元数据地址。

参考 Auriti `validators.py` 的 _BLOCKED_NETWORKS 思路，用 stdlib `ipaddress` 复刻。
"""
from seogeo.fetch import _ip_is_blocked, is_safe_url


def test_loopback_ip_blocked():
    assert _ip_is_blocked("127.0.0.1") is True


def test_cloud_metadata_ip_blocked():
    # 169.254.169.254 是云厂商元数据端点（link-local），SSRF 头号目标
    assert _ip_is_blocked("169.254.169.254") is True


def test_private_ips_blocked():
    for ip in ["10.0.0.5", "192.168.1.1", "172.16.0.1"]:
        assert _ip_is_blocked(ip) is True


def test_public_ip_not_blocked():
    assert _ip_is_blocked("8.8.8.8") is False


def test_ipv6_loopback_blocked():
    assert _ip_is_blocked("::1") is True


def test_unparseable_ip_blocked_conservatively():
    assert _ip_is_blocked("not-an-ip") is True


def test_non_http_scheme_rejected():
    assert is_safe_url("ftp://example.com/x") is False
    assert is_safe_url("file:///etc/passwd") is False


def test_safe_url_blocks_localhost():
    assert is_safe_url("http://127.0.0.1/") is False


def test_safe_url_allows_public_ip_literal():
    # 8.8.8.8 是 IP 字面量，getaddrinfo 直接返回、无需真实 DNS
    assert is_safe_url("http://8.8.8.8/") is True
