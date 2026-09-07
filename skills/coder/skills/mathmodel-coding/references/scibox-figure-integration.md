# sci-box 科研绘图模板接入

仅在编码阶段已经产生真实结果数据，且目标图型与下表模板接近时读取本文件。模板来自 `jihe520/sci-box` 的 `skills/scibox-figure`，固定检查版本为提交 `9687d2a52037e92bf68a781b9b1e061ca03c8125`（2026-08-17）。当前 11 个模板已由 `$mathmodel-figure-templates` 集成，无需再安装同名 skill。

## 图型路由

| 需求 | 模板 id |
|---|---|
| 多分类特征贡献、SHAP 柱状图与蜂群图 | `multiclass-shap-combo` |
| 配对观测的分布、个体变化与组间趋势 | `paired-raincloud` |
| 交叉验证 ROC、均值曲线与置信区间 | `cv-roc-ci` |
| 多模型相关性、标准差和误差综合比较 | `taylor-diagram` |
| 多变量分布、拟合关系与相关系数 | `correlation-pairgrid` |
| 预测值与真实值及其边缘分布 | `prediction-marginal-grid` |
| 两个超参数对应的 TPE/RF 响应曲面 | `rf-tpe-surface` |
| 分组相关矩阵与半边小提琴分布 | `grouped-corr-split-violin` |
| 多组、多指标的环形热图 | `grouped-circular-heatmap` |
| 城市或对象的多指标组合比较 | `urban-park-cooling-combo` |
| 类别之间的流量、关联或转移关系 | `nature-chord-diagram` |

## 接入流程

1. 先把模型输出整理为可追溯的 CSV、JSON 或其他结构化结果，记录字段、单位、分组、样本量和误差定义。
2. 调用 `$mathmodel-figure-templates`，由其从 `references/figure-catalog.md` 核对模板并执行 `scripts/render_template.py <template-id>`。
3. 将复制到项目工作区的模板脚本改为读取真实结果文件；不得直接把模板自带的确定性模拟数据当作比赛结果。
4. 保留结果数据到图表字段的转换代码、随机种子、生成命令以及 PNG、PDF/SVG 输出。
5. 执行 `$mathmodel-figure-templates` 的 Figure Contract 和 Figure QA，并在 `reports/RESULTS_REPORT.md` 中登记数据来源、生成脚本和用途。

## 边界

- 模板只提供图形结构，不决定统计方法、误差定义、分组方式或结论。
- 没有与论证目标匹配的模板时，按项目需要直接编写绘图代码，不为使用模板而改变分析。
- 技术路线图、模型结构图、算法流程图等非数据示意图仍交给 `$mathmodel-figure-templates` 路由至 `$mathmodel-drawio`，不由本接入处理。
- `sci-box` 仓库中的 `scibox-figure` frontmatter 名称为 `mathmodel-figure-templates`；禁止与现有增强版并行安装，以免自动调用冲突。
