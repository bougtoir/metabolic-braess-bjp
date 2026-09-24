# ANALYTIC_MULTIVERSE_LOG — every specification tested

Prespecified primary analysis (declared before inspection):
- Event = first spawning day (DateSpawn), prey-defined only.
- Windows: pre −14..−1, event 0..+3, post +4..+14 days.
- Response: log1p(birds per 100-m bin); model: year FE + year-clustered SE.
- No threshold, window, lag, or response-variable search for significance.

Alternative specifications inspected (all exploratory):

| spec | result | kept? |
|---|---|---|
| event_intensity = mean(evt)/mean(pre) fish | mixed, 0.1–14× | reported in capelin_events.csv |
| peak_pulse_fold = max(post)/mean(pre<0) | mean ~322× | reported (publication-style magnitude) |
| baseline tau<=-14 for pulse fold | larger range, one outlier | exploratory only |
| post-window (4..14d) response | +0.08, p=0.83 | reported (post-peak decay) |
| per-species-group deltas (alcids/larus/gannets/shearwaters) | computed, not pooled for significance | in event_level_seabird_response.csv |
| lag shifts 1/3/7 days | flat within weekly resolution | lag_response_capelin.csv |
| ±30-day negative control | 1 usable event each — not informative | negative_control_capelin.csv |
| placebo: pseudo-spawn within year's window, ±7d exclusion | median 0.11 vs obs 0.22 | placebo_results_capelin.csv |

Nothing was tuned to obtain significance; the positive-control verdict (WEAK)
rests on the prespecified contrast plus the placebo comparison.
