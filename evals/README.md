# End-to-end evaluations

本目录定义 8 类公开评测、独立故障恢复门禁和统一 100 分 rubric。公开案例用于开发回归；真正的 9.5 结论还需要按 [HOLDOUT_POLICY.md](HOLDOUT_POLICY.md) 运行 evaluator-only 题目，不能把公开样例成绩当成泛化能力。

## 评分输入

人工或隔离评测器为每次运行生成一个 JSON，包含 `runs` 和 `reliability`。每个 run 必须提供公开案例 ID、唯一 run ID、rubric 七维得分、致命错误列表和运行时；核心案例至少重复 3 次。

## 聚合

```text
python evals/run_evals.py --input <scores.json> --output <report.json>
```

评分器验证维度和范围，计算单案例均值、标准差、通过率、致命错误率和运行时，并执行发布、9.0、9.5 与 Reliability Gate。它只聚合评测者给出的证据，不会自行假装运行完整建模任务。

未运行的基线保持 `not_run`。只有生成的报告中 `claim_9_5_eligible: true`，且独立 holdout 记录可审计时，才可以把本仓库描述为“经评测达到约 9.5”。
