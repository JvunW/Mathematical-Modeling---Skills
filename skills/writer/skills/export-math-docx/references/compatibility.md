# Pandoc DOCX 数学兼容性

## 推荐输入

优先把论文整理为 UTF-8 Markdown：

```markdown
行内公式 $x_{ijkt} \ge 0$。

$$
\min Z = \sum_{i=1}^{n} c_i x_i
$$
```

脚本对 Markdown 使用 `markdown+tex_math_dollars` reader，对 `.tex` 使用 `latex` reader。DOCX writer 将 Pandoc 内部数学节点写为 Word Office Math（OMML），不是公式截图。

## 通常可以转换

- 上下标、分式、根式、希腊字母；
- 求和、积分、极限和常见关系运算符；
- 矩阵、向量、括号和常见 `amsmath` 风格表达式；
- Markdown 表格、标题、列表、脚注和本地图片；
- Pandoc 能识别的交叉引用和参考文献流程。

## 需要预处理

- 自定义 `\newcommand`：在转换前展开宏，或确认 Pandoc 能读取宏定义；
- TikZ、PGFPlots 和依赖 TeX 引擎绘制的内容：先导出为 SVG/PNG/PDF，再作为图片插入；
- `align`、`cases`、复杂嵌套环境：先用小样本转换并检查 Word 中的换行与对齐；
- 不受 Pandoc LaTeX reader 支持的宏包命令：改写为标准 LaTeX 数学语法。

## Word 模板

`--reference-doc` 主要继承 Word 样式、页面设置、页眉页脚等定义。Pandoc 不会把参考文档正文当成目标正文保留下来。若比赛模板包含必须保留的封面表格、填写区域或固定正文：

1. 先制作只包含所需样式和页眉页脚的 Pandoc reference DOCX；或
2. 先生成 DOCX，再使用专门的 DOCX 编辑流程把生成内容合入官方模板；
3. 最终必须在 Word 或兼容渲染器中逐页检查。

## 验证解释

- `<m:oMath>`：一个 Word 原生数学对象；
- `<m:oMathPara>`：一个 Word 行间数学段落；
- MathML 节点或残留 `$...$`：视为转换失败；
- 结构验证只能证明公式是 OMML，不能证明所有公式的视觉换行和模板版式正确。
