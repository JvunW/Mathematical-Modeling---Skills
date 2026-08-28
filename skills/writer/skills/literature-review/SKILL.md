---
name: literature-review
description: "Conduct systematic, multi-database literature reviews and research synthesis. Use for comprehensive searches, screening, evidence tables, narrative synthesis, systematic reviews or meta-analysis preparation with verified citations."
---

# Literature Review

## Overview

Conduct systematic, comprehensive literature reviews following rigorous academic methodology. Search multiple literature databases, synthesize findings thematically, verify all citations for accuracy, and generate professional output documents in markdown and PDF formats.

Follow the repository-wide [citation policy](../mathmodel-writing/references/citation_policy.md): use current web search and official paper pages for direct verification, `$paper-lookup` for reproducible scholarly APIs, and this Skill for systematic screening and synthesis. Domain-specific tools such as gget or BioServices are optional enhancements and are never required for the core review workflow.

## When to Use This Skill

Use this skill when:
- Conducting a systematic literature review for research or publication
- Synthesizing current knowledge on a specific topic across multiple sources
- Performing meta-analysis or scoping reviews
- Writing the literature review section of a research paper or thesis
- Investigating the state of the art in a research domain
- Identifying research gaps and future directions
- Requiring verified citations and professional formatting

## Visual Enhancement

Add a PRISMA flow diagram, thematic synthesis diagram, evidence map, or conceptual framework only when it improves the review. Do not force decorative figures into a short narrative review.

Use an image/diagram capability already available in the host. As an optional fallback, the bundled OpenRouter-based schematic script can be used when the user authorizes the external request and has configured `OPENROUTER_API_KEY`:

```text
python "<SKILL_DIR>/scripts/generate_schematic.py" "your diagram description" -o "<WORK_ROOT>/figures/output.png"
```

The optional script sends the diagram prompt and generated image through an external model service. Disclose that transfer before using it, never pass confidential material, and do not provide API keys as command-line arguments.

**When to add schematics:**
- PRISMA flow diagrams for systematic reviews
- Literature search strategy flowcharts
- Thematic synthesis diagrams
- Research gap visualization maps
- Citation network diagrams
- Conceptual framework illustrations
- Any complex concept that benefits from visualization

If no image capability is available, a text-only review is valid; record that no figure was produced.

---

## Core Workflow

A literature review runs in seven phases, documented in full with commands and templates
in [references/core_workflow.md](references/core_workflow.md):

1. **Planning and scoping** — the question, inclusion and exclusion criteria, and scope.
2. **Systematic literature search** — multi-database searching with recorded queries.
3. **Screening and selection** — title/abstract then full-text screening with counts kept
   for the PRISMA flow.
4. **Data extraction and quality assessment** — structured extraction and risk-of-bias
   or quality appraisal.
5. **Synthesis and analysis** — thematic or quantitative synthesis across studies.
6. **Citation verification** — every citation checked against the actual source.
7. **Document generation** — assembling the review with a complete bibliography.

Record every search string and date as you go: a review that cannot reproduce its own
search is not systematic. Per-database search guidance and citation styles are in
[references/search_and_citation.md](references/search_and_citation.md), and a full worked
review is in [references/example_workflow.md](references/example_workflow.md).

## Best Practices

### Search Strategy
1. **Follow the shared retrieval priority**: Use current web search/official pages for direct verification and `$paper-lookup` for reproducible structured retrieval; record exact queries, endpoints, dates, limits, and result counts.
2. **Use multiple databases** (normally at least 3): Choose databases that fit the discipline; a general web search is discovery support, not a substitute for every scholarly index.
3. **Include preprint servers**: Captures latest unpublished findings
4. **Document everything**: Save search strings, dates, database names, result counts, and raw or normalized results to the chosen workspace.
5. **Test and refine**: Run pilot searches, review results, adjust search terms
6. **Sort by citations**: When available, sort search results by citation count to surface influential work first
7. **Verify promising results**: Fetch permissible abstracts or full text from primary scholarly sources before full-text screening.

### Screening and Selection
1. **Use clear criteria**: Document inclusion/exclusion criteria before screening
2. **Screen systematically**: Title → Abstract → Full text
3. **Document exclusions**: Record reasons for excluding studies
4. **Consider dual screening**: For systematic reviews, have two reviewers screen independently

### Synthesis
1. **Organize thematically**: Group by themes, NOT by individual studies
2. **Synthesize across studies**: Compare, contrast, identify patterns
3. **Be critical**: Evaluate quality and consistency of evidence
4. **Identify gaps**: Note what's missing or understudied

### Quality and Reproducibility
1. **Assess study quality**: Use appropriate quality assessment tools
2. **Verify all citations**: Run verify_citations.py script
3. **Document methodology**: Provide enough detail for others to reproduce
4. **Follow guidelines**: Use PRISMA for systematic reviews

### Writing
1. **Be objective**: Present evidence fairly, acknowledge limitations
2. **Be systematic**: Follow structured template
3. **Be specific**: Include numbers, statistics, effect sizes where available
4. **Be clear**: Use clear headings, logical flow, thematic organization

## Common Pitfalls to Avoid

1. **Single database search**: Misses relevant papers; always search multiple databases
2. **No search documentation**: Makes review irreproducible; document all searches
3. **Study-by-study summary**: Lacks synthesis; organize thematically instead
4. **Unverified citations**: Leads to errors; always run verify_citations.py
5. **Too broad search**: Yields thousands of irrelevant results; refine with specific terms
6. **Too narrow search**: Misses relevant papers; include synonyms and related terms
7. **Ignoring preprints**: Misses latest findings; include bioRxiv, medRxiv, arXiv
8. **No quality assessment**: Treats all evidence equally; assess and report quality
9. **Publication bias**: Only positive results published; note potential bias
10. **Outdated search**: Field evolves rapidly; clearly state search date

## Integration with Other Skills

Use the bundled skills first so the workflow remains self-contained:

- `$paper-lookup`: reproducible searches across OpenAlex and other scholarly APIs.
- `$citation-verification`: existence, metadata, thematic, and claim-level citation checks.
- `$statistical-analysis`: quantitative synthesis and statistical reporting when needed.
- `$mathmodel-writing` or `$typst-author`: final paper integration and typesetting.

If the host already provides additional database, extraction, visualization, or venue-template capabilities, they may be used as optional enhancements. Their absence must not block the review.

## Resources

### Bundled Resources

**Scripts:**
- `scripts/verify_citations.py`: Verify DOIs and generate formatted citations
- `scripts/generate_pdf.py`: Convert markdown to professional PDF
- `scripts/search_databases.py`: Process, deduplicate, and format search results

**References:**
- `references/citation_styles.md`: Detailed citation formatting guide (APA, Nature, Vancouver, Chicago, IEEE)
- `references/database_strategies.md`: Comprehensive database search strategies

**Assets:**
- `assets/review_template.md`: Complete literature review template with all sections

### External Resources

**Guidelines:**
- PRISMA (Systematic Reviews): http://www.prisma-statement.org/
- Cochrane Handbook: https://training.cochrane.org/handbook
- AMSTAR 2 (Review Quality): https://amstar.ca/

**Tools:**
- MeSH Browser: https://meshb.nlm.nih.gov/search
- PubMed Advanced Search: https://pubmed.ncbi.nlm.nih.gov/advanced/
- Boolean Search Guide: https://www.ncbi.nlm.nih.gov/books/NBK3827/

**Citation Styles:**
- APA Style: https://apastyle.apa.org/
- Nature Portfolio: https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards
- NLM/Vancouver: https://www.nlm.nih.gov/bsd/uniform_requirements.html

## Dependencies

### Core requirements

- Network access to the selected scholarly APIs.
- Python 3.10+ for bundled helper scripts.
- `requests` for the bundled citation verifier and optional schematic client.

### Optional tools

- Pandoc plus a TeX distribution for PDF generation.
- `OPENROUTER_API_KEY` only for the optional external schematic generator.

Check PDF-generation dependencies without assuming the current directory:

```text
python "<SKILL_DIR>/scripts/generate_pdf.py" --check-deps
```

## Summary

This literature-review skill provides:

1. **Systematic methodology** following academic best practices
2. **Reproducible scholarly search** through `$paper-lookup`, with optional broad web discovery
3. **Multi-database integration** through APIs and optional local scientific packages
4. **Citation verification** ensuring accuracy and credibility
5. **Professional output** in markdown and PDF formats
6. **Comprehensive guidance** covering the entire review process
7. **Quality assurance** with verification and validation tools
8. **Reproducibility** through detailed documentation requirements

Conduct thorough, rigorous literature reviews that meet academic standards and provide comprehensive synthesis of current knowledge in any domain.
