---
name: mathmodel-verification
description: "验收数学建模论文及配套产物。用于提交前检查 Typst、LaTeX 或 Word/DOCX 的结构、图表、数值一致性、占位符、内部信息泄漏、参考文献、代码可复现性、编译、Word 原生 OMML 公式和页面视觉质量。"
---

# 数学建模交付验收

这是完整工作流的最后一关：发现硬错误、复核可复现性和版面，并输出人类报告与机器报告。本 Skill 不重新设计模型，也不为通过验收而发明或重算结果。

## 输入与边界

按项目实际布局定位，不假定固定目录名：

- Typst/LaTeX/Markdown 论文源和官方模板；
- 最终 PDF 或 DOCX；
- 图表、表格、引用文件和复现代码；
- `reports/model_manifest.json`；
- `results/results_manifest.json`；
- `reports/paper_evidence_map.json`；
- `reports/PAPER_GRILL_REPORT.md`；
- 中文论文执行语言润色时的 `reports/HUMANIZATION_REPORT.md` 及保护检查 JSON；
- `state/artifact_registry.json`。

输出 `reports/VERIFY_REPORT.md` 和符合 `schemas/verification_report.schema.json` 的 `reports/verification.json`。机器报告必须区分 `pass`、`fail`、`warning`、`skipped` 和 `blocked`；工具缺失不能记作通过。

## 验收流程

1. **刷新状态。** 校验四类结构化文件并检查 Artifact 引用。关键输入为 stale、missing、blocked、superseded，或正文指向旧版本/hash 时直接失败。
2. **运行文本门禁。** 对 Typst/LaTeX 使用本 Skill 的跨平台检查器：

   ```text
   python "<SKILL_DIR>/scripts/writing_check.py" --help
   ```

   根据实际入口、章节、引用、图表和结果路径传参。Word 路线直接检查 Markdown，再调用 `$export-math-docx` 的结构验证。
3. **核对论文用户十问。** 确认 `PAPER_GRILL_REPORT.md` 中论证计划门禁和正文成稿门禁各有恰好 10 个展示给用户的问题及其显式回答；缺答、Agent 代答、默认答案整体接受或内部自检记录都不能算通过。
4. **核对语言润色证据。** 中文论文存在 `HUMANIZATION_REPORT.md` 时，确认正文起草模式和成稿润色模式均有执行记录，每个成稿阶段已改源文件的保护比较为 `pass`，润色后已重新编译/导出，且 AI 使用披露仍真实完整。用户明确跳过某一模式时只记录，不强制补做。
5. **核对内容覆盖。** 题目有几问就验收几问。每问至少有模型/算法、真实结果、解释和适合题型的验证或边界。检查 `reports/PAPER_CONTENT_PLAN.md` 中的证据缺口是否已处理。
6. **核对数字与证据。** 目标值、误差、排名、权重、阈值和敏感性结论应与 frozen/fresh 结果一致；公式、正文、表格和图中的同一指标应一致。
7. **核对公式。** 检查编号、标签、引用和豁免；检查公式后是否解释变量与单位。
8. **核对图表与引用。** 所有路径存在、媒体已嵌入、caption 合理、正文有解释；引文对应真实且已核验的条目。
9. **编译或导出。** 仅在工具可用时执行；修复语法、路径、图片和交叉引用后重跑。Word 必须通过 `$export-math-docx` 的 OMML、编号和图片嵌入检查。
10. **逐页视觉检查。** PDF 可用本 Skill 的渲染脚本；DOCX 使用当前环境可用的 Word/LibreOffice/文档渲染器。检查裁切、重叠、缺字、越界、空页、模板破坏和编号位置。
11. **写报告并定 Gate。** 所有硬错误清零后才可 `PASS`；未执行的必要检查保持 `skipped`/`blocked` 并说明原因。

## 三条交付路线

### Typst/PDF

- 入口、include 顺序和标题层级与实际子问题一致。
- 存在自动展示公式编号规则；标签唯一且引用闭合。
- 图表路径有效，编译后 PDF 非空。

### LaTeX/PDF

- `\input`/`\include`、标题层级、图片和引用闭合。
- 展示公式默认使用带编号环境；需要引用的公式有唯一 `\label{eq:...}`。
- 未编号展示公式仅在紧邻上一非空行含 `% equation-numbering: intentional-unnumbered reason=<原因>` 时豁免；关键模型和被引用公式不得豁免。
- 编译覆盖交叉引用收敛所需轮次，PDF 非空。

### Word/DOCX

- Markdown 标题与官方模板样式映射合理。
- DOCX 内公式是可编辑 OMML，图片是嵌入媒体。
- `omml_total` 不少于源公式数；`equation_number_fields` 不少于应编号公式数；`equation_number_values` 从 1 连续递增。
- 没有原始 `$...$`、MathML、损坏的 ZIP/XML 或失效绝对图片路径。

## 视觉检查

PDF 渲染命令：

```text
python "<SKILL_DIR>/scripts/render_pdf_pages.py" "<OUTPUT_PDF>" --output-dir "<TEMP_DIR>" --dpi 160
```

逐页检查页面尺寸和数量、标题/摘要/正文、页眉页脚、表格、图片、caption、公式和编号、字体与参考文献。渲染器不可用时只能写“完成结构检查，未执行视觉检查”，不得把 XML 检查描述成视觉通过。

## 必须判为失败

- 缺少核心源文件、正文或最终交付物；
- 入口引用的章节/图片不存在，或模板示例和占位符仍残留；
- 关键数字与当前结果冲突，或证据 Artifact 不是 frozen/fresh；
- 任一论文门禁没有恰好 10 个用户显式回答，问题未展示给用户，或记录包含 Agent 代答、默认答案整体接受；
- 公式编号、标签或引用不闭合，未经审计地使用不编号展示公式；
- Word 的 OMML、编号连续性、图片嵌入或包结构验证失败；
- 引用无法对应真实条目；
- 中文论文缺少正文起草或成稿润色模式记录且无用户显式跳过、成稿保护检查失败、检查报告与最终源文件不对应，或润色后未重新生成交付物；
- 语言润色删除、弱化或伪造比赛要求的 AI 使用披露；
- 编译器可用但编译失败；
- 页面存在影响阅读或提交的裁切、重叠、越界、乱码、缺页；
- 正文泄露内部工作流、临时路径或调试信息。

## 可记录为警告或跳过

未引用的备用图、轻微 caption/篇幅失衡、非核心风格问题可以警告。编译器、渲染器或外部网络确实不可用时可以 `skipped`，但报告必须记录证据与影响；因此无法确认提交可用性时，总结论不能表述为“全部通过”。

## 报告最小结构

`VERIFY_REPORT.md` 至少包含结论、检查项表、结构、两个论文门禁的用户十问证据、中文润色保护证据（适用时）、公式、图表、数值一致性、引用、复现、编译/导出、视觉检查和未解决问题。`verification.json` 同时记录每项状态、证据路径、消息、时间和适用 waiver。

## 完成标准

结构化清单有效；所有关键 Artifact fresh；论文覆盖题目；数字、公式、图表和引用一致；选定格式可打开；必要工具可用时已实际编译/导出并逐页检查；不存在硬错误；报告足以让另一位验收者复核结论。
