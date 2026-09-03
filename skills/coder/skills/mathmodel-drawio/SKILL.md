---
name: mathmodel-drawio
description: "绘制数学建模论文所需的非数据型图示。用于根据模型和结果生成技术路线图、求解流程图、模型结构图或数据处理图，并在可用时导出 PDF。"
---

# DrawIO 非数据图示绘制

本 skill 通常由 `$mathmodel-figure-templates` 的引擎路由承接 `$mathmodel-coding`。它只负责论文中的**非数据型 DrawIO 图示**，例如技术路线图、求解流程图、模型结构图、数据处理流程图、变量关系图、指标体系图等；风格 profile 与跨引擎 Figure QA 仍由 `$mathmodel-figure-templates` 统一约束。

## 数学建模规范参考

如需额外的数学建模领域规范，并且 `$mathmodel-references` 已随建模手插件安装，可调用它查询“图表与可视化”和“非数据图工具选择”。未安装建模手插件时不得因此阻塞绘图，也不得为了凑数量生成额外图示。

## 阶段边界

- 本阶段负责：DrawIO 源文件、非数据图 PDF、图示生成记录。
- 本阶段不负责：折线图、柱状图、散点图、热力图、箱线图、雷达图等数据图。这些由 `$mathmodel-coding` 生成。
- 本阶段不重跑模型、不修改 `code/`，不改写 `reports/RESULTS_REPORT.md` 的数值结论。

## 必须产出

在当前工作目录创建或更新：

```text
figures/
  fig_roadmap.drawio
  fig_roadmap.pdf
  fig_flow_q1.drawio
  fig_flow_q1.pdf
  ...
reports/DRAWIO_REPORT.md
```

当模型包含三个以上相互依赖的阶段、多个分支，或仅靠文字难以解释结构时，优先绘制 `fig_roadmap` 技术路线图。若流程简单、版面受限或图不能提供额外信息，可以不画，并在 `reports/DRAWIO_REPORT.md` 中简要说明。

读取这些文件的目的不是提取数据作图，而是理解论文方法、章节结构、子问题关系和已有图表，避免重复。

## 工作流程

### Step 1: 盘点已有图表和需求

先读取以下文件（存在则读取）：`reports/ANALYSIS_MODELING_REPORT.md`、`reports/RESULTS_REPORT.md`、`figures/` 目录列表。

然后从前序文档提取非数据图需求，输出一个清单：

```text
DRAWIO PLAN CHECKLIST:
[ ] fig_roadmap      技术路线图，放在问题重述/绪论
[ ] fig_flow_q1      问题一求解流程图
[ ] fig_flow_q2      问题二求解流程图
[ ] fig_flow_q3      问题三求解流程图
[ ] fig_pipeline     数据处理流程图
[ ] fig_model        模型结构/变量关系图
```

清单不是固定模板，要根据题目实际删减或增补。不要为了凑图生成无意义图示。

### Step 2: 判定图类型

常见图示选择：

| 图类型 | 文件名建议 | 适用场景 |
| --- | --- | --- |
| 技术路线图 | `fig_roadmap` | 展示整体解题路线、章节逻辑、方法串联 |
| 子问题求解流程图 | `fig_flow_q1`, `fig_flow_q2` | 展示单个子问题的输入、判断、算法、输出 |
| 数据处理流程图 | `fig_pipeline` | 展示数据清洗、特征构造、建模输入 |
| 模型结构图 | `fig_model` | 展示模块关系、变量关系、模型层次 |
| 指标体系图 | `fig_index_system` | 展示目标层、准则层、指标层 |
| 决策树/规则图 | `fig_decision_tree` | 展示分类规则、设备选择、策略分支 |

不要用 DrawIO 画这些图：

- 结果对比柱状图
- 预测误差曲线
- 灵敏度曲线
- 相关性热力图
- 分布图和箱线图

### Step 3: 生成 DrawIO 源文件

每张图一个 `.drawio` 文件，放在 `figures/`。

DrawIO 内容要求：

- 文字语言与论文语言一致。
- 节点文字短，必要时双行，不堆长句。
- 同类节点样式统一。
- 箭头方向清晰，避免交叉。
- 图中不写大段解释，解释留给论文正文。
- 不使用装饰性阴影和过度渐变。

生成 XML 时使用当前 harness 提供的文件编辑能力，确保文件是完整、合法的 UTF-8 XML。不要依赖 Bash heredoc；写入后重新读取文件头尾并检查 XML 结构是否闭合。

### Step 4: 导出 PDF

优先使用本 skill 自带的跨平台导出脚本。将 `<SKILL_DIR>` 替换为本 `SKILL.md` 所在目录：

```text
python "<SKILL_DIR>/scripts/export_drawio.py" figures/fig_roadmap.drawio
```

脚本会依次检查 `DRAWIO_BIN` 环境变量、系统 PATH 和常见 Windows/macOS 安装位置。可用 `--output` 指定输出文件，或用 `--drawio-bin` 明确指定可执行文件。如果无法导出 PDF，保留 `.drawio`，在 `reports/DRAWIO_REPORT.md` 记录失败原因和脚本输出。

### Step 5: 自检和修复

每张图必须检查：

- `.drawio` 文件非空。
- 若导出成功，`.pdf` 文件非空。
- 节点没有明显重叠。
- 箭头不穿过核心节点。
- 字号、颜色、边框风格一致。
- 文件名和图意一致。
- 没有与 `$mathmodel-coding` 的数据图重复。

发现问题要修 `.drawio` 并重新导出，不要只在报告里解释。

### Step 6: 写生成记录

创建 `reports/DRAWIO_REPORT.md`，至少包含：

```markdown
# DrawIO 图示生成报告

## 图示清单
| 文件 | 类型 | 来源依据 | 用途 | 状态 |
| --- | --- | --- | --- | --- |

## 未生成图示及原因

## 导出与自检记录

## 给论文阶段的嵌入建议
```

嵌入建议只说明每张图适合放入哪个章节和建议 caption，不生成 `*_typst_includes.typ`。最终的图表插入代码（Typst 的 `#figure(image(...), caption: [...])` 或 LaTeX 的 `\begin{figure}...\end{figure}`）由 `$mathmodel-writing` 根据论文结构和所选引擎决定。

## 质量要求

- 图示服务论文论证，不为装饰而画。
- 每张图必须能对应到`reports/ANALYSIS_MODELING_REPORT.md` 中的真实方法。
- 数据型图表不得在本阶段重复生成。
- 论文阶段引用的非数据图都应有 `.drawio` 源文件和 PDF，或者在 `reports/DRAWIO_REPORT.md` 说明导出失败。
