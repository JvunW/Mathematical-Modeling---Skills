---
name: mathmodel-writing
description: "撰写并排版数学建模论文，支持 Typst、LaTeX 和用于 Word 原生公式导出的 Markdown。用于根据模型、真实计算结果和图表组织章节，并通过 Codex 联网搜索、OpenAlex 或人工 Deep Research 检索和核验参考文献；需要 DOCX 时与 $export-math-docx 配合。"
---

# 数学建模论文写作

把已经验证的模型、结果与图表组织成可提交的 Typst/PDF、LaTeX/PDF 或 Word/DOCX 论文。本 Skill 不重新求解模型，也不把未经运行的数字写成事实。

## 触发边界

用于论文内容规划、正文撰写、图表叙事、公式与引用排版、摘要和结论。若模型尚未定稿，先用 `$mathmodel-analysis`；若结果尚未计算或冻结，先用 `$mathmodel-coding`；只需最终验收时用 `$mathmodel-verification`。

## 输入契约

开始前确认：

- 赛题、比赛模板和交付格式；
- `reports/model_manifest.json`；
- `results/results_manifest.json` 及其 `frozen + fresh` Artifact；
- 图表、表格与对应数据；
- 已核验参考文献及可复核来源；
- 用户对语言、篇幅和版式的要求。

任一关键输入为 `missing`、`blocked`、`stale` 或 `superseded` 时，不得据此写确定性结论。记录证据缺口，回到产生该输入的阶段。

## 路由

- 内容结构与逐问覆盖：读取 [content_planning.md](references/content_planning.md)。
- 数值、图表与证据绑定：读取 [numeric_claims_and_evidence.md](references/numeric_claims_and_evidence.md)。
- Typst/PDF：读取 [typst_route.md](references/typst_route.md)。
- LaTeX/PDF：读取 [latex_route.md](references/latex_route.md)。
- Word/DOCX：读取 [word_route.md](references/word_route.md)，并调用 `$export-math-docx`。
- 外部文献：读取唯一规范源 [citation_policy.md](references/citation_policy.md)。
- 公式编号：读取 [equation_numbering.md](references/equation_numbering.md)。
- 中文正文写作与成稿润色：调用 `$mathmodel-humanizer-zh` 两次；计划门禁后先以正文起草模式约束初稿，成稿门禁后再以成稿润色模式修改源文件。两次均不得改变数字、公式、引用或结论强度。

只读取当前路线需要的 reference；不要一次加载全部排版细节。

## 核心流程

1. **锁定交付路线。** 从比赛要求和官方模板选择 Typst/PDF、LaTeX/PDF 或 Word/DOCX；不得为了方便擅自更换官方格式。
2. **建立内容计划。** 创建 `reports/PAPER_CONTENT_PLAN.md`，按每个实际子问题列出论点、模型、证据文件、预期图表、验证方式和状态；随后调用 `$mathmodel-writing-grill` 向用户发出论证计划门禁的恰好 10 个问题。用户未逐题答完前暂停写作，禁止 Agent 自答或内部通过。
3. **建立证据映射。** 创建或更新 `reports/paper_evidence_map.json`，遵循仓库 `schemas/paper_evidence_map.schema.json`，以 `artifact_id + version + content_hash` 绑定关键主张。
4. **启用中文正文起草模式。** 中文论文在写第一节正文前调用 `$mathmodel-humanizer-zh` 的正文起草模式，并在后续全部章节持续使用其表达与证据保护规则；英文论文跳过。
5. **先写逐问正文。** 每问至少说明目标、变量与假设、模型或算法、真实结果、解释以及适合该模型的验证或边界；题目不是三问时不得套三问结构。
6. **嵌入图表和公式。** 图表紧邻首次解释位置；公式定义变量、单位和适用条件；需要正文引用的展示公式必须有稳定编号和标签。
7. **处理引用。** 只采用已核验条目，记录检索来源与日期；联网不可用时允许基于用户资料写作，但明确标注“未完成外部核验”。
8. **最后写摘要与结论。** 摘要必须包含任务、方法、关键数值、验证和结论，不引入正文没有的新结果；中文摘要与结论继续遵守正文起草模式。
9. **完成正文成稿门禁。** 全部问题章节、摘要和结论完成后再次调用 `$mathmodel-writing-grill`，向用户发出另一组恰好 10 个成稿决策问题。用户未逐题答完前不得修改、润色或交付论文。
10. **执行中文成稿润色模式。** 中文论文在正文成稿门禁通过后再次调用 `$mathmodel-humanizer-zh`，本次明确使用成稿润色模式；只编辑 Typst、LaTeX 或 Markdown 源文件。用户明确要求保持原文风格或跳过时记录原因。英文论文不调用。
11. **重新生成并交给验收。** 润色后重新编译或导出最终文件，再调用 `$mathmodel-verification`；Word 路线必须先完成 `$export-math-docx` 的 OMML 与图片嵌入验证。

## 输出契约

至少产生：

- 所选路线的论文源文件；
- 编译后的 PDF，或导出并验证过的 DOCX；
- `reports/PAPER_CONTENT_PLAN.md`；
- `reports/paper_evidence_map.json`；
- 中文论文执行语言润色时的 `reports/HUMANIZATION_REPORT.md`；
- 实际使用的图表、表格和参考文献文件。

正文不应暴露内部临时路径、Agent 名称、状态文件名或调试过程。附录中的复现信息除外，但必须面向读者表述。

## 不可妥协的规则

- 不编造数据、结果、文献、DOI、页码、图表或验证结论。
- 关键数字只能来自当前 frozen/fresh 结果或可复核的外部来源。
- 公式、正文、表格和图中的同一指标必须一致。
- 展示公式默认编号；有意不编号只能按 reference 中的可审计标记豁免，关键模型和被引用公式不得豁免。
- 图表必须真实存在并被正文解释；不能用装饰图替代证据。
- 任何引用都不能只凭模型记忆确认。
- 中文论文必须在正文起草与成稿润色两个阶段调用 `$mathmodel-humanizer-zh`；不得把它降级为只在最后运行的“去 AI 味”步骤。两种模式均不得改变数字、单位、公式、变量、图表、引用、结论强度、局限或 AI 使用披露；成稿保护检查失败时不得继续交付。
- 两个 `$mathmodel-writing-grill` 门禁都必须向用户展示恰好 10 题并等待 1–10 的显式回答；不得由 Agent 自问自答、提供可整体接受的默认答案或以内部自检代替用户访谈。
- 无法完成编译、外部核验或视觉检查时，应标记为 `skipped`/`blocked` 并说明原因，不能写成通过。

## 验收标准

交付前确认：两个论文门禁各自的 10 个用户回答均已记录；所有子问题均被回答；内容计划无未解释的关键缺口；证据映射只指向 fresh Artifact；关键数字一致；公式编号和引用闭合；图表路径有效；引用可复核；中文论文的正文起草模式与成稿润色模式均已记录，成稿保护检查已通过或记录了用户要求的跳过；选定格式可打开；最终文件通过 `$mathmodel-verification`。

## 失败处理

- 结果变化：让受影响的证据映射、图表和正文主张变为 `stale`，只重写受影响部分。
- 官方模板损坏：保留原文件，复制到工作区修复，并记录差异。
- 联网失败：保留检索式和失败原因，使用用户资料继续非引用部分，外部引用保持未核验状态。
- 篇幅超限：优先删重复叙述和低价值图表，不删假设、关键公式、验证和边界。
