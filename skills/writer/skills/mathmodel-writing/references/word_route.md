# Word/DOCX route

用 Pandoc 可解析的 Markdown 或 LaTeX 源写作，再调用 `$export-math-docx`。若比赛提供官方 DOCX，以其副本作为 reference DOCX，保留样式、页边距、页眉页脚和编号要求。

- 数学内容保持可转换语法，不粘贴公式截图。
- 图片路径必须存在，最终 DOCX 内必须嵌入媒体而不是外链本机绝对路径。
- 展示公式通过导出流程生成 Word 原生 OMML；编号使用连续的 Word 字段。
- 导出后运行 `$export-math-docx` 的结构验证，核对公式数量、编号连续性、图片嵌入和 ZIP/XML 完整性。
- 将 DOCX 渲染成页面逐页检查。没有渲染器时只能声明“结构验证完成，视觉检查未执行”。

不得把 Typst 源直接转换为 DOCX；应从 Markdown/LaTeX 写作源走 Word 路线。
