---
name: mathmodel-doctor
description: "检查独立数学建模 Skills 所需的 Python 包、论文编译器和图形工具。仅在用户明确要求环境检查、依赖诊断或安装指导时使用。"
---

# MathModel Doctor

本 skill 诊断独立 MathModel Skills 的运行环境。它只在用户明确要求时使用，只做读取和检查；不得自行安装软件、修改环境变量或提升权限。

## 快速检查

把本 `SKILL.md` 所在目录解析为 `<SKILL_DIR>`，运行：

```text
python "<SKILL_DIR>/scripts/check_environment.py"
```

需要机器可读结果时使用 `--json`；需要让缺失的核心依赖产生非零退出码时使用 `--strict`。

脚本检查：

- Python 版本（完整脚本集要求 3.11+）。
- 论文编译器：Typst、XeLaTeX（至少一个即可）。
- 图形工具：Draw.io、XeLaTeX、Poppler、MuPDF、ImageMagick、Mermaid CLI。
- 核心 Python 包：NumPy、pandas、matplotlib。
- 扩展包：SciPy、scikit-learn、openpyxl、seaborn、pingouin、statsmodels、pint、uncertainties、requests、Pillow、PyMuPDF、scikit-image。

OpenAlex 检索脚本使用 Python 标准库，不要求 `requests`。OpenAlex 自 2026 年 2 月 13 日起要求所有 API 请求携带免费 API Key；检查器只报告 `OPENALEX_API_KEY` 是否已配置，绝不显示密钥值。

## 解释结果

按任务类型区分依赖，不要把所有可选项都判为阻塞：

- 只做赛题分析：通常只需要 Codex 本身。
- 运行模型和绘图：需要 Python；NumPy、pandas、matplotlib 为通用核心包，其他包按具体模型选装。
- 编译论文：Typst 或 XeLaTeX 至少一个。
- 编译和预览 TikZ：需要 XeLaTeX 与 Poppler；PDF 坐标级重叠检查额外需要 PyMuPDF。
- Mermaid 草图导出：需要 Mermaid CLI；缺失时可保留 `.mmd` 或改走 TikZ/DrawIO。
- 导出 Draw.io PDF：需要 Draw.io Desktop CLI；缺失时仍可交付 `.drawio` 源文件。
- PDF 逐页视觉检查：Poppler、MuPDF 或 ImageMagick 至少一个。
- OpenAlex 文献检索：需要网络访问和 `OPENALEX_API_KEY`；缺失时只阻塞 OpenAlex，不阻塞离线建模与写作。

## 安装指导

只有用户明确授权安装后才能执行安装命令。优先使用用户现有的虚拟环境和包管理器，不要求特定项目目录。

Python 包示例：

```text
python -m pip install numpy pandas matplotlib scipy scikit-learn openpyxl seaborn statsmodels pint uncertainties Pillow PyMuPDF scikit-image
```

若用户使用 `uv`、Conda、Poetry 或容器，应改用其现有依赖管理方式。Typst、TeX 发行版、Draw.io 和 PDF 渲染工具属于系统软件，应依据当前操作系统使用官方安装渠道。

## 输出要求

报告应包含：

1. 已检测的平台和 Python 版本。
2. 已安装、缺失的命令和 Python 包。
3. 当前可以运行的工作流阶段。
4. 只针对用户目标的最小缺失依赖清单。
5. 若用户尚未授权安装，给出命令但不执行。

不得把“可选工具缺失”误报为整个插件不可用。
