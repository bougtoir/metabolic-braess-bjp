# Reference Verification Audit Report

**Generated:** 2026-08-22T09:25:21Z
**Method:** Articles → Crossref API | Books → Open Library API | URLs → HTTP reachability
**Source:** `scripts/create_scrr_hypothesis_commentary.py` REFERENCES list
**Total references:** 18

## Summary

| Status | Count | Meaning |
|--------|-------|---------|
| MATCH | 18 | Verified correct (INFO-level notes only) |
| WARNING | 0 | Possible metadata error (year/vol/pages) |
| CRITICAL_MISMATCH | 0 | Crossref found different paper — likely wrong ref |
| UNVERIFIED | 0 | Could not verify (book, API miss) |

### Severity Legend

- **CRITICAL**: Title or first-author mismatch → Crossref matched a different paper
- **WARNING**: Volume, pages, year (>1yr diff), or co-author surname mismatch → needs manual check
- **INFO**: Journal abbreviation vs full name, year +/-1 → acceptable/expected

## All Results (Quick View)

| # | Status | First Author | Year | Notes |
|---|--------|--------------|------|-------|
| 1 | MATCH | Kirkeby A | 2025 |  |
| 2 | MATCH | Yamanaka S | 2020 |  |
| 3 | MATCH | Volpato V | 2018 |  |
| 4 | MATCH | Volpato V | 2020 |  |
| 5 | MATCH | Ortmann D | 2017 |  |
| 6 | MATCH | Panina Y | 2020 |  |
| 7 | MATCH | McCreery KP | 2024 |  |
| 8 | MATCH | Chui JS | 2024 |  |
| 9 | MATCH | Sato S | 2023 |  |
| 10 | MATCH | Ameneiro C | 2020 |  |
| 11 | MATCH | Bi S | 2020 |  |
| 12 | MATCH | Cai J | 2025 |  |
| 13 | MATCH | Agarwal N | 2017 |  |
| 14 | MATCH | Czyz J | 2004 |  |
| 15 | MATCH | Diatroptova MA | 2022 |  |
| 16 | MATCH | Mizuno M | 2020 |  |
| 17 | MATCH | Klein SG | 2022 |  |
| 18 | MATCH | Barrett T | 2012 |  |

## Methodology

1. Each reference is parsed to extract: first author surname, title, year, volume, pages
2. Reference type detected: article → Crossref API, book → Open Library API, URL → HTTP check
3. **Articles**: Crossref queried with `query.bibliographic` + `query.author`; metadata compared
4. **Books**: Open Library queried with title + author; title/author/year compared
5. **URLs**: HTTP HEAD request to verify reachability (status code < 400)
6. Issues classified by severity: CRITICAL > WARNING > INFO
7. Journal abbreviation differences (NLM vs full name) classified as INFO (acceptable)
8. Article IDs (e.g., 'deaf008', 'e201900534') recognized as valid page identifiers
9. Year differences of exactly +/-1 classified as INFO (online-first vs print)

### Limitations

- Crossref coverage is not 100% (some older/non-English journals may be missing)
- Open Library coverage varies; some books may not have entries
- URL reachability may be affected by geoblocking, authentication, or temporary outages
- Author name transliterations may differ between databases
- This script verifies metadata accuracy, NOT whether the citation supports the claim in text
- A MATCH status means the API confirmed the work exists with matching metadata —
  it also checks the first three co-author surnames against Crossref

### Reproducibility

Re-run: `python scripts/verify_references.py`

Results are deterministic for a given REFERENCES list and Crossref database state.
Crossref metadata may be updated over time (corrections, retractions).
Commit the JSON/MD reports as audit artifacts alongside the manuscript.