---
description: 生成去品牌化监控问题，用于测 AI 引用率 / SoV
argument-hint: "<行业/品类>"
---

为「$ARGUMENTS」生成的去品牌化监控问题：

!`seogeo monitor prompts --industry "$ARGUMENTS"`

把这些问题逐条粘进豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi（或 ChatGPT / Perplexity），收集回答后：零 key 用 `seogeo monitor score --answers <f.json> --brand <品牌>`，或自带 key 用 `seogeo monitor run --industry "$ARGUMENTS" --brand <品牌>` 自动跑。基准：引用率 <10% 差 / 10–30% 良 / >30% 优。
