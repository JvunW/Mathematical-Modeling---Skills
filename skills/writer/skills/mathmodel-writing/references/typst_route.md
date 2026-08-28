# Typst/PDF route

使用比赛提供或仓库已有的 Typst 模板。入口通常为 `main.typ`，章节路径按项目实际结构确定。

- 在入口设置展示公式编号，例如 `#set math.equation(numbering: "(1)")`。
- 用稳定标签标记需要引用的公式、图和表，并使用 Typst 交叉引用。
- 图片优先使用可缩放或高分辨率格式，caption 与正文语言一致。
- 使用当前环境的 Typst 编译器生成 PDF；编译器缺失时记录 `skipped`，不得伪称通过。
- 编译后逐页渲染检查裁切、缺字、表格越界、公式与编号重叠。

Typst 语法或模板问题可调用 `$typst-author`。
