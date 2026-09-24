# Transition handoff: CCT → Contemporary Clinical Trials Communications (CCTC)

## Decision
- **Original target**: Contemporary Clinical Trials (CCT)
- **Outcome**: Desk reject with transfer offer
- **New target**: Contemporary Clinical Trials Communications (CCTC)
- **Rationale**: Open-access companion to CCT; scope explicitly covers clinical-trial design, analysis, methodology, and evidence synthesis; not disease-specific.

## Current deliverables (generated for CCT, mostly reusable)
- `KOTHA_Framework_CCT.docx` — main manuscript with Word-native OMML equations
  - Main text: ~2,107 words
  - Total: ~3,539 words
  - 8 figures, 7 tables, 29 references
  - `word/document.xml` contains 43 `<m:oMath>` and 2 `<m:oMathPara>` elements; no raw `$` remain
- `KOTHA_Framework_CCT_figures.pptx` — editable English figure deck (1 slide/figure)
- `KOTHA_Framework_CCT_tables.docx` — editable tables with OMML equations preserved
- `cover_letter_CCT.docx` — cover letter drafted for CCT; must be retargeted to CCTC
- `submission_package_CCT.zip` — reproducibility package (code, data, docx, figures)
- `researchsquare_upload.zip` — ResearchSquare upload package
- `ADEMP_checklist_KOTHA.docx` — ADEMP reporting checklist

## Items that must be checked/updated for CCTC
1. **Author guidelines** for CCTC
   - Article types and word limits
   - Abstract structure and word limit
   - Figure/table limits and accepted file formats
   - Reference style (likely Vancouver)
   - Open-access APC confirmation
2. **Cover letter**
   - Retarget to CCTC Editor-in-Chief (verify current name)
   - Emphasize trial-design methodology and transparency angle
3. **Title page / manuscript**
   - Confirm running head and article type
   - Insert final author list, affiliations, and corresponding author
   - Update "Prepared for submission to ..." line
4. **Abstract**
   - The 250-word version shared in chat should replace the current abstract
   - Verify it fits CCTC abstract limits
5. **Highlights / CRediT / Data availability / Ethics statements**
   - Add any CCTC-specific required files
6. **Figures**
   - Verify resolution and format requirements
   - Ensure all figures are cited and appear in correct order
7. **References**
   - Re-verify all 29 references are real and cited in order
8. **ResearchSquare**
   - If a v2 was uploaded to CCT, re-upload for CCTC (or use Editorial Manager if CCTC uses it)

## Reproducibility
- All outputs are reproduced by `make cct` from the `devin/1774274321-rct-decomposition-paper` branch.
- `generate_cct_docx.py` now depends on pandoc (`~/.local/pandoc/bin/pandoc` or PATH).
- Public mirror: `bougtoir/kotha-rct-decomposition` branch `devin/1774274321-rct-decomposition-paper`
- WIP repo: `bougtoir/wip` branch `devin/1774274321-rct-decomposition-paper`

## TBD before submission
- Author names, affiliations, corresponding author, ORCID
- Funding statement
- Competing interests / COI statement
- Acknowledgements

## Next steps for the new session
1. Read CCTC Guide for Authors and confirm article type/word limits.
2. Update `cover_letter_CCT.docx` → `cover_letter_CCTC.docx`.
3. Update title page metadata in `05_paper_cct.md` and regenerate docx/zip.
4. Replace abstract with the 250-word version if not already updated in files.
5. Produce final CCTC submission package.
