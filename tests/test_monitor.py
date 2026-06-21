"""引用监控核心（零 key，确定性部分）。

- generate_prompts：去品牌化 prompt 矩阵（让 AI 自己推荐，再看引不引你）。
- count_mentions：中文友好的提及计数（词典子串匹配，不靠"首字母大写"——gego 那套对中文失效）。
- score_answers：按引擎算 引用率（被引问题数÷答题数）与 真 SoV（本品牌÷同题全竞品）。
- verdict：经验基准 <10% 差 / 10–30% 良 / >30% 优。
"""
from seogeo.monitor import count_mentions, generate_prompts, score_answers, verdict


# ---- generate_prompts ----

def test_prompts_fill_topic():
    ps = generate_prompts("智能客服")
    assert len(ps) >= 10
    assert all("智能客服" in p["text"] for p in ps)


def test_prompts_cover_three_stages():
    stages = {p["stage"] for p in generate_prompts("智能客服")}
    assert stages == {"informational", "comparison", "decision"}


# ---- count_mentions（中文安全）----

def test_count_chinese_substring():
    assert count_mentions("我推荐豆包，豆包很好", ["豆包"]) == 2


def test_count_case_insensitive_with_aliases():
    assert count_mentions("用 DeepSeek 或 deepseek 都行", ["DeepSeek", "深度求索"]) == 2


def test_count_zero_when_absent():
    assert count_mentions("没提到任何品牌", ["豆包"]) == 0


# ---- score_answers ----

def test_citation_rate_per_engine():
    answers = {"豆包": ["推荐 我的品牌 和 竞品A", "只推荐 竞品A"]}
    r = score_answers(answers, brand="我的品牌", brand_aliases=[], competitors={"竞品A": []})
    assert r["豆包"]["citation_rate"] == 0.5  # 2 题答了，本品牌被引 1 题


def test_share_of_voice():
    answers = {"豆包": ["我的品牌 我的品牌 竞品A"]}  # 本品牌 2、竞品 1 → SoV 2/3
    r = score_answers(answers, brand="我的品牌", brand_aliases=[], competitors={"竞品A": []})
    assert r["豆包"]["share_of_voice"] == round(2 / 3, 3)


def test_overall_averages_engines():
    answers = {"豆包": ["我的品牌"], "DeepSeek": ["竞品A"]}  # 1.0 与 0.0 → 0.5
    r = score_answers(answers, brand="我的品牌", brand_aliases=[], competitors={"竞品A": []})
    assert r["_overall"]["citation_rate"] == 0.5


# ---- verdict ----

def test_verdict_tiers():
    assert verdict(0.05) == "差"
    assert verdict(0.2) == "良"
    assert verdict(0.5) == "优"


# ---- 问题1：ASCII 品牌名词边界防误匹配 ----

def test_ascii_brand_no_prefix_match():
    """DeepSeeker 不应计入 DeepSeek 的匹配数。"""
    assert count_mentions("DeepSeeker is awesome", ["DeepSeek"]) == 0


def test_ascii_brand_no_infix_match():
    """AIsolution 不应计入 AI 的匹配数。"""
    assert count_mentions("AIsolution works great", ["AI"]) == 0


def test_ascii_brand_counts_standalone():
    """'DeepSeek 好，DeepSeek！' 应计 2 次。"""
    assert count_mentions("DeepSeek 好，DeepSeek！", ["DeepSeek"]) == 2


def test_chinese_brand_still_substring():
    """中文 '通义' 在 '通义千问' 中仍计 1（CJK 子串保留）。"""
    assert count_mentions("通义千问是阿里的产品", ["通义"]) == 1


# ---- 问题2：_overall 按问答数加权，而非算术平均 ----

def test_overall_weighted_by_sample_size():
    """
    引擎1：答10题、命中9题 → citation_rate = 0.9
    引擎2：答1题、命中0题  → citation_rate = 0.0
    算术平均 = (0.9 + 0.0) / 2 = 0.45（错误）
    加权平均 = 9 / (10 + 1)  = 9/11 ≈ 0.818（正确）
    """
    # 引擎1：10 条回答，前 9 条含品牌、最后 1 条不含
    answers_eng1 = ["推荐 我的品牌"] * 9 + ["竞品A 不错"]
    # 引擎2：1 条回答，不含品牌
    answers_eng2 = ["竞品A 就够了"]
    answers = {"引擎1": answers_eng1, "引擎2": answers_eng2}
    r = score_answers(answers, brand="我的品牌", brand_aliases=[], competitors={"竞品A": []})
    expected = round(9 / 11, 3)
    assert r["_overall"]["citation_rate"] == expected, (
        f"期望加权 {expected}，实际 {r['_overall']['citation_rate']}"
    )
