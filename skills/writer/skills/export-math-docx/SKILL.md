---
name: export-math-docx
description: "将包含 LaTeX 数学公式和论文图片的 Markdown 或 LaTeX 论文通过 Pandoc 导出为 .docx，验证公式已成为 Word 原生可编辑 OMML，并阻止缺图或图片未嵌入的 DOCX 发布。用于需要 Word 交付、DOCX 比赛模板、LaTeX/Markdown 转 Word、Pandoc 数学转换、OMML 公式校验、论文图片嵌入或排查公式/图片丢失的任务；不用于把 Typst 源文件直接转换为 DOCX。"
---

# 导出数学公式 Word 文档

使用随 Skill 分发的确定性脚本完成“TeX 数学语法 → Pandoc 数学结构 → Word OMML”链路。只创建临时工作文件，不在运行时重新编写转换脚本。

## 工作流程

1. 确认输入、输出和模板。
   - 优先使用 UTF-8 Markdown；支持 `$...$`、`$$...$$`、`\(...\)` 和 `\[...\]` 数学定界符。
   - 行内公式保持不编号；每个行间公式会在 Pandoc 转换后自动获得连续的 Word `SEQ Equation` 编号。不要在源公式中手写 `(1)`。
   - 允许输入 `.tex`，但只保证 Pandoc LaTeX reader 能解析的内容；复杂宏和依赖宏包的版式先按 `references/compatibility.md` 处理。
   - 将比赛提供的纯样式 Word 文件作为 `--reference-doc`。若模板正文包含必须保留的封面字段或固定内容，先阅读兼容性说明，不要假设 Pandoc 会保留模板正文。

2. 检查 Pandoc，但不要静默安装依赖：

   ```text
   python "<SKILL_DIR>/scripts/export_docx.py" --check
   ```

   脚本依次查找 `--pandoc` 指定路径、`PANDOC_PATH`、系统 `pandoc` 和 `pypandoc`/`pypandoc-binary` 自带可执行文件。全部缺失时，说明缺失项并在获得用户许可后再安装。

3. 确认图片资源并执行转换。
   - 脚本先通过 Pandoc AST 枚举 Markdown、HTML 或 LaTeX 图片引用，再按源文件目录和每个 `--resource-path` 依次解析。
   - 任一源图片缺失时必须停止，不得继续生成无图 DOCX，也不得用无关图片或虚构科研图替代。
   - 把本 `SKILL.md` 所在目录解析为 `<SKILL_DIR>`，传入绝对路径或当前工作区内明确路径：

   ```text
   python "<SKILL_DIR>/scripts/export_docx.py" \
     "<INPUT.md>" "<OUTPUT.docx>" \
     --resource-path "<FIGURES_DIR>" \
     --reference-doc "<REFERENCE.docx>" \
     --report "<REPORT.json>"
   ```

   `--resource-path` 和 `--reference-doc` 都是可选参数。只有用户明确允许覆盖已有文件时才传 `--force`。不要增加 `--mathml`；Pandoc 的 DOCX writer 负责输出 OMML。
   - Pandoc 生成临时 DOCX 后，脚本自动把每个 `<m:oMathPara>` 放入无边框三列表格：左右列等宽，中间列保留原生 OMML，右列写入连续的 `SEQ Equation` 字段。该步骤是原子操作，重复运行不会重复编号。

4. 检查脚本结果。
   - 主脚本在发布最终文件前自动检查 DOCX ZIP 完整性、OOXML 可解析性、OMML 数量、行间公式数量、`SEQ Equation` 字段数量、编号连续性、MathML 残留、原始 TeX 定界符残留、源公式数量、图片节点数量、图片关系和媒体文件数量。
   - 源文件含行间公式时，`equation_number_fields` 必须不少于 `expected_numbered_equations`，且 `equation_number_values` 必须从 1 连续递增；否则不得发布 DOCX。
   - 源文件含图片时，图片引用次数和唯一图片数量必须在 DOCX 中得到满足；Pandoc 的图片资源警告即使返回码为 0 也视为失败。
   - 验证失败时不得交付临时 DOCX；返回 Pandoc 诊断或结构化验证错误。
   - 如需独立复查已有文件，运行：

     ```text
     python "<SKILL_DIR>/scripts/verify_omml.py" \
       "<OUTPUT.docx>" --source "<INPUT.md>" --report "<REPORT.json>"
     ```

   - 报告中的 `expected_source_images`、`image_occurrences`、`media_files` 和 `image_relationships` 用于复查图片是否真正写入 Word 包。
   - 报告中的 `expected_numbered_equations`、`equation_number_fields` 和 `equation_number_values` 用于复查公式编号是否齐全且连续。

5. 完成视觉检查。
   - 使用当前 harness 可用的 Word、LibreOffice 或 DOCX 渲染工具检查分页、公式换行、表格、图片、中文字体和模板样式。
   - 无法渲染时明确说明只完成了结构验证，不能声称视觉检查通过。

## 安全和清理

- 脚本使用系统安全临时目录，并在成功或失败后自动删除转换中的 DOCX 和临时工作目录。
- 最终 DOCX 只有通过 OMML 验证后才原子发布到目标路径。
- 保留用户输入、参考模板、最终 DOCX 和用户明确要求的 JSON 报告。
- 不删除用户目录，不使用宽泛递归删除，不把最终输出放进临时目录。

## 依赖与边界

- 必需：Python 3.10+，以及系统 Pandoc 或可导入的 `pypandoc`/`pypandoc-binary`。
- 不需要：Typst、XeLaTeX、MathModelAgent 后端、Redis 或项目虚拟环境。
- 本 Skill 负责格式转换、行间公式自动编号和 OMML 结构验证，不负责重新撰写论文、修正数学推导或保证比赛模板的所有视觉细节。
- 遇到自定义宏、TikZ、复杂 LaTeX 环境、模板正文保留或公式兼容性问题时，读取 `references/compatibility.md`。
