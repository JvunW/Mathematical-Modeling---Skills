# TikZ engine

Use TikZ when the figure needs native mathematical notation, exact anchors, causal or variable relations, 2D geometry, a compact model architecture, or a LaTeX-native vector source.

## Authoring contract

- Start from the Figure Contract in `../../SKILL.md`.
- Prefer semantic node names and relative placement from the `positioning` library. Use explicit coordinates only for geometry or charts that require them.
- Keep one paper-wide style vocabulary for fonts, arrows, border widths, fills, spacing, and semantic colors.
- Use modern `arrows.meta` tips; at final print size, the arrow shaft must remain visibly longer than the tip.
- Give centimetre-scale offsets explicit units. Unitless `xshift` and `yshift` are points, while picture coordinates are commonly centimetres.
- Use no shell escape and no generated external code during compilation.
- Do not place invented benchmark values, citations, sample sizes, or model parameters in a decorative Panel.

## Layout selection

- Single chain or mathematical comparison: write directly; no Hero required.
- Pipeline with three or more stages: start from `assets/example-skeletons/pipeline.tex` if its topology matches.
- Overview whose claim depends on one mechanism: start from `assets/example-skeletons/central-hero.tex`.
- Use snippets as local components, not as a checklist to fill every empty area.

For complex figures, follow the Module-first sequence in `../../SKILL.md`. Compile the Hero alone before surrounding it with the main flow and supporting Panels.

## Required checks

Run `check_tikz_safety.py`, `tikz_validator.py`, `tikz_design_linter.py`, `compile_render.py`, and—when PyMuPDF is installed—`pdf_overlap_checker.py`. Then inspect the PNG at its intended paper width. A green static report cannot verify semantic direction, visual hierarchy, or scientific truth.
