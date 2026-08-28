---
name: paper-lookup
description: "Search scholarly APIs with reproducible provenance, with optional ChatGPT Deep Research for broad literature discovery. Use for papers, DOI/PMID/arXiv lookups, abstracts, citations, author works, preprints or open full text across OpenAlex, PubMed, Crossref, Semantic Scholar, arXiv and related sources."
---

# Paper lookup

Turn a literature question into bounded, reproducible retrieval with identifiers, query parameters, access dates and explicit coverage limits.

## Use this Skill when

Use it for DOI/PMID/arXiv resolution, author or citation searches, metadata verification, preprint discovery, abstract/full-text availability and batch scholarly API queries. Use `$literature-review` when the task requires systematic searching, screening records and an evidence table. For paper writing, follow the repository-wide [citation policy](../mathmodel-writing/references/citation_policy.md).

## Inputs and outputs

Clarify the topic or identifier, date/language/type filters, desired databases, result limit, deduplication rule and whether full text is required.

Return:

- the exact databases/endpoints and parameters used;
- access date and pagination/completeness status;
- normalized title, authors, year, venue and persistent identifiers;
- source links and access/full-text status;
- deduplication/reconciliation notes;
- empty, partial, rate-limited or unverified states explicitly labeled.

## Database routing

- DOI metadata and broad registration records: [crossref.md](references/crossref.md).
- Broad scholarly graph, citation counts and author works: [openalex.md](references/openalex.md).
- Biomedical metadata: [pubmed.md](references/pubmed.md) and [europepmc.md](references/europepmc.md).
- PubMed Central full text: [pmc.md](references/pmc.md).
- Preprints: [arxiv.md](references/arxiv.md), [biorxiv.md](references/biorxiv.md), [medrxiv.md](references/medrxiv.md).
- Citation graph cross-check: [semantic-scholar.md](references/semantic-scholar.md).
- Open-access location: [unpaywall.md](references/unpaywall.md) and [core.md](references/core.md).

Read the selected database references before calling an endpoint; they contain field mappings, pagination and API-specific failure modes.

## Workflow

1. **Normalize the request.** Prefer a persistent identifier when available. Otherwise build a query from distinctive title terms, author, year and topic concepts.
2. **Select authoritative sources.** Use the narrowest database that can answer the question, then one independent source for high-stakes metadata. Do not query every API by default.
3. **Record the protocol.** Save endpoint, query, filters, sort order, page/cursor, page size, requested fields, access date and key/version information without exposing secrets.
4. **Retrieve politely.** Respect documented rate limits and use bounded pagination. API keys are optional unless the selected service requires one; never print them.
5. **Validate the response body.** HTTP 200 alone is insufficient. Check API error fields, expected record shape, requested identifier, returned totals, pagination advancement and full-text body presence.
6. **Normalize and deduplicate.** Prefer DOI, then PMID/PMCID/arXiv ID, then a conservative normalized title-year-author key. Preserve source-specific records and explain merges.
7. **Verify claims.** Cross-check title, authors, year and identifier on an official publisher/database page when the result will be cited. Citation counts are database- and date-dependent.
8. **Report coverage.** State whether retrieval was exhaustive within the documented query or a bounded sample. Empty results mean “not found in this search,” not proof of absence.

## Bundled parsers

Resolve `<SKILL_DIR>` from this file. Use these scripts for saved API responses or pagination bookkeeping:

```text
python "<SKILL_DIR>/scripts/openalex_abstract.py" --help
python "<SKILL_DIR>/scripts/arxiv_atom.py" --help
python "<SKILL_DIR>/scripts/jats_to_text.py" --help
python "<SKILL_DIR>/scripts/paginate.py" --help
```

Fetch using the current environment's network capability, save the response in the workspace, then parse it. Do not claim a script or query ran without captured output.

## Deep Research

Deep Research is an optional discovery fallback when ordinary network tools are unavailable or the user explicitly requests it. Preserve its query and date, then verify candidate papers against official pages or scholarly APIs before treating them as evidence. A Deep Research summary is not a bibliographic authority.

## Hard constraints

- Never invent a DOI, PMID, arXiv identifier, author list, abstract, citation count or access status.
- Never infer that no literature exists from one empty source.
- Do not silently substitute a preprint for the version of record.
- Do not treat a well-formed error payload as a valid record.
- Do not redistribute unavailable full text; provide lawful access information instead.
- Distinguish source metadata from your inference and quote only within applicable limits.

## Failure handling

- Rate limit/server error: record status and retry guidance; switch sources only if it answers the same metadata question.
- Malformed or suspicious 200 response: reject it and preserve a sanitized sample/error field for diagnosis.
- Conflicting metadata: present the conflict, prefer the publisher/registration source for the relevant field, and avoid guessing.
- No network: work only from user-provided materials and mark external verification incomplete.
- Incomplete pagination: report retrieved/claimed totals and the stopping reason.

## Completion criteria

Every returned record has provenance; identifiers and core metadata were validated to the level required by the task; pagination and coverage are explicit; duplicates are reconciled conservatively; failures are visible; and no unverified candidate is presented as a confirmed citation.
