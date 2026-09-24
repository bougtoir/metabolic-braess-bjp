# Phase 5 Report — Candidate refinement, classification, mechanisms

## Classification (src/classify.py, tol 1e-4)
Type II (NOPM): J(u*) > J(0) AND J(u*) > J(1) for interior u*.
Fine-grid (0.05) pilot: 13 combos; genome-wide coarse: 12 (human2) / 8 (recon3d).

## Mechanism 1 — efficiency NOPM (atp_per_glc, atp_per_carbon)
Response curves (GAPDH MAR04373, stage3 grid):
  u:        0     .25   .50   .75   .90   1.0
  ATP:      120   115   110   105   100.2 96.7
  glc in:   10    8.33  6.67  5.00  3.33  3.33
  ATP/glc:  12    13.8  16.5  21.0  30.05 29.0
Restricting mid-glycolysis throttles glucose UPTAKE ~2-3x faster than the
ATP rate falls: remaining glucose is oxidized more completely, so measured
stoichiometric yield rises toward complete-oxidation values (~30 ATP/glc).
The optimum is interior because at u=1 the residual pathway can no longer
sustain the same fully-oxidizing solution. Same signature in recon3d
(ENO/PGM/GAPD: 12.15 -> 31.5 at u*=.75).

## Mechanism 2 — parsimony NOPM (total_flux interior minima)
Partial restriction of PDH-complex members (DLAT MAR06412, DLD MAR06409,
PDH-E1 MAR08746/MAR20069, all u*=0.75-0.9), O2 transport (MAR04896, u*=.3),
complex I (MAR06921, u*=.15), TPI (MAR04391, u*=.7-.75): the pFBA
(min-|flux|) state minimizes total flux at interior u — the restriction
prunes a wasteful flux cycle before forced rerouting inflates |v| again.

## Negative controls
- test_negative_control_nested_sets: direct objective cannot rise (pass).
- All Type II hits verified J(u*) > J(1): full block damages — consistent
  with a genuine interior optimum, not a boundary artifact.
- No NOPM outside the energetic core in either model.
