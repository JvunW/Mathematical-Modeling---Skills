---
name: systematic-debugging
description: "Diagnose bugs, failed tests and unexpected behavior by finding the root cause before proposing a fix. Use whenever software or scientific code behaves incorrectly."
---

# Systematic debugging

Find the earliest incorrect state, explain why it occurs, and verify the smallest safe correction. A symptom disappearing is not evidence that the root cause is fixed.

## Use this Skill when

Use it for test failures, incorrect numerical results, crashes, hangs, flaky behavior, performance regressions, integration failures and environment-specific differences. For a requested implementation with no observed defect, use the normal development workflow; once behavior is specified, `$test-driven-development` may guide the change.

## Inputs and outputs

Gather the exact command or action, expected and actual behavior, relevant data/configuration, environment/version, recent changes, logs and the smallest reproducible case.

Return:

- a reproducible observation;
- evidence locating the first incorrect boundary;
- one explicit root-cause statement;
- a regression test or equivalent executable check;
- the minimal correction and fresh verification results;
- remaining uncertainty or untested environments.

## Core workflow

### 1. Reproduce and preserve evidence

Run the exact failing path before editing. Capture exit status, complete relevant error, inputs and environment. If it is intermittent, measure frequency and vary only one factor at a time. Do not clean caches or reinstall everything before preserving the failure.

### 2. Trace backward to the first bad state

Start from the observed symptom and inspect each producer boundary: caller/callee, serialized data, configuration, process, API, database or rendering stage. Log both the value and its provenance. For deep call chains, use [root-cause-tracing.md](references/root-cause-tracing.md).

For multi-component systems, verify what enters and leaves every boundary. Ask where the first divergence from a known-good run appears, not which final component printed the error.

### 3. Compare with a known-good pattern

Find the smallest similar path that works. List every difference in code, data, version, ordering and environment. Check documentation or source when API behavior is uncertain. Avoid assuming a difference is irrelevant before testing it.

### 4. Form one falsifiable hypothesis

State: “The root cause is X because evidence Y first diverges at boundary Z.” Design the smallest experiment that can disprove it. Change one variable; do not bundle speculative fixes.

### 5. Add the regression check

When behavior can be automated, write the smallest failing test before changing production code. For scientific calculations, also preserve a representative input, invariant, constraint or tolerance. If automation is impossible, write an exact manual reproduction with expected evidence.

### 6. Implement the smallest safe fix

Correct the producer of the bad state. Avoid unrelated refactoring, broad exception swallowing, arbitrary retries, disabled validation or inflated tolerances. If multiple defensive layers are warranted, use [defense-in-depth.md](references/defense-in-depth.md) after the root fix is known.

### 7. Verify freshly

Re-run the original reproduction, the new regression check and the relevant surrounding suite. Confirm logs are clean and that the test fails when the fix is intentionally absent or otherwise truly exercises the defect. For timing problems, replace sleeps with conditions; see [condition-based-waiting.md](references/condition-based-waiting.md).

## Stop conditions

Stop editing and return to investigation if you are:

- proposing a fix before reproducing or locating the first bad state;
- changing multiple variables at once;
- relying on “probably,” “should work,” or an unrelated successful test;
- adding retries, sleeps, null guards or exception swallowing without explaining the invalid state;
- widening numeric tolerances without a justified error budget;
- blaming a dependency without a minimal reproduction or version evidence;
- attempting a third speculative fix without revising the causal model.

After two disproved hypotheses, summarize observations and redraw the data/control flow. If the system is externally unavailable, mark the affected verification `blocked` and state what evidence would unblock it.

## Scientific and numerical checks

For mathematical modeling code, include invariants beyond “the script ran”: dimensions and units, constraint residuals, objective recomputation, baseline comparison, deterministic seeds, data-leakage checks, finite/NaN behavior, plausible ranges and sensitivity to tolerances. A visually plausible chart does not validate its underlying numbers.

## Completion criteria

The failure is reproducible or its intermittency is quantified; evidence identifies the earliest incorrect state; the explanation predicts the failure; the fix addresses that cause; a regression check covers it; original and surrounding tests pass freshly; and limitations are explicit.
