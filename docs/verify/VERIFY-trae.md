# 人工验证清单：在 Trae（字节）里实跑 chinese-geo

> ⏳ 给**人**执行的验证模板。loop 只备模板（装法 / 落点是确定性的，已自动填好）；
> 带 ⏳ 的实跑结果（transcript / 截图 / 版本号）请你在真实 Trae 里跑完后补上，**不要编造**。
> 配套用法见 [docs/agents/trae.md](../agents/trae.md)。

## 0. 环境
- [ ] `pip install Chinese-Geo`，`chinese-geo --help` 能跑
- [ ] （要 MCP）`pip install "Chinese-Geo[mcp]"`，`chinese-geo-mcp` 在 PATH
- Trae 版本：⏳ 待人工填

## 1. 接入产物落点（`chinese-geo init --agent trae` 应写出）
- [ ] `.trae/rules/project_rules.md`（项目规则 / 指令文件）
- [ ] `.trae/mcp.json`（项目级 MCP，键 `mcpServers`；路径以 Trae 官方文档为准）
- [ ] 已存在的同名文件**未被覆盖**

## 2. CLI 直调（必过，与 agent 无关）
- [ ] 让 Trae 跑 `chinese-geo audit https://example.com` → 看到"# chinese-geo 体检报告"+ 7 维度打分 + 🔴 必修清单
- 实跑 transcript：⏳ 待人工填

## 3. Trae 原生调法
- [ ] MCP：确认 `.trae/mcp.json` 就位、`chinese-geo` 工具可调
- [ ] Skills：放进 `.trae/skills/<name>/SKILL.md` 后可触发
- 截图 / transcript：⏳ 待人工填

## 4. 结论
- [ ] 整体可用判定：⏳ 待人工填（✅通过 / ⚠️部分 / ❌不通过 + 备注）
- [ ] 发现的问题 → 提 issue：⏳ 待人工填
