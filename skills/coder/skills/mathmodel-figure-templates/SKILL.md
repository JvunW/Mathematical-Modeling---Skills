---
name: mathmodel-figure-templates
description: "复用内置科研绘图模板生成论文图表。用于 SHAP 组合图、雨云图、ROC、Taylor 图、相关矩阵、边缘分布、三维调参曲面、环形热图、公园降温图或和弦图。"
---

# MathModel Figure Templates

This skill contains portable Python/matplotlib templates for publication figures. Resolve `<SKILL_DIR>` as the directory containing this `SKILL.md`; do not assume a particular home directory, repository, or harness.

## Fast Path

1. Match the requested chart in `references/figure-catalog.md`.
2. From the user's chosen workspace, run the renderer with the template id:

```text
python "<SKILL_DIR>/scripts/render_template.py" paired-raincloud
```

3. The renderer copies the bundled template script into `绘图复刻/scripts/`, runs it there, and writes outputs to `绘图复刻/outputs/`.
4. Return the generated PNG/PDF/SVG paths and the copied script path to the user.

Use `--list` to show supported ids:

```text
python "<SKILL_DIR>/scripts/render_template.py" --list
```

## Output Contract

- Work under the current workspace unless the user gives another path.
- Default project folder: `绘图复刻`.
- Script path: `绘图复刻/scripts/make_<template>.py`.
- Outputs: `绘图复刻/outputs/<template>_replica.png`, `.pdf`, `.svg`.
- Use the bundled scripts as the first choice; edit the copied workspace script only when the user requests customization.
- The bundled scripts use deterministic simulated data. Do not claim simulated values reproduce a source study exactly.

## Template Ids

- `multiclass-shap-combo`
- `paired-raincloud`
- `cv-roc-ci`
- `taylor-diagram`
- `correlation-pairgrid`
- `prediction-marginal-grid`
- `rf-tpe-surface`
- `grouped-corr-split-violin`
- `grouped-circular-heatmap`
- `urban-park-cooling-combo`
- `nature-chord-diagram`

## When Customizing

If the user asks for changes, copy/run the nearest template first, then edit the copied file in `绘图复刻/scripts/`. Preserve:

- `MPLCONFIGDIR` before importing matplotlib.
- deterministic seeds for simulated data.
- PNG/PDF/SVG export.
- readable labels, legends, and high-DPI output.

Use `references/plot-recipes.md` for implementation patterns.
