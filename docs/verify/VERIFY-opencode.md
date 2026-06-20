# 人工验证清单：在 opencode 里实跑 chinese-geo

> ⏳ 给**人**执行的验证模板。loop 只备模板（装法 / 落点是确定性的，已自动填好）；
> 带 ⏳ 的实跑结果（transcript / 截图 / 版本号）请你在真实 opencode 里跑完后补上，**不要编造**。
> 配套用法见 [docs/agents/opencode.md](../agents/opencode.md)。

## 0. 环境
- [ ] `pip install Chinese-Geo`，`chinese-geo --help` 能跑
- [ ] （要 MCP）`pip install "Chinese-Geo[mcp]"`，`chinese-geo-mcp` 在 PATH
- opencode 版本：⏳ 待人工填

## 1. 接入产物落点（`chinese-geo init --agent opencode` 应写出）
- [ ] `AGENTS.md`（指令文件，opencode 自动读到）
- [ ] `opencode.json`（MCP 配置——**键是 `mcp`、server 带 `type:"local"`**，不是通用 `mcpServers`）
- [ ] 已存在的同名文件**未被覆盖**

## 2. CLI 直调（必过，与 agent 无关）
- [ ] 让 opencode 跑 `chinese-geo audit https://example.com` → 看到"# chinese-geo 体检报告"+ 7 维度打分 + 🔴 必修清单
- 实跑 transcript：⏳ 待人工填

## 3. opencode 原生调法
- [ ] MCP：确认 `opencode.json` 里 `mcp.chinese-geo.type == "local"`、`command` 含 `chinese-geo-mcp`，工具可调
- [ ] Skills：opencode 复用 `.claude/skills/`、`~/.claude/skills/` 后可触发
- 截图 / transcript：⏳ 待人工填

## 4. 结论
- [ ] 整体可用判定：⏳ 待人工填（✅通过 / ⚠️部分 / ❌不通过 + 备注）
- [ ] 发现的问题 → 提 issue：⏳ 待人工填
