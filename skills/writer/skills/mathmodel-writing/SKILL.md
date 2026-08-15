---
name: mathmodel-writing
description: "撰写并排版数学建模论文，支持 Typst、LaTeX 和用于 Word 原生公式导出的 Markdown。用于根据模型、真实计算结果和图表组织章节，并通过 OpenAlex 等学术来源检索和核验参考文献；需要 DOCX 时与 $export-math-docx 配合。"
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

存在匹配模板时，绝不从零开始写论文。

**LaTeX 模板**：

```text
<SKILL_DIR>/assets/templates/zh/<竞赛>-latex/main.tex
```

- **文件存在**：将 `assets/templates/zh/<竞赛>-latex/` 整目录复制到 `<WORK_ROOT>/paper/`。
- **文件不存在（MISSING）**：说明 skill 未完整安装或在沙箱中，此时依照本 SKILL.md 步骤 3 列出的对应节文件结构，从零重建最小可编译 LaTeX 框架，并在 `paper/` 内注明"重建自 default-latex 结构"。


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

#### OpenAlex 强制检索与核验

凡论文需要引用方法来源、领域背景、参数依据或相关研究时，必须先调用 OpenAlex API，不得仅凭模型记忆生成参考文献。在创建 `paper/references.typ`、`paper/references.tex` 或 Word 版参考文献章节前，至少完成一次 OpenAlex 检索；即使没有检索到合适文献，也要保存空结果和失败原因。

按以下顺序执行：

1. 根据论文主题和具体方法构造 2 至 5 个中英文检索式，避免只使用宽泛的赛题名称。
2. 优先调用 `$paper-lookup` 进行 OpenAlex 检索；也可以运行本 skill 自带的标准库脚本。把 `<SKILL_DIR>` 替换为本文件所在目录，把 `<WORK_ROOT>` 替换为当前论文任务目录：

   ```text
   python "<SKILL_DIR>/scripts/openalex_search.py" --query "<检索式>" --output "<WORK_ROOT>/reports/openalex_results.json"
   ```

   脚本使用 OpenAlex Works API 的 `search` 和 `per_page` 参数，并从 `OPENALEX_API_KEY` 环境变量读取凭据。自 2026 年 2 月 13 日起，OpenAlex 要求所有 API 请求使用 API Key；密钥可在 `https://openalex.org/settings/api` 免费获取。未配置密钥时，真实请求必须停止并给出配置提示，不得退回匿名请求。旧的 `mailto` polite-pool 参数已经废止。不得把 API Key 写入论文、报告、命令行参数、日志或版本库。
3. 将未经改写的返回数据保存到 `reports/openalex_results.json`，至少保留 `id`、`display_name`、`authorships`、`publication_year`、`primary_location`、`doi`、`biblio` 和 `cited_by_count` 字段。
4. 按内容相关性筛选文献。优先选择有 DOI、来源明确且与实际模型或论点直接相关的记录；引用次数和发表年份只能作为辅助指标，不能替代相关性判断。
5. 对每篇拟引用文献，再通过 OpenAlex ID 或 DOI 核验标题、作者、年份和来源。API 未返回的卷、期、页码或 DOI 必须省略，禁止推测或补造。
6. 创建 `reports/LITERATURE_REPORT.md`，记录检索式、采用的 OpenAlex ID、对应 DOI、拟支持的论文论点，以及舍弃候选文献的主要原因。
7. 论文正文和参考文献文件只能使用已经写入 `reports/LITERATURE_REPORT.md` 的文献。每个正文引用必须能映射到一个已核验的 OpenAlex 记录。

OpenAlex 请求失败时，采用有限失败策略：单个请求最多重试 3 次并逐步延长等待时间。仍然失败时，在 `reports/LITERATURE_REPORT.md` 中记录请求时间、检索式和错误原因，再使用当前 harness 可用的网页检索或 DOI/Crossref 等权威来源核验候选文献；不得因 OpenAlex 不可用而改用模型记忆编造引用。后续验收必须能够区分 OpenAlex 结果与降级检索结果。

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

在所有章节完成后撰写中文摘要或英文 Summary Sheet。必须包含每个子问题的方法和精确的数值结果。

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

% 三线表
\begin{table}[htbp]
  \centering
  \caption{表注}
  \begin{tabular}{ccc}
    \toprule
    \textbf{列1} & \textbf{列2} & \textbf{列3} \\
    \midrule
    数据 & 数据 & 数据 \\
    \bottomrule
  \end{tabular}
\end{table}
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
