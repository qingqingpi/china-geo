"""国内主流 AI 爬虫清单（seogeo 的差异化核心数据）。

这是需要持续维护的数据资产，而非散落常量——单独成文件，便于后续更新。
注：国内爬虫倾向只读精确匹配自己 UA 的块，被合并进 `*` 的规则可能被忽略。
"""

# UA token → 所属引擎/说明
DOMESTIC_BOTS = {
    "Baiduspider": "百度搜索 / 文心一言",
    "Bytespider": "字节 / 豆包（不完全遵守 robots，建议服务端硬拦）",
    "PetalBot": "华为 PetalSearch / 华为 AI",
    "Sogou web spider": "搜狗 / 腾讯元宝（微信搜一搜底层）",
    "YisouSpider": "神马搜索（阿里 / 夸克 / UC）",
}

# 反向 DNS 校验后缀（验证 access.log 里自称某爬虫的 IP 真伪；monitor/日志分析用）
DOMESTIC_BOT_RDNS = {
    "Baiduspider": ".crawl.baidu.com",
    "Bytespider": ".crawl.bytedance.com",
    "PetalBot": ".aspiegel.com",
    "Sogou web spider": ".crawl.sogou.com",
    "YisouSpider": ".crawl.sm.cn",
}
