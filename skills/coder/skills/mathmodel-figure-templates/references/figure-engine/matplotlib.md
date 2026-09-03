# Matplotlib engine

Use Matplotlib for figures whose geometry is determined by real result data: trends, distributions, uncertainty, residuals, optimization traces, model comparison, sensitivity, heatmaps, networks, and multi-panel evidence.

## Data contract

- Every plotted mark must trace to an input file or frozen result object.
- Save the plotting table beside the figure when the transformation is not obvious.
- Record filtering, aggregation, units, ordering, uncertainty definition, sample size, and random seed.
- Do not turn a categorical sequence into a connected line merely because a line chart is visually compact.
- Show observations or distributions when sample size is small; a mean bar alone hides the evidence.
- Avoid dual y-axes unless the relationship cannot be stated with normalization, facets, or aligned panels.

## Output contract

- Size the canvas at intended publication dimensions before tuning text.
- Export PDF or editable SVG plus a high-resolution PNG preview.
- Keep SVG text editable (`svg.fonttype = "none"`) and PDF text as TrueType (`pdf.fonttype = 42`) when the target accepts it.
- Use restrained, color-vision-safe colors and redundant encodings where color carries meaning.
- Multi-panel layouts use GridSpec or subfigures, aligned labels, shared legends, and lowercase panel letters when the target profile requires them.

Start from `../figure-catalog.md` when a packaged template matches. A template using simulated data is a layout baseline, not scientific evidence.

For new figures, import `scripts/figure_style.py`, call `apply_profile()` before creating axes, obtain final-size dimensions from `figure_size()`, add multi-panel labels with `add_panel_label()`, and export PDF/SVG/PNG with `save_figure()`.
