---
name: mathmodel-writing
description: "撰写并排版数学建模论文，支持 Typst、LaTeX 和用于 Word 原生公式导出的 Markdown。用于根据模型、真实计算结果和图表组织章节，并通过 Codex 联网搜索、OpenAlex 或人工 Deep Research 检索和核验参考文献；需要 DOCX 时与 $export-math-docx 配合。"
---

# 竞赛论文撰写（Typst / LaTeX / Word）

本 skill 通常承接 `$mathmodel-coding` 和 `$mathmodel-drawio`。前序阶段只提供真实数据、图表 PDF 和记录文件；本阶段负责选择比赛模板和排版引擎、组织论文结构，并决定每张图表放入哪个章节。

**Typst 引擎**下可调用 typst-author skill 学习 typst 写法；**LaTeX 引擎**参考本文件末尾的“LaTeX 写作要点”；**Word 交付**使用 Markdown 写作并调用 `$export-math-docx` 生成原生 OMML 公式。

## 数学建模规范参考

如需额外的数学建模领域规范，并且 `$mathmodel-references` 已随建模手插件安装，可调用它查询“论文写作”“图表与可视化”和“非数据图工具选择”。未安装建模手插件时不得因此阻塞写作，论文结构仍按比赛模板和当前赛题内容决定。

## 模板族

本技能内捆绑的模板位于：

```text
assets/templates/zh/<竞赛>/main.typ         # Typst 模板
assets/templates/zh/<竞赛>-latex/main.tex   # LaTeX 模板
assets/templates/en/<竞赛>/main.typ         # Typst 模板
assets/templates/en/<竞赛>-latex/main.tex   # LaTeX 模板
```

**LaTeX 模板覆盖范围**：所有中文模板和英文模板均已提供 LaTeX 版本（`-latex` 后缀），使用 xelatex 编译。

支持的中文模板（Typst + LaTeX 双版本）：

```text
apmcm, changsanjiao, cumcm, default, diangongbei, dongsansheng,
huashubei, huaweibei, huazhongbei, mathorcup, mcm, shuweibei, stats, wuyibei
```

华为杯、华中杯、五一杯统一使用 `huaweibei`、`huazhongbei`、`wuyibei` 作为模板。

支持的英文模板（Typst + LaTeX 双版本）：

```text
apmcm, default, mcm
```

论文中的所有数值图表结论必须来自 `reports/RESULTS_REPORT.md` 或 `figures/*`。不得编造、估算或使用不同的四舍五入方式。

## 内容最低契约（CUMCM）

排版模板只规定外观，不代表论文内容已经完成。对题目中的每个子问题，正文必须同时交付：

1. **问题对象与数据口径**：说明样本单位、标签/响应变量、筛选规则和有效样本量；重复测量必须说明按个体划分还是按记录计算。
2. **可复核模型**：给出目标函数或模型方程、变量含义、参数估计/搜索方法，以及关键超参数或成本参数的来源。
3. **真实结果证据**：至少一张由当前运行结果生成的表格或图，报告精确指标、分组数量、系数/概率/误差或最优解；正文必须解释证据而非只放图表。
4. **验证与边界**：至少报告一种误差、交叉验证、残差/显著性、敏感性或稳定性检验，并明确不能从结果推出的结论。

问题章节不能只写“采用某模型”和“得到某结论”。如果某一问没有可计算的验证指标，应写出原因、替代检查和局限。摘要中的每个子问题也必须与正文结果逐项对应。附录应直接嵌入本次运行所用的完整源代码（优先使用 `\\lstinputlisting` 或等价机制），不能只列出命令和输出文件名。

### 问题清单门禁

正式写作前，必须从题面和结果报告建立实际问题清单，不得从模板文件数量推断问题数量。清单至少记录：

- 题目中的子问题编号和原始要求；
- 每问的输入、输出、决策变量或评价指标；
- 对应的结果文件、图表和预计正文章节；
- 与其他问题的依赖关系，以及该问的验证方式。

`PAPER_CONTENT_PLAN.md` 必须包含一行对应每个实际子问题的清单。摘要、问题重述、正文入口文件和结果章节中的问题集合必须完全一致：题面有而正文没有的子问题属于硬错误；摘要提到而正文没有模型、结果和结论的子问题属于硬错误。不得用“问题一至三”的固定示例替代实际清单。

## 逐问内容矩阵（CUMCM）

正式写作前，先创建 `reports/PAPER_CONTENT_PLAN.md`，先列出实际问题清单，再把每个子问题拆成“论点—证据—章节”映射。每个论点必须绑定到已有的 `reports/*.md`、`results/*.csv`、`results/*.json` 或 `figures/*.pdf`；论文手可以整理和计算这些文件中的确定性汇总，但不得凭记忆补造数值。

```text
Q1...Qn -> 问题分析、数据口径、模型假设、公式/目标函数、算法参数、结果证据、验证、局限和题目回答
```

计划文件至少使用以下字段，便于验收阶段逐项核对：

```markdown
| 问题 | 题目要求 | 输入/输出 | 模型与参数 | 核心论点 | 结果证据 | 验证/边界 | 正文章节 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | ... | ... | ... | ... | results/q1.csv | 分组交叉验证 | 5_problem1 | READY |
```

如果某个格子没有真实证据，必须在计划中标记 `EVIDENCE_GAP`，并在正文中说明缺失原因及其对结论的影响；不得用泛化的“结果表明”代替缺失证据。每个问题必须形成以下闭环：题目要求 -> 模型/算法 -> 真实结果 -> 结果解释 -> 验证或替代检查 -> 适用边界 -> 对题目要求的明确回答。

### 正文章节最低结构

章节数量按题目实际子问题确定，不强行添加不存在的问题。对三问及以上的 CUMCM 论文，正文至少满足：

- **问题重述**：背景、任务分解、研究目标三个层次，不能只有一段概述。
- **问题分析**：每个子问题各有一个分析小节，说明输入、输出、关键难点和与后续模型的关系。
- **每个问题章节**：至少包含“模型建立”“算法与参数”“结果与验证”三个小节；若题目有模型比较或参数扰动，再增加“模型比较/敏感性分析”。
- **结果与验证**：至少一张核心结果表，表后有数值解释；另有误差、交叉验证、稳定性、敏感性或边界证据中的至少一项。
- **问题小结**：明确回答题目要求，指出结果适用范围和不能推出的结论。

正文目标是论证完整而不是凑页数。某一问题篇幅明显偏少时，先检查是否缺少推导、参数、结果解释或验证；不得通过增大字号、空行或重复结论补页。篇幅只能作为人工复核线索，不能替代内容证据。

### 按模型类型选择验证证据

验证不能只套用“报告一个指标”。根据实际模型类型，至少选择与结论风险匹配的一组证据；没有相应证据时必须降低结论强度并说明原因：

- **连续回归/响应面**：分组交叉验证或 Bootstrap，并补充残差、误差区间、基线比较或系数稳定性中的至少一项。
- **生存/删失模型**：说明事件和删失口径，报告置信区间、风险集或分组稳定性，并对关键时点权重、阈值或删失假设做敏感性检查。
- **分类模型**：按个体或其他合理单位划分训练验证集，至少报告混淆矩阵和类别不平衡相关指标；概率模型还应检查校准或 Brier，不能只用 Accuracy/F1。
- **优化/决策模型**：报告约束可行性、基线方案或替代算法比较，并检查参数扰动、重复求解或边界条件下的稳定性。

若一篇论文同时包含多种模型，按问题分别验收，不得用一个分类指标替代回归、生存或优化问题的验证。

## CUMCM 提交约束与数量控制

以下是 CUMCM 最终提交版的硬约束；字体、字号、行距和颜色只作为项目默认风格，不得伪装成全国统一规则：

- 电子版论文从摘要页开始，不包含承诺书、编号专用页和目录；纸质版的专用页按赛区要求另行处理。
- 中文摘要（含标题和关键词）原则上不超过一页，摘要必须覆盖每个实际子问题的方法和关键结果。
- 正文不超过比赛当年官方规定的页数；附录可包含完整、可运行的本次源代码和支撑材料清单。
- 论文、章节、图表和附录不得出现学校、赛区、队号、队员姓名等身份信息。
- 页数、表格数和图片数只用于发现内容失衡，不设“每问必须几页、几张图表”的硬目标。

- 每个子问题原则上放 1--2 张核心结果表和 0--2 张核心图；至少有一项证据用于回答题目，另一项用于验证、比较或敏感性分析。只有在图表表达不同证据时才增加。整篇正文建议不超过 10 张表和 8 张图。
- 表格优先三线表，不使用竖线和大面积底色；单位写在列名中，数值保留与误差水平匹配的 3--4 位有效数字，同一指标在全文使用同一精度。表题置于表格上方，表格必须在正文中先解释后出现或出现后解释，不能连续堆放。
- 表格宽度按信息量决定，而不是所有表格统一铺满：2--3 列的系数/符号表使用 `0.68--0.82\\textwidth` 并居中；4 列及以上、结果对比表或含长文本的表使用 `tabularx`/等价版心约束，宽度通常为 `0.82--1.00\\textwidth`。表格横线应与表格主体等宽，不能只按文字自然宽度生成一条孤立的窄线。
- LaTeX 宽表优先使用 `tabularx`、`p{}` 或 `X` 列自动换行；Typst 使用显式列宽（如 `1fr`）和 `width` 约束。不得为了“铺满一行”拉伸只有两三列的窄表，也不得用 `\\resizebox` 把宽表缩到难以阅读。
- 使用 CUMCM Typst 模板的 `three-line-table` 时，结果表默认使用 `table-width: 86%`；符号/参数表可显式传入 `table-width: 74%`，禁止依赖内容自然宽度产生窄横线。
- 默认表格参数保持克制：`\arraystretch` 约 `1.15--1.30`、`\tabcolsep` 约 `5--8pt`；不通过极小字号或负间距压缩表格。符号表的含义列允许换行，单位统一使用中文或规范数学单位，禁止同一列混用 `degree` 等非统一写法。
- 图表宽度以版心为上限，单栏图通常为 `0.78--0.88\\textwidth`；图题简洁并说明样本、指标和条件。禁止用同一数据同时做表格和图，除非二者承担不同阅读任务。
- 正文采用黑、灰和一种低饱和强调色；颜色只表达分组或模型差异，不把红/绿作为唯一语义。图表转为灰度后仍应靠线型、点型或文字区分，保证打印和色觉缺陷阅读。
- 颜色、字号和线宽在全篇统一；不使用渐变、装饰性背景、彩色大标题或与数据无关的插图。任何颜色选择都不能牺牲表格可读性和正式竞赛风格。


## 工作流

### 步骤 0：确定排版引擎

**撰写论文前必须让用户选择排版引擎。** 引擎决定后续所有步骤（模板路径、章节文件扩展名、图片插入语法、编译命令），选错会导致整篇论文格式错误。

如果用户尚未指定，使用当前 harness 可用的询问方式确认：“撰写论文使用哪种排版引擎？”

- 选项 1：LaTeX（xelatex 编译，数学建模竞赛主流，模板已全部就绪）— 推荐选项放第一位
- 选项 2：Typst（typst 编译，调用 typst-author skill 辅助写作）
- 选项 3：Word（Markdown 写作，Pandoc 导出 DOCX，公式为原生 OMML）

询问前先读取 `plan.md` 的"用户偏好 → 排版引擎"字段作为预选项：
- 若 plan.md 已记录引擎选择，向用户确认："检测到之前选择的引擎是 <LaTeX/Typst/Word>，是否沿用？"
- 若 plan.md 不存在或未记录引擎选择，直接询问用户选择。
- 若用户未明确指定或跳过，**默认使用 LaTeX**。

根据确定的引擎选择对应模板族：

- **Typst 引擎**：使用 `assets/templates/<lang>/<竞赛>/main.typ`，调用 `$typst-author`。编译命令 `typst compile main.typ`。
- **LaTeX 引擎**：使用 `assets/templates/<lang>/<竞赛>-latex/main.tex`，xelatex 编译（中文和英文均需跑两遍解决交叉引用）。编译命令 `xelatex -interaction=nonstopmode main.tex`（执行两次）。
- **Word 交付**：使用 UTF-8 `paper/paper.md`，数学公式采用 `$...$` / `$$...$$`，完成写作后调用 `$export-math-docx`。不需要 Typst 或 XeLaTeX。

**后续步骤中的所有代码示例、文件扩展名、图片插入语法都必须按所选引擎选择对应版本，不要混用。**

### 步骤 1：选择语言和模板


除非用户明确要求中文，否则 MCM/ICM/COMAP 一律使用英文。所有中文竞赛名称使用中文。

模板键示例（Typst 引擎）：

```text
长三角 -> zh/changsanjiao
APMCM 英文版 -> en/apmcm
全国赛/国赛/CUMCM -> zh/cumcm
统计建模 -> zh/stats
MCM/ICM/COMAP -> en/mcm
```

模板键示例（LaTeX 引擎）：

```text
全国赛/国赛/CUMCM -> zh/cumcm-latex
MCM/ICM/COMAP -> en/mcm-latex
```

Word 交付不使用上述 Typst/LaTeX 模板目录。确认用户提供的官方 `.docx` 是仅供样式继承的 reference DOCX，还是包含必须保留正文的固定模板；后者不能直接假定通过 Pandoc `--reference-doc` 完整保留。

### 步骤 2：准备模板

把本 `SKILL.md` 所在目录解析为 `<SKILL_DIR>`，再检查对应模板文件是否存在。不要假设 Skill 位于某个固定的用户目录或项目目录。

**Word 交付**：创建 `<WORK_ROOT>/paper/paper.md`。若用户给出纯样式 reference DOCX，记录其路径供 `$export-math-docx` 使用；若没有模板，使用 Pandoc 默认 DOCX 样式并明确说明。若官方模板含必须保留的封面、表格或填写区，先规划生成后合入模板的 DOCX 编辑步骤，不得把它当作普通 reference DOCX。

**Typst 模板**：

```text
<SKILL_DIR>/assets/templates/zh/<竞赛>/main.typ
```

- **文件存在**：直接将 `assets/templates/zh/<竞赛>/` 整目录复制到 `<WORK_ROOT>/paper/`。这些模板是自包含入口文件，不依赖额外共享样式文件。
- **文件不存在（MISSING）**：说明 skill 未完整安装或在沙箱中，此时依照本 SKILL.md 步骤 3 列出的对应节文件结构，从零重建最小可编译 Typst 框架，并在 `paper/` 内注明"重建自 default 结构"。

存在匹配模板时，绝不从零开始写论文；复制后必须先清除模板中的可见示例正文、示例数值、示例变量和示例图表，再写入当前赛题内容。模板只提供版式和空章节骨架，不能作为论文内容来源。

**LaTeX 模板**：

```text
<SKILL_DIR>/assets/templates/zh/<竞赛>-latex/main.tex
```

- **文件存在**：将 `assets/templates/zh/<竞赛>-latex/` 整目录复制到 `<WORK_ROOT>/paper/`。
- **文件不存在（MISSING）**：说明 skill 未完整安装或在沙箱中，此时依照本 SKILL.md 步骤 3 列出的对应节文件结构，从零重建最小可编译 LaTeX 框架，并在 `paper/` 内注明"重建自 default-latex 结构"。

复制 CUMCM 模板后，根据题目实际顶层问题数量重写入口文件的 `\\input{}` 或 `#include()` 列表。不得保留不存在的问题章节，也不得因为模板自带三个问题文件就强行写成三问论文。


### 步骤 3：构建图表规划

在写正文各节之前，根据 `figures/*.pdf`、`reports/RESULTS_REPORT.md`，以及 `reports/DRAWIO_REPORT.md`（如果存在）构建图表规划：

```text
图表规划
fig_roadmap.pdf -> 引言/问题重述
fig_flow_q1.pdf -> 问题一模型构建
fig_flow_q2.pdf -> 问题二模型构建
fig_pipeline.pdf -> 数据预处理/方法节
结果图 -> 对应的结果节
```

图片路径相对于写入该图片的文件：写在 `paper/main.typ` 或 `paper/main.tex` 中通常用 `../figures/xxx.pdf`，写在 `paper/sections/*.typ` 或 `paper/sections/*.tex` 中通常用 `../../figures/xxx.pdf`。

Word 交付优先使用 PNG、JPEG 或 SVG，避免直接嵌入 Word 不支持的 PDF 图片；图片路径相对于 `paper/paper.md`。

**Typst 引擎**图片插入：

```typst
#figure(
  image("../../figures/fig_q1_error_dist.pdf", width: 85%),
  caption: [问题一预测误差分布],
)
```

**LaTeX 引擎**图片插入：

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{../../figures/fig_q1_error_dist.pdf}
  \caption{问题一预测误差分布}
  \label{fig:q1_error}
\end{figure}
```

**Word 交付**图片插入：

```markdown
![问题一预测误差分布](../figures/fig_q1_error_dist.png)
```

英文论文使用英文图注。

### 步骤 4：撰写各节

**以下章节文件名按所选引擎使用 `.typ`（Typst）或 `.tex`（LaTeX）扩展名。** 例如 Typst 引擎用 `1_restatement.typ`，LaTeX 引擎用 `1_restatement.tex`。文件名主体保持一致。

写作时先读取并列出当前工作区中全部结果来源，再按内容矩阵逐节生成正文：

1. 读取 `ANALYSIS_MODELING_REPORT.md`、`RESULTS_REPORT.md` 和 `PAPER_CONTENT_PLAN.md`，先核对题面实际问题清单。
2. 枚举 `results/` 和 `figures/`，将每个结果文件绑定到具体问题和具体小节；不能只引用报告摘要而忽略结果明细。
3. 先完成问题重述、逐问分析、假设和符号，再逐问完成“模型—算法—结果—验证—小结”；不得先复制模板后只替换标题和一段结论。
4. 每完成一问，立即检查该问是否覆盖题目要求，并且有模型公式、算法/参数、真实结果表或图、结果解释、匹配模型类型的验证和适用边界；缺项回到该问补齐。
5. 如果某问的结果被后续问题使用，必须在正文中写出变量、特征或决策结果如何传递，不能只用“为后续分析提供基础”代替。
6. 发现 `EVIDENCE_GAP` 时保留缺口说明并降低结论强度，不得以示例数据、通用模型描述或虚构置信区间填充正文。

在生成最终 PDF 前必须完成一次逐问内容门禁：实际问题清单、摘要、问题分析、正文入口和问题章节的编号集合必须一致；每个问题章节都要有与当前结果文件对应的模型公式或目标函数、真实结果证据、解释该证据的段落、匹配模型类型的验证、适用边界和明确的小结。最终结论或建议型题目还必须有一张统一的决策/推荐汇总表，避免不同章节给出无法比较的结果。缺少任一项时停止编译交付并回到该问题补写；不能以“待补充”、空章节或只有摘要数字通过验收。

Word 交付不拆成这些 `.typ` / `.tex` 文件；在单个 `paper/paper.md` 中按相同章节顺序使用 Markdown 一级、二级标题。公式只使用 Pandoc 能解析的标准 LaTeX 数学语法，行内用 `$...$`，行间用 `$$...$$`，避免自定义宏和 TikZ。

中文数学建模通用模板各节文件（`changsanjiao`、`diangongbei`、`huashubei`、`mathorcup`、`wuyibei`）：

```text
1_restatement.typ  - 问题重述与分析
2_analysis.typ     - 数据理解与总体思路
3_assumptions.typ  - 模型假设
4_symbols.typ      - 符号说明
5_problem1.typ     - 问题一建模与求解
6_problem2.typ     - 问题二建模与求解
7_problem3.typ     - 问题三建模与求解
...         - 根据题目调整问题数量  
8_evaluation.typ   - 灵敏度分析、模型评价与推广
A_code.typ         - 附录代码
```

国赛/华中杯/华为杯（`cumcm`、`huazhongbei`、`huaweibei`）按以下章节结构：

```text
1_restatement.typ
2_analysis.typ
3_assumptions.typ
4_symbols.typ
5_problem1.typ
6_problem2.typ
7_problem3.typ
...        - 根据题目调整问题数量
8_sensitivity.typ
9_evaluation.typ
A_code.typ
```

东三省模板（`dongsansheng`）额外使用单独摘要文件：

```text
abstract.typ
1_restatement.typ
2_analysis.typ
3_assumptions.typ
4_symbols.typ
5_problem1.typ
6_problem2.typ
7_problem3.typ
...       - 根据题目调整问题数量
8_evaluation.typ
A_code.typ
```

数维杯模板（`shuweibei`）保留原 LaTeX 的示例入口命名：

```text
Abstract.typ
Introduction.typ
2_analysis.typ
3_assumptions.typ
4_symbols.typ
5_problem1.typ
6_problem2.typ
7_problem3.typ
...      - 根据题目调整问题数量
8_evaluation.typ
Appendices1.typ
A_code.typ
```

中文默认模板（`default`）：

```text
1_restatement.typ
2_assumptions.typ
3_symbols.typ
4_problem1.typ
5_problem2.typ
6_problem3.typ
...      - 根据题目调整问题数量
7_sensitivity.typ
8_evaluation.typ
A_code.typ
```

中文统计建模各节文件：

```text
1_introduction.typ
2_method.typ
3_data.typ
4_analysis.typ
5_results.typ
6_conclusion.typ
A_code.typ
```

英文 MCM/APMCM 各节文件（`en/mcm`、`en/apmcm`、`zh/mcm`、`zh/apmcm`）：

```text
1_introduction.typ
2_assumptions.typ
3_model_design.typ
4_solution.typ
5_sensitivity.typ
6_strengths_weaknesses.typ
7_conclusions.typ
A_code.typ
```

**LaTeX 模板章节文件**（对应 `-latex` 后缀模板，结构与 Typst 版本一一对应）：

国赛 LaTeX 模板（`zh/cumcm-latex`，对应 `cumcm` Typst 版本）：

```text
1_restatement.tex
2_analysis.tex
3_assumptions.tex
4_symbols.tex
5_problem1.tex
6_problem2.tex
7_problem3.tex
8_sensitivity.tex
9_evaluation.tex
A_code.tex
```

MCM/ICM LaTeX 模板（`en/mcm-latex`）：

```text
1_introduction.tex
2_assumptions.tex
3_model_design.tex
4_solution.tex
5_sensitivity.tex
6_strengths_weaknesses.tex
7_conclusions.tex
A_code.tex
```

其余 LaTeX 模板（`changsanjiao-latex`、`default-latex`、`huashubei-latex`、`mathorcup-latex`、`wuyibei-latex`、`huazhongbei-latex`、`huaweibei-latex`、`diangongbei-latex`、`dongsansheng-latex`、`shuweibei-latex`、`stats-latex`、`apmcm-latex`、`mcm-latex`、`en/apmcm-latex`、`en/default-latex`）的章节文件命名与上述结构类似，以 `main.tex` 中 `\input{}` 引用的文件名为准。

英文默认模板（`en/default`）：

```text
1_introduction.typ
2_assumptions.typ
3_notations.typ
4_model.typ
5_sensitivity.typ
6_evaluation.typ
7_conclusions.typ
A_code.typ
```

**正文写作应使用连贯的学术段落。避免在最终论文中出现工作流内部名称，如 `reports/`、`figures/` 或 `CLAUDE.md`。**

### 步骤 5：参考文献

只使用真实存在的参考文献。文件名按引擎选择：Typst 用 `paper/references.typ`，LaTeX 用 `paper/references.tex`；Word 交付把完整参考文献条目写入 `paper/paper.md` 末尾的“参考文献”章节。

#### 文献检索与核验

凡论文需要引用方法来源、领域背景、参数依据或相关研究时，必须先进行可追溯检索，不得凭模型记忆生成参考文献。优先使用当前 Codex 会话提供的联网搜索工具或 `$paper-lookup` 的结构化数据库；ChatGPT Deep Research 仅作为当前环境没有联网工具时的人工备用流程，不作为本地脚本自动调用的接口。

按以下顺序执行：

1. 根据论文主题和具体方法构造 2 至 5 个中英文检索式，避免只使用宽泛的赛题名称。
2. 若已配置 `OPENALEX_API_KEY`，可优先使用 OpenAlex；将原始结果保存到 `reports/openalex_results.json`。未配置密钥时，不得发送匿名 OpenAlex 请求。
3. 若 OpenAlex 未配置或不可用，且当前 Codex 会话提供联网搜索工具，直接使用该工具发现候选论文、方法和权威来源页；联网搜索不需要额外的 OpenAI API 密钥。
4. 若当前环境没有联网搜索工具，再提示用户手动使用 ChatGPT Deep Research；不得声称已经自动调用 Deep Research，也不得把 Deep Research 报告本身当作参考文献。
5. 对联网搜索、Deep Research 或其他数据库得到的每篇候选文献，使用 Crossref、Semantic Scholar、arXiv、PubMed 或 DOI/出版社页面核验标题、作者、年份、来源和 DOI。API 未返回的卷、期、页码或 DOI 必须省略，禁止推测或补造。
6. 按内容相关性筛选文献。优先选择来源明确、与实际模型或论点直接相关的记录；引用次数和发表年份只能作为辅助指标，不能替代相关性判断。
7. 创建 `reports/LITERATURE_REPORT.md`，记录检索式、来源类型（OpenAlex、Codex 联网搜索或 Deep Research）、候选文献的核验状态、拟支持的论文论点，以及舍弃候选文献的主要原因。
8. 论文正文和参考文献文件只能使用已经写入 `reports/LITERATURE_REPORT.md` 且已独立核验的文献。

任何检索源请求失败时，记录请求时间、检索式和错误原因，再按上述顺序切换到可用来源；不得因某个数据库不可用而改用模型记忆编造引用。后续验收必须能够区分结构化数据库结果、Codex 联网搜索结果、Deep Research 发现结果和最终核验结果。

完成检索后再按所选排版引擎生成参考文献文件。

**Typst 引擎**：

```typst
#set enum(numbering: "[1]")
#enum[
  作者. 题名[J]. 期刊名, 年份, 卷(期): 页码.
  Author. "Title." Journal or Conference, year.
]
```

正文上标引用：`相关研究已用于物流网络优化#super("[1]")。`

**LaTeX 引擎**：

```latex
\begin{thebibliography}{99}
  \bibitem{ref1} 作者. 题名[J]. 期刊名, 年份, 卷(期): 页码.
  \bibitem{ref2} Author. "Title." Journal, year.
\end{thebibliography}
```

正文引用用 `\cite{ref1}` 或 `\cite{ref1,ref2}`。

**Word 交付**：正文使用稳定的数字引用标记，如 `[1]` 或 `[1–3]`；在 `paper/paper.md` 末尾使用有序列表写入已经核验的完整条目。不得输出只存在于内部报告而未进入最终 Word 的参考文献文件。

### 步骤 6：最后撰写摘要或总结

在所有章节完成后撰写摘要或总结。CUMCM 中文论文使用中文摘要和关键词，不使用 MCM/ICM 的 Summary Sheet 结构；摘要必须包含每个实际子问题的方法和精确的数值结果。

Word 交付完成 `paper/paper.md` 后，调用 `$export-math-docx` 生成最终 DOCX 和 JSON 验证报告。只有当 OMML 数量不少于源公式数量、没有 MathML 或原始数学定界符残留，并完成可用工具范围内的视觉检查后，才能交付。

## LaTeX 写作要点

以下要点供 **LaTeX 引擎**使用。Typst 引擎请调用 typst-author skill 获取语法帮助。

### 编译命令

```bash
# 中文模板（xelatex，跑两遍解决交叉引用）
xelatex main.tex && xelatex main.tex

# 英文模板（xelatex，同样跑两遍）
xelatex main.tex && xelatex main.tex
```

### 文档结构

```latex
\documentclass[a4paper,12pt]{article}   % 英文
\documentclass[a4paper,12pt]{ctexart}   % 中文

\usepackage{...}   % 宏包加载
\usepackage{graphicx}   % 图片支持
\usepackage{booktabs}   % 三线表
\usepackage{tabularx}   % 按版心宽度自动分配列宽
\usepackage{array}      % 自定义列类型
\usepackage{amsmath,amssymb}   % 数学公式
\usepackage{hyperref}   % 交叉引用（需两遍编译）
```

### 图表插入

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=0.85\textwidth]{../../figures/fig_q1.pdf}
  \caption{图注}
  \label{fig:q1}
\end{figure}

% 结果类三线表：4 列及以上使用版心约束，避免自然宽度过窄
\begin{table}[htbp]
  \centering
  \caption{表注}
  \renewcommand{\arraystretch}{1.2}
  \setlength{\tabcolsep}{6pt}
  \begin{tabularx}{0.86\textwidth}{@{}>{\centering\arraybackslash}p{0.16\textwidth}*{3}{>{\centering\arraybackslash}X}@{}}
    \toprule
    \textbf{列1} & \textbf{列2} & \textbf{列3} & \textbf{列4} \\
    \midrule
    数据 & 数据 & 数据 & 数据 \\
    \bottomrule
  \end{tabularx}
\end{table}

% 符号/参数表可适度紧凑，但必须居中，不要贴在页边
```

### 交叉引用

```latex
如图~\ref{fig:q1}所示，...   % 图片引用
式~(\ref{eq:objective}) 给出...   % 公式引用
见第~\pageref{fig:q1} 页   % 页码引用
```

### 数学公式

```latex
行内公式：$f(x) = \sum_{i=1}^n \theta_i \phi_i(x)$

行间公式：
\begin{equation}
  \mathcal{L}(\theta) = \frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i)^2
  \label{eq:objective}
\end{equation}
```

### 章节和强调

```latex
\section{问题重述}
\subsection{问题背景}
\textbf{问题一：} xxx   % 对应 Typst 的 #strong
```
