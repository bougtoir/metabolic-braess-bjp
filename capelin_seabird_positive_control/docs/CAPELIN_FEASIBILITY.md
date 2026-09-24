# CAPELIN_FEASIBILITY — positive-control assessment

**Classification: WEAK POSITIVE CONTROL.**

## Event inventory

- Events defined from prey data only: first day of capelin spawning
  (`DateSpawn`, ordinal) per year — 10 years, one pulse/year.
- n_raw_observations = 62 surveys; n_years = 10; n_independent_events = 10.
- Usable events (≥1 survey in pre AND event window): 8 years
  (2015/2020 lack event-window surveys; 2016 lacks event+post).
- n_events_with_complete_predator_data (pre+event+post all present): 5
  (2009, 2010, 2012, 2014, 2017).

## Observed event effect

- Primary contrast (prespecified): event window 0..+3 d vs pre −14..−1 d,
  Y = log1p(birds per 100-m bin).
- Year-FE model, year-clustered SE: **evt coef = +0.92 log units, p = 0.03**
  (n=27 windowed surveys). Post-window (+4..+14 d) coefficient ≈ +0.08,
  p = 0.83 — consistent with the published "peak at onset, then decay".
- Per-year deltas positive in 7/8 usable years (median +0.22 log units).

## Placebo comparison

- Pseudo-spawn dates within each year's surveyed window, excluding ±7 d
  around the true onset: placebo median delta +0.11; observed median +0.22;
  fraction of valid placebos ≥ observed = **0.45** (empirical two-sided
  p ≈ 0.90). The event-level median does NOT clearly exceed the placebo
  distribution — driven by extremely coarse weekly sampling, which makes
  individual placebo deltas noisy.
- The pooled model (p=0.03) is significant, but the simple per-event median
  is not distinguishable from placebo — honest divergence between the two
  summaries.

## Negative control

±30-day shifts leave only 1 usable event each — seasonal window too narrow.
Reported but not informative.

## Leave-one-event-out

Coefficients 0.69–1.09, all positive, zero sign reversals; largest p = 0.12
(dropping 2010). No single event dominates.

## Lag structure

0/1/3/7-day shifts of the event window: medians 0.22/0.13/0.57/0.46 — flat
within weekly resolution; timing cannot be resolved below ~7 days.
Recorded as a limitation, not tuned.

## Spatial coupling

Not feasible: all data are from one ~10 km² area; no within-study spatial
coordinates. Documented in `outputs/figures/spatial_coupling_example.png`.

## Why WEAK, not STRONG

The published effect is directionally reproduced and the pooled event contrast
is significant and LOEO-stable, but the strongest "clearly exceeds placebo"
criterion fails at the event-median level (0.45 exceedance) and several years
have ≤1 usable survey per window. Not FAILED: effect is present, positive,
directionally stable across years.

## Strongest validity threat

Sparse, coarse weekly sampling around the event window — a few surveys per
year carry the whole estimate, and response variable choice (birds per bin)
mixes aggregation with abundance.
