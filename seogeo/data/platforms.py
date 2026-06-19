"""国内社媒 / 站外平台矩阵——差异化核心数据（每家 AI 主要"吃自己生态"）。

多角度：每个平台标注「喂哪些国内 AI 引擎 × 受众(b2b/consumer) × 开放/封闭」。
来源：项目深度调研（方向可信、占比为单行业样本，数值仅参考）。海外工具完全没有这套。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    name: str
    engines: tuple      # 喂哪些国内 AI 引擎（豆包/元宝/文心/通义/DeepSeek/Kimi）
    audiences: tuple    # "b2b"（B2B/科技）/ "consumer"（消费/生活），可多
    open: bool          # True=公网可被抓引；False=封闭，需做平台内 SEO
    tip: str


DOMESTIC_PLATFORMS = (
    Platform("微信公众号", ("元宝",), ("b2b", "consumer"), True,
             "元宝主力（约占其引用一半，微信搜一搜底层搜狗）"),
    Platform("知乎", ("DeepSeek", "Kimi", "文心"), ("b2b", "consumer"), True,
             "跨引擎高价值，重论证"),
    Platform("CSDN", ("DeepSeek", "Kimi", "文心"), ("b2b",), True, "开发者技术内容"),
    Platform("掘金", ("DeepSeek", "Kimi"), ("b2b",), True, "前端 / 开发者"),
    Platform("人人都是产品经理", ("DeepSeek",), ("b2b",), True, "产品 / B2B"),
    Platform("百家号", ("文心",), ("b2b", "consumer"), True, "百度系，原创同步"),
    Platform("百度百科", ("文心",), ("b2b", "consumer"), True, "实体权威锚点（E-E-A-T）"),
    Platform("门户自媒体（网易号/企鹅号/搜狐号）", ("通义",), ("b2b", "consumer"), True,
             "通义/夸克吃门户（网易/企鹅/搜狐 60%+），搜狐权重普遍高"),
    Platform("今日头条 / 头条号", ("豆包",), ("consumer", "b2b"), True, "字节系，喂豆包"),
    Platform("抖音", ("豆包",), ("consumer",), False, "字节系；抖音内 AI 只引抖音 → 做平台内 SEO"),
    Platform("小红书", ("豆包", "通义"), ("consumer",), False,
             '消费/生活；自家"点点"只引小红书 → 也要做平台内'),
    Platform("B站", ("豆包", "通义"), ("consumer", "b2b"), True, "视频 + 图文，科技区偏 b2b"),
    Platform("视频号", ("元宝",), ("consumer",), True, "腾讯系，喂元宝"),
)
