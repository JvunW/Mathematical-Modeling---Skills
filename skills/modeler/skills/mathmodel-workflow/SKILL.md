---
name: mathmodel-workflow
description: "启动并协调完整数学建模任务。用于从赛题和附件开始，确认偏好、建立可移植工作区，并按分析、编码、图示、论文和验收阶段推进。"
---

# 数学建模工作流

本 skill 是数学建模任务的总控入口。它不替代后续阶段 skill，而是负责启动流程、确认偏好、记录决策、生成计划，并按顺序调用各阶段 skill。

## 数学建模规范参考

如需领域判断，读取 `../mathmodel-references/references/math-modeling-norms.md`。该文件只提供数学建模基本规范和防错知识，不改变本 skill 的阶段顺序和产出约定。

## 必须产出

把用户明确指定的任务目录作为 `<WORK_ROOT>`；若用户未指定，则使用当前工作目录。只在 `<WORK_ROOT>` 中创建或更新以下文件：

- `plan.md`：整体流程方案、建模方向、阶段顺序、预期产物和风险控制。
- `todo.md`：具体待办事项列表，记录每个阶段的任务和状态。

## 工作流

### 1. 确认用户偏好

在规划前，只询问会实质影响流程的问题。问题要少而关键。

优先询问（按重要性排序）：

1. **排版引擎**：Typst 还是 LaTeX？— 决定 `mathmodel-writing` 使用哪套模板和编译命令。Typst 使用 `typst` 命令编译；LaTeX 使用 `xelatex` 命令编译（需跑两遍解决交叉引用）。
2. **竞赛类型**：国赛/华为杯/华中杯/MCM/...— 决定模板选择，见 `mathmodel-writing` 的模板族清单。
3. **论文语言**：中文/英文 — MCM/ICM/COMAP 强制英文，其他默认中文。
4. **子问题数量是否已知**：影响章节文件生成数量。若未知，由 `mathmodel-analysis` 阶段根据题面确定。

将用户的选择记录到 `plan.md` 的"方案"小节中。


### 2. 制定方案

按以下结构编写 `plan.md`：

```markdown
# 方案

要依次调用这些 skill，按照里面要求完成任务。

用户偏好：
- 排版引擎：<Typst / LaTeX>
- 竞赛类型：<国赛 / 华为杯 / MCM / ...>
- 论文语言：<中文 / 英文>
- 子问题数量：<已知 N 个 / 待分析确定>

workflow:
   step      skills
1. 赛题分析与建模设计 - `$mathmodel-analysis`
2. 编程实现和图表生成 - `$mathmodel-coding`
3. 流程与架构图绘制 - `$mathmodel-drawio`
4. 竞赛论文撰写 - `$mathmodel-writing`
5. 验证和验收 - `$mathmodel-verification`
```

## 项目目录结构

各阶段按此骨架创建和填充文件：

```text
.
├── plan.md                      # 1: 本文件
├── todo.md                      # 1: 待办事项
├── reports/                     # 各阶段文档报告
│   ├── ANALYSIS_MODELING_REPORT.md  # 1: 赛题分析-建模报告
│   ├── RESULTS_REPORT.md            # 2: 结果报告
│   ├── DRAWIO_REPORT.md             # 3: 非数据图说明
│   ├── VERIFY_REPORT.md             # 5: 验收报告
├── code/                        # 2: 代码
│   ├── problem1.py
│   ├── problem2.py
│   ├── problem3.py               # 问题的数量应该更具题目动态调整
│   ├── ... 
│   └── utils.py
├── results/                     # 2: 结果记录
├── figures/                     # 2+3: 所有图表
│   ├── *.pdf                    #     数据图 + 非数据图 PDF
│   ├── *.drawio                 #     非数据图源文件
├── paper/                       # 4: 论文
│   ├── main.typ / main.tex      #     论文主文件（按用户选择的引擎）
│   └── sections/                #     各节文件（.typ 或 .tex）
```

方案必须明确每个阶段由哪个下游 skill 负责，以及该阶段应产出什么文件。

### 3. 生成待办

将 `todo.md` 写成阶段性 checklist，格式如下：

```markdown
# 待办事项

- [ ] 1. 赛题分析与建模设计 - `$mathmodel-analysis`
- [ ] 2. 编程实现和图表生成 - `$mathmodel-coding`
- [ ] 3. 流程与架构图绘制 - `$mathmodel-drawio`
- [ ] 4. 竞赛论文撰写 - `$mathmodel-writing`
- [ ] 5. 验证和验收 - `$mathmodel-verification`
```

每完成一个阶段，都要更新 `todo.md` 中对应任务的状态。

### 4. 依次执行阶段

按以下顺序调用下游 skills：

| 阶段 | Skill | 作用 | 主要产物 |
| --- | --- | --- | --- |
| 赛题分析与建模设计 | `$mathmodel-analysis` | 解析题意、识别变量/约束/数据/评价指标，并建立数学模型、目标函数、约束条件和求解策略。 | `reports/ANALYSIS_MODELING_REPORT.md` |
| 编程实现和图表生成 | `$mathmodel-coding` | 实现可复现代码，运行实验，生成结果表和数据图表。 | `code/`, `results/`, `reports/RESULTS_REPORT.md`, `figures/` |
| 流程与架构图绘制 | `$mathmodel-drawio` | 在论文确实需要时，绘制方法流程图、架构图和非数据型概念图。 | `figures/*.drawio`, `figures/*.pdf`, `reports/DRAWIO_REPORT.md` |
| 竞赛论文撰写 | `$mathmodel-writing` | 基于分析、建模、代码结果和图表撰写最终竞赛论文，并按章节直接插入图表。 | `paper/` |
| 验证和验收 | `$mathmodel-verification` | 检查可复现性、一致性、产物完整性、格式规范和提交就绪状态。 | `reports/VERIFY_REPORT.md` |

## 阶段边界

- `$mathmodel-coding` 负责生成所有依赖计算结果或实验输出的数据图表。
- `$mathmodel-drawio` 只负责概念图、算法流程图、架构图、路线图等非数据型图示。
- 不要让 `$mathmodel-drawio` 重复绘制 `$mathmodel-coding` 已经生成的统计图或数据图。
- `$mathmodel-writing` 负责决定图表在论文中的位置，并按所选引擎写入图表代码：
  - Typst：`#figure(image("../../figures/xxx.pdf", width: 85%), caption: [...])`
  - LaTeX：`\begin{figure}[H]\centering\includegraphics[width=0.85\textwidth]{../../figures/xxx.pdf}\caption{...}\label{fig:xxx}\end{figure}`
- 不要让 `$mathmodel-writing` 编造数值结论。论文中的数值必须来自 `reports/RESULTS_REPORT.md`、结果表或已生成图表的数据。
