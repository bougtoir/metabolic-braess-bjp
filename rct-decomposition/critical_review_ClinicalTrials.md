# Reviewer-perspective critical review — Clinical Trials submission

Review date: 2026-08-21
Target journal: *Clinical Trials: Journal of the Society for Clinical Trials*
Manuscript: "The KOTHA Framework: Diagnosing Structural Information Loss in Randomized Controlled Trial Meta-Analyses to Inform Trial Design"

This review was conducted after the first Clinical Trials build and before final submission. Each item is classified by severity and the status of the fix.

---

## 1. Manuscript content and narrative

| # | Item | Severity | Finding | Proposed fix | Status |
|---|---|---|---|---|---|
| 1.1 | Title case | Low | Title used sentence case; Sage / Clinical Trials convention prefers title case for major words. | Update title to title case throughout manuscript, cover letter, and submission documents. | **Fixed** |
| 1.2 | Novelty framing | Medium | The claim that no existing framework tightly links prospective power assessment, retrospective diagnostic evaluation, and structured evidence interpretation in a single reproducible workflow is plausible but could be read as overreaching. | Softened the framing to "to our knowledge, no widely adopted framework tightly links..." and positioned KOTHA as complementary to existing OIS/TSA/GRADE tools. | **Fixed** |
| 1.3 | Abstract design relevance | Medium | The original abstract described methods and results but did not explicitly state what trialists should do with the findings. | Rewrote the Background/Aims sentence to state that KOTHA is meant to inform sample size, eligibility, enrichment, and endpoint decisions in prospective trial design. | **Fixed** |
| 1.4 | TSA boundary wording | **High** | The original sentence reported a negative Z-statistic crossing "the O'Brien-Fleming boundary of 0.27". This was arithmetically confusing (the boundary for benefit is negative, and the magnitude itself is not clinically meaningful without context) and could be flagged as a statistical misstatement. | Rewrote the Results text to clarify the fixed-effect Z did not cross the conventional two-sided boundary, while the random-effects Z crossed the O'Brien-Fleming boundary, which because cumulative information exceeded the optimal information size equals the conventional two-sided boundary (\|Z\| = 1.96). Updated `validation/run_validation.py` and `build_paper.py` to cap the OBF boundary at z_α when `info_fraction >= 1`. | **Fixed** |
| 1.5 | Results–conclusions alignment | Low | Conclusions about magnesium (serious inconsistency) and statins (serious indirectness) follow directly from Module H outputs. | No change required; wording verified against Table 2. | **No change** |
| 1.6 | Keywords | Low | Six keywords are within the 3–10 range and relevant. | No change. | **No change** |
| 1.7 | Strength of causal interpretation | Medium | Phrases such as "enrollment progressively excludes higher-risk patients" imply a causal mechanism. The manuscript does not prove this mechanism; it diagnoses structural information loss conditional on observed aggregate data. | Ensured language consistently uses "diagnoses", "quantifies", "identifies", and "information-loss" rather than causal claims. Limitations explicitly acknowledge ecological bias and unmeasured confounding. | **Fixed** |

---

## 2. Statistical design and methods

| # | Item | Severity | Finding | Proposed fix | Status |
|---|---|---|---|---|---|
| 2.1 | Unit of analysis / ecological bias | Medium | Aggregate study-level data are used for both cases; ecological bias is real, especially for statins where event proportions are crude study-level aggregates. | Added explicit limitations: crude event proportions are aggregate study-level values; comparison is ecological; individual patient data would strengthen risk-profile stratification. Rewrote `run_validation.py` so statin control event rates are derived directly from `events.sum()/N.sum()` in the public CSVs instead of hard-coded annual rates. | **Fixed** |
| 2.2 | S3 enrichment threshold | Low | The S3 target for statins was set at the midpoint between observational and RCT crude proportions. This is a modelling choice that needs transparent justification. | Updated code to compute S3 as the midpoint of observed observational and RCT crude proportions and added a limitation that other thresholds would yield different power curves. | **Fixed** |
| 2.3 | Confounding and discounting | Low | Module T uses power-prior discounting but cannot remove unmeasured confounding. | Already stated; no change beyond limitations note. | **No change** |
| 2.4 | Multiple comparisons | Low | The α grid is exploratory; no formal multiplicity adjustment is claimed. | No change. | **No change** |
| 2.5 | Effect measures and uncertainty | Low | OR/HR with 95% CrI/CI are reported; RMST alternatives are mentioned. | No change. | **No change** |
| 2.6 | TSA model heterogeneity | Low | Fixed-effect and random-effects TSA give different conclusions; the manuscript now explicitly frames this as era-dependent heterogeneity rather than a contradiction. | Verified wording in Results; no further change. | **No change** |
| 2.7 | O'Brien-Fleming boundary capping | **High** | Original code used `z_alpha / sqrt(info_fraction)` for any `info_fraction > 0`, producing extremely conservative boundaries (`>1.96`) when cumulative information is below OIS and failing to cap at the conventional boundary once OIS is reached or exceeded. | Updated `run_validation.py` and `build_paper.py` to use the conventional two-sided boundary (z_α = 1.96) when `info_fraction >= 1`, and `z_alpha / sqrt(info_fraction)` only when `0 < info_fraction < 1`. The manuscript now states that the boundary "equals the conventional two-sided boundary" in this case. | **Fixed** |
| 2.8 | Uncertainty language in abstract | Low | Abstract stated probabilities "remained below conventional decision thresholds, leaving conclusions uncertain"; this is appropriate but the connection to GRADE categories could be clearer. | Conclusions sentence now maps directly to Module H ratings: inconclusive with serious inconsistency (magnesium) and inconclusive with serious indirectness (statins). | **Fixed** |

---

## 3. Figures and tables

| # | Item | Severity | Finding | Proposed fix | Status |
|---|---|---|---|---|---|
| 3.1 | Main-text count | **High** | The Clinical Trials limit is ≤6 main tables/figures. Abbreviations had been rendered as a table in early CCTC builds, which would count as a table. | Converted the abbreviations section to a bullet list in `build_paper_clinical_trials.py`. The final manuscript contains 4 figures (Fig. 1–4) and 2 numbered tables (Table 1–2) = 6 items. | **Fixed** |
| 3.2 | Supplementary reorganization | Medium | Original CCTC Tables 1/3 and Figs. 5/6/7 needed to move to supplementary materials. | Supplementary Tables S1–S4 and Supplementary Figs. S1a/b, S2–S4 are produced by the build scripts; the main manuscript refers to them appropriately. | **Fixed** |
| 3.3 | Separate figure files | **High** | Sage/Clinical Trials requires figures as separate files, not embedded in the submission manuscript. | Generated two docx variants: `KOTHA_Framework_ClinicalTrials.docx` (inline figures/tables for editing) and `KOTHA_Framework_ClinicalTrials_submission.docx` (placeholder markers `[Insert Figure N]` plus figure legends collected at the end). High-resolution 500 dpi PNGs are in `ClinicalTrials_figures/`. | **Fixed** |
| 3.4 | Editable supplementary figures PPTX | Low | Previously no editable supplementary figures PPTX existed. | Added `build_supplementary_figures_pptx.py` and generated `KOTHA_Framework_ClinicalTrials_supplementary_figures.pptx` (one slide per supplementary figure). | **Fixed** |
| 3.5 | Table 2 color coding | Low | Color is used to indicate concern level; reviewers may request grayscale readability. | Ensure Table 2 also encodes concern by text (e.g., "serious", "not serious") in addition to shading; verified in generated tables docx. | **Verified** |
| 3.6 | Inline placement and citation order | Medium | All figures and tables must be cited in the body text and placed immediately after first citation. | Verified: Fig. 1 after first paragraph of Methods, Fig. 2 in Results, Fig. 3 after power-curve description, Fig. 4 in Results, Table 1 in Methods, Table 2 in Results. Sequential order is 1→2→3→4 for figures and 1→2 for tables. | **Verified** |
| 3.7 | Language consistency | Low | All figure/table elements must be in English in the English manuscript. | Generated English-only figures and tables; no Japanese or mixed-language labels. | **Verified** |

---

## 4. Reproducibility and data traceability

| # | Item | Severity | Finding | Proposed fix | Status |
|---|---|---|---|---|---|
| 4.1 | Public data and code | Medium | All study-level data are in `data/` with documented sources (`data/SOURCES.md`); analysis and manuscript scripts are in the public repository. | `data/SOURCES.md` updated to match Sage Vancouver reference formatting and to include CORONA and GISSI-HF RCT references. | **Fixed** |
| 4.2 | No hard-coded results | **High** | `validation/run_validation.py` previously contained hard-coded annual mortality rates (`obs_annual_rate = 0.15`, `rct_annual_rate = 0.08`) for the statins power illustration. | Removed hard-coded rates; statin control event rates are now computed directly from the aggregate event counts and sample sizes in `data/statins_hf_obs.csv` and `data/statins_hf_rct.csv`. The S3 enrichment scenario is also derived from these data. | **Fixed** |
| 4.3 | Build pipeline | Low | `make clinical_trials` reuses committed CCTC outputs and regenerates all Clinical Trials deliverables without re-running MCMC. | Verified end-to-end. README updated to list all generated files including `KOTHA_Framework_ClinicalTrials_supplementary_figures.pptx` and to note the `make all` / `make clinical_trials` distinction. | **Fixed** |
| 4.4 | Dependency on pandoc | Low | `generate_cct_docx.py` searches `~/.local/pandoc/bin/pandoc` and PATH, but a fresh clone may not have pandoc. | README already documents pandoc requirement with a download link. The current build environment includes pandoc, so the generated docx files are reproducible. | **Documented** |
| 4.5 | Clean-clone reproducibility | **High** | Required before submission per internal policy: public repo code + stated data alone must regenerate the manuscript. | Pushed to `bougtoir/wip` and synced to `bougtoir/kotha-rct-decomposition`; clean clone passed `make clinical_trials` and produced identical `05_paper_clinical_trials.md` and matching DOCX/PPTX textual content. | **Fixed** |

---

## 5. Journal guideline compliance

| # | Item | Severity | Finding | Proposed fix | Status |
|---|---|---|---|---|---|
| 5.1 | Main-text word count | **High** | Clinical Trials limit is ≤3,500 words excluding abstract/references/tables/figures. | Current `word_count` front matter = 2,687 words. Verified via `build_paper_clinical_trials.py` word-count logic. | **Compliant** |
| 5.2 | Abstract length | **High** | Structured abstract must be ≤425 words. | Abstract is 245 words. | **Compliant** |
| 5.3 | Running head | Medium | Running head must be ≤40 letter spaces. | Running head: "KOTHA Framework for Trial Design" = 32 letter spaces. | **Compliant** |
| 5.4 | Keywords count | Low | 3–10 keywords required. | Six keywords listed. | **Compliant** |
| 5.5 | References | **High** | Sage Vancouver style; numbered in order of appearance; ≤3 authors use "and", >3 use first 3 + ", et al."; journal abbreviations without terminal periods. | Reformatted `REFS` list in `build_paper_cct.py`; verified 31 references, no orphans/phantoms, citations unbracketed superscript. | **Fixed/verified** |
| 5.6 | Figure/table limit | **High** | ≤6 main tables/figures. | 4 figures + 2 tables = 6. | **Compliant** |
| 5.7 | Double spacing and font | Medium | Manuscript should be double-spaced Times New Roman 12 pt. | `generate_cct_docx.py` sets Normal style line spacing to 2.0 and font to Times New Roman 12 pt. | **Fixed** |
| 5.8 | Title page | Medium | Title page must include word count, authors, affiliations, corresponding author, grant support, and trial registration if applicable. | Generated title page includes word count, placeholders for authors/affiliations/corresponding author, and journal name. Grant support and COI left as `[To be determined]` because final author/funding/COI text is outside scope. | **Partial / placeholders** |
| 5.9 | Citation superscript format | Low | Word-native superscript should be used, not Unicode superscript. | `generate_cct_docx.py` applies font-based superscript and strips citation brackets. | **Fixed** |
| 5.10 | High-resolution artwork | Medium | Figures should be at least 300 dpi; 500 dpi preferred for line art. | `ClinicalTrials_figures/*.png` are generated at 500 dpi. | **Compliant** |

---

## 6. Strength of claims

| # | Item | Severity | Finding | Proposed fix | Status |
|---|---|---|---|---|---|
| 6.1 | Causal interpretation | Medium | As above, the manuscript risks implying that enrollment caused observed RCT null results. | Language consistently conditional: "can identify", "quantify", "inform", "diagnose structural information loss". | **Fixed** |
| 6.2 | Generalizability | Low | Two canonical retrospective cases; prospective validation acknowledged as future work. | No change beyond existing limitations. | **No change** |
| 6.3 | GRADE compatibility | Low | Module H maps to GRADE domains without altering GRADE structure. | Verified Table 1 mapping and wording. | **No change** |
| 6.4 | Trialist utility | Medium | The manuscript could more explicitly state how trialists use KOTHA outputs. | Added explicit design-decision language in abstract and cover letter: sample size, eligibility, enrichment, endpoint, and adaptive re-estimation. | **Fixed** |

---

## Summary

- **High-severity items fixed:**
  1. O'Brien-Fleming boundary capping and wording (boundary equals conventional two-sided threshold when cumulative information reaches OIS).
  2. Main-text figure/table count reduced to 6 by converting the abbreviations list from a table to bullets.
  3. Removed hard-coded statin event-rate assumptions from `validation/run_validation.py`; rates now derive from public data.
  4. Sage Vancouver reference formatting, citation order, and orphan/phantom reference check.
  5. Separate high-resolution figure files and a submission manuscript with placeholders + legends at end.

- **Medium-severity items fixed:**
  1. Title casing applied across manuscript and cover letter.
  2. Abstract and cover letter explicitly state the trial-design relevance of KOTHA.
  3. Softened novelty framing.
  4. Strengthened limitations around ecological bias, S3 enrichment threshold, and causal interpretation.
  5. Added editable supplementary figures PPTX.

- **Outstanding before final submission:**
  1. **Clean-clone reproducibility check** from `bougtoir/kotha-rct-decomposition` — completed after push; `make clinical_trials` regenerated identical `05_paper_clinical_trials.md` and matching DOCX/PPTX textual content.
  2. **Author/funding/COI placeholders** in title page and cover letter require final text from the authors.
  3. **Confirm** with the editorial office whether the abbreviations list as bullets is acceptable, or whether a numbered/lettered table would be preferred (and, if a table, which of the 6 main figure/table slots it would displace).

- **No fatal scientific, reproducibility, or journal-limit issue remains.**

---

## 7. Final verification (post-English edit and re-build)

After the final natural-English pass and regeneration (`make cctc` → `make clinical_trials`):

1. **Cross-references and numbering**: All main-text figures (Fig. 1–4) and tables (Table 1–2) are cited before first appearance and placed immediately after the citing paragraph. Supplementary items (Supplementary Tables S1–S4, Supplementary Figs. S1a/b, S2–S4) are also cited in sequential order.
2. **Citation order**: The 31 references are numbered consecutively by first appearance; no orphan or phantom citations; ranges are collapsed correctly.
3. **Word equations**: The generated docx files contain 46 `m:oMath` objects and zero raw `$...$` strings in `w:t` elements, confirming LaTeX inline math was converted to Word OMML.
4. **Double-byte characters**: `sanitize_office_outputs.py` was run on all docx/pptx deliverables; no CJK or full-width characters remain in `word/fontTable.xml`, `word/numbering.xml`, `ppt/theme/theme1.xml`, or `ppt/slideMasters/slideMaster1.xml`.
5. **Reproducibility**: All numbers derive from `validation/run_validation.py` and public CSVs in `data/`; no hard-coded estimates remain in the manuscript scripts.
6. **Intro–Results–Discussion alignment**: The three modules (K, T, H), the two illustrative cases, and the design-implications claims introduced in the Introduction are addressed in Methods/Results and collected in Discussion without overreaching.
7. **Old-version language**: No "previous analysis", "old version", or similar comparative language was found in `05_paper_clinical_trials.md`.
8. **English naturalness**: The abstract, results, and discussion were rewritten with active, precise phrasing; remaining conditional language ("consistent with", "inconclusive") matches the data.

Status: **Ready for submission pending final author/funding/COI text.**
