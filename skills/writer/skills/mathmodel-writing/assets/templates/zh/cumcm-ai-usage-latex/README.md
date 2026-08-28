# CUMCM AI 工具使用详情 LaTeX 模板

本目录由 `mathmodel-writing` Skill 的 CUMCM LaTeX 模板改制，并参考用户提供的 5 页示例版式。

## 填写方法

1. 在 `config.tex` 中修改参赛队号、赛题编号和论文题目。
2. 在 `sections/ai_usage.tex` 中逐项替换灰色 `【填写提示】`。
3. 工具信息使用 `\AItoolrow` 增删；AI 输出处理记录使用 `\adoptionrow` 增删。
4. 典型交互使用 `interactionrecord` 环境；复制整段即可增加 R3、R4 等记录。
5. 提交前搜索 `placeholder` 或 `【`，确保没有未替换提示。

## 编译

必须使用 XeLaTeX，并至少编译两遍：

```powershell
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

主要依赖：`ctex`、`fontspec`、`fancyhdr`、`booktabs`、`tabularx`、`xcolor`、`hyperref`。

## 真实性提醒

示例图片只用于复刻结构和版式。正文中的工具、版本、提示词、AI 回复、采纳情况、人工修改和核验方法必须根据本队真实使用过程填写，不能直接沿用示例内容。
