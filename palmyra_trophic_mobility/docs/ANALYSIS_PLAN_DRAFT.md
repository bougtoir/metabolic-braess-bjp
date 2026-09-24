# ANALYSIS_PLAN_DRAFT — if a case study proceeds

Scope: event-based, exploratory. Language constrained to "compatible with",
"suggests", "preliminary", "event-associated redistribution".

## Design

1. **Events**: primary definition B_percentile (Δlog10 regional chl-a beyond
   5th/95th pctile, ≥ 7-day separation → 22 events); sensitivity definitions
   A/C/D reported alongside. Events defined from environmental data only.
2. **Response metrics** (per event × species, retaining n): centroid shift,
   Δradius-of-gyration, Δdistance-to-Palmyra, Δpath length; windows
   pre −7..−1 d, event 0..+2 d, post +3..+14 d. These windows are fixed a
   priori and not optimized.
3. **Advection control**: regress daily displacement vectors on co-located
   geostrophic u/v; report alignment and residual fraction per species.
4. **Model**: per-event slope of log10(response) vs mobility rank; pooled
   event-level OLS with event fixed effects. Individuals are the replication
   unit; report medians with n, never pooled raw fixes.
5. **Robustness**: leave-one-event-out (report slope range); temporal placebo
   (season-matched ±30–60 d dates, same pipeline); report fraction of placebo
   slopes ≥ observed.
6. **Reporting**: all figures/tables in `outputs/`; every estimate regenerable
   via `make all`; no fabricated data; flagged QC rows retained.

## Known limitations to disclose

- Contemporaneous multi-guild coverage effectively Jun–Nov 2022 (~10 events).
- Bird tags minutely vs fish tags ~12 h — temporal resolution asymmetry.
- chl-a cloud missingness ~67 %/day; Ekman currents unusable near equator.
- Small per-guild n (≤ 11 individuals/event-window).
- ~15-month record → single seasonal cycle; seasonality confounds partially
  addressed by placebo only.
