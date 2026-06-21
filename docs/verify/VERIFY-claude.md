# 人工验证清单：在 Claude Code 里实跑 chinese-geo

> ⏳ 给**人**执行的验证模板。loop 只备模板（装法 / 落点是确定性的，已自动填好）；
> 带 ⏳ 的实跑结果（transcript / 截图 / 版本号）请你在真实 Claude Code 里跑完后补上，**不要编造**。
> 配套用法见 [docs/agents/claude.md](../agents/claude.md)。

## 0. 环境
- [ ] `pip install Chinese-Geo`，`chinese-geo --help` 能跑
- [ ] （要 MCP）`pip install "Chinese-Geo[mcp]"`，`chinese-geo-mcp` 在 PATH
- Claude Code 版本：⏳ 待人工填

## 1. 接入产物落点（`chinese-geo init --agent claude` 应写出，或用一键插件）
- [ ] `CLAUDE.md`（指令文件，含 chinese-geo 命令与技能说明）
- [ ] `.mcp.json`（注册 `chinese-geo` MCP 服务）
- [ ] 已存在的同名文件**未被覆盖**

## 2. CLI 直调（必过，与 agent 无关）
- [ ] 让 Claude 跑 `chinese-geo audit https://example.com` → 看到"# chinese-geo 体检报告"+ 7 维度打分 + 🔴 必修清单
- 实跑 transcript：⏳ 待人工填

## 3. Claude Code 原生调法
- [ ] 一键插件：`/plugin marketplace add qingqingpi/Chinese-Geo` → `/plugin install chinese-geo` 成功
- [ ] 斜杠命令 `/chinese-geo:audit <域名>` 跑通、注入体检结果
- [ ] 技能可触发：`/chinese-geo:chinese-geo-optimize`（或 chinese-geo-audit 等 6 个）
- [ ] MCP 工具可调（audit / offsite / monitor_* 等 8 个）
- 截图 / transcript：⏳ 待人工填

## 4. 结论
- [ ] 整体可用判定：⏳ 待人工填（✅通过 / ⚠️部分 / ❌不通过 + 备注）
- [ ] 发现的问题 → 提 issue：⏳ 待人工填
