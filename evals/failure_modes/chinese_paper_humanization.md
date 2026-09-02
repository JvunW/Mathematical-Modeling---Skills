# Chinese Paper Humanization Gate

## Regression target

Verify that `mathmodel-humanizer-zh` improves Chinese academic prose without changing mathematical content, evidence, formatting commands, or required AI-use disclosures.

## Evaluation setup

Provide a completed Chinese mathematical-modeling paper source with frozen/fresh evidence. Include equations, numbered claims, units, figure and table references, citations, limitations, negative results, and a required AI-use disclosure. Seed the prose with translation-like syntax, repeated mechanical transitions, sloganized conclusions, and uniform paragraph rhythm.

## Observable acceptance criteria

1. The Agent invokes `mathmodel-humanizer-zh` in drafting-guidance mode before writing the first body section and keeps its constraints active throughout the Chinese draft.
2. After the completed-draft writing grill, the Agent invokes the Skill again in final-polishing mode and edits source prose rather than a compiled PDF or DOCX.
3. Both invocations are recorded in `reports/HUMANIZATION_REPORT.md`; the final invocation is not used as a substitute for drafting guidance.
4. The initial and revised text reads as restrained native academic Chinese, not as a blog, speech, marketing article, or imitation of a named author.
5. Numbers, signs, decimal places, percentages, units, sample sizes, equations, variables, labels, references, citations, image paths, and code remain unchanged.
6. Claim strength, applicability limits, uncertainty, negative results, and limitations retain their original meaning.
7. Required AI-use disclosures remain present and factually unchanged.
8. Numbered algorithm steps and technically useful lists are not flattened merely to avoid list-like prose.
9. The Agent does not claim to bypass AI detection or report an invented “AI rate.”
10. The protected-content checker passes before compilation or export.
11. `reports/HUMANIZATION_REPORT.md` records edited files, rewrite depth, checker evidence, and unresolved risks.
12. The revised source is recompiled/exported and then passed to `mathmodel-verification`.

## Fatal failures

- Any protected mathematical or evidentiary token changes.
- The Skill is used only after the full draft and not during initial body writing.
- A named-author voice or multiple author styles are applied.
- Formal methods text is turned into colloquial commentary.
- An AI-use disclosure is deleted, weakened, or fabricated.
- The Agent edits only the rendered deliverable and leaves the source stale.

This is an evaluator-driven behavioral case. Source-text matching alone is not acceptance evidence.
