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


# ---- websearch 索引层（平台 → 被哪个搜索索引 → 引擎联网后端）----

def test_every_platform_declares_search_index():
    for p in DOMESTIC_PLATFORMS:
        assert p.indexed_by, f"{p.name} 未标注被哪个 websearch 索引"


def test_wechat_official_is_sogou_gated():
    gz = next(p for p in DOMESTIC_PLATFORMS if "公众号" in p.name)
    assert "搜狗" in gz.indexed_by  # 公众号锁在搜狗（微信搜一搜）


def test_toutiao_indexed_by_bytedance_own_search():
    tt = next(p for p in DOMESTIC_PLATFORMS if "头条" in p.name)
    assert "头条搜索" in tt.indexed_by  # 字节自家搜索，百度索引不到


def test_open_platform_zhihu_broadly_indexed():
    zh = next(p for p in DOMESTIC_PLATFORMS if p.name == "知乎")
    assert "百度" in zh.indexed_by  # 开放站，被多搜索广泛索引


# ---- open 字段语义：True=能被外部主流搜索（百度/Bing/Google）广泛索引 ----

def test_wechat_official_is_closed():
    """公众号只锁搜狗/微信搜一搜，外部百度/Google 基本搜不到正文 → open=False。"""
    gz = next(p for p in DOMESTIC_PLATFORMS if "公众号" in p.name)
    assert gz.open is False, "微信公众号对外部搜索近封闭，open 应为 False"


def test_weixin_video_is_closed():
    """视频号外部索引弱，不被外部主流搜索广泛覆盖 → open=False。"""
    vz = next(p for p in DOMESTIC_PLATFORMS if "视频号" in p.name)
    assert vz.open is False, "视频号对外部搜索近封闭，open 应为 False"


def test_closed_platforms_includes_wechat_official_and_video():
    """closed_platforms() 应包含公众号与视频号。"""
    closed_names = " ".join(p.name for p in closed_platforms())
    assert "公众号" in closed_names, "closed_platforms() 应包含微信公众号"
    assert "视频号" in closed_names, "closed_platforms() 应包含视频号"


def test_recommend_by_engine_still_returns_wechat_official():
    """open=False 不影响 recommend() 按引擎过滤结果（元宝主力平台仍可被推荐）。"""
    res = recommend(engine="元宝")
    names = [p.name for p in res]
    assert any("公众号" in n for n in names), "按元宝过滤后仍应包含公众号"


def test_recommend_by_audience_still_returns_video():
    """open=False 不影响 recommend() 按受众过滤结果（视频号仍属 consumer）。"""
    res = recommend(audience="consumer")
    names = [p.name for p in res]
    assert any("视频号" in n for n in names), "按 consumer 受众过滤后仍应包含视频号"
