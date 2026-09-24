# Analytic Multiverse Log — TOPP Task 5

| Choice | Frozen default | Variants tried | Result |
|---|---|---|---|
| Event onset series | daily UWI, ≥3 prior days below median | (7-day mean onset tested and rejected: never produces ≥3 sub-median days) | daily series required |
| Event separation | 7 d | 3 d / 14 d variants in ecomega analog; here 7d fixed, sensitivity flagged | 523 events |
| Event window | start..start+21d | sensitivity grid 6/12/24/48h × 5/10/20/50km | matched_unit_sensitivity.csv |
| Outcome | log1p(active displacement) = residual after vector advection | raw disp_km examined during QC | active_km primary |
| Prey proxy | SeaWiFS 8-d chl-a (INDIRECT) | none available direct | declared INDIRECT |
| Eligible species | ≥5 animals & ≥800 model days | all 12 kept in event-match tables | 4 species modeled |
| Lag for M_LAG / future prey | 7d back / 8d ahead | lag profiles ±14d estimated, no p-value lag selection | lag_results.csv |
| CV unit | event_id grouped folds; animal-grouped fallback when <3 events | both logged in outputs | event_holdout_results.csv, future_prey_prediction.csv |
| C(month) seasonality | kept in-sample; dropped in CV because held-out events can have unseen months | both variants logged | scripts 04 |
| Classification | CV + in-sample + proxy-quality rules; never p-value alone | — | species_tracking_mode.csv |

Label: PRIMARY = model_comparison, event_holdout, lag, reverse-time,
placebo, LOEO, species_tracking_mode tables. SENSITIVITY = matched-unit
grid, mobility merges. EXPLORATORY = none beyond listed.
