"""引用监控核心（零 key、确定性）。

填补竞品空白：真零 key（手动抽样，不依赖 API / 付费爬虫）+ 中文友好（词典子串匹配，
不靠"首字母大写"——gego 那套对中文失效）+ 真 SoV（按引擎算"本品牌÷同题全竞品"）。

数据流：generate_prompts 出去品牌化问题 → 用户把各引擎回答粘回 → score_answers 算指标。
"""
from __future__ import annotations
import re

# 去品牌化 prompt 模板（只含 {topic}，绝不含品牌名——让 AI 自己推荐，再看引不引你）
_TEMPLATES = {
    "informational": [
        "{topic}是什么？有哪些主流的解决方案？",
        "做{topic}一般用什么工具/平台？",
        "{topic}领域有哪些值得关注的公司或产品？",
        "新手想了解{topic}，该从哪些品牌入手？",
    ],
    "comparison": [
        "{topic}哪个好？请对比几个主流选择的优缺点。",
        "推荐几款{topic}，并说明区别。",
        "{topic}有哪些平替/国产替代方案？",
        "预算有限时，{topic}选哪个性价比高？",
        "{topic}里口碑比较好的有哪些？",
    ],
    "decision": [
        "我要选一个{topic}，请直接给出你的首选推荐和理由。",
        "{topic}里现在公认最好的是哪个？",
        "如果只能选一个{topic}，你会选哪个？为什么？",
    ],
}


def generate_prompts(topic: str) -> list:
    """按行业/品类词生成去品牌化 prompt 矩阵（informational / comparison / decision 三阶段）。"""
    out = []
    for stage, templates in _TEMPLATES.items():
        for tpl in templates:
            out.append({"stage": stage, "text": tpl.format(topic=topic)})
    return out


def _occurrence_spans(text: str, kw: str) -> list:
    """返回 kw 在 text 中所有命中的 [start, end) 区间（与 _count_occurrences 同语义）。

    - ASCII 关键词：加词边界（前后无 A-Za-z0-9），防止前缀/后缀误匹配
      （例：搜索 "DeepSeek" 不命中 "DeepSeeker"，搜索 "AI" 不命中 "AIsolution"）。
    - 中文/混合关键词：保持子串匹配（CJK 字符无词边界概念），按 len(kw) 非重叠前进。
    """
    if not kw:
        return []
    if kw.isascii():
        pat = re.compile(
            r'(?<![A-Za-z0-9])' + re.escape(kw) + r'(?![A-Za-z0-9])',
            re.IGNORECASE,
        )
        return [(m.start(), m.end()) for m in pat.finditer(text)]
    # 中文/混合：大小写无关子串，非重叠前进（对齐原有语义）
    lower, k = text.lower(), kw.lower()
    spans, i = [], 0
    while True:
        j = lower.find(k, i)
        if j == -1:
            break
        spans.append((j, j + len(k)))
        i = j + len(k)
    return spans


def _count_occurrences(text: str, kw: str) -> int:
    """大小写无关的关键词计数（ASCII 加词边界 / CJK 子串）。"""
    return len(_occurrence_spans(text, kw))


def count_mentions(text: str, names) -> int:
    """统计 text 中 names（品牌名 + 别名）的提及次数，按物理出现去重。

    当多个名字命中同一段文本时（典型：竞品名 "通义" 与其别名 "通义千问"），那一处
    文本只算一次提及——对所有名字的命中区间取并集，按合并后的不相交区间计数。否则
    重叠别名会把单次出现重复累加，进而虚高 share-of-voice（本工具核心指标）。
    只合并真正重叠的区间（start < cur_end），相接但不重叠（如 "豆包豆包" 的两段）
    仍各算一次，避免误吞真实的多次提及。
    """
    spans = []
    for n in names:
        if n:
            spans.extend(_occurrence_spans(text, n))
    if not spans:
        return 0
    spans.sort()
    count, cur_end = 1, spans[0][1]
    for start, end in spans[1:]:
        if start < cur_end:          # 与当前区间重叠 → 同一处提及
            cur_end = max(cur_end, end)
        else:                        # 不重叠 → 新的一处提及
            count += 1
            cur_end = end
    return count


def score_answers(answers: dict, brand: str, brand_aliases, competitors: dict) -> dict:
    """按引擎算 引用率 + 真 SoV。

    answers: {引擎名: [回答文本, ...]}（每条对应一个 prompt 的回答）
    competitors: {竞品名: [别名, ...]}
    返回: {引擎: {answered, brand_mentions, citation_rate, share_of_voice}, "_overall": {...}}
    """
    if not isinstance(answers, dict):
        raise ValueError("answers 必须是 {引擎: [回答文本, ...]} 形状的对象")
    brand_names = [brand] + list(brand_aliases or [])
    out: dict = {}
    for engine, texts in answers.items():
        if not isinstance(texts, (list, tuple)):
            raise ValueError(f"引擎「{engine}」的值必须是回答文本列表，例如 [\"回答1\", \"回答2\"]")
        answered = brand_hits_q = brand_total = comp_total = 0
        for t in texts:
            if t is not None and not isinstance(t, str):
                raise ValueError(
                    f"引擎「{engine}」的回答必须是字符串（或 null 表示未答），收到 {type(t).__name__}")
            if not t or not t.strip():
                continue
            answered += 1
            bm = count_mentions(t, brand_names)
            brand_total += bm
            if bm > 0:
                brand_hits_q += 1
            for comp, aliases in (competitors or {}).items():
                comp_total += count_mentions(t, [comp] + list(aliases or []))
        pool = brand_total + comp_total
        out[engine] = {
            "answered": answered,
            "brand_mentions": brand_total,
            "citation_rate": round(brand_hits_q / answered, 3) if answered else 0.0,
            "share_of_voice": round(brand_total / pool, 3) if pool else 0.0,
        }
    # _overall：按各引擎实际问答数加权，避免样本量悬殊时算术平均失真
    total_answered = sum(v["answered"] for v in out.values())
    total_hits = sum(
        round(v["citation_rate"] * v["answered"])  # 还原命中题数（整数）
        for v in out.values()
    )
    out["_overall"] = {
        "citation_rate": round(total_hits / total_answered, 3) if total_answered else 0.0
    }
    return out


def verdict(citation_rate: float) -> str:
    """经验基准：<10% 差 / 10–30% 良 / >30% 优。"""
    if citation_rate < 0.1:
        return "差"
    if citation_rate <= 0.3:
        return "良"
    return "优"
