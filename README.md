# MathModel Skills

MathModel Skills 是一个可独立分发的 Codex Skills 插件包，包含建模手、编程手和论文手三个可分别安装的 skills-only 插件，覆盖数学建模中的任务协调、模型设计、程序实现、科研绘图、学术检索、论文撰写和提交前验收。

本目录不依赖 MathModelAgent 的后端、前端、Redis、数据库或其 Python 虚拟环境。将整个 `mathmodel-skills/` 目录单独复制、压缩或发布为新的 Git 仓库后，Skills 仍可使用。

## 目录结构

```text
mathmodel-skills/
├── skills/                     # 三个可分别安装的角色插件
│   ├── modeler/                # 建模手：6 个 Skill
│   │   ├── .codex-plugin/plugin.json
│   │   ├── ROLE.md
│   │   └── skills/<skill-name>/
│   ├── coder/                  # 编程手：7 个 Skill
│   │   ├── .codex-plugin/plugin.json
│   │   ├── ROLE.md
│   │   └── skills/<skill-name>/
│   └── writer/                 # 论文手：7 个 Skill
│       ├── .codex-plugin/plugin.json
│       ├── ROLE.md
│       └── skills/<skill-name>/
│           ├── SKILL.md
│           ├── agents/openai.yaml  # Codex/ChatGPT 展示与调用策略
│           ├── scripts/            # 可选的确定性脚本
│           ├── references/         # 可选参考资料
│           └── assets/             # 可选模板和静态资源
├── THIRD_PARTY_NOTICES.md
└── README.md
```

所有 Skill 已按 `modeler`（建模手）、`coder`（编程手）和 `writer`（论文手）分开存放。角色目录只是分类层，Skill 自身名称和调用方式不变，例如仍使用 `$mathmodel-analysis` 和 `$mathmodel-writing`。

## 安装

### 作为插件分发

`skills/modeler/`、`skills/coder/` 和 `skills/writer/` 各自都是完整的 skills-only Codex 插件。开发或内测时，可使用 Codex 的 `$plugin-creator` 把需要的角色插件加入个人 marketplace，再刷新 Codex、安装并在新任务中测试。完整工作流应安装三个插件；只做某一阶段时可以单独安装对应角色。

本包当前不包含个人 marketplace 配置，因为这类配置属于安装者自己的 Codex 环境，不应写入可分享插件。

### 作为本地 Skills 使用

不使用插件系统时，将需要的一个或多个 `skills/<role>/skills/<skill-name>/` 文件夹复制或链接到以下位置之一：

- 当前仓库：`<repo>/.agents/skills/`
- 当前用户：`$HOME/.agents/skills/`

也可以在发布到 GitHub 后，让 Codex 的 `$skill-installer` 从仓库安装。Skill 修改通常会被自动发现；如果没有出现，重启 Codex。

不要只复制 `SKILL.md`：含有 `scripts/`、`references/` 或 `assets/` 的 Skill 必须整目录复制。若只给某个身份使用，可按该身份的 `ROLE.md` 选择 Skill；完整工作流需要三个角色目录同时存在。

## 快速使用

完整建模任务：

```text
请使用 $mathmodel-workflow，从这道赛题和附件开始完成建模、代码、论文和验收。
```

只写论文并强制使用 OpenAlex：

```text
请使用 $mathmodel-writing，根据现有分析报告、真实计算结果和图表撰写论文，并用 OpenAlex 检索和核验参考文献。
```

单独检索论文：

```text
请使用 $paper-lookup，通过 OpenAlex 查找与鲁棒优化相关的近五年论文，保留 DOI 和查询来源。
```

## 三个角色与 20 个 Skills

### 建模手

身份使用手册：[`skills/modeler/ROLE.md`](skills/modeler/ROLE.md)

| Skill | 作用 |
| --- | --- |
| [`mathmodel-workflow`](skills/modeler/skills/mathmodel-workflow/SKILL.md) | 完整工作流入口；确认偏好、创建任务目录、生成计划并协调后续阶段。 |
| [`mathmodel-analysis`](skills/modeler/skills/mathmodel-analysis/SKILL.md) | 拆解赛题、理解数据、检查假设并给出可编码的模型、公式、约束和求解方案。 |
| [`mathmodel-references`](skills/modeler/skills/mathmodel-references/SKILL.md) | 共享的题型选模、防错、图表和论文规范知识库；默认不自动触发。 |
| [`statistical-analysis`](skills/modeler/skills/statistical-analysis/SKILL.md) | 选择统计检验，检查假设，报告效应量、置信区间、功效、回归或贝叶斯结果。 |
| [`experimental-design`](skills/modeler/skills/experimental-design/SKILL.md) | 在采集数据前设计随机化、区组、因子、响应面、交叉或顺序实验。 |
| [`uncertainty-and-units`](skills/modeler/skills/uncertainty-and-units/SKILL.md) | 审计量纲和单位，完成 GUM、不确定度传播、蒙特卡洛和数量级检查。 |

### 编程手

身份使用手册：[`skills/coder/ROLE.md`](skills/coder/ROLE.md)

| Skill | 作用 |
| --- | --- |
| [`mathmodel-coding`](skills/coder/skills/mathmodel-coding/SKILL.md) | 把模型实现为可复现代码，运行求解、检查约束并生成真实结果与数据图。 |
| [`mathmodel-drawio`](skills/coder/skills/mathmodel-drawio/SKILL.md) | 生成技术路线、流程、结构等非数据图，并在 Draw.io 可用时导出 PDF。 |
| [`mathmodel-doctor`](skills/coder/skills/mathmodel-doctor/SKILL.md) | 跨平台检查 Python 包、编译器、Draw.io 和 PDF 渲染工具；默认不自动触发。 |
| [`mathmodel-figure-templates`](skills/coder/skills/mathmodel-figure-templates/SKILL.md) | 复用 11 类科研绘图模板，生成可编辑脚本和 PNG/PDF/SVG。 |
| [`systematic-debugging`](skills/coder/skills/systematic-debugging/SKILL.md) | 面对错误、失败测试或异常结果时，先定位根因再提出修复。 |
| [`test-driven-development`](skills/coder/skills/test-driven-development/SKILL.md) | 用红灯—绿灯—重构实现新行为或修复缺陷。 |
| [`verification-before-completion`](skills/coder/skills/verification-before-completion/SKILL.md) | 在声称完成前运行最新测试、构建或检查并给出真实证据。 |

### 论文手

身份使用手册：[`skills/writer/ROLE.md`](skills/writer/ROLE.md)

| Skill | 作用 |
| --- | --- |
| [`mathmodel-writing`](skills/writer/skills/mathmodel-writing/SKILL.md) | 使用 Typst/LaTeX 模板组织论文，嵌入真实结果，并强制进行 OpenAlex 文献检索与核验。 |
| [`export-math-docx`](skills/writer/skills/export-math-docx/SKILL.md) | 通过 Pandoc 将 Markdown/LaTeX 数学结构导出为 DOCX 原生 OMML，并在发布前验证公式与论文图片均未丢失。 |
| [`mathmodel-verification`](skills/writer/skills/mathmodel-verification/SKILL.md) | 检查论文结构、图表、数值、占位符、引用、编译结果、Word OMML 和最终页面质量。 |
| [`typst-author`](skills/writer/skills/typst-author/SKILL.md) | 创建、编辑、编译和排错 Typst，附带本地语法参考。 |
| [`paper-lookup`](skills/writer/skills/paper-lookup/SKILL.md) | 查询 OpenAlex、Crossref、PubMed、Semantic Scholar、arXiv 等学术来源并保留 provenance。 |
| [`literature-review`](skills/writer/skills/literature-review/SKILL.md) | 设计多数据库检索、筛选和证据综合，形成系统性文献综述。 |
| [`citation-verification`](skills/writer/skills/citation-verification/SKILL.md) | 检查引用格式、文献真实性以及文献与正文论点的主题和语义匹配。 |

## 依赖不是全部必装

Skill 是工作说明和可选脚本，不需要“安装进模型”。运行依赖应安装在 Codex 当前能访问的计算机、容器或虚拟环境中，并按任务最小化安装。

### 基础层

| 依赖 | 用途 | 是否必需 |
| --- | --- | --- |
| Python 3.11+ | 环境检查、OpenAlex 客户端、数据处理和绘图脚本 | 推荐；执行全部捆绑脚本时必需 |
| 网络/HTTPS | OpenAlex 和其他学术 API | 只在检索文献时必需 |
| Codex 文件读写能力 | 读取题目、写报告、代码和论文 | 执行工作流时必需 |

### 常用 Python 包

```text
numpy pandas matplotlib scipy scikit-learn openpyxl seaborn
```

扩展统计和不确定度任务按需安装：

```text
pingouin statsmodels pint uncertainties pyDOE3
```

可选能力还可能需要 `pymc`、`arviz`、`requests` 或具体模型的求解器。`openalex_search.py` 使用 Python 标准库，不依赖 OpenAlex SDK 或 `requests`。

### 系统工具

| 工具 | 作用 | 何时需要 |
| --- | --- | --- |
| Typst CLI | 编译 `.typ` 论文 | 选择 Typst 时 |
| XeLaTeX/TeX 发行版 | 编译 `.tex` 论文 | 选择 LaTeX 时 |
| Pandoc 或 `pypandoc-binary` | 将 Markdown/LaTeX 数学结构与图片导出为 Word 原生 OMML，并核对图片嵌入 | 选择 DOCX 交付时 |
| Draw.io Desktop CLI | 将 `.drawio` 导出为 PDF | 可选；源文件生成不需要 |
| Poppler `pdftoppm` | PDF 转 PNG 视觉检查 | 推荐，三选一 |
| MuPDF `mutool` | PDF 转 PNG 备用 | 可选，三选一 |
| ImageMagick `magick` | PDF 转 PNG 备用 | 可选，三选一 |
| `typstyle` | Typst 格式检查 | 可选 |
| CiteCheck CLI | 自动解析和批量核验引用 | `citation-verification` 的可选增强 |

无需安装 Bash。核心辅助脚本均提供跨平台 Python 入口；保留的 `.sh` 文件只用于兼容 Unix 环境的扩展流程。

## 一键环境检查

从插件根目录运行：

```text
python skills/coder/skills/mathmodel-doctor/scripts/check_environment.py
```

机器可读输出：

```text
python skills/coder/skills/mathmodel-doctor/scripts/check_environment.py --json
```

检查器不会自动安装任何东西。只有用户明确同意后，才应在其现有虚拟环境或包管理器中安装缺失依赖。

## OpenAlex

`mathmodel-writing` 已要求：论文需要方法来源、背景或参数依据时，先检索 OpenAlex，再生成参考文献。自 2026 年 2 月 13 日起，OpenAlex 要求所有 API 请求携带免费 API Key；先在 [OpenAlex 设置页](https://openalex.org/settings/api)获取密钥并配置环境变量。

直接运行捆绑客户端：

```text
python skills/writer/skills/mathmodel-writing/scripts/openalex_search.py --query "robust optimization" --output reports/openalex_results.json
```

环境变量：

| 环境变量 | 用途 |
| --- | --- |
| `OPENALEX_API_KEY` | OpenAlex API Key；调用 OpenAlex 时必需，免费账户每天含免费额度 |
| `NCBI_API_KEY` | PubMed/PMC 高频查询 |
| `S2_API_KEY` | Semantic Scholar |
| `CORE_API_KEY` | CORE 的部分能力 |
| `OPENROUTER_API_KEY` | `literature-review` 的可选增强步骤 |

密钥只放在本地环境变量或密钥管理器中，不得写入 Skill、命令行参数、论文、报告、日志或版本库。`openalex_search.py` 只记录是否配置了凭据，不记录凭据值。旧的 OpenAlex `mailto` polite-pool 参数已经废止，本插件不再发送该参数。

## 可移植工作目录约定

完整工作流把用户指定目录视为 `<WORK_ROOT>`；未指定时使用当前工作目录。默认产物为：

```text
<WORK_ROOT>/
├── plan.md
├── todo.md
├── reports/
├── code/
├── results/
├── figures/
└── paper/
```

Skill 不再引用 `backend/`、项目虚拟环境、固定用户目录、Claude 专用路径或 MathModelAgent 网页服务。每个带资源的 Skill 都从自己的 `<SKILL_DIR>` 解析脚本、参考资料和模板。

## 安全与限制

- Skill 可以要求访问 OpenAlex，但不能绕过宿主的网络沙箱或组织策略；网络被禁止时应记录失败并请求授权或使用可用的权威检索能力。
- 任何软件安装、权限提升、外部写操作或 API 凭据使用仍受 Codex 的确认和沙箱规则约束。
- 学术 API 返回“未找到”不等于文献不存在；引用核验需要交叉查询和人工复核。
- 论文数值必须来自实际代码输出或用户提供的数据，不得由写作 Skill 编造。
- 本插件包含改编的第三方开源 Skills 和 Typst 文档，来源与许可证见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

## 发布前说明

本目录已经可以技术上独立运行和分发。原 MathModelAgent 仓库目前没有顶层 LICENSE，因此本插件没有擅自替项目所有者选择整体许可证。若要公开发布或允许第三方再分发，请由版权所有者补充顶层 `LICENSE`，并保留 `THIRD_PARTY_NOTICES.md` 中的第三方声明。
