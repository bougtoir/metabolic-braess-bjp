# Modern protocol compatibility audit

Per spec §20: existing modern analyses are preserved; this audit maps them
into the Core Protocol and lists only the minimum additions needed.

## Terrestrial (phase8b / phase9 / geb)

**What exists.** BBS route-year panel (116 widespread species), ridge models
M0–M3, 2×2 persistence-vs-history decomposition, matched-environment
occupancy hysteresis (0), abundance state dependence (+0.63 log-count),
simulation falsification machinery, plus phase8b cross-ecosystem panels
(elk GPS, FOSS, NEON).

**Mapping.** See `protocols/modern_terrestrial/VARIABLE_MAP.md`. Direct
exports: temporal lag / persistence, nulls, robustness. Translated exports:
spatial persistence (route-demeaned contrast) under `distance_decay_effect`.
**Missing**: M1 trophic spatial-turnover contrast — minimal add = one
guild-split Δβ analysis over the same route incidence matrices; if the guild
structure is not defensible in BBS, export NA with justification.
**Pending**: observer-persistence control (GAP_AUDIT §10) — belongs to the
system's own program, not forced here.

**Reproduction.** `phase9/Makefile` documents the run order; raw BBS data
are gitignored and re-downloaded by `src/env_fetch.py` + data pull scripts.

## Marine (candidate portfolio)

**What exists.** `marine_dataset_screen` (23-candidate rank),
`palmyra_trophic_mobility` (feasibility audit only — no confirmatory test),
`ecomega_trophic_propagation` (ACCESS/CCS matched survey; verdict
COMMON-ENVIRONMENT DOMINATED), `topp_tracking_modes` (H1–H4 mechanism
comparison), `capelin_seabird_positive_control` (WEAK POSITIVE CONTROL).

**Mapping.** See `protocols/modern_marine/VARIABLE_MAP.md`. Direct exports:
temporal lag structure, nulls/placebos, robustness verdicts. Translated:
distance decay via centroid displacement; sampling sensitivity via
matched-unit/LOEO. **Missing**: native spatial Δβ — marine survey units are
tow-matched transects; export path-coefficient contrast instead and mark
`delta_beta_*` NA until the running marine session settles a final system.

**Reproduction.** Each project has a Makefile (`make all`); raw data
downloads are scripted (NOAA ERDDAP / WFS / DataONE) and not committed.

## Verdict

| System | Compatible now | Needs minimal add | Notes |
|---|---|---|---|
| Modern terrestrial | M2–M9 | M1 guild Δβ (or documented NA) | pipeline preserved |
| Modern marine | M2, M4–M7 (translated) | formal `observation_bias_score`; M1 as translated path contrast | final dataset unsettled |
