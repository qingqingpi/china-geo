"""国内社媒 / 站外平台矩阵（差异化核心）：按引擎喂养 × 受众 × 开放/封闭 多角度。

把 offsite skill 里的平台知识沉成确定性数据 + 查询（"确定性→CLI"原则）。
"""
from seogeo.data.platforms import DOMESTIC_PLATFORMS
from seogeo.offsite import closed_platforms, cross_post_set, recommend


def test_matrix_covers_key_domestic_platforms():
    names = " ".join(p.name for p in DOMESTIC_PLATFORMS)
    for key in ("知乎", "CSDN", "公众号", "小红书", "百家号"):
        assert key in names


def test_every_platform_feeds_at_least_one_engine():
    for p in DOMESTIC_PLATFORMS:
        assert p.engines, f"{p.name} 未标注喂哪个引擎"


def test_filter_by_engine_doubao():
    res = recommend(engine="豆包")
    assert res
    assert all("豆包" in p.engines for p in res)
    assert any("头条" in p.name or "抖音" in p.name for p in res)  # 字节系喂豆包


def test_filter_by_audience_b2b_includes_csdn_excludes_consumer_only():
    names = {p.name for p in recommend(audience="b2b")}
    assert any("CSDN" in n for n in names)
    assert not any("小红书" in n for n in names)  # 纯消费平台不进 b2b


def test_closed_platforms_flag_xiaohongshu_and_douyin():
    closed = " ".join(p.name for p in closed_platforms())
    assert "小红书" in closed and "抖音" in closed  # 封闭型：自家 AI 只引自己


def test_cross_post_set_is_multi_platform():
    cp = cross_post_set()
    assert len(cp) >= 4
    assert any("CSDN" in x for x in cp)


def test_recommend_no_filter_returns_all():
    assert len(recommend()) == len(DOMESTIC_PLATFORMS)
