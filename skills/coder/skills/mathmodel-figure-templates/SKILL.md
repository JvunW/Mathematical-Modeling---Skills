---
name: mathmodel-figure-templates
description: "为数学建模论文设计、生成和验收数据图与结构图。用于 Matplotlib、TikZ、DrawIO 或 Mermaid 引擎选择，Nature/Science/IEEE/MCM/CUMCM 风格适配，以及编译、重叠、差异和视觉 QA；普通模型计算仍由 mathmodel-coding 负责。"
---

# 数学建模 Figure System

本 skill 把原有 Matplotlib 模板扩展为三层系统：`figure-engine` 决定怎样画，`figure-style` 决定怎样呈现，`figure-qa` 决定能否交付。路径均相对于本 `SKILL.md` 所在目录解析。

## 1. Figure Contract：先结论，后画图

任何新图先写一个不超过 8 行的 Figure Contract，并把它保存到绘图脚本、TikZ 文件头部或生成报告中：

```text
核心结论：这张图要让读者相信什么？必须包含动作或比较。
证据来源：对应哪个真实结果文件、字段、模型步骤或公式？
读者路径：读者应按什么顺序读完这张图？
视觉中心：Hero 模块是什么；若图很简单，明确写“无 Hero”。
辅助证据：每个 Panel 分别增加哪条不可由其他 Panel 推回的信息？
目标载体：论文路线、最终尺寸、语言和 style profile。
可删项：删掉哪些元素仍不损害结论？能删就删。
```

Conclusion-first 是硬约束：不得先挑模板再反向拼凑结论。数据含义、单位、分组、误差定义或模型方向不明确时，先核对证据，不用审美掩盖歧义。

## 2. 路由引擎

只读取本次需要的引擎说明：

- 数据驱动的折线、分布、误差、模型比较与多 Panel 图：读 `references/figure-engine/matplotlib.md`。
- 需要公式节点、精确连线、变量关系、几何或论文内原生矢量图：读 `references/figure-engine/tikz.md`。
- 可编辑技术路线图、指标体系或人工拖拽布局：读 `references/figure-engine/drawio.md`，并调用 `$mathmodel-drawio`。
- 需要轻量文本化流程草图或文档内预览：读 `references/figure-engine/mermaid.md`；Mermaid 不自动成为最终投稿图。

不要用 TikZ 重画大规模真实数据曲线；不要用 Matplotlib 冒充需要精确公式关系的结构图。混合图允许 Matplotlib 负责数据 Panel、TikZ 负责结构总览，但必须统一风格与尺寸。

## 3. 风格层

按目标载体只读一个 profile：

- `references/figure-style/nature.md`
- `references/figure-style/science.md`
- `references/figure-style/ieee.md`
- `references/figure-style/mcm.md`
- `references/figure-style/cumcm.md`

风格层不能改变数据、统计定义或模型含义。期刊或竞赛的数字规范可能更新；正式投稿或参赛前核对当年官方要求。

## 4. 复杂图的 Module-first 流程

对包含多层结构、嵌入数据图或多个 Panel 的复杂图，按以下顺序迭代：

1. 从论文内容和结果证据中冻结核心结论。
2. 先画 Hero 模块，单独编译、渲染和检查。
3. 加入主流程、分区和关键连线，再编译检查读者路径。
4. 加入辅助 Panel；每个 Panel 必须提供独有证据，不能重复 Hero 或主流程。
5. 执行完整编译，按最终栏宽渲染。
6. 运行结构检查并亲眼执行视觉 QA；有 blocker 就修复后从完整编译重跑。
7. 将图插入论文主文件，完成整页尺度检查，防止单图合格但页面失衡。

简单几何图、单链流程或单一数据图可以一次生成，不强制制造 Hero 或辅助 Panel。复杂度由论证需要决定，不由节点数量或“看起来高级”决定。

## 5. TikZ 快速路径

1. 从 `assets/example-skeletons/` 选择 `pipeline.tex` 或 `central-hero.tex`，仅在拓扑匹配时复用。
2. 需要局部组件时，从 `assets/tikz-snippets/` 选择 heatmap、bar、line、formula、pipeline、layer、feedback 或 palette 片段。
3. 生成独立 `.tex` 后运行：

```text
python "<SKILL_DIR>/scripts/run_figure_qa.py" figure.tex --report figure-qa.json
```

需要逐项诊断时，运行同一流程拆出的命令：

```text
python "<SKILL_DIR>/scripts/check_tikz_safety.py" figure.tex
python "<SKILL_DIR>/scripts/tikz_validator.py" figure.tex
python "<SKILL_DIR>/scripts/tikz_design_linter.py" figure.tex --type auto
python "<SKILL_DIR>/scripts/compile_render.py" figure.tex --dpi 180
python "<SKILL_DIR>/scripts/pdf_overlap_checker.py" figure.pdf --json
```

安全检查和编译失败是 blocker。设计 linter 默认提供建议，不会强迫简单图增加装饰。缺少可选的 PDF 几何依赖时必须报告 `skipped`，不得伪装通过。

## 6. Matplotlib 模板快速路径

先在 `references/figure-catalog.md` 中匹配图型，再运行：

```text
python "<SKILL_DIR>/scripts/render_template.py" paired-raincloud
```

模板的模拟数据只用于展示布局。替换成用户数据时保留源数据、转换、误差定义、随机种子、PNG 预览以及 PDF/SVG 矢量输出；不得声称模拟值复现了某篇研究。

## 7. Figure QA

任何交付都读 `references/figure-qa/qa-workflow.md`。人工视觉检查读 `references/figure-qa/visual-checklist.md`。最低证据包括：

- 源数据或结构语义可追溯；
- 源文件可重新生成；
- 编译或绘图命令刚刚成功运行；
- 最终尺寸下文字可读，无裁切、重叠、错误箭头或空白失衡；
- 灰度和色觉缺陷条件下仍能区分关键编码；
- 图注解释误差、样本量、单位和必要的统计信息；
- 插入论文后完成整页视觉检查。

有参考图时可运行 `scripts/figure_diff.py` 定位结构差异，但相似度不能替代科学正确性和人工审美判断。

## 8. 输出契约

交付至少包含：

- 可编辑源文件：`.py`、`.tex`、`.drawio` 或 `.mmd`；
- 论文用矢量文件：PDF 或 SVG；
- 用于视觉检查的 PNG；
- Figure Contract、生成命令、数据来源和 QA 结果；
- 未执行或被跳过的检查及原因。

禁止把截图作为唯一成果，禁止在绘图阶段手工改数，禁止以“风格像 Nature”暗示图已满足目标期刊的全部投稿规范。

维护本 skill 或重新同步上游思想时，先读 `references/source-provenance.md`，遵守其中的固定 revision、许可证和 clean-room 边界。
