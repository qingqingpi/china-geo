# 真实站点案例研究模板（chinese-geo）

> ⏳ 这是给**人**填的案例模板。loop 只备结构（字段 / 采集 schema / 步骤是确定性的，已填好）；
> 带 ⏳ 的真实数据（站点、分数、引用率）需要**真站 + 真 API key + 时间**，由你跑完后补。
> **绝不编造**：没有真实数据就留 ⏳，别写假数字（AI 联网结果会波动、可被操控，假数据害己害人）。

## 1. 基本信息
- 站点：⏳ 待人工填（域名）
- 行业 / 品类：⏳ 待人工填
- 日期（初检）：⏳　｜　日期（复检）：⏳

## 2. 体检前后（跑 `chinese-geo audit <域名> --format json`）
| 维度 | 初检 | 复检 |
|---|---|---|
| **总分** | ⏳ | ⏳ |
| ★国内 AI 爬虫准入 | ⏳ | ⏳ |
| 海外 AI 爬虫准入 | ⏳ | ⏳ |
| 结构化 | ⏳ | ⏳ |
| 内容可引用性 | ⏳ | ⏳ |
| AI 可发现性 | ⏳ | ⏳ |
| JS 渲染可见性 | ⏳ | ⏳ |
| 技术基线 | ⏳ | ⏳ |

## 3. 改了什么（对照 audit 的 🔴 必修清单）
- ⏳ 待人工填（例：补唯一 H1 / 加 JSON-LD / 补 OG / robots 放行 Bytespider+各家单独成块 / 加 sitemap …）

## 4. 引用监控前后（跑 `chinese-geo monitor`）
步骤（优化前做一遍、改站收录几周后再做一遍）：
1. `chinese-geo monitor prompts --industry "<你的品类>"` → 生成去品牌化 prompt 矩阵。
2. 把每条 prompt 逐条粘进各 AI 引擎（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi…），收集回答存为 `answers.json`。
3. `chinese-geo monitor score --answers answers.json --brand "<你的品牌>"` → 算引用率 / SoV。
4. （可选）配了 API key 可 `chinese-geo monitor run --industry <X> --brand <X>` 自动跑（注：API 模型默认不联网，与消费版有差）。

| 指标 | 优化前 | 优化后 |
|---|---|---|
| 引用率（被引问题数 ÷ 总问题数） | ⏳ | ⏳ |
| SoV（本品牌提及 ÷ 同题全部竞品提及） | ⏳ | ⏳ |

> 基准：引用率 <10% 差 / 10–30% 良 / >30% 优。占比类数字是单行业样本、仅供参考。

## 5. 采集 schema（结构化记录，便于汇总多个案例；`null` / `⏳` 待真实值替换）
```json
{
  "site": "⏳",
  "industry": "⏳",
  "audit_before": {"date": "⏳", "score": null, "breakdown": {}},
  "audit_after": {"date": "⏳", "score": null, "breakdown": {}},
  "changes": ["⏳"],
  "monitor_before": {"citation_rate": null, "share_of_voice": null},
  "monitor_after": {"citation_rate": null, "share_of_voice": null}
}
```

## 6. 结论
- ⏳ 待人工填（总分 Δ、引用率 Δ、哪些改动最有效、踩过的坑）

> 提醒：AI 联网检索结果会波动、可被操控 → 引用率是"持续监控"指标，别凭一次结果定论（见 `chinese-geo monitor`）。
