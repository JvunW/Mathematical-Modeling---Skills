# Example Workflow

A complete worked review from scoping through generated document.

## Example Workflow

Complete workflow for a biomedical literature review:

```bash
# 1. Create the review document from the bundled template.
# 2. Use $paper-lookup for OpenAlex, PubMed, Crossref, Semantic Scholar,
#    arXiv, and relevant preprint sources. Save raw JSON and query provenance.
# 3. Use the current harness's web search only as a discovery supplement,
#    then verify candidates through scholarly APIs or primary source pages.
# 4. Aggregate and process database results.
python scripts/search_databases.py combined_results.json \
  --deduplicate \
  --rank citations \
  --year-start 2015 \
  --year-end 2024 \
  --format markdown \
  --output search_results.md \
  --summary

# 5. Screen results and extract data
# - Retrieve permissible full text from primary scholarly sources
# - Manually screen titles, abstracts, full texts
# - Extract key data into the review document
# - Organize by themes

# 6. Write the review following template structure
# - Introduction with clear objectives
# - Detailed methodology section
# - Results organized thematically
# - Critical discussion
# - Clear conclusions

# 7. Verify all citations
python scripts/verify_citations.py crispr_sickle_cell_review.md

# Review the citation report
cat crispr_sickle_cell_review_citation_report.json

# Fix any failed citations and re-verify
python scripts/verify_citations.py crispr_sickle_cell_review.md

# 8. Generate professional PDF
python scripts/generate_pdf.py crispr_sickle_cell_review.md \
  --citation-style nature \
  --output crispr_sickle_cell_review.pdf

# 9. Review final PDF and markdown outputs
```
