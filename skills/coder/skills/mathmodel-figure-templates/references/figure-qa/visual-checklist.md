# Visual QA checklist

Answer every applicable item from the rendered PNG/PDF, not from source code.

## First impression

- [ ] In three seconds, the visual centre matches the Figure Contract's Hero or clearly communicates that no Hero is needed.
- [ ] The eye follows the intended main flow without reversing direction or getting trapped.
- [ ] Removing any decorative or repeated element would lose useful information; otherwise remove it.

## Geometry

- [ ] No text, marker, arrow, line, node, legend, panel letter, or annotation is clipped or overlapping.
- [ ] Connectors stop at the intended boundary and do not cross unrelated nodes.
- [ ] Aligned rows and columns share baselines, heights, and spacing where the layout implies equality.
- [ ] Supporting Panels do not crowd the Hero or create unexplained empty regions.

## Typography and colour

- [ ] Text is readable at final physical size; font substitution and missing glyphs are absent.
- [ ] Typography has at most a small, consistent hierarchy and no isolated oversized label.
- [ ] The key distinction survives grayscale and common colour-vision deficiencies.
- [ ] One semantic object keeps the same colour, marker, or line style across Panels and sibling figures.

## Scientific meaning

- [ ] Axes, units, legends, sample sizes, uncertainty, and statistical annotations are defined.
- [ ] Panel order and arrow direction agree with the model and manuscript.
- [ ] Numeric and formula annotations are recomputed from evidence, not copied from a decorative template.
- [ ] No two Panels encode the same conclusion without adding a distinct comparison or mechanism.

## Delivery

- [ ] Vector source remains editable and the PNG is only a preview, not the sole artifact.
- [ ] The integrated manuscript page has balanced scale, caption spacing, and consistent styling.
- [ ] The QA report records blockers fixed, known limitations, and checks skipped with reasons.
