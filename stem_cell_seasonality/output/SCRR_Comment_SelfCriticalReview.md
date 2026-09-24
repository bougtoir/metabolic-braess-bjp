# Pre-submission self-critical review — Comment version

**Manuscript:** *The Invisible Variables: Why Clonal Systems Are Not Immune to Environmental Confounding*  
**Target journal / form:** *Stem Cell Reviews and Reports*, Comment (≤1,500 words, 1 figure, ≤5 references, no abstract)  
**Review date:** 2026-08-22

## Overall assessment

The manuscript now meets the Comment format: 919 main-body words and 1,204 total words including the figure legend, declarations, and reference list; one inline figure with three panels; five Vancouver-numbered references; and no abstract. The figure order is A (variance components), B (public-data natural experiment), C (schematic temporal drift), so the empirical evidence appears before the conceptual forward projection. The central proposition — *clonality removes genetic variance, not environmental variance* — is carried through a straight-line argument: clonal uniformity → environmental sensitivity → unmeasured environmental variance → reproducibility problem → continuous environmental metadata.

The reference distribution follows the recommended balance: three sources rooted in pluripotent/stem-cell biology (iPSC reproducibility, mechano-osmotic iPSC sensitivity, PM2.5 effects on hESC pluripotency), one IVF proof-of-concept for continuous environmental monitoring, and one archive source for the GEO metadata screen. No empirical numbers are hard-coded; all GEO-derived values are computed from `output/geo_psc_metadata.csv` and `output/geo_country_full.csv`.

## Checklist results

| Item | Status | Notes |
|---|---|---|
| Figures/tables cited in order | PASS | One figure (Figure 1) is first cited in Section 3 and inserted immediately after that paragraph; no tables. |
| LaTeX math | PASS | No `$` or `\` markup in the manuscript DOCX. |
| References real | PASS | 5/5 verified against Crossref (0 warning, 0 critical). |
| Full-width/2-byte characters | PASS | No two-byte characters in visible text or OOXML theme/fontTable XML of any DOCX/PPTX. |
| Public reproducibility | PASS | A clean clone of `bougtoir/stem-cell-seasonality` regenerates identical summaries and figures from public GEO metadata. |
| Intro → later sections | PASS | The four opening ideas (clonal complacency, PSC environmental sensitivity, GEO limits, monitoring need) are picked up in Sections 2–4. |
| Discussion vs results balance | PASS | GEO findings are descriptive and exploratory; the path-forward section does not claim causal effects beyond the cited literature. |
| No old-version language | PASS | No "旧版", "previous analysis", "old version", or similar wording. |
| Natural English / AI-like phrasing | PASS | Revised to avoid stilted constructions; the final paragraph ties measurement directly back to the clonal complacency trap. |

## Reviewer-perspective improvements implemented in this round

1. **Three-panel Figure 1 with a GEO natural-experiment panel (B)** — Replaced the two-panel conceptual figure with a 1×3 layout. Panel A shows variance components, panel B uses public GEO metadata to show monthly PSC Series release proportions by academic-year start group, and panel C schematically illustrates unmonitored environmental drift. The empirical evidence (B) now appears before the conceptual forward projection (C), and no new reference was needed (NCBI GEO is already reference 5).

2. **Figure placement and citation order** — Figure 1 is first mentioned in Section 3 and inserted immediately after the paragraph describing the GEO analysis, so all in-text references precede the figure and its caption.

3. **Tighter interpretation of GEO results** — The Japan/Korea group shows a significant March peak, but the larger September-start group and the small Southern Hemisphere group do not show clear seasonality. Wording was softened from "rather than in a hemisphere-inverted season" to "consistent with institutional rather than hemisphere-inverted biological timing, although the deviation from uniformity was not significant," avoiding over-interpretation of non-significant p-values.

4. **Reduced unsupported regulatory claims** — The clinical-transition paragraph no longer names specific frameworks (QbD/PAT) without citations. It now states generally that manufacturing guidelines treat environmental parameters as process variables that should be logged.

5. **Figure readability** — Panel B y-axis was relabeled "Outcome deviation" (from "Differentiation efficiency") so that negative schematic values are not biologically implausible.

6. **Caption/superscript consistency** — PPTX figure caption mirrors the manuscript caption, and both use font-based superscripts for the NCBI GEO citation.

7. **CJK/full-width sanitization** — OOXML sanitizer is applied to DOCX and PPTX outputs, ensuring no full-width bytes remain in the submission files.

8. **Explicit homogeneity caveat** — Added a sentence noting that many published protocols still assume environmental homogeneity while the cited evidence suggests that assumption is frequently violated, reinforcing the "clonal complacency trap" message.

9. **Figure 1B/C distinction** — Panel B is the empirical natural experiment: monthly GEO Series release proportions by academic-year start group. Panel C is a schematic of plausible unmonitored environmental drift, not an empirical environmental time series, because GEO metadata do not contain laboratory sensor data.

## Residual author-side items

- Replace `1[Affiliation to be added]` with the real affiliation before submission.
- Confirm the Funding statement is correct (currently "This work received no specific funding.").
- Select **Comment** as the article type in the Springer Nature submission system.
