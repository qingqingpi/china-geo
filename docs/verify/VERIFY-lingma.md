# 人工验证清单：在通义灵码 Lingma（阿里）里实跑 chinese-geo

> ⏳ 给**人**执行的验证模板。loop 只备模板（装法 / 落点是确定性的，已自动填好）；
> 带 ⏳ 的实跑结果（transcript / 截图 / 版本号）请你在真实通义灵码里跑完后补上，**不要编造**。
> 配套用法见 [docs/agents/lingma.md](../agents/lingma.md)。

## 0. 环境
- [ ] `pip install Chinese-Geo`，`chinese-geo --help` 能跑
- [ ] （要 MCP）`pip install "Chinese-Geo[mcp]"`，`chinese-geo-mcp` 在 PATH
- 通义灵码版本：⏳ 待人工填

## 1. 接入产物落点（`chinese-geo init --agent lingma` 应写出）
- [ ] `.lingma/rules/seogeo.md`（项目规则 / 指令文件）
- [ ] `MCP-SETUP-lingma.md`（手动指引——灵码的 MCP 是 UI-only、跨工程共享，不自动写其私有路径）
- [ ] 已存在的同名文件**未被覆盖**

## 2. CLI 直调（必过，与 agent 无关）
- [ ] 让灵码跑 `chinese-geo audit https://example.com` → 看到"# chinese-geo 体检报告"+ 7 维度打分 + 🔴 必修清单
- 实跑 transcript：⏳ 待人工填

## 3. 通义灵码原生调法
- [ ] MCP：按 `MCP-SETUP-lingma.md` 把 JSON 贴进灵码 MCP 设置，确认 `chinese-geo` 工具可调（路径以官方面板为准）
- [ ] Skills：目录官方未证实，可先只用 CLI / MCP
- 截图 / transcript：⏳ 待人工填

## 4. 结论
- [ ] 整体可用判定：⏳ 待人工填（✅通过 / ⚠️部分 / ❌不通过 + 备注）
- [ ] 发现的问题 → 提 issue：⏳ 待人工填
