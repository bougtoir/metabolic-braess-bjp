# Phase 3 Report — Central-carbon pilot

## Setup
- Model: Human-GEM (human2), aerobic minimal medium, pFBA state selection,
  fva_informed (Method B) modulation, coarse grid {0,.1,.25,.5,.75,.9,1},
  then fine grid 0.05 on all responders.
- Candidate reactions = the 39 non-boundary reactions carrying flux
  (|v|>1e-6) in the baseline pFBA state (glycolysis, PDH, TCA, ETC, ATP
  turnover, exchange-linked transports).

## Response landscape (coarse grid)
- Mid/lower glycolysis (ENO MAR04363, PGM MAR04365, PGK MAR04368,
  GAPDH MAR04373): atp_per_glc rises from 12 toward ~30 while ATP rate
  falls — partial restriction REDUCES glucose uptake proportionally more
  than ATP output, so measured per-glucose yield improves (the cell burns
  less glucose per ATP it still produces).
- Complex IV (MAR06914): graded Warburg switch — ATP 120→20,
  lactate 0→20 mmol/glc-6 as u→1.
- O2 transport MAR04896: non-monotone lactate peak at u=0.5.

## NOPM (Type II) hits — fine grid (class_fine_pilot.csv, 13 combos / 10 reactions)
- **Efficiency metrics (atp_per_glc, atp_per_carbon)**:
  - MAR04368 PGK: u*=0.75, J 12.0→21.0 (atp_per_glc); 2.0→3.5 (per-carbon)
  - MAR04373 GAPDH: u*=0.85, J 12.0→30.6 (atp_per_glc); 2.0→5.10 (per-carbon)
- **Total-flux interior minima** (u* where |v|_sum is minimized):
  - MAR04896 O2 transport (u*=0.30), MAR06916 ATP phosphohydrolase (0.15),
    MAR06921 NADH:ubiquinone oxidoreductase / complex I (0.15),
    MAR04391 TPI (0.70), MAR06409 DLD (0.80),
    MAR06412 DLAT / MAR08746 PDH-E1 / MAR20069 (0.85),
    MAR04373 GAPDH (0.85).

## Interpretation (preliminary)
- Two distinct NOPM classes emerge: (i) *efficiency* interior optima —
  partial inhibition of upper/mid glycolysis suppresses total ATP output
  less than glucose flux, improving stoichiometric yield; (ii) *parsimony*
  interior minima — total |flux| minimized at nonzero restriction before
  forced rerouting raises it again.
- Control checks: negative control passes (direct objective cannot rise);
  u=1 full block lowers atp_demand for all glycolytic hits (monotone damage
  at full inhibition is required for a genuine interior optimum).
