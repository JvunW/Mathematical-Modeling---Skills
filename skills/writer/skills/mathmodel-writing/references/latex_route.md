# LaTeX/PDF route

保留官方类文件、封面、页眉页脚和提交要求。入口通常为 `main.tex`，中文模板优先用 XeLaTeX。

- 章节使用 `\input`/`\include`，图片使用 `\includegraphics` 并给出 caption 与 label。
- 展示公式使用带编号环境；需要引用的公式添加唯一 `\label{eq:...}`，正文使用 `\eqref`。
- 引文通过模板指定的 BibTeX/BibLaTeX 或明确的 `thebibliography` 管理。
- 编译至少覆盖交叉引用收敛所需轮次，并检查未定义引用、缺图和 overfull 警告。
- 编译后逐页视觉检查；不得用极小字号或负间距掩盖内容超限。
