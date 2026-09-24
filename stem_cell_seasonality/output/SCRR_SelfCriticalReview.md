# Final pre-submission review: SCRR Hypothesis and Commentary

**Manuscript:** *The Invisible Variables: Why Clonal Systems Are Not Immune to Environmental Confounding*  
**Target journal / form:** Stem Cell Reviews and Reports, Hypothesis and Commentary (3,000–5,000 words)  
**Review date:** 2026-08-19

## Executive summary

This final reviewer-perspective review confirms the manuscript is submission-ready once the author replaces the affiliation placeholder. All previously identified substantive issues have been addressed: the GEO natural-experiment description is consistent with the analysis report, the unsupported HSC claim has been removed, the GMP quote/citation issue is fixed, and the English has been lightly polished to reduce formulaic phrasing.

## Checklist verification

| Requirement | Method | Result |
|---|---|---|
| All figures/tables cited in order | Automated scan of the generated DOCX | Figure 1, Table 1, Table 2 all cited in first-appearance order; no orphans |
| Word math in Word, no LaTeX | Auto scan for `$...$` and `\commands` | No LaTeX markers found |
| All references exist | `verify_references.py` against Crossref | 18/18 MATCH, 0 warning/critical |
| Numbers/figures reproducible from public repo + cited data | Clean clone of `bougtoir/stem-cell-seasonality`, run `create_scrr_hypothesis_commentary.py`, `analysis_with_country.py`, `natural_experiment.py` | Identical: 6,101 records, March peak, >95% NH, Japan n=200, Sep-start January peak, detrended solar correlation vanishing |
| Intro promises collected in Discussion/Results | Keyword coverage check | Clonal complacency, environmental variance, GMP gap, IoT roadmap, 6,101 GEO, natural experiment, prospective monitoring all returned |
| Result numbers and Discussion claims consistent | Manual cross-check against `analysis_report.md` and `natural_experiment_report.md` | Claims match; no over-causal language; causality restricted to future Phase III experiments |
| No old-version language | Auto scan for “old version,” “previous analysis,” etc. | None found |
| Natural English, reduced AI-like phrasing | Manual read-through; formulaic transitions replaced | “Taken together” -> “Together,” “What is unknown” -> “What remains unknown,” “A coordinated next step would be” -> “A logical next step is,” etc. |
| Section-level consistency | Section-by-section reading | Introduction -> Why PSCs -> GMP gap -> IoT roadmap -> Retrospective limits -> Discussion -> Declarations all flow; no contradictions |
| SCRR guidelines priority over generic inline figure rule | Manuscript has Figure Legends and Tables sections at end + separate PPTX/DOCX for journal upload | Consistent with SCRR “Hypothesis and Commentary” submission file conventions |

## Severity-ranked findings

### Must fix before upload (author input)
1. **Affiliation placeholder** — `1[Affiliation to be added]` must be replaced.
2. **Confirm Funding statement** — currently “This work received no specific funding.” Update if incorrect.

### Acceptable as-is
- Word count: total ≈3,472 words; excluding references ≈3,006 words (within 3,000–5,000).
- Citation style: Vancouver, numbered by first appearance; no orphan references.
- Declarations, References, Figure Legends, and Tables sections ordered correctly.
- Data/Code Availability statements are present.

### Optional polish
- Add one or two concrete sensor brands/specifications if the author wants more distance from the lower word-count boundary.
- The line “with typical lags of 6-18 months from bench to deposition” is an estimate; if a citation for this lag range is available, adding it would strengthen the claim.

## Reviewer-priority consensus

| Priority | Items |
|---|---|
| Fatal if ignored | None identified. |
| Major | Affiliation and funding placeholders |
| Minor | Word count near lower bound (within range, but close); optional sensor specificity |
| Trivial | Cosmetic English polish already performed. |

## Conclusion

The package is scientifically coherent, all empirical numbers trace to cited public data or reproducible code, and the submission structure follows the SCRR Hypothesis and Commentary format. After filling in the affiliation and confirming the funding statement, the author can upload the body DOCX and the separate figure/table files to the journal.
