# KOTHA Framework — Session Handoff to Statistical Methods in Medical Research (SMMR)

## Decision

- **Next target journal**: *Statistical Methods in Medical Research* (Sage Publications)
- **IF**: ~1.6–1.9
- **APC**: ~$3,000 USD (Sage Choice hybrid OA; standard rate; exceptions possible)
- **Scope fit**: medical statistics methodology; methods motivated by real medical problems.

## What was completed in the previous session

- Reviewed BMC Medical Research Methodology rejection and Reviewer 1 / Reviewer 2 comments.
- Created `response_to_reviewers_BMC_MRM.md` with point-by-point responses and a summary of implemented changes.
- Updated `04_paper_rsm.md` (manuscript):
  - Tempered claims about observational-RCT discordance.
  - Added Module K ideal vs. realized counterfactual simulation note.
  - Added HR/PH assumptions and RMST alternative discussion.
  - Added empirical prior discussion in Module T.
  - Clarified α = 0 as a single-study/fixed-effect limiting case.
  - Added TSA futility boundary and reconciled fixed-effect vs. random-effects cumulative Z.
  - Changed statin interpretation to “inconclusive.”
  - Added Table 1 comparison and module prerequisites discussion.
  - Replaced validation language with “illustration.”
  - Renumbered references in Vancouver order (now 31 refs).
- Updated `validation/run_validation.py`:
  - Added fixed-effect and random-effects cumulative TSA functions.
  - Added futility-boundary logic.
  - Corrected Module H recommendation language.
  - Translated Figure 1 label from German to English.
  - Updated Figure 8 wording.
- Regenerated all figures and `results_summary.txt`.
- Generated `KOTHA_Framework_RSM.docx` and `KOTHA_Framework_RSM_figures.pptx`.
- Updated `journal_recommendation.md` with full candidate table (IF, APC, publisher, fit).
- Pushed to `bougtoir/wip` branch `devin/1774274321-rct-decomposition-paper` (PR #9).

## Key numerical results (verified)

- Magnesium pre-ISIS-4 random-effects OR = 0.54 (95% CI 0.40–0.75), I² = 6%.
- Magnesium all-trials random-effects OR = 0.56 (95% CI 0.38–0.83), I² = 62%.
- Fixed-effect cumulative TSA final Z = 0.80.
- Random-effects cumulative TSA final Z = -2.90.
- Statin observational random-effects HR = 0.72 (95% CI 0.64–0.80), I² = 82%.
- Statin RCT random-effects HR = 0.97 (95% CI 0.90–1.05), I² = 0%.
- Statin final TSA Z = -0.74 → interpreted as inconclusive.

## Files that matter for the SMMR submission

- `rct-decomposition/04_paper_rsm.md` — source manuscript
- `rct-decomposition/generate_rsm_docx_final.py` — docx generator
- `rct-decomposition/KOTHA_Framework_RSM.docx` — formatted manuscript
- `rct-decomposition/KOTHA_Framework_RSM_figures.pptx` — editable figures
- `rct-decomposition/validation/run_validation.py` — reproducible analysis code
- `rct-decomposition/validation/figures/*.png` — figure files
- `rct-decomposition/validation/results_summary.txt` — numerical summary
- `rct-decomposition/journal_recommendation.md` — full journal candidate comparison
- `rct-decomposition/response_to_reviewers_BMC_MRM.md` — rejection response for record

## Remaining work for the new session

1. **Verify SMMR Author Guidelines** at https://journals.sagepub.com/home/SMM
   - Check word limits, abstract format, reference style, figure/table limits, file formats.
2. **Draft a SMMR-specific cover letter** emphasizing medical-statistics relevance, counterfactual power simulation, and Bayesian integration with real examples.
3. **Align manuscript tone with SMMR**:
   - Ensure methods are framed as medical-statistical developments, not clinical recommendations.
   - Keep the statistical notation self-contained and avoid clinical guideline language.
   - Highlight that the two cases are illustrative, not clinical-practice-changing.
4. **Check citation style**: SMMR uses Vancouver with journal title abbreviations and standard numbering.
5. **Confirm public-repo reproducibility** before submission:
   - Clone `bougtoir/kotha-rct-decomposition` and run `run_validation.py`.
   - Regenerate docx/pptx from the public repo files.
   - Verify all numbers in `04_paper_rsm.md` match `results_summary.txt`.
6. **Optional / if time permits**:
   - Prepare a table of SMMR vs. Statistics in Medicine submission requirements.
   - Update Research Square preprint to v2 documenting the revisions.

## Important constraints from user knowledge notes

- All results must be reproducible from the public repo and the real data mentioned in the paper.
- Do not hard-code numerical results in the manuscript generator.
- Citations are already in Vancouver order; keep them in first-appearance order if references are added or reordered.
- Figures/tables are inline in the docx and also provided as editable pptx.
- Do not resubmit to BMC Medical Research Methodology, Journal of Clinical Epidemiology, or Research Synthesis Methods.

## Branch / PR status

- Working branch: `devin/1774274321-rct-decomposition-paper` in `bougtoir/wip`
- PR: `bougtoir/wip#9`
- Public mirror sync: `sync-to-repos.yml` maps this branch → `bougtoir/kotha-rct-decomposition`.
