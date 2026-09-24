# Phase-9 bug-fix impact audit

Pre-fix tables preserved under results/tables/pre_fix/; post-fix pipeline is the sole source of final values.

## Bug-by-bug

| bug | pre | post |
|---|---|---|
| occupancy conflation (unsurveyed=absent) | 1.0 | 0.3833419555095706 |
| M1 vs M3 different eval samples | see pre_fix tables | see post tables |
| predicted redistribution ~1.0 from any continuous change | 1.0/0.8212521179502513 | 0.30770217251038967/0.26387747766252434 |
| cluster bootstrap lost route-draw multiplicities (isin) | CI width 0.233 (abundance, median) | CI width 0.329 (abundance, median); CI>0 count unchanged 40/41 |

## Inclusion audit

included: pre 124 -> post 116

Dropped species (present pre, absent post):

- 1200: nz_frac 0.233, routes 1267, reason: low_prevalence
- 2630: nz_frac 0.278, routes 1611, reason: low_prevalence
- 3430: nz_frac 0.206, routes 1361, reason: low_prevalence
- 3520: nz_frac 0.205, routes 1529, reason: low_prevalence
- 3640: nz_frac 0.274, routes 1211, reason: low_prevalence
- 3880: nz_frac 0.259, routes 1309, reason: low_prevalence
- 3900: nz_frac 0.252, routes 2778, reason: low_prevalence
- 6160: nz_frac 0.292, routes 1433, reason: low_prevalence

## HG post-fix (116 species)

- HG_A: median 0.2994, IQR [0.1938,0.3895], P>0 0.99
- HG_B: median 0.0245, IQR [0.0138,0.0420], P>0 0.97
- HG_C: median 0.3150, IQR [0.2041,0.4070], P>0 0.98
- HG_D: median 0.0059, IQR [0.0003,0.0139], P>0 0.77

## Common eval assertion

n_eval_M1 == n_eval_M3 == n_common_eval asserted per species (final_common_eval_assert.csv).

## Occupancy semantics

surveyed 71694 / total 176564 route-years; unsurveyed cells are NaN (never counted as absent).

## Matched-environment (post-fix)

occupancy prior-state median 0.000 (defined for 41/116 species); abundance prior-state median 0.629 (CI>0 in 40/41 defined, 34% of all).

## Conclusion diff

- **static persistence dominant?**: pre `A0.287->B0.024, C0.306->D0.006 (collapse)` -> post `A0.299->B0.024, C0.315->D0.006`
- **prospective HG exists (HG_D>0)?**: pre `median 0.0055, P>0 0.75` -> post `median 0.0059, P>0 0.77`
- **abundance prior-state effect**: pre `median 0.362, CI>0 0.73` -> post `median 0.629, CI>0 0.34`
- **occupancy hysteresis (matched env)**: pre `median 0.000` -> post `median 0.000`
- **redistribution lag / speed bias**: pre `env 1.000 hist 0.821` -> post `env 0.308 hist 0.264`
- **regional HG**: pre `0.271` -> post `-0.043`
- **final GO category**: pre `WEAK GO (Nature stopped)` -> post `WEAK GO (Nature stopped)`
