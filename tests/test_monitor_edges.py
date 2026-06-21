"""引用监控边界：除零、空样本、别名、CJK 子串推进、_overall 加权退化。

补 test_monitor.py 盲区，聚焦"分母为 0 不崩"与计数语义。均为 characterization（绿）。
"""
from seogeo.monitor import (
    _count_occurrences,
    count_mentions,
    score_answers,
    verdict,
)


# ---- 除零守卫：答题数 0 / 提及池 0 ----

def test_all_empty_answers_no_division_error():
    # 全空白回答 → answered=0，citation_rate / share_of_voice 均退化为 0.0，不抛 ZeroDivisionError
    r = score_answers({"豆包": ["", "   ", None]}, brand="X", brand_aliases=[], competitors={})
    assert r["豆包"]["answered"] == 0
    assert r["豆包"]["citation_rate"] == 0.0
    assert r["豆包"]["share_of_voice"] == 0.0


def test_empty_answers_dict_only_overall():
    # 完全没有引擎数据 → 只剩 _overall=0.0，不崩
    r = score_answers({}, brand="X", brand_aliases=[], competitors={})
    assert r == {"_overall": {"citation_rate": 0.0}}


def test_sov_zero_when_nobody_mentioned():
    # 本品牌与竞品都没出现 → pool=0 → SoV 0.0（除零守卫）
    r = score_answers({"e": ["这里没有任何品牌"]}, brand="X", brand_aliases=[],
                      competitors={"Y": []})
    assert r["e"]["share_of_voice"] == 0.0


def test_sov_is_one_when_only_brand_no_competitors():
    # 只有本品牌、无竞品 → pool=brand_total → SoV=1.0
    r = score_answers({"e": ["X 真好，X 推荐"]}, brand="X", brand_aliases=[], competitors={})
    assert r["e"]["share_of_voice"] == 1.0


# ---- 别名计入品牌提及 ----

def test_brand_alias_counts_as_brand_mention():
    r = score_answers({"e": ["我选深度求索"]}, brand="DeepSeek",
                      brand_aliases=["深度求索"], competitors={})
    assert r["e"]["brand_mentions"] == 1
    assert r["e"]["citation_rate"] == 1.0


def test_competitor_alias_counts_in_pool():
    # 竞品有别名时 count_mentions 对每个名字各自计数（名 + 别名分别命中、不去重）：
    # "通义千问" 命中 "通义"(1) 与 "通义千问"(1) 共 2 → pool=本1+竞2=3 → SoV=1/3。
    r = score_answers({"e": ["X 和 通义千问"]}, brand="X", brand_aliases=[],
                      competitors={"通义": ["通义千问"]})
    assert r["e"]["share_of_voice"] == round(1 / 3, 3)


def test_competitor_single_name_counts_once():
    # 竞品仅一个名（无重叠别名）→ pool=本1+竞1 → SoV=0.5
    r = score_answers({"e": ["X 和 竞品B"]}, brand="X", brand_aliases=[],
                      competitors={"竞品B": []})
    assert r["e"]["share_of_voice"] == 0.5


# ---- count_mentions：空 / None 名称被跳过 ----

def test_count_mentions_skips_empty_and_none_names():
    assert count_mentions("abc 出现", ["", None, "abc"]) == 1


def test_count_mentions_empty_text():
    assert count_mentions("", ["豆包"]) == 0


# ---- _count_occurrences：ASCII 词边界 vs CJK 子串推进 ----

def test_occurrences_empty_keyword_is_zero():
    assert _count_occurrences("任意文本", "") == 0


def test_occurrences_ascii_word_boundary_blocks_substring():
    assert _count_occurrences("DeepSeeker", "DeepSeek") == 0  # 后缀不算


def test_occurrences_cjk_non_overlapping_advance():
    # CJK 子串按 len(kw) 前进，不重叠：'啊啊啊' 里找 '啊啊' 只计 1 次
    assert _count_occurrences("啊啊啊", "啊啊") == 1


def test_occurrences_cjk_disjoint_counts_each():
    assert _count_occurrences("豆包好，豆包棒", "豆包") == 2


def test_occurrences_ascii_case_insensitive():
    assert _count_occurrences("OpenAI 与 openai", "OpenAI") == 2


# ---- _overall 加权退化：单引擎时等于该引擎引用率 ----

def test_overall_single_engine_equals_its_rate():
    r = score_answers({"e": ["X 在", "无", "X 又在"]}, brand="X",
                      brand_aliases=[], competitors={})
    # 3 题答了，2 题命中 → 0.667；_overall 单引擎应一致
    assert r["e"]["citation_rate"] == round(2 / 3, 3)
    assert r["_overall"]["citation_rate"] == round(2 / 3, 3)


def test_overall_skips_engine_with_zero_answered():
    # 一个引擎全空（answered=0）不应让 _overall 除零；以有效引擎为准
    answers = {"满": ["X", "X"], "空": ["", "  "]}
    r = score_answers(answers, brand="X", brand_aliases=[], competitors={})
    assert r["空"]["answered"] == 0
    # total_answered = 2（仅"满"），total_hits=2 → 1.0
    assert r["_overall"]["citation_rate"] == 1.0


# ---- verdict 阈值边界（10% / 30% 端点）----

def test_verdict_boundaries():
    assert verdict(0.0) == "差"
    assert verdict(0.099) == "差"
    assert verdict(0.1) == "良"   # 10% 进"良"
    assert verdict(0.3) == "良"   # 30% 含在"良"
    assert verdict(0.301) == "优"
