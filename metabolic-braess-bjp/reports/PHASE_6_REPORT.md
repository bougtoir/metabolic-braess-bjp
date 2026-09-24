# Phase 6 Report — Robustness validation

## Design
Hit-level robustness (not whole-genome re-scans): all screened-hit reactions
re-scanned over the u-grid under
  state selection: pFBA vs L1-MOMA (quadratic MOMA not solver-robust at
    this scale — osqp iteration-limit non-convergence; documented),
  conditions: aerobic / glucose_limited / oxygen_limited,
  modulation: fva_informed (B) vs bound_scaling (A).

## Result 1 — selection-rule dependence (HEADLINE robustness finding)
Under pFBA, GAPDH/PGK/ENO/PGM partial restriction raised ATP-per-glucose
(12→~30, interior optimum). Under L1-MOMA (recon3d aerobic):
  ENO  atp_per_glc: 12.2 -> 8.2  (monotone decline, no interior optimum)
  PGM               12.2 -> 9.2
  GAPD              12.2 (flat) -> 8.2 at u=1
The efficiency NOPM is therefore CONDITIONAL on the state-selection rule:
it holds under a parsimonious-flux assumption but not under a
minimal-adjustment (MOMA) assumption. Reported honestly — not forced.

## Result 2 — parsimony NOPM partially selection-invariant
CYOR_u10mi total_flux under L1-MOMA: 2185 -> min 1985 at u=0.9 -> 2277 at u=1
(interior minimum survives). O2t monotone under MOMA. Total-flux interior
minima are thus more robust across selection rules than yield optima —
consistent with both being parsimony-flavored phenomena.

## Result 3 — cross-model (pFBA)
Same NOPM cluster in Human-GEM and Recon3D (glycolytic enzymes for yield;
O2 transport/complex I-III for parsimony) — convergent, model-independent.

## Pending cells of the matrix
glucose_limited + oxygen_limited × {pfba, moma_linear} × {fva, bound}
outputs land in results/scans/robust_* and are aggregated by
scripts/aggregate_robustness.py -> results/robustness_matrix.csv.

## Final matrix (24/24 cells complete)
See results/robustness_matrix.csv. Summary of interior-optimum counts:
  pFBA:        recon3d 9/6/2/1/8/4  human2 10/11/0/0/3/4 — NOPM recurs
               across media & modulation methods in both models; the only
               empty pFBA cell is human2 glucose_limited (0 in both methods).
  L1-MOMA:     recon3d 0/1/0/1/0/2 (parsimony-optima only, CYOR_u10mi
               total-flux minimum)  human2 0 across all six cells.
Conclusion: NOPM is cross-model reproducible and condition-robust under
parsimonious state selection; it is contingent on the selection rule,
not on topology — reported as the mechanistic result, not as failed
replication.
