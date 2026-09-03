# Figure QA workflow

QA has five gates. A skipped gate is recorded as skipped, never passed.

## Q0 — Scientific contract

- Recompute or trace every number, sign, direction, unit, sample size, and formula shown.
- Confirm that every Panel contributes unique evidence to the Figure Contract.
- Confirm that the selected engine and style profile do not change the claim.

## Q1 — Source safety and structure

- TikZ: run `check_tikz_safety.py`, `tikz_validator.py`, and the advisory `tikz_design_linter.py`.
- Matplotlib: verify input paths, output paths, deterministic settings, saved plotting data, and vector export.
- DrawIO/Mermaid: validate source syntax and connector topology.

## Q2 — Build and render

- Compile or execute from the editable source with a fresh command.
- Record tool versions and the actual command.
- Produce a vector artifact and PNG preview.
- Treat missing glyphs, failed references, blank output, and crop failures as blockers.

## Q3 — Geometry and visual review

- Run `pdf_overlap_checker.py` when its dependency is available.
- With a supplied reference, run `figure_diff.py` to find changed regions.
- Inspect the PNG using `visual-checklist.md` at intended physical size and in grayscale.
- Fix blockers, rebuild, and repeat Q2–Q3. A fix can introduce a new defect.

## Q4 — Paper integration

- Insert the final asset into the actual manuscript.
- Compile the full paper and inspect the whole page: scale, caption, whitespace, float placement, and consistency with sibling figures.
- Update the results manifest or figure report with source, hash, command, outputs, and QA status.

Do not declare a figure complete from a static linter alone. Semantic truth and visual hierarchy require a human-visible render.
