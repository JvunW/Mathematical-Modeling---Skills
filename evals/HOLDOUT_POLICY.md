# Holdout Evaluation Policy

Public cases are development fixtures. A formal score must use evaluator-only answers, traps, and rubrics that are **不得放入被评 Agent 的工作区**.

For each run, freeze and record:

- case version and input hash;
- model identifier and reasoning setting;
- plugin/Skill release and Git revision;
- operating system, Python version, optional toolchain, and network policy;
- complete user request and permitted artifacts;
- runtime, outcome, fatal errors, and evaluator decision.

Run every core case at least three times. Report mean, standard deviation, pass rate, observed fatal-error count, runtime, and cost when available. Do not report the best run alone.

Use at least one independent blind evaluator. Calibrate evaluators on shared examples and record disagreements. Public development scores are not holdout scores.
