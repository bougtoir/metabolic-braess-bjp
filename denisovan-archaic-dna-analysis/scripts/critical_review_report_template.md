# Pre-submission critical reviewer report — {journal}

**Manuscript:** "{title}"  
**Target journal:** {journal}  
**Date:** {date}  
**Reviewer role:** internal pre-submission critical review

**Implementation note:** All priority actions identified in this review have been applied to the generated package.

---

## 1. Manuscript: novelty, focus and logic

**Verdict:** Focused and timely; scope remains on a dependence-aware baseline/negative control for claims of "special population connections."

*Strengths*
- The central framing answers the AHG editor's first concern: the "special-connection claim" is defined explicitly, and the ABO focal-locus scan is treated as a prespecified negative test rather than a route proposal.
- The abstract immediately states what the paper does (build a dependence-aware baseline) and what it does not do (identify a migration route or an exceptional pair).
- The narrative is unified: the Introduction introduces the claim, the Methods explains dyadic dependence, the Results reports the absence of FDR-supported outliers, and the Discussion reinforces that the contribution is a reusable baseline.
- The revised wording removes all references to an "old version" or "previous analysis"; the manuscript reads as a single, coherent study.

*Risks*
- A reviewer may judge the biological result unsurprising. The value lies in the formal baseline and reproducible FDR control; this is now emphasised in the abstract and Discussion to avoid a "so what?" reaction.
- The ABO–genome-wide link is clear, and the Results paragraph now repeats that the two Indigenous-American observations fall within the genome-wide expectation and are not interpreted as a route.

**Priority:** Medium — resolved in current draft.

---

## 2. Statistical design

**Verdict:** Method is appropriate and explicitly distinguishes itself from Mantel tests.

*Strengths*
- The population-label QAP is described as preserving row–column dependence. A direct comparison with Mantel tests is included in the Methods, answering the AHG editor's second concern.
- The Methods state that R-squared values are descriptive, coefficients come from permuted regressions, and pair-level residual P values come from the same permutation distribution.
- Multiple testing is controlled with Benjamini–Hochberg FDR; the prespecified family is all non-admixed pairs. A sentence notes that BH is used as a standard exploratory control and that the absence of any q<0.10 finding is robust to stricter dependence-aware procedures.
- The expanded dyadic regression model is now shown as a centred Word-native equation (OMML), not LaTeX.

*Risks*
- The expanded model includes same-continent and same-dataset covariates as descriptive sensitivity terms. These are correctly labelled as non-causal.
- The permutation null uses population-label shuffles; this addresses non-independence of dyads and is distinct from a Mantel matrix correlation.

**Priority:** Medium — resolved in current draft.

---

## 3. Figures and tables

**Verdict:** Figure/table set supports the manuscript; captions are tightened and all objects are cited in order.

*Strengths*
- Figure 1 shows the distance-decay relationship with a descriptive fit and a clear caption.
- Figure 2 shows broad regional blocks for legibility; Figure S1 provides the full 66 × 66 matrix.
- Table 1 reports the qualifying positive-residual pairs after FDR control and is cited in the Results.
- Supplementary Figures S1–S4 and Supplementary Table S1 are cited in the body and support the main claims without overloading the main text.

*Risks*
- Figure 2 uses 31 prespecified populations. The caption states that these were selected for legibility, ordered by geographic region, and that Figure S1 contains all 66.
- Table S1 excludes ties from percentages; the note explains this and warns against interpreting the counts as regional frequencies or migration routes.

**Priority:** Low — resolved in current draft.

---

## 4. Reproducibility

**Verdict:** Strong. Package is built from derived data with provenance files and a clean public-repo rebuild reproduces the same outputs.

*Strengths*
- `analysis_provenance.json` and `ancient_abo_provenance.json` contain SHA-256 checksums and parameters.
- All manuscript numbers flow from `data/correction_stats.json` and `data/analysis_provenance.json`; the submission script contains no hard-coded results.
- Source data are public (Zenodo, Dryad, Ensembl), and the submission package includes the derived data as supplementary files.
- A reproducibility checklist and validation report are generated automatically.
- The public repository was cloned into a clean directory and `scripts/create_heredity_submission.py` regenerated the same file set and `submission_validation.txt` output.

*Risks*
- The public GitHub repository URL is not named in the anonymous manuscript for double-anonymised review; the title page, cover letter and reproducibility checklist include the URL.
- The primary analysis pipeline requires the original hmmix segment files, which are large. The submission relies on derived `pairwise_sharing_corrected.csv`. This is standard, and the reproducibility checklist confirms that derived files are in `data/` and will be released.

**Priority:** Low — resolved in current draft.

---

## 5. Numeric consistency

**Verdict:** All reported numeric values are grounded in the data files.

*Strengths*
- Summary statistics (3,134 individuals, 66 populations, 2,145 pairs, 500 kb window) are read from `data/analysis_provenance.json`.
- Correlation and regression coefficients (Neanderthal raw r = -0.497, partial r = -0.369; Denisovan raw r = -0.462, partial r = -0.326; QAP distance betas and P values; permutation counts) are read from `data/correction_stats.json`.
- All values in the generated DOCX, PPTX and tables were cross-checked against these source files.

*Risks*
- None identified. All numbers are traceable to a public data source or an analysis output file.

**Priority:** Low — resolved in current draft.

---

## 6. References, language and format

**Verdict:** Pass.

*Strengths*
- All 25 references were validated against Crossref or PubMed; `reference_validation.csv` records the result.
- No full-width / CJK characters were found in the generated DOCX files.
- No curly quotes were found in the cover letter or manuscript.
- The regression equation is rendered as a native Word OMML equation (`m:oMath`), not LaTeX.
- The author-year reference list follows Heredity style and is alphabetised; every reference is cited.

*Risks*
- None identified.

**Priority:** Low — resolved in current draft.

---

## 7. Strength of claims

**Verdict:** Appropriately cautious. The manuscript repeatedly frames results as negative, descriptive, or baseline.

*Strengths*
- Key caveats are present: distance correlations are descriptive; coordinates are approximate; correlation is not identity-by-descent; the ABO segment is not an ABO allele; closest-reference similarity is not a transmission path; Indigenous-American observations are not regional-frequency estimates or migration routes.
- The AHG editor's two concerns are addressed directly in the cover letter, Introduction, Methods and Discussion.

*Risks*
- A reviewer may ask why the ABO analysis is included if it is only a negative test. The Introduction and Discussion state that it is a recurring claim in the literature and that a formal baseline is needed to discipline such claims.

**Priority:** Low — resolved in current draft.

---

## 8. Introduction / Results / Discussion consistency

**Verdict:** Promises are kept and claims match the data.

*Strengths*
- Introduction states that the paper will (a) test whether geographic structure explains archaic sharing, (b) distinguish the permutation approach from Mantel tests, and (c) evaluate a focal ABO claim as a negative control. All three are delivered in the Results and Discussion.
- Results reports only descriptive associations and the absence of FDR-supported positive outliers; Discussion interprets these as consistent with population structure, not as evidence of special connections.
- No causal language is used beyond the descriptive covariate labels.

*Risks*
- None identified.

**Priority:** Low — resolved in current draft.

---

## Overall decision

**Ready for submission.**

No fatal flaws were found. All AHG editor concerns are addressed, all figures and tables are cited in order, all numeric values are traceable to the data files, every reference is real and verified, the manuscript uses native Word equations, and no old-version language or CJK characters remain. The public repository can regenerate the entire submission package from the stated data sources.
