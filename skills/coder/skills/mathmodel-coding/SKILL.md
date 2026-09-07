---
name: mathmodel-coding
description: "实现、运行和验证数学建模代码，处理竞赛数据，保存可追溯的中间结果，生成论文级数据图表。适用于将建模方案转化为 Python、R、MATLAB 或其他可复现程序，以及进行参数估计、优化求解、预测评估、敏感性分析、约束检查和结果导出。所有新增代码必须使用清晰的英文变量名、中文注释、无 emoji，并保留可复现实验记录。"
---

# 数学建模编程手

本 skill 负责把已经确定的数学模型实现成可运行、可检查、可复现的程序。目标不是只输出一个结果，而是让其他人能够根据代码、输入数据、参数和运行记录复核结果。

若存在 `reports/model_manifest.json`，把它作为变量、目标、约束和计划指标的机器可读输入；发现与 Markdown 建模报告冲突时停止冻结结果并记录差异，不静默选择其中一个版本。

## 一、职责边界

本 skill 负责：

- 读取和检查原始数据；
- 完成数据清洗、变量转换和特征构造；
- 实现回归、分类、聚类、时间序列、优化、仿真、评价和敏感性分析；
- 检查模型约束、边界、残差、误差和数值稳定性；
- 保存参数、随机种子、迭代历史、中间表格和最终结果；
- 生成论文需要的数据图表和图表源数据；
- 编写 `reports/RESULTS_REPORT.md`，说明方法、结果和验证证据。

本 skill 不负责：

- 重新定义题目或擅自修改建模报告中的目标函数；
- 直接撰写论文正文；
- 生成流程图、系统架构图或概念示意图；
- 伪造缺失的实验结果；
- 把截图当作唯一结果而不保存原始数值和绘图代码。

## 二、开始前的检查

按以下顺序读取上下文：

1. `plan.md`，确认任务目标、项目结构、运行环境和输出要求；
2. `reports/ANALYSIS_MODELING_REPORT.md`，确认变量、公式、约束、评价指标和假设；
3. 原始数据、数据字典、题目附件和已有代码；
4. 用户提供的运行命令、依赖版本和时间限制。

如果建模报告没有明确样本范围、目标变量、约束条件或评价指标，先记录歧义并向建模手或用户确认，不要为了方便编码自行改变模型定义。

开始修改前检查工作区状态，保留用户已有改动，不覆盖无关文件，不删除原始数据，不把密钥写入代码、日志或结果文件。

## 三、强制代码风格

### 3.1 注释规范

- 所有新增注释必须使用中文；
- 注释解释“为什么这样做”和“输入输出是什么”，不要只重复代码字面含义；
- 复杂公式、约束、数据筛选、异常处理、单位换算和统计检验必须有注释；
- 每个主要函数都要有中文文档字符串，写明功能、参数、返回值和关键假设；
- 不使用无意义的注释，例如“定义变量”“进行循环”；
- 不在代码注释、字符串、日志和图表标签中使用 emoji；
- 不使用颜文字、装饰性 Unicode 符号或依赖字体的特殊图标作为状态标记。

推荐写法：

```python
def convert_gestational_week(week_text):
    """把“周数+天数”转换为十进制孕周。

    参数：
        week_text: 例如“12w+3”或“12周+3天”的文本。
    返回：
        十进制孕周；无法解析时返回缺失值。
    """
    # 天数除以 7，便于后续回归和时间排序。
    if week_text is None:
        return float("nan")
    ...
```

### 3.2 变量和函数命名

- 变量名使用英文，优先使用 `snake_case`；
- 变量名必须表达含义，避免 `a`、`b`、`tmp`、`data1`、`result2` 这类无语义名称；
- 数学推导中的符号可以在公式说明中使用，但程序变量仍使用易懂的英文名称；
- 布尔变量使用 `is_`、`has_`、`should_` 或 `can_` 开头；
- 数量、比例、时间和误差在变量名中体现单位或尺度，例如 `gestational_week`、`read_count`、`error_std`、`rate_percent`；
- 函数名使用动词开头，例如 `load_dataset`、`fit_regression_model`、`calculate_risk`、`save_results`；
- 类名使用 PascalCase，例如 `RiskOptimizer`；
- 常量使用全大写加下划线，例如 `TARGET_THRESHOLD`、`RANDOM_SEED`；
- 同一项目中不要混用 `BMI_value`、`bmiValue`、`body_mass_index` 三种风格，先选择一种并保持一致；
- 只有在循环索引、矩阵维度和数学公式中，才允许使用短名称如 `index`、`row_index`、`column_index`；
- 不用拼音缩写作为核心变量名，除非该缩写是领域通用名称，例如 `BMI`、`AUC`、`RMSE`。

推荐命名对照：

| 不推荐 | 推荐 | 原因 |
|---|---|---|
| `df1` | `male_detection_records` | 说明数据内容 |
| `x` | `gestational_week` | 说明变量含义 |
| `y` | `y_chromosome_concentration` | 说明响应变量 |
| `res` | `regression_residuals` | 说明结果类型 |
| `p` | `predicted_probability` | 说明概率含义 |
| `n` | `sample_count` | 说明计数对象 |

### 3.3 代码内容限制

- 代码中不得出现 emoji；
- 不把关键数字直接散落在计算公式中，阈值、权重、随机种子和边界统一放入配置区；
- 不使用无限循环、隐式全局变量或依赖当前工作目录的相对路径；
- 不用字符串拼接替代结构化数据处理；
- 不在没有验证的情况下静默填补缺失值、删除异常值或改变标签定义；
- 对随机算法固定随机种子，并把种子写入结果报告；
- 对大数据使用向量化、分块读取或合理的迭代器，不无理由逐行处理；
- 绘图代码与模型计算代码可以分离，但图表必须能追溯到结果数据。

## 四、推荐项目结构

根据已有项目结构执行，只有在项目没有结构时才创建以下目录：

```text
project/
├── code/
│   ├── run_model.py          # 主运行入口
│   ├── data_processing.py    # 数据读取和清洗
│   ├── model_fitting.py      # 模型拟合或优化求解
│   ├── evaluation.py         # 指标、残差和约束检查
│   └── visualization.py      # 论文图表生成
├── results/
│   ├── tables/               # CSV、JSON 或 Excel 结果表
│   ├── intermediate/         # 清洗数据、参数和迭代记录
│   └── run_metadata.json     # 时间、版本、随机种子和命令
├── figures/
│   ├── source/               # 图表所用数据
│   └── *.pdf                 # 论文图表
└── reports/
    ├── ANALYSIS_MODELING_REPORT.md
    └── RESULTS_REPORT.md
```

已有仓库使用其他目录名时，遵循已有结构，不强行重建目录。

## 五、标准实现流程

### 第一步：建立可复现入口

主程序应支持从命令行运行，至少包含输入路径、输出目录和随机种子参数。示例：

```python
import argparse
from pathlib import Path


def parse_command_arguments():
    """解析主程序所需的命令行参数。"""
    argument_parser = argparse.ArgumentParser(description="运行数学建模实验")
    argument_parser.add_argument("--input", required=True, help="原始数据文件路径")
    argument_parser.add_argument("--output-dir", required=True, help="结果输出目录")
    argument_parser.add_argument("--seed", type=int, default=2025, help="随机种子")
    return argument_parser.parse_args()


if __name__ == "__main__":
    command_arguments = parse_command_arguments()
    # 由主入口统一传递路径、参数和随机种子，避免函数依赖隐式全局变量。
    run_experiment(
        input_path=Path(command_arguments.input),
        output_directory=Path(command_arguments.output_dir),
        random_seed=command_arguments.seed,
    )
```

### 第二步：读取和检查数据

必须记录：

- 文件路径和文件格式；
- 工作表、字段名和字段类型；
- 样本量、个体数、重复记录数；
- 缺失值、重复值、异常值和标签分布；
- 单位、时间范围和筛选条件。

数据清洗函数不得直接覆盖原始数据。建议返回 `cleaned_data`、`cleaning_summary` 和 `dropped_record_ids`，便于审计。

同时生成 `results/results_manifest.json`，遵循仓库 `schemas/results_manifest.schema.json`，记录 run ID、代码/数据/环境指纹、参数、随机性策略、指标、图表、表格和检查结果。关键数字不得只存在于日志或论文正文。

### 第三步：实现每个子问题

按题目问题顺序实现，每个子问题至少包含：

1. 输入数据和变量定义；
2. 模型公式或算法步骤；
3. 参数、边界和约束；
4. 求解过程；
5. 结果指标；
6. 可行性和误差检查；
7. 结果表和图表数据；
8. 对结果的中文说明。

优化问题必须先验证初始解可行，再进行优化；预测或分类问题必须做训练验证划分、交叉验证或合理的误差评估；评价问题必须说明指标方向、归一化方法和权重来源。

### 第四步：保存中间结果

至少保存以下内容：

- 清洗后的数据摘要；
- 模型参数和配置；
- 随机种子和依赖版本；
- 迭代历史或收敛记录；
- 约束残差和异常检查结果；
- 图表使用的汇总数据；
- 最终结果 JSON、CSV 或其他结构化文件；
- 实际运行命令和运行时间。

## 六、统计与优化的最低验证要求

### 回归与相关分析

- 报告样本数和有效样本数；
- 报告估计系数、标准误、置信区间和显著性；
- 检查残差、异常点、多重共线性和模型拟合程度；
- 重复测量数据要考虑个体聚类、随机效应或分层抽样；
- 不仅报告 p 值，还要说明效应方向和实际意义。

### 分类与预测

- 防止同一对象同时出现在训练集和测试集；
- 类别不平衡时报告正负样本数，并说明权重或采样策略；
- 至少报告 AUC、准确率、灵敏度、特异度和混淆矩阵中适用的指标；
- 阈值选择必须说明依据，不能只选择让结果最好看的阈值；
- 对高风险筛查问题优先明确漏诊代价和误报代价。

### 优化与仿真

- 明确目标函数、决策变量、约束和单位；
- 记录初始解、可行性检查和停止条件；
- 检查不同初值、参数或随机种子下的稳定性；
- 保存收敛曲线、最优值和约束违反量；
- 若采用启发式算法，必须说明算法不能保证全局最优，并进行基准或多次重复实验。

## 七、图表规范

- 图表必须由真实计算结果生成，不手工改数；
- 图表源数据保存到 `figures/source/` 或 `results/`；
- 中文论文使用中文坐标轴、图例和单位；
- 不在图内放大标题，标题交给论文图注；
- 优先输出 PDF、SVG 等矢量格式；需要 Word 时同时输出清晰的 PNG；
- 图表不能遮挡数据、截断标签或使用不可解释的颜色；
- 图表中不得使用 emoji；
- 每张图至少在 `RESULTS_REPORT.md` 中记录数据来源、生成脚本和用途。

### 7.1 二维与三维图表的选择

图表不应只停留在二维散点图或折线图。根据变量数量、模型结构和论文表达需要，适当加入三维图表，但不得为了视觉效果强行使用三维图。

优先考虑以下三维图表：

- 三维散点图：展示三个连续变量之间的观测关系，例如“孕周-BMI-Y 浓度”；
- 三维曲面图：展示两个决策变量对目标函数、预测值或风险函数的共同影响；
- 三维等高线图：展示参数组合下的响应面，并辅助标出最优区域；
- 三维敏感性图：展示两个参数变化时模型输出或误差指标的变化。

使用三维图表时必须满足：

- 三个坐标轴都有清晰的中文名称、单位和变量含义；
- 使用颜色条表达第四个变量或响应值时，必须标明颜色条名称和单位；
- 记录视角、颜色映射、采样网格和插值方式，保证图表可以复现；
- 避免遮挡、透视变形和过密点云；必要时降低点大小、增加透明度或使用等高线辅助；
- 对三维曲面不得把稀疏观测数据未经说明地当作连续真实曲面；
- 同一个结论同时提供二维投影、切片图或表格，避免读者只能依靠旋转图片理解结果；
- 静态论文优先保存高清 PNG、SVG 或 PDF，交互式三维图可额外保存 HTML；
- 三维图中不得使用 emoji、装饰性图标或与数据无关的立体元素。

推荐的三维绘图代码结构：

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def draw_three_dimensional_response_surface(
    input_x_grid,
    input_y_grid,
    response_grid,
    output_path,
):
    """绘制两个输入变量对应的三维响应面。

    参数：
        input_x_grid: 第一个输入变量的网格。
        input_y_grid: 第二个输入变量的网格。
        response_grid: 每个网格点对应的模型输出。
        output_path: 图片保存路径。
    """
    # 先建立固定视角，避免每次运行得到不同的静态图片。
    figure = plt.figure(figsize=(8, 6))
    axis = figure.add_subplot(111, projection="3d")
    surface = axis.plot_surface(
        input_x_grid,
        input_y_grid,
        response_grid,
        cmap="viridis",
        edgecolor="none",
        alpha=0.9,
    )
    axis.view_init(elev=28, azim=-125)
    axis.set_xlabel("输入变量一")
    axis.set_ylabel("输入变量二")
    axis.set_zlabel("模型输出")
    figure.colorbar(surface, ax=axis, shrink=0.65, label="模型输出")
    figure.tight_layout()
    figure.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(figure)
```

若使用 Plotly、Mayavi 或其他三维工具，仍需同时保存静态论文图片和生成参数，不得只保存浏览器中的临时截图。

常用图表包括：

- 数据理解：分布图、箱线图、缺失率图、相关矩阵；
- 回归预测：真实值与预测值、残差分布、误差分位数；
- 优化求解：收敛曲线、方案比较、敏感性曲线；
- 分类判定：ROC 曲线、PR 曲线、混淆矩阵和阈值分析；
- 时间问题：趋势图、首达时间分布和分组时点曲线。
- 三维关系：三维散点图、响应曲面图、三维等高线图和三维敏感性图。

### 7.2 sci-box 科研绘图模板

当所需图型与 `sci-box` 模板接近时，读取 [references/scibox-figure-integration.md](references/scibox-figure-integration.md)，再调用 `$mathmodel-figure-templates` 中已经集成的模板。编程手仍负责准备真实结果数据、替换模板的演示数据、保存转换步骤和生成入口；模板选择、版式适配和 Figure QA 由 `$mathmodel-figure-templates` 负责。

不得另外安装仓库中的 `scibox-figure` 副本：其 skill 名称同样是 `mathmodel-figure-templates`，会与现有增强版发生名称冲突。没有匹配模板时按现有绘图规范实现，不强行套用模板。

结果完成后使用 `$mathmodel-workflow` 的 Runtime 注册必需结果。只有内容 hash 未变化、code/data/config/environment 指纹齐全且随机性策略已记录的结果才能冻结；冻结不等于验证正确，仍须通过后续论文和交付 Gate。

## 八、结果报告模板

`reports/RESULTS_REPORT.md` 至少包含：

```markdown
# 计算结果

## 运行环境
- Python/R/MATLAB 版本：
- 主要依赖及版本：
- 随机种子：
- 实际运行命令：

## 数据读取与预处理
- 数据文件和工作表：
- 原始样本数：
- 有效样本数：
- 缺失值和异常值处理：

## 问题一结果
- 模型和变量：
- 参数估计：
- 显著性或误差指标：
- 约束检查：

## 问题二结果

## 问题三结果

## 问题四结果

## 灵敏度分析

## 约束与一致性校验

## 输出文件索引

## 可复现运行方式
```

所有论文候选数值必须能在结果文件、日志或该报告中找到对应来源，不能在写论文阶段临时估算或改写。

## 九、交付前检查清单

运行完成后逐项确认：

- [ ] 主程序可以从干净环境或明确的依赖环境运行；
- [ ] 代码中没有 emoji；
- [ ] 新增注释和文档字符串均为中文；
- [ ] 变量名和函数名语义清晰、风格统一；
- [ ] 原始数据没有被覆盖；
- [ ] 缺失值、异常值、重复记录和筛选范围有记录；
- [ ] 随机种子、参数和依赖版本已保存；
- [ ] 结果不是只保存在终端，结构化结果文件已经落盘；
- [ ] 图表源数据和绘图代码已经保存；
- [ ] 约束、误差、敏感性和稳定性已经检查；
- [ ] `reports/RESULTS_REPORT.md` 已更新；
- [ ] 论文中的关键数值可以追溯到结果文件；
- [ ] 失败、限制和未完成项已经如实记录。

## 十、与其他 skill 的协作

- 模型定义和假设：使用建模分析相关 skill，先确认模型再编码；
- 环境和依赖：需要时调用环境诊断 skill，不把缺少可选依赖误判为模型失败；
- 系统性错误：复现问题后使用调试相关 skill，实施最小修复；
- 新功能或缺陷修复：优先先写失败测试，再实现修复；
- 流程图和架构图：交给 Draw.io 相关 skill；
- 论文正文和排版：交给数学建模写作相关 skill；
- TikZ、Nature/Science/IEEE/MCM/CUMCM 风格、多 Panel 组合与 Figure QA：交给 `$mathmodel-figure-templates`；本 skill 仍负责提供真实图表数据和可复现绘图入口；
- SHAP、配对云雨图、交叉验证 ROC、Taylor 图、相关组合图、预测边缘分布、TPE 三维曲面、分组环形热图或 Nature 和弦图：按需读取 `references/scibox-figure-integration.md`，使用已集成的 `sci-box` 模板；
- 最终交付：运行验证相关 skill，并把最新测试证据写入报告。

编程手的最终判断标准是：代码能运行，结果有来源，约束已检查，图表可复现，命名和注释便于下一位成员接手。
