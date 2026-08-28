---
name: uncertainty-and-units
description: "Check units and propagate scientific uncertainty. Use for dimensional analysis, GUM budgets, Type A/B evaluation, Monte Carlo propagation, significant-figure reporting, curve-fit uncertainty, code audits, and order-of-magnitude plausibility checks."
---

# Uncertainty and units

Keep physical dimensions, uncertainty, correlation and reporting precision consistent from raw measurements to final claims.

## Use this Skill when

Use it for unit conversion, dimensional audits, Type A/B uncertainty, GUM budgets, Monte Carlo propagation, fitted-parameter uncertainty, significant figures or plausibility checks. It complements statistical analysis; it does not replace a sampling model or experimental design.

## Inputs and outputs

Required inputs include the measurement equation, values and units, uncertainty definitions, coverage/confidence convention, dependence or covariance information, and any physical bounds or reference scales.

Return:

- canonical values with explicit units;
- a dimensional-consistency result;
- an uncertainty budget or simulation specification;
- combined/expanded uncertainty with stated convention;
- sensitivity or contribution information;
- plausibility checks and publication-ready rounding;
- reproducible commands or code actually run.

## Reference routing

- GUM vocabulary, Type A/B and budgets: [gum-methodology.md](references/gum-methodology.md).
- Pint implementation patterns: [pint-recipes.md](references/pint-recipes.md).
- `uncertainties` implementation patterns: [uncertainties-recipes.md](references/uncertainties-recipes.md).
- Offset, logarithmic and domain-specific conversions: [domain-conversions.md](references/domain-conversions.md).
- Rounding and coverage reporting: [reporting-rules.md](references/reporting-rules.md).
- Order-of-magnitude checks: [plausibility-scales.md](references/plausibility-scales.md).

Read only the references relevant to the current calculation.

## Workflow

1. **Define the measurand.** Write the measurement equation, target unit and reporting context before calculating.
2. **Canonicalize inputs.** Retain units at ingestion; identify affine temperatures, logarithmic units, angles, percentages and scale factors before arithmetic.
3. **Audit dimensions.** Confirm every sum compares compatible dimensions and every output dimension matches the model. A conversion that runs is not automatically physically meaningful.
4. **Classify uncertainty.** Record source, distribution, standard uncertainty, degrees of freedom or justification, and whether it is Type A or Type B.
5. **Model dependence.** Preserve repeated-use correlation and covariance. Do not add correlated components in quadrature as if independent.
6. **Choose propagation.** Use analytic/automatic linear propagation for smooth, locally linear models; use Monte Carlo for material nonlinearity, bounds, discontinuities, asymmetric inputs or complex correlation.
7. **Validate the method.** Compare linearized and Monte Carlo results when linearity is uncertain; check seeds, convergence, domain failures and coverage definition.
8. **Check plausibility.** Compare sign, range, dimensionless groups and order of magnitude with explicit physical scales.
9. **Report and round.** Round uncertainty first, then the estimate to the same decimal place; state unit, standard/expanded uncertainty, coverage factor or interval, method and dominant sources.

## Bundled commands

Resolve `<SKILL_DIR>` from this file and inspect `--help` before use:

```text
python "<SKILL_DIR>/scripts/convert_units.py" --help
python "<SKILL_DIR>/scripts/audit_units.py" --help
python "<SKILL_DIR>/scripts/propagate_uncertainty.py" --help
python "<SKILL_DIR>/scripts/uncertainty_budget.py" --help
python "<SKILL_DIR>/scripts/check_plausibility.py" --help
python "<SKILL_DIR>/scripts/format_result.py" --help
```

Prefer the bundled scripts for auditable, machine-readable calculations. Do not claim a command ran unless its output was captured.

## Hard constraints

- Never strip units at an unknown scale or silently reinterpret a unitless number.
- Convert affine temperatures as quantities; apply temperature differences separately.
- Treat decibels, pH and similar logarithmic units according to their definitions, not as ordinary linear units.
- Preserve covariance through every unit conversion using the correct scale transformation.
- Do not assume independence without justification.
- Do not report symmetric uncertainty when bounds or nonlinearity make the distribution materially asymmetric.
- Constants, tolerances and instrument specifications require a source and uncertainty convention.
- Significant digits must reflect uncertainty, not display preference.

## Failure handling

- Unknown unit or scale: mark the calculation `blocked` and ask for the missing definition.
- Non-physical domain samples: investigate model domain and input distributions; report rejection/truncation rules rather than silently dropping samples.
- Singular covariance: verify construction and dependence assumptions; do not regularize without disclosure.
- Analytic/Monte Carlo disagreement: treat linearization as invalid until the discrepancy is explained.
- Missing optional library: use an auditable manual calculation for simple cases or provide unexecuted code separately; do not fabricate results.

## Acceptance checklist

The measurand and unit are explicit; equations are dimensionally valid; every uncertainty component has provenance and a distribution; dependence is modeled; the propagation method is justified and checked; results are plausible; and estimate, uncertainty, coverage and rounding are reported consistently.
