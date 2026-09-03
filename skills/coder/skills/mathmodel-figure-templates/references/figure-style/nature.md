# Nature profile

This profile targets quiet, evidence-first figures compatible with Nature-family visual conventions. It is not a claim that a figure satisfies every journal or article-type requirement; verify the current target journal before submission.

## Verified production baseline

- Prepare figures at final size. Nature guidance commonly uses about 89–90 mm for one column and 180–183 mm for two columns, depending on the specific guide and stage.
- Use a consistent sans-serif family, preferably Helvetica or Arial.
- Nature's current author guidance uses 5–7 pt figure text at final size and 8 pt bold upright lowercase panel letters.
- Keep graphs, charts, schematics, and other line art editable and vector-based. Produce PDF or SVG working outputs; follow the target page's accepted-format list for final submission.
- Define every error bar, report exact sample sizes where statistical comparisons are shown, and avoid rainbow colour scales.

## Visual language

- White background, little or no grid, no decorative shadows or gradients.
- One restrained accent for the central method or conclusion; baselines use cool grey/blue-grey or neutral tones.
- Encode categories with lightness, shape, line style, or position as well as hue.
- Remove redundant in-panel titles; let panel labels and the figure legend carry hierarchy.
- Prefer outside, shared, or inline legends when an internal legend would cover data.
- Give the Hero more area or contrast, not merely a larger font.

For Matplotlib, preserve editable SVG text and test the 5–7 pt range at actual print size. For TikZ, use the same font and semantic palette across all paper figures. The source URLs and access date belong in the project QA report, not inside the figure.

Official references checked on 2026-09-03:

- <https://research-figure-guide.nature.com/>
- <https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/>
- <https://www.nature.com/nature/for-authors/initial-submission>
- <https://www.nature.com/nature/for-authors/final-submission>
