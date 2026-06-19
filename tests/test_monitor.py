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
