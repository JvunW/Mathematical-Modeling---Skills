# Equation numbering

展示公式默认连续编号，正文引用使用稳定标签或 Word 字段。行内公式不编号。

- Typst：设置自动编号，用标签和交叉引用闭合。
- LaTeX：使用 `equation`、`align`、`gather` 或 `multline` 等带编号环境；需要引用的公式添加唯一 label。
- Word：由 `$export-math-docx` 生成 OMML 和连续的 `SEQ Equation` 字段，并核对编号值。

只有解释性、过渡性且正文不会引用的展示公式可以不编号。LaTeX 中必须在其紧邻上一非空行写：

```latex
% equation-numbering: intentional-unnumbered reason=<具体原因>
```

验收报告列出所有豁免。关键模型、核心推导、目标函数、约束、评价指标和正文引用公式不得豁免。
