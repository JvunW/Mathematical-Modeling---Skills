# Migration to 2.0.0

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
