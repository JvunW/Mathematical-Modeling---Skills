---
name: statistical-analysis
description: "Guide statistical analysis from test selection through reporting. Use for group comparisons, hypothesis tests, assumption checks, effect sizes, power, regression, non-parametric or Bayesian alternatives, and publication-ready statistical writeups."
---

# Statistical analysis

Choose, run, diagnose, and report statistical analyses without turning a p-value into the whole argument.

## Use this Skill when

The task involves group comparisons, association, regression, repeated measures, categorical outcomes, non-parametric tests, power or sensitivity analysis, or Bayesian inference. Use `$experimental-design` before data collection when design and randomization are the main question. Use `$uncertainty-and-units` when measurement uncertainty or dimensional consistency dominates.

## Inputs and outputs

Required inputs are the research question, outcome and predictor definitions, sampling/design structure, units, missing-data information, candidate confounders, and the actual data or sufficient summaries.

Return:

- a justified analysis specification;
- assumption and data-quality diagnostics;
- estimates with uncertainty and effect sizes;
- multiplicity or model-selection handling where relevant;
- reproducible code and machine-readable results;
- a concise report that separates evidence from interpretation.

## Reference routing

- Choose a test or model: [test_selection_guide.md](references/test_selection_guide.md).
- Diagnose assumptions and residuals: [assumptions_and_diagnostics.md](references/assumptions_and_diagnostics.md).
- Compute and interpret effect sizes or planning power: [effect_sizes_and_power.md](references/effect_sizes_and_power.md).
- Use Bayesian methods: [bayesian_statistics.md](references/bayesian_statistics.md).
- Format the final write-up: [reporting_standards.md](references/reporting_standards.md).

Read only the references required for the selected analysis.

## Workflow

1. **Translate the question.** State the estimand, unit of analysis, comparison or association, direction if pre-specified, and decision context.
2. **Audit the design.** Identify independence, pairing, clustering, repeated measures, censoring, weights, temporal order and possible leakage. Do not treat repeated observations as independent.
3. **Inspect the data.** Check types, units, impossible values, missingness, group sizes, distributions and influential points. Preserve an audit trail for exclusions.
4. **Choose the analysis.** Match outcome type and design to a test/model. Prefer a robust alternative when assumptions are materially violated; do not choose solely from a normality-test p-value.
5. **Specify before fitting.** Record transformations, contrasts, covariates, interactions, multiplicity correction, alpha/credible interval and model-selection rule.
6. **Fit and diagnose.** Run the primary analysis, then check residuals, variance, dependence, influence, convergence and predictive adequacy as applicable. The bundled `scripts/assumption_checks.py` may support frequentist diagnostics.
7. **Quantify magnitude.** Report the estimate, compatible uncertainty interval and an appropriate effect size. A non-significant result is not proof of equivalence; use equivalence or non-inferiority methods when that is the claim.
8. **Stress-test conclusions.** Compare reasonable transformations, robust/non-parametric alternatives, influential-observation handling or prior sensitivity when these could change the conclusion.
9. **Report completely.** Name the method, design, sample size, estimate, uncertainty, test statistic or posterior quantity, correction, diagnostics, limitations and reproducibility details.

## Hard constraints

- Never invent observations, sample sizes, p-values, intervals or diagnostics.
- Preserve pairing, clustering and time order.
- Do not delete outliers merely because they are inconvenient; investigate provenance and report sensitivity.
- Do not mechanically drop variables at a fixed VIF threshold. Diagnose scale, coding, estimand and identifiability; choose among reparameterization, domain-guided removal, regularization, dimension reduction or uncertainty-aware interpretation.
- Do not use post-hoc power to explain a null result. Use interval width, equivalence bounds or a clearly labeled sensitivity analysis.
- Correct or hierarchically model multiple comparisons when the inferential family requires it.
- Separate confirmatory from exploratory analyses.
- Bayesian claims require prior specification, convergence checks and posterior predictive assessment; Bayes factors are not interchangeable with posterior probabilities.

## Failure handling

- Missing data or design metadata: mark the affected conclusion `blocked`; describe the minimum information needed.
- Violated assumptions: change the model or use a justified robust alternative, then compare conclusions.
- Non-convergence or separation: do not report unstable coefficients as final; simplify, regularize, collect more information or bound the claim.
- Very small samples: emphasize raw data, exact/robust methods and wide uncertainty; avoid asymptotic certainty.
- Dependency unavailable: provide a method specification and unexecuted code separately, clearly labeled as not run.

## Acceptance checklist

The analysis answers the stated estimand; the data structure is respected; assumptions were checked with more than one mechanical test; estimates, uncertainty and effect sizes are present; multiplicity and missingness are addressed; code is reproducible; and every reported number can be traced to actual output.
