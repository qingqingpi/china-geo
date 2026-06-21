# Chinese-Geo

> 中文 / 国内生态优先的开源 SEO + GEO（生成式引擎优化）工具包。
> 让你的网站被豆包 / DeepSeek / 文心一言 / 通义千问 / 腾讯元宝 / Kimi 等国内 AI 引擎抓得到、看得懂、更可能被引用——海外主流（ChatGPT / Claude / Perplexity / Google AI）一并覆盖。

现有 SEO/GEO 工具几乎全是英文 / 海外生态视角（只盯 ChatGPT / Perplexity，只认 Wikipedia / llms.txt）。Chinese-Geo 把国内这一套补全，同时不丢海外主流：国内爬虫准入、百度系结构化、知乎 / CSDN / 公众号站外矩阵、国产引擎引用监控——这是海外工具的空白。

确定性引擎，运行时零依赖（纯 Python 标准库），可进 CI、可复现。命令名 `chinese-geo`。

---

## 三种用法

一条命令给站做「AI 可见性体检」，再告诉你哪里该改、改完怎么验证。

1. 命令行直接用 —— `chinese-geo audit 你的域名` → 中文体检报告 + 优先级修复清单。零 key、零网络也能自证。
2. 装进 AI 编程 Agent（Claude Code / Codex / Cursor / CodeBuddy / Kimi / opencode…）—— 让 agent 自动调它，边写边优化。
3. 进 CI —— `--format json` + 退出码，做「AI 可见性不达标就拦住合并」的质量门禁。

---

## 快速开始

需要 Python 3.9+，无需任何第三方包。

```bash
git clone https://github.com/qingqingpi/Chinese-Geo
cd Chinese-Geo
pip install -e .

chinese-geo demo                 # 先跑这条
chinese-geo audit example.com    # 再体检你自己的站
```

`chinese-geo demo` 零 key、零网络，当场把一个内置差站从 36/100 修到 100/100（用工具自己的生成器补 H1 / JSON-LD / OG / 正文 + 放行国内爬虫，体检 → 修复 → 复检全跑一遍）——这是最小自证。没装也能跑：`python -m seogeo.cli demo`。

更多开发者级样例（差站 fixture + quickstart 脚本 + 真实样例报告）见 [examples/](examples/)。

---

## 全部命令 → 你能拿到什么

| 命令 | 干什么 | 你拿到的结果 |
|---|---|---|
| `chinese-geo demo` | 内置差站 体检→修复→复检 | 36→100 前后对比表（零 key 零网络、可复现的自证） |
| `chinese-geo audit <url>` | 7 维 12 项 AI 可见性体检 | 中文报告：总分 + 分项得分 + 优先级修复清单。`--format json` 出机器可读（喂 agent / CI） |
| `chinese-geo structure <url>` | 确定性结构信号（非评分） | 标题层级、FAQ、表格/列表、答案胶囊字数分布——供判断层参考 |
| `chinese-geo bots gen [--sitemap <url>]` | 生成推荐 robots.txt | 可直接贴站的 robots：国内各家单独成块 + 海外合并块 + Sitemap 行 |
| `chinese-geo bots verify <ip> <bot>` | 反向+正向 DNS 校验爬虫真伪 | 真 / 伪判定（识破伪造的爬虫 UA） |
| `chinese-geo schema gen <type>` | JSON-LD 脚手架 | organization / article / faqpage / breadcrumb 模板，填空即用 |
| `chinese-geo llms gen --title <X>` | llms.txt 脚手架 | 填好标题的 llms.txt（主要面向海外引擎） |
| `chinese-geo init [--site <X>]` | 一键打包站点产物 | robots + llms.txt + schema + canonical 自查清单 → 输出目录 |
| `chinese-geo init --agent` | 把工具接入某 agent（11 家，见下） | 该 agent 的指令文件 + MCP 配置 / 接入指引（不覆盖已有） |
| `chinese-geo monitor prompts --industry <X>` | 生成去品牌化问题 | 12 个问题（informational/comparison/decision），粘进各 AI 引擎收集回答 |
| `chinese-geo monitor score --answers <f.json> --brand <X>` | 零 key 算引用率 / SoV | 各引擎引用率 + SoV + verdict（<10%差 / 10–30%良 / >30%优） |
| `chinese-geo monitor run --industry <X> --brand <X>` | BYOK 自带 key 自动跑各引擎 | 配了 API key 一条命令跑完各引擎，直接出指标 |
| `chinese-geo offsite [--engine <X>\|--audience <b2b\|consumer>]` | 国内社媒 / 站外平台矩阵 | 平台 → 喂哪个引擎 × 受众 × 开放/封闭 + 一题多发打法 |

> 退出码（便于 CI 做质量门禁）：`audit` 有必修项 → `1`，无 → `0`，用法/输入错误 → `2`。

### 示例输出

真实样例（`chinese-geo audit https://example.com` 实跑落盘，完整见 [examples/sample-report.md](examples/sample-report.md)）：

```
# chinese-geo 体检报告：https://example.com
**总分 63/100 · 等级：待打基础**

## 分项得分
| 维度 | 得分 |
|---|---|
| 国内 AI 爬虫准入 | 26/26 |
| 内容可引用性 | 4/24 |
| 结构化 | 3/22 |
| …（完整 7 维 + 必修清单见 examples/sample-report.md）

### 必须修
- [+16分 · 内容可引用性] 补强：H2 小节切分、正文≥300字、列表/表格（利于被 AI 抽取引用）
- [+16分 · 结构化] 添加 Organization / Article / FAQPage 等 JSON-LD（schema.org）
```

---

## 各类 Agent 怎么用

分层设计：越底层越通用，CLI 100% 覆盖，上层按 agent 支持度优雅降级——「做一次，到处能跑」。

一键接入命令：`chinese-geo init --agent <claude|codex|gemini|cursor|generic|codebuddy|opencode|kimi|qoder|trae|lingma>` —— 自动写好该 agent 的指令文件 + MCP 配置 / 接入指引（不覆盖已有）。

| Agent | 怎么接 | 接完什么样 |
|---|---|---|
| Claude Code（主场） | `/plugin marketplace add qingqingpi/Chinese-Geo`<br>`/plugin install chinese-geo` | 6 个技能 + MCP + 斜杠命令 `/chinese-geo:audit`·`monitor` 全自动可用 |
| Codex / opencode / CodeBuddy / Kimi / Qoder / Trae / Lingma / Cursor | 在项目根跑 `chinese-geo init --agent <name>` | 自动写好该 agent 的指令文件 + MCP 配置 / 接入指引（不覆盖已有）；支持 MCP 的可结构化调 8 个工具，支持 Agent Skills 的放 `skills/*/SKILL.md` |
| 任何 agent（兜底） | shell 直接 `chinese-geo audit <域名>` | L0 CLI 全覆盖，命令行就能拿到约 80% 价值 |

`<name>` ∈ `claude` / `codex` / `gemini` / `cursor` / `codebuddy` / `kimi` / `opencode` / `qoder` / `trae` / `lingma` / `generic`。

### CLI / MCP / Skill 有什么区别？用哪个？

三者是同一套能力的三种调用方式，从底层到上层叠加——不是三个独立产品：

| | 是什么 | 解决什么 | 你什么时候用 |
|---|---|---|---|
| CLI `chinese-geo` | 确定性引擎本体（纯脚本、零依赖） | 抓取 / 算分 / 校验 / 生成——可复现、能进 CI | 命令行直接跑；任何 agent 都能 shell 调；做 CI 门禁 |
| MCP `chinese-geo-mcp`（8 工具） | 把 CLI 包成「agent 能结构化调用的工具」 | 让 agent 不用解析命令行文本，像调函数一样调引擎、拿结构化结果 | 你的 agent 支持 MCP（Claude / Codex / Cursor…），想让它自动、稳定地调 |
| Skill `skills/*`（6 个） | 用自然语言写的「GEO 方法论剧本」 | 教 agent 判断型活怎么做（把体检结果翻成行动清单、改文案、选平台），到该算数时再回头调 CLI/MCP | 你想让 agent 带你走完整套 GEO，而不只是跑一条命令 |

一句话：CLI 是引擎，MCP 是让 agent 握住引擎的把手，Skill 是会用引擎的老师傅。叠起来就是：Skill（判断 + 编排）→ 调 MCP / CLI（确定性执行）。没有 agent？只用 CLI 也能拿约 80% 价值。

6 个 Skill（判断层，自然语言触发，跑在 agent 里）：

| Skill | 干什么 |
|---|---|
| `chinese-geo-optimize` | 全流程总入口：想「从头到尾完整做一遍 GEO」时，按六阶段编排，逐段委派下面 5 个专项 |
| `chinese-geo-audit` | AI 可见性体检：跑 CLI 体检 → 给中文优先级行动清单 |
| `chinese-geo-structure` | 页面结构 / 骨架：答案胶囊、FAQ、表格、schema 与正文对齐 |
| `chinese-geo-content` | 文案改写成可引用形态：结论前置、TL;DR、问题式标题、加数据 / 引文 / 出处 |
| `chinese-geo-offsite` | 站外平台矩阵 + 实体权威层：按引擎 × 受众选知乎 / CSDN / 公众号…，sameAs / NAP / 百度百科 |
| `chinese-geo-monitor` | 引用率 / SoV：生成去品牌化问题 → 粘回各引擎回答 → 算指标 |

> 触发例子：在 Claude Code 里说「帮我把站从头到尾做一遍 GEO」会自动走 `chinese-geo-optimize`；说「我的文案怎么写 AI 才爱引」会走 `chinese-geo-content`。不支持 Skill 的 agent，直接调对应 CLI 也能拿到主要价值。

8 个 MCP 工具（= 上面 CLI 能力的结构化版，agent 直接调）：`audit` · `bots_gen` · `schema_gen` · `llms_gen` · `monitor_prompts` · `monitor_score` · `monitor_run` · `offsite`。

> 详细装法 + 调法见 [INSTALL.md](INSTALL.md)；每家 agent 的用法卡（含真实 CLI 输出样例）在 [docs/agents/](docs/agents/)，人工验收清单在 [docs/verify/](docs/verify/)。

---

## 开发

```bash
pip install -e ".[dev]"
pytest
```

纯标准库，运行时零依赖（渲染 / MCP 等重能力走 optional-dependencies）。全程 TDD。

## License

MIT © 2026 qingqingpi
