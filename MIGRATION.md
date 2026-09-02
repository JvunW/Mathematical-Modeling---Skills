# Release migration notes

## 2.1.0 additive update

- The Writer plugin adds `mathmodel-humanizer-zh` for evidence-preserving Chinese academic drafting and final polishing.
- `mathmodel-writing-grill` now runs an exact 10-question user decision interview at each of its two gates; Agent self-review, default answers, and fewer-question shortcuts are no longer accepted.
- Chinese papers call this Skill in two modes: once after the content-plan grill to guide drafting, and again after the completed-draft grill before compilation or DOCX export.
- The new protected-content checker compares numbers, mathematical spans, citations, labels, image paths, commands, and code before and after editing.
- No schema migration is required. Existing projects can skip this optional language stage or add `reports/HUMANIZATION_REPORT.md` when it is used.
- Writer 2.1.0 remains compatible with Modeler 2.0.0 and Coder 2.0.0.

## Migration to 2.0.0

## Breaking changes

- The complete workflow now supports Typst/PDF, LaTeX/PDF, and Word/DOCX.
- Workflow state and important artifacts use versioned JSON contracts.
- Artifact `lifecycle` and `validity` are separate fields.
- References to unavailable legacy namespaces, standalone power-analysis helpers, and retired parallel command wrappers were removed.
- Plugin versions move to 2.0.0 because the workflow and output contracts changed.

## Existing projects

1. Back up the existing project workspace.
2. Run `workflow_runtime.py init <project-root>`; this creates only missing state files.
3. Register existing final result files as draft artifacts.
4. Verify their code, data, configuration, environment, and randomness provenance before freezing.
5. Generate the four manifest files from actual project evidence; do not invent fields for legacy work.
6. Run full verification before treating the project as G6 complete.

Legacy projects may continue without Runtime, but must be described as pre-2.0 and cannot claim state-resume or automatic stale-propagation guarantees.

## Rollback

Use the `v1.x` Git tag or the pre-install backup of each Skill directory. Schema 1.0 files are additive project artifacts; rollback does not delete them.
