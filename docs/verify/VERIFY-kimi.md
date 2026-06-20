# 人工验证清单：在 Kimi CLI（Moonshot）里实跑 chinese-geo

> ⏳ 给**人**执行的验证模板。loop 只备模板（装法 / 落点是确定性的，已自动填好）；
> 带 ⏳ 的实跑结果（transcript / 截图 / 版本号）请你在真实 Kimi CLI 里跑完后补上，**不要编造**。
> 配套用法见 [docs/agents/kimi.md](../agents/kimi.md)。

## 0. 环境
- [ ] `pip install Chinese-Geo`，`chinese-geo --help` 能跑
- [ ] （要 MCP）`pip install "Chinese-Geo[mcp]"`，`chinese-geo-mcp` 在 PATH
- Kimi CLI 版本：⏳ 待人工填

## 1. 接入产物落点（`chinese-geo init --agent kimi` 应写出）
- [ ] `AGENTS.md`（事实标准指令文件，Kimi 自动读到）
- [ ] `MCP-SETUP-kimi.md`（手动指引——Kimi 的 MCP 是全局 `~/.kimi/mcp.json`，不自动写 home）
- [ ] 已存在的同名文件**未被覆盖**

## 2. CLI 直调（必过，与 agent 无关）
- [ ] 让 Kimi 跑 `chinese-geo audit https://example.com` → 看到"# chinese-geo 体检报告"+ 7 维度打分 + 🔴 必修清单
- 实跑 transcript：⏳ 待人工填

## 3. Kimi CLI 原生调法
- [ ] MCP：按 `MCP-SETUP-kimi.md` 把 JSON 并进 `~/.kimi/mcp.json`（或 `--mcp-config-file`），确认 `chinese-geo` 工具可调
- [ ] Skills：放进 `.kimi/skills/` 或复用 `.claude/skills/` 后可触发
- 截图 / transcript：⏳ 待人工填

## 4. 结论
- [ ] 整体可用判定：⏳ 待人工填（✅通过 / ⚠️部分 / ❌不通过 + 备注）
- [ ] 发现的问题 → 提 issue：⏳ 待人工填
