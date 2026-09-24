# Stage 1c — Locked Nemegt validation (preregistered, VALIDATION_HYPOTHESES.md v2)

Dataset: Nemegt Formation (Maastrichtian, Mongolia) via PBDB 1.2 API;
sha256 provenance in `metadata/sources.csv`. Dominant predator fixed
prospectively: *Tarbosaurus*. Primary metric: Jaccard; genus level;
collection-level assemblages; body fossils only (ootaxa and pure trace
records excluded from matrices, analysed separately as taphonomic data).

## Sample

- dinosaur occurrences (genus-resolved body fossils): 319 raw, matrices below
- herbivore: 8 genera in 30 collections
- predator: 26 genera in 78 collections

## Locked results

| quantity | value | 95% bootstrap CI |
|---|---|---|
| Δβ_full (Jaccard) | 0.094 | [-0.079, 0.300] |
| Δβ_{-Tarbosaurus} | 0.134 | [-0.062, 0.346] |
| A_D = Δβ_{-T} − Δβ_full | 0.040 | [-0.106, 0.159] |

Secondary metrics (not decision-relevant): Δβ_full Simpson
0.034, Sørensen 0.079;
Δβ_{-T} Simpson 0.161, Sørensen
0.147.

## Downsampling *Tarbosaurus* (999 stochastic replicates each)

| target                |   k |   delta_beta_mean |     lo95 |     hi95 |
|:----------------------|----:|------------------:|---------:|---------:|
| median_other_predator |   1 |          0.140259 | 0.133528 | 0.142671 |
| p75_other_predator    |   2 |          0.146456 | 0.133954 | 0.150985 |
| half_original         |  23 |          0.169945 | 0.162045 | 0.177386 |

## Bias controls

- Taxon-pool matched null: degenerate — herbivore γ (8
  genera) is smaller than predator γ (26), so the
  null collapses onto the observed value; asymmetry is reversed vs Morrison.
- Downsampling *Tarbosaurus* to the median/p75 of other-predator counts
  leaves Δβ **more positive** (removing the most widespread taxon raises
  apparent predator turnover, opposite sign to the Morrison effect).

## Taphonomic diagnostics (Tarbosaurus vs all other dinosaur records)

| field   |     chi2 |           p | tarbosaurus_top       |   tarb_share_top_cat | other_top             |   other_share_top_cat |
|:--------|---------:|------------:|:----------------------|---------------------:|:----------------------|----------------------:|
| env     | 14.8665  | 0.0377487   | terrestrial indet.    |             0.734694 | terrestrial indet.    |              0.444444 |
| lt1     |  5.17295 | 0.395141    | sandstone             |             0.653061 | sandstone             |              0.533333 |
| gsc     | 22.0248  | 1.64955e-05 | small collection      |             0.571429 | outcrop               |              0.755556 |
| cct     | 10.4343  | 0.0152136   | general faunal/floral |             0.571429 | general faunal/floral |              0.751852 |

Environment (chi² p=0.038):
Tarbosaurus records concentrate in 'terrestrial indet.' /
fluvial-associated settings more than other taxa; collection-type contrast is
significant for geographic scale (gsc p=0.000)
and collection kind (cct p=0.015).
Trace/egg records (independent taphonomic comparison) are dominated by
non-theropod taxa — consistent with the published footprint-vs-skeleton
bias — see `results/tables/nemegt_trace_records.csv`.

## Classification

**NO REPLICATION (D)**

Δβ_full = 0.094 with 95% CI
[-0.079, 0.300] — the
point estimate is **positive** and the interval crosses zero. Under the
frozen criteria the Morrison reverse signal does **not** replicate in the
Nemegt Formation. Per the preregistration, Hell Creek is not analysed.

## Interpretation (guarded)

- The Morrison Δβ < 0 pattern is not a generic cross-formation feature of
  dinosaur guilds; it remains best classified as Morrison-specific,
  Allosaurus-driven spatial continuity.
- Nemegt's herbivore guild is extremely depauperate in the PBDB record
  (8 genera / 30 collections),
  so herbivore turnover sits near its ceiling — a structural ceiling
  effect, not evidence that herbivores were genuinely more provincial.
- Spatial continuity ⇒ migration remains forbidden; nothing here supports
  or refutes movement mechanisms.
- Language: this result is "no replication", not "disproof" of any
  biological hypothesis — the Nemegt record is sparse and the test has low
  power in the positive direction only.
