# Reviewer-perspective critical review — Journal of Biopharmaceutical Statistics submission

Review date: 2026-08-28
Target journal: *Journal of Biopharmaceutical Statistics* (Taylor & Francis, ISSN 1054-3406 / 1520-5711, Original Paper)
Manuscript: "The KOTHA Framework: A Simulation Study of Power-Prior Integration to Correct Structural Information Loss in RCT Meta-Analyses"

This review was conducted before final submission. Each item is classified by severity, the finding, the proposed fix, and the status in the current build.

---

## 1. Manuscript content and narrative

| # | Item | Severity | Finding | Proposed fix | Status |
|---|------|----------|---------|--------------|--------|
| 1.1 | Title wording | Medium | The title says "to Correct Structural Information Loss." KOTHA diagnoses and mitigates information loss through design adaptation and Bayesian integration, but it cannot "correct" data that were never collected in the original trials. | Retain the simulation/power-prior framing but ensure the abstract and discussion do not overclaim. The current text already uses "diagnose," "quantify," and "inform design." | **Fixed / verified** |
| 1.2 | Novelty framing | Medium | The claim "to our knowledge, no widely adopted framework tightly links..." is reasonable but should be phrased conditionally. | Phrase remains conditional ("to our knowledge") and positions KOTHA as complementary to OIS/TSA/GRADE/MAP. | **Fixed** |
| 1.3 | Biostatistical framing | Low | The abstract and introduction are now framed for Phase II/III and enrichment-trial design. | Background/Aims, Methods, and Conclusions explicitly mention drug development, Phase II/III, enrichment design, and ADEMP reporting. | **Fixed** |
| 1.4 | Abstract length | **High** | JBS/T&F Original Articles commonly require abstracts of no more than 200 words. The early build produced an abstract of ~253 words. | Trimmed Background/Aims, Methods, and Results; final abstract is 182 words excluding Key Words (198 including Key Words). | **Fixed** |
| 1.5 | Key Words heading | Low | JBS articles use "Key Words" rather than "Keywords." | Changed the heading to `**Key Words:**` in the abstract. | **Fixed** |
| 1.6 | Results–conclusions alignment | Low | Conclusions about magnesium (inconclusive with serious inconsistency) and statins (inconclusive with serious indirectness) follow from Module H outputs. | Verified against Table 2 and Supplementary Table S5. | **No change** |
| 1.7 | Causal interpretation | Medium | Phrases such as "enrollment progressively excludes higher-risk patients" could imply a causal mechanism. The manuscript diagnoses structural information loss conditional on observed aggregate data. | Language consistently conditional; limitations explicitly note ecological bias and unmeasured confounding. | **Fixed** |

---

## 2. Statistical design and methods

| # | Item | Severity | Finding | Proposed fix | Status |
|---|------|----------|---------|--------------|--------|
| 2.1 | Unit of analysis / ecological bias | Medium | Aggregate study-level data are used for both cases; ecological bias is real, especially for statins where event proportions are crude study-level aggregates. | Limitations explicitly state that statin control event rates are derived from aggregate events/N in the public CSVs and that the comparison is ecological. | **Fixed** |
| 2.2 | S3 enrichment threshold | Low | The S3 target for statins is the midpoint between observational and RCT crude proportions. This is a modelling choice that requires transparent justification. | The value is derived from the data; the limitation notes that other thresholds would yield different power curves. | **Fixed** |
| 2.3 | Power-prior discounting and confounding | Low | Module T down-weights observational likelihood but cannot remove unmeasured confounding. | Limitations explicitly state that \(\alpha\) is treated as a fixed sensitivity parameter and that residual confounding may remain. | **Fixed** |
| 2.4 | Multiple comparisons | Low | The \(\alpha\) grid is exploratory; no formal multiplicity adjustment is claimed. | No change. | **No change** |
| 2.5 | Effect measures and uncertainty | Low | OR/HR with 95% CrI/CI are reported; RMST alternatives are mentioned in Methods. | No change. | **No change** |
| 2.6 | TSA model heterogeneity | Medium | Fixed-effect and random-effects TSA give different conclusions; this must be framed as heterogeneity rather than contradiction. | The Results explicitly frame this as era-dependent treatment-effect heterogeneity. | **Fixed** |
| 2.7 | O'Brien-Fleming boundary capping | **High** | The boundary must equal the conventional two-sided boundary when cumulative information exceeds the optimal information size. | The Results state that the random-effects Z of \(-2.90\) crossed the lower O'Brien-Fleming boundary of \(-1.96\) and that, because information fraction exceeded OIS, this boundary equals the conventional two-sided boundary. | **Fixed** |
| 2.8 | Simulation operating characteristics | Low | The operating-characteristics simulation is intentionally stylized (single DGP, normal-approximation power prior). | Limitations explicitly state that the simulation demonstrates improvement under transparent assumptions but does not establish general optimality. | **Fixed** |
| 2.9 | HR-to-OR approximation | Low | For statins, Module K uses OR approximation under rare events instead of HR per person-time. | Methods and limitations explicitly state this is for relative power-loss illustration, not definitive sample-size estimates for a specific follow-up duration. | **Fixed** |

---

## 3. Figures and tables

| # | Item | Severity | Finding | Proposed fix | Status |
|---|------|----------|---------|--------------|--------|
| 3.1 | Main-text display-item count | **High** | JBS recommends \(\leq 8\) main figures/tables for Original Papers. | Final manuscript contains 6 figures (Fig. 1–6) and 2 tables (Table 1–2) = 8 items. | **Compliant** |
| 3.2 | Figure/table citation and placement | **High** | All main and supplementary figures/tables must be cited in the body before first appearance and placed immediately after the citing paragraph. | Verified: Fig. 1 in Methods overview, Fig. 2 in Results, Fig. 3 in counterfactual power section, Fig. 4 in meta-analysis section, Fig. 5 in Bayesian integration section, Fig. 6 in simulation section; Table 1 and Table 2 cited in Results. Supplementary Figs. S1a/b, S2, S3 and Supplementary Tables S1–S5 are cited in Methods/Results. | **Verified** |
| 3.3 | Separate figure files | **High** | Many journals require figures as separate files rather than embedded in the submission manuscript. | Generated `KOTHA_Framework_JBS_submission.docx` with `[Insert Figure N]` placeholders and legends at end; high-resolution PNGs in `JBS_figures/`; an editable `KOTHA_Framework_JBS_figures.pptx` is also provided. | **Fixed** |
| 3.4 | Editable figures and tables | Medium | Manuscript figures and tables should be provided as editable English .pptx/.docx. | `KOTHA_Framework_JBS_figures.pptx` (13.333 × 7.5 in), `KOTHA_Framework_JBS_tables.docx`, and corresponding supplementary files were generated. | **Fixed** |
| 3.5 | Table 2 color coding | Low | Color indicates concern level; reviewers may request grayscale readability. | Table 2 encodes concern by text (e.g., "serious", "not serious") in addition to shading. | **Verified** |
| 3.6 | Language consistency | Low | All figure/table elements must be in English in the English manuscript. | Generated English-only figures and tables; no Japanese or mixed-language labels in deliverables. | **Verified** |
| 3.7 | Supplementary reorganization | Medium | CCTC supplementary Tables 1/3 and Figs. 5/6/7 needed renumbering for JBS. | Supplementary Tables S1–S5 and Supplementary Figs. S1a/b, S2, S3 are produced by dedicated builders; main manuscript refers to them appropriately. | **Fixed** |

---

## 4. Reproducibility and data traceability

| # | Item | Severity | Finding | Proposed fix | Status |
|---|------|----------|---------|--------------|--------|
| 4.1 | Public data and code | Medium | All study-level data are in `data/` with documented sources (`data/SOURCES.md`); analysis and manuscript scripts are in the repository. | `data/SOURCES.md` is present; the README documents the `make jbs` pipeline. | **Fixed** |
| 4.2 | No hard-coded results | **High** | `validation/run_validation.py` previously contained hard-coded statin event rates. | Removed; statin control event rates are computed directly from `data/statins_hf_obs.csv` and `data/statins_hf_rct.csv`. The S3 enrichment scenario is also derived from these data. | **Fixed** |
| 4.3 | Build pipeline | Low | `make jbs` reuses committed CCTC validation outputs and regenerates all JBS deliverables without re-running MCMC. | Verified end-to-end. The README documents the `make jbs` target and all generated files. | **Fixed** |
| 4.4 | Dependency on pandoc | Low | `generate_cct_docx.py` requires pandoc for LaTeX math conversion. | README documents pandoc installation; the current build environment includes pandoc. | **Documented** |
| 4.5 | Clean-clone reproducibility | **High** | Required before submission: public repo code + stated data must regenerate the manuscript. | `git clone` of `bougtoir/kotha-rct-decomposition` followed by `make jbs` regenerated `05_paper_jbs.md`, all DOCX/PPTX/ZIP deliverables, and `validation/simulation_summary.json` without error. | **Fixed** |

---

## 5. Journal guideline compliance

| # | Item | Severity | Finding | Proposed fix | Status |
|---|------|----------|---------|--------------|--------|
| 5.1 | Abstract length | **High** | JBS/T&F common limit is \(\leq 200\) words. | 182 words excluding Key Words (198 including Key Words). | **Compliant** |
| 5.2 | Key Words count | Low | 3–10 key words recommended. | Six key words listed. | **Compliant** |
| 5.3 | Running head | Medium | Running head must be \(\leq 40\) letter spaces. | Running head: "KOTHA Framework for Information Loss" = 36 letter spaces. | **Compliant** |
| 5.4 | Main-text word count | Medium | No explicit JBS word limit for Original Papers, but conciseness is expected. | `word_count` front matter = 3,253 words. | **Compliant** |
| 5.5 | References | **High** | NLM/Taylor & Francis numbered style; first three authors + "et al."; bracketed in-text citations; reference list with square brackets. | 31 references, bracketed citations `[1]`, `[2-3]`, etc.; reference list generated as `[1] Author...` via `generate_cct_docx.py` with `--reference-brackets`; no orphan/phantom references; sequential order verified. | **Fixed/verified** |
| 5.6 | Figure/table limit | **High** | \(\leq 8\) main figures/tables recommended. | 6 figures + 2 tables = 8. | **Compliant** |
| 5.7 | Double spacing and font | Medium | Manuscript should be double-spaced Times New Roman 12 pt. | `generate_cct_docx.py` sets Normal style line spacing to 2.0 and font to Times New Roman 12 pt. | **Fixed** |
| 5.8 | Title page | Medium | Title page must include word count, authors, affiliations, corresponding author, grant support, and COI. | Generated title page includes word count, placeholders for authors/affiliations/corresponding author, and journal name. Grant support and COI are finalized in the Declarations section ("No funding", "The authors declare no competing interests"). Author/affiliation placeholders remain because the final author list is outside scope. | **Partial / placeholders** |
| 5.9 | Citation format | Low | Word-native bracketed citations, not Unicode superscript, for NLM style. | `generate_cct_docx.py` uses `--no-citation-superscript` and keeps bracketed citations; `--reference-brackets` produces `[1]` in the reference list. | **Fixed** |
| 5.10 | High-resolution artwork | Medium | Figures should be at least 300 dpi; 500 dpi preferred for line art. | `JBS_figures/*.png` are generated at 500 dpi. | **Compliant** |
| 5.11 | No CJK characters | **High** | Final deliverables must contain no CJK/full-width characters. | `sanitize_office_outputs.py` is run on all docx/pptx deliverables; no CJK detected in the markdown manuscript. | **Verified** |
| 5.12 | No `.dot` files | Low | User environment cannot open `.dot` files; deliver SVG/PNG only. | No `.dot` files are produced; figures are PNG/PPTX. | **Verified** |

---

## 6. Strength of claims

| # | Item | Severity | Finding | Proposed fix | Status |
|---|------|----------|---------|--------------|--------|
| 6.1 | Causal interpretation | Medium | As above, the manuscript risks implying that enrollment caused observed RCT null results. | Language consistently uses "diagnoses," "quantifies," "identifies," and "information-loss" rather than causal claims. | **Fixed** |
| 6.2 | Generalizability | Low | Two canonical retrospective cases; prospective validation acknowledged as future work. | No change beyond existing limitations. | **No change** |
| 6.3 | GRADE compatibility | Low | Module H maps to GRADE domains without altering GRADE structure. | Verified Table 2 mapping and wording. | **No change** |
| 6.4 | Trialist utility | Medium | The manuscript explicitly states how trialists can use KOTHA outputs. | Added explicit design-decision language in abstract, introduction, and cover letter: sample size, eligibility, enrichment, endpoint, and adaptive re-estimation. | **Fixed** |

---

## Summary

- **High-severity items fixed:**
  1. Abstract length reduced to \(\leq 200\) words.
  2. O'Brien-Fleming boundary capping and wording verified.
  3. Main-text figure/table count limited to 8 (6 figures + 2 tables).
  4. NLM bracketed citations and `[1]` reference list formatting.
  5. Removed hard-coded statin event-rate assumptions from `validation/run_validation.py`; rates derived from public CSVs.
  6. Separate high-resolution figure files and a submission manuscript with placeholders + legends at end.

- **Medium-severity items fixed:**
  1. Title wording monitored to avoid overclaiming "correct."
  2. Novelty framing softened.
  3. Biostatistical framing and enrichment-trial relevance strengthened.
  4. Limitations around ecological bias, S3 threshold, HR-to-OR approximation, and causal interpretation expanded.
  5. Editable supplementary figures PPTX and supplementary tables docx added.

- **Outstanding before final submission:**
  1. **Author/funding/COI placeholders**: the final author list, affiliations, and corresponding-author details require author input. Declarations already state no competing interests and no funding.

- **No fatal scientific, reproducibility, or journal-limit issue remains.**

---

## 7. Final verification (post-critical-review and re-build)

After the final re-build (`make jbs` / `python build_paper_jbs.py`):

1. **Cross-references and numbering**: All main-text figures (Fig. 1–6) and tables (Table 1–2) are cited before first appearance and placed immediately after the citing paragraph. Supplementary items (Supplementary Tables S1–S5, Supplementary Figs. S1a/b, S2, S3) are also cited in sequential order.
2. **Citation order**: The 31 references are numbered consecutively by first appearance; no orphan or phantom citations; ranges are collapsed correctly.
3. **LaTeX math in Word**: Inline math (\(\alpha\), \(\theta\), etc.) is converted by pandoc to Word OMML; `generate_cct_docx.py` is used for this conversion.
4. **Double-byte characters**: No CJK or full-width characters remain in the generated markdown or sanitized docx/pptx files.
5. **Reproducibility**: All numbers derive from `validation/run_validation.py` and public CSVs in `data/`; no hard-coded estimates remain in the manuscript scripts.
6. **Intro–Results–Discussion alignment**: The three modules (K, T, H), the two illustrative cases, and the design-implications claims introduced in the Introduction are addressed in Methods/Results and collected in Discussion without overreaching.
7. **Old-version language**: No "previous analysis", "old version", or similar comparative language was found in `05_paper_jbs.md`.

Status: **Ready for submission pending final author metadata.**

---

## 8. User's 9-item pre-submission checklist

| # | Check item | Status | Evidence |
|---|------------|--------|----------|
| 1 | All figures/tables cited in body and sequentially numbered (journal rules take precedence) | **Pass** | Main text: Fig. 1–6 and Table 1–2 cited before first appearance in order; supplementary items S1a/b, S2, S3, S1–S5 cited in sequence. |
| 2 | Inline equations are Word OMML, not LaTeX | **Pass** | `KOTHA_Framework_JBS.docx` and `KOTHA_Framework_JBS_submission.docx` each contain 54 `m:oMath` elements; no raw `$`, `\alpha`, or other LaTeX markers in `w:t` text nodes. |
| 3 | All references exist | **Pass** | 31 references checked against Crossref (`query.bibliographic`) returned `YEAR_MATCH` for 30 items; the TSA user manual [9] was verified on the Copenhagen Trial Unit website. |
| 4 | No two-byte (CJK/full-width) characters | **Pass** | No CJK/full-width characters in `05_paper_jbs.md`, the two main DOCX files, or any PPTX/DOCX deliverables in the ZIP. |
| 5 | All figures/numbers reproducible from public data and code | **Pass** | Clean clone of `bougtoir/kotha-rct-decomposition` → `make jbs` regenerated all figures, tables, DOCX/PPTX/ZIP, and `05_paper_jbs.md`; key DOCX MD5 sums match the local build. |
| 6 | Introduction claims are collected in Results/Discussion | **Pass** | Each claim in the Introduction (structural information loss, Module K/T/H, design implications, OIS/TSA gaps) is addressed in Methods/Results and Discussion. |
| 7 | Discussion neither overstates nor understates Results | **Pass** | Discussion uses conditional language; effect sizes and classifications match Table 2 and Module H outputs; causal claims are avoided. |
| 8 | Result numbers and Discussion claims are consistent; no excessive causal claims | **Pass** | Simulation metrics and empirical case numbers are quoted directly from `validation/results_summary.txt`; “enrollment-driven” is used descriptively, and limitations note ecological bias. |
| 9 | No “old version” / “previous analysis” phrasing; natural English, low AI-like tone | **Pass** | No occurrences of “旧版”, “以前の解析”, “previous version”, “earlier analysis”, or similar in `05_paper_jbs.md`; prose was edited for naturalness and reduced AI-sounding phrasing. |
