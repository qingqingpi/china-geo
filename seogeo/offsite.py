"""站外平台矩阵查询（确定性，零依赖）——给 offsite skill 当确定性背书。

按目标引擎 / 受众筛平台，列出"一题多发"主力与"封闭型"平台。
"""
from __future__ import annotations

from seogeo.data.platforms import DOMESTIC_PLATFORMS

# 一题多发主力：同一篇好内容改写成各平台变体同步发，一次产出、多源覆盖
_CROSS_POST = ("头条号", "百家号", "知乎", "搜狐号", "CSDN")


def recommend(engine: str | None = None, audience: str | None = None) -> list:
    """按引擎（豆包/元宝/文心/通义/DeepSeek/Kimi）和/或受众（b2b/consumer）筛平台。"""
    out = []
    for p in DOMESTIC_PLATFORMS:
        if engine and engine not in p.engines:
            continue
        if audience and audience not in p.audiences:
            continue
        out.append(p)
    return out


def closed_platforms() -> list:
    """封闭型平台：外部 AI 不引，想被引就得做平台内 SEO。"""
    return [p for p in DOMESTIC_PLATFORMS if not p.open]


def cross_post_set() -> tuple:
    return _CROSS_POST
