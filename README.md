# Mathematical Modeling Skills

一套面向数学建模竞赛与研究型任务的 Codex Skills。它把题意分析、模型设计、可复现编码、科研图表、论文写作、文献核验和最终交付组织成可独立使用、也可协同运行的工作流。

## 三个插件与 22 个 Skill

### Modeler（7）

| Skill | 用途 |
|---|---|
| `mathmodel-workflow` | 启动完整任务，维护 Gate、状态和交付路线 |
| `mathmodel-analysis` | 拆题、定义变量、假设、目标和约束 |
| `mathmodel-analysis-grill` | 在编码前压力测试建模方案 |
| `mathmodel-references` | 查询数学建模规范与方法参考 |
| `experimental-design` | 随机化、区组、因子和序贯实验设计 |
| `statistical-analysis` | 统计检验、效应量、功效和回归诊断 |
| `uncertainty-and-units` | 单位、量纲、不确定度和数量级检查 |

### Coder（7）

| Skill | 用途 |
|---|---|
| `mathmodel-coding` | 实现模型、运行求解、保存结果和数据图 |
| `mathmodel-doctor` | 检查建模、排版和外部工具环境 |
| `mathmodel-drawio` | 绘制确有必要的路线图和结构图 |
| `mathmodel-figure-templates` | 复用科研图表模板 |
| `systematic-debugging` | 复现问题并定位根因 |
| `test-driven-development` | 用红—绿—重构实现可测行为 |
| `verification-before-completion` | 在完成声明前运行新鲜验证 |

### Writer（8）

| Skill | 用途 |
|---|---|
| `mathmodel-writing` | 撰写并排版数学建模论文 |
| `mathmodel-writing-grill` | 压力测试论文论证和证据映射 |
| `mathmodel-verification` | 验收论文、代码、引用和最终文件 |
| `export-math-docx` | 导出含 Word 原生 OMML 公式的 DOCX |
| `paper-lookup` | 通过学术 API 检索论文并保存来源 |
| `citation-verification` | 核验引用真实性、格式和相关性 |
| `literature-review` | 系统检索、筛选和研究综合 |
| `typst-author` | 编写、编译和排查 Typst 文档 |

## 五分钟开始

完整任务使用：

```text
使用 $mathmodel-workflow，从赛题和附件开始完成建模、编码、论文和验收。
```

单阶段任务直接调用对应 Skill，例如：

```text
使用 $mathmodel-analysis，把这道题拆成可编码的模型方案。
使用 $mathmodel-verification，提交前验收这份论文及配套代码。
```

## 安装与依赖

推荐用 Codex 的 `$skill-installer` 从本仓库 `main` 分支安装所需的完整 Skill 目录；升级时先备份并替换同名目录，安装后开启新任务使发现缓存刷新。三个插件 manifest 用于仓库分组和版本治理；不支持插件命令的 Codex CLI 仍可逐个安装 22 个 Skill。

依赖分层：

- 核心层：Python 3.10+ 和标准库，支持状态机、契约、仓库校验和基础检查；
- 建模层：按题型选择 NumPy、pandas、SciPy、statsmodels、scikit-learn、优化器等；
- 排版层：Typst、TeX Live/XeLaTeX 或 Pandoc/`pypandoc-binary` 按交付路线安装；
- 可选层：Word/LibreOffice、PDF 渲染器和第三方学术 API 仅在对应检查中需要。

脚本不得假设固定盘符、用户名或工作区目录。缺少可选依赖时应报告 `skipped`/`blocked` 和安装建议，不能把未执行的检查写成通过。

## 完整工作流

```text
题面与附件
  → mathmodel-analysis
  → mathmodel-analysis-grill
  → mathmodel-coding
  → 结果冻结
  → mathmodel-writing
  → mathmodel-writing-grill
  → mathmodel-verification
  → 最终 PDF 或 DOCX
```

七个阶段门：

```text
G0 环境就绪 → G1 题意解析 → G2 方法验证 → G3 实现验证
→ G4 结果冻结 → G5 论文证据完整 → G6 交付验收
```

## Typst、LaTeX 与 Word 三种交付路线

| 路线 | 论文源文件 | 最终文件 | 核心检查 |
|---|---|---|---|
| Typst/PDF | `paper/main.typ` | PDF | 编译、公式编号、交叉引用、页面视觉 |
| LaTeX/PDF | `paper/main.tex` | PDF | 两遍编译、标签引用、字体和页面视觉 |
| Word/DOCX | `paper/paper.md` | DOCX | 官方模板、图片嵌入、原生 OMML、SEQ 公式编号 |

Word 路线由 `export-math-docx` 负责 Markdown→Pandoc→DOCX；不支持把 Typst 源文件直接转换为 DOCX。

## 状态恢复与结果追溯

完整工作流在项目工作区维护：

```text
state/workflow_state.json
state/artifact_registry.json
state/gate_history.jsonl
state/stale_report.json
```

重要产物具有稳定 ID、版本、内容 hash 和依赖。结果冻结时记录代码、数据、配置和环境指纹；上游变化会把依赖它的结果、图表和论文论点标记为 stale。状态变更只更新元数据，不删除用户文件。

新会话可读取这些文件，从第一个未通过或失效的 Gate 恢复，不依赖聊天记忆重复判断。

## 项目产物契约

```text
reports/model_manifest.json          # 变量、假设、目标、约束和验证计划
results/results_manifest.json        # 运行、指标、图表、表格和检查结果
reports/paper_evidence_map.json       # 论文论点到结果/图表/引用的映射
reports/verification.json             # 最终验收结论和未解决项
```

对应 schema 位于 `schemas/`。破坏性 schema 变更必须升级主版本并提供迁移说明。

## 文献检索

1. 当前环境有联网搜索时，优先使用当前 Codex 联网搜索和论文官方页面。
2. 需要可复现元数据时使用 `paper-lookup`。
3. 系统综述式任务使用 `literature-review`。
4. ChatGPT Deep Research 只作为无联网工具时的人工发现回退，发现结果仍须独立核验。
5. 不得凭模型记忆生成最终参考文献。

## 验证仓库

快速验证：

```text
python scripts/validate_repo.py --quick
```

完整验证：

```text
python scripts/validate_repo.py --full --json reports/repo_validation.json
```

快速检查覆盖 Skill 结构、UI 元数据、插件 manifest、内部引用、Python 语法和单元测试。完整检查额外探测可选排版工具链并写入报告；具体项目的 PDF/DOCX 编译和逐页验收仍由 `mathmodel-verification` 执行。缺少可选工具时会明确报告 skipped，不会伪装成 pass。

## 端到端评测

`evals/public/` 用于开发回归；正式评分应使用与被评 Agent 隔离的 holdout 输入和 evaluator-only rubric。记录模型、推理等级、Skill 版本、Git commit、环境、提示词、运行时间和独立结果。

9.5 目标要求：8/8 无致命错误，至少 7/8 得分不低于 85，平均分不低于 90，关键维度不低于各自满分的 80%。该分数必须来自实际评测，不能由目录或文档数量推断。

## 已知边界

- 无数据、附件或关键用户选择时应阻断或降级，不编造。
- Word 页面视觉验收需要 Windows 原生 Word 或人工复核；跨平台 CI 主要验证 DOCX 内部结构。
- 第三方 API 和可选排版工具不可用时，保留可复现降级路径并标记未完成检查。
- Skills 提供决策指导和确定性辅助脚本，不替代竞赛规则、领域专家判断或用户授权。

## 贡献规范

修改行为前先补能复现问题的测试；运行 `python scripts/validate_repo.py --quick`；影响排版或导出时再用真实 PDF/DOCX 做视觉与结构回归。新增或重命名 Skill 时同步更新 `agents/openai.yaml`、插件 manifest、README 和内部引用。破坏性运行时或 schema 变更需要新的主版本、迁移说明、基线记录和可恢复回滚目标。

## 许可证

许可证和第三方声明见 `licenses/` 与 `THIRD_PARTY_NOTICES.md`。
