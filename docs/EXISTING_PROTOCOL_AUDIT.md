# Existing Protocol Audit (Phase 1)

Audit of the three ecological systems that already exist in this repository,
prior to refactoring them onto a shared Core Protocol. No code was altered for
this audit. Each system is described by what it actually does today, not by
what the shared protocol will require.

## Systems inventoried

| System | Directory | Status in repo | Observation class |
|---|---|---|---|
| Dinosaur (Late Jurassic + validation) | `dinosaur_migration_foodweb/` | Stage 1/1b/1c complete, merged into this branch | Fossil occurrences (PBDB-derived) |
| Modern terrestrial | `phase8b/`, `phase9/`, synthesis in `geb/` | Phases 8B/9 complete; manuscript architecture drafted | Repeat-survey panel (BBS routes + telemetry + NEON/FOSS) |
| Modern marine | `marine_dataset_screen/`, `palmyra_trophic_mobility/`, `ecomega_trophic_propagation/`, `topp_tracking_modes/`, `capelin_seabird_positive_control/` | Dataset screen + feasibility audits + one mechanism verdict (ecomega); still under active development in the parallel "海洋生物回遊" session | Telemetry / matched survey transects |

Not yet present in the repository: `cenozoic_mammals` (built in this branch),
`quaternary` and `ancient_marine` (being built in parallel sessions; their
adapter specs are written here but their pipelines are out of scope for this
branch).

## 1. Dinosaur system (`dinosaur_migration_foodweb/`)

**Data source.** Maidment et al. 2024 Morrison Formation occurrence package
(Dryad `10.5061/dryad.6m905qg77`, PBDB-derived): 651 dinosaur occurrences,
239 collections, 38 genera (26 herbivore / 12 predator). Independent
validation set: Nemegt Formation (Maastrichtian, Mongolia) fetched live from
the PBDB 1.2 API (`src/download/fetch_pbdb_nemegt.py`).

**Trophic contrast.** Guild assigned from the PBDB `class` field:
Sauropoda + Ornithischia → herbivore; Theropoda → predator.

**Primary endpoint.** `Δβ(d) = β_predator(d) − β_herbivore(d)` with Simpson
turnover (primary) and Sorensen (sensitivity) on genus-incidence matrices per
collection; spatial unit = collection; distance = great-circle km between
collection centroids; distance bins = 100 km.

**Uncertainty & nulls.** Collection bootstrap (rows resampled with
replacement, n=999) for CIs on mean pairwise β and Δβ; Mantel test
(Spearman, 9999 permutations) per guild for distance decay.

**Sampling corrections.** (A) raw, (B) dominant-quarry exclusion (>p95
occurrences per collection), (C) singleton exclusion (<2 sampled genera),
(D) equalized collection counts between guilds (999 reps), (E) 1° spatial
thinning (999 reps). See `analysis/06_sampling_bias.py`.

**Results (frozen).** Stage 1a confirmatory H1 (`β_predator > β_herbivore`)
falsified: Δβ_Simpson = −0.543, 95% CI [−0.623, −0.452], P(Δ>0)=0; Mantel r≈0
both guilds. Stage 1b exploratory reverse-signal characterization
(`results/stage1b_*` tables: taxon-pool null, frequency-matched null,
Allosaurus dominance, systems tract, interval, resolution, metric scale).
Stage 1c Nemegt preregistered validation: **NO REPLICATION (Outcome D)**,
Δβ_full = +0.094 [−0.079, +0.300].

**Governance.** Preregistered hypotheses (`VALIDATION_HYPOTHESES.md`), frozen
results (`results/stage1a_freeze_report.md`, freeze commit 4f4b6372), staged
go/no-go gates (`NATURE_GO_NO_GO.md`), report regenerators
(`analysis/99_stage1_report.py` etc.) that write manuscript-facing numbers
from tables — no hard-coded results.

**Reproduce.** `pip install -r requirements.txt && python3 src/download/fetch_data.py && make stage1`. Dryad download requires Chrome via Playwright CDP (AWS WAF); Nemegt and all analysis inputs are pure HTTPS/CSV. Processed inputs are committed (`data/processed/`), so analyses 03–06 and the report builders run offline.

## 2. Modern terrestrial system (`phase8b/`, `phase9/`, `geb/`)

**Data source.** North American Breeding Bird Survey route-year panel
(RunType==1), environmental covariates from Open-Meteo / NASA POWER; Phase 8B
adds elk GPS telemetry, FOSS fish survey, NEON plots for cross-ecosystem
history-dependence comparison. `data/` is gitignored — raw downloads are
scripted, not committed.

**Design.** Not a raw-protocol copy of the dinosaur test — an ecological
translation. The studied phenomenon is lagged-state predictability of species
distributions: ridge-regression family M0–M3 with lagged occurrence/abundance
terms; 2×2 evaluation (leave-one-year-out vs forward-chaining × with/without
route demeaning) decomposing apparent "history" into persistent spatial
heterogeneity vs genuine temporal path dependence; matched-environment
occupancy hysteresis contrast; occupancy-vs-abundance state-dependence
contrast; simulation validation (`phase9/src/sim9.py`, `phase8b/src/sim_fp.py`).

**Headline results (from `geb/docs/`).** Apparent history gain ≈ 0.30 median
without spatial control → ≈ +0.006 median after route demeaning under
forward-chaining; occupancy hysteresis = 0 in all definable species;
abundance state dependence ≈ +0.63 log-count (40/41 definable species CI>0).
Phase 9 verdict: WEAK GO — hysteresis/delayed-redistribution falsified.
Outstanding reviewer-risk item: observer-persistence control on the
abundance prior-state effect (`geb/docs/GEB_GAP_AUDIT.md` §10).

**Trophic axis.** Not guild-structured. The cross-system trophic contrast
(lower vs higher trophic spatial turnover) does not exist natively in this
pipeline — see `protocols/modern_terrestrial/VARIABLE_MAP.md` for the
translated mapping and the minimal additions needed.

## 3. Modern marine system (candidate set)

The marine side is a screened candidate portfolio rather than one settled
pipeline (the sibling "海洋生物回遊" session is still running):

- `marine_dataset_screen/` — DataCite/catalog screen: 23 candidate datasets,
  20-point scoring rubric → `outputs/tables/marine_candidate_ranking.csv`,
  `docs/TOP10_MARINE_SYSTEMS.md`.
- `palmyra_trophic_mobility/` — feasibility & data audit only (Palmyra
  telemetry, 88-file archive, MD5-verified). No confirmatory test run.
- `ecomega_trophic_propagation/` — ACCESS (California Current) matched
  tow-anchored survey units; Type-A (common environment tracking) vs Type-B
  (trophic propagation) discrimination: M0/M1/M2 + mediation + event-holdout
  CV + lag curves + placebos + LOEO. **Verdict: COMMON-ENVIRONMENT
  DOMINATED** — env→predator significant, env→prey and prey→predator null.
- `topp_tracking_modes/` — TOPP predator tracking modes (H1 env tracking,
  H2 prey-mediated, H3 shared forcing, H4 predictive cueing), CCS window.
- `capelin_seabird_positive_control/` — positive-control check that the
  event framework recovers a known response (capelin spawning → seabird
  aggregation). Verdict: WEAK POSITIVE CONTROL.

**Implication for the refactor.** Modern marine currently answers the
propagation/tracking question (env→prey→predator lags), which maps onto Core
Protocol metrics 4 (distance decay → spatial displacement) and 5 (temporal
lag) but not metric 1 natively; the translation mapping is in
`protocols/modern_marine/`.

## Cross-cutting findings

- **Common skeleton already exists de facto**: every project uses numbered
  pipeline scripts, `results/tables`/`outputs/tables` CSVs, `docs/` verdicts,
  `metadata/` provenance (sha256 manifests), and Makefiles. The refactor
  formalizes rather than replaces this.
- **Different native units**: Simpson turnover (dinosaur), History Gain /
  state dependence (terrestrial), mediation coefficients & lag structure
  (marine). The common schema therefore stores native `effect_estimate` plus
  a separately justified `standardized_effect`; native metrics are never
  meta-analyzed directly.
- **Reproducibility asymmetry**: dinosaur commits processed inputs;
  phase8b/9 and marine systems gitignore raw data and script the download.
  Regression baselines for the modern systems are captured from committed
  result tables, not from re-running downloads.
- **Parallel sessions**: `quaternary`, `ancient_marine`, and continued
  `modern_marine` development are in flight on other branches; this branch
  must not depend on them, and their adapters are specification-only until
  they land.
