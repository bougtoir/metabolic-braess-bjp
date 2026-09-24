# Core Protocol v1 — cross-system falsification framework

**Status: v1 (frozen).** Every study in this program (Phases 1–9 and future
phases/papers) MUST implement this protocol. The purpose is comparability: as
papers accumulate, the fixed items must not drift.

A study is "on-protocol" iff it implements every FIXED item below, declares every
VARIABLE item explicitly in its analysis plan before results are seen, and keeps
honest nulls.

*This file is the markdown transcription of the canonical CORE_PROTOCOL_v1.docx
(provided 2026-09-21). The docx is authoritative; this file mirrors it verbatim
and adds the instantiation table for the Morrison/beta-diversity system in §6.*

---

## 1. Fixed items (identical across all systems)

### F1. Primary contrast
Every study has exactly ONE pre-declared primary contrast: the target
out-of-sample skill of a history/state-bearing model minus that of its matched
environment-only (or process-only) baseline, evaluated on identical observations.

Form: `HG = OOS(target model) − OOS(reference model)`.

Both models must be evaluated on the SAME evaluation sample — asserted
programmatically, not assumed.

No secondary contrast may silently replace the primary one; additional contrasts
are labelled secondary/exploratory.

### F2. Effect direction
The sign convention and the pre-registered direction of the effect under the
hypothesis are fixed before analysis:

- Under the memory/persistence hypothesis: `HG > 0` (history helps beyond
  environment).
- Under the falsification/null expectation: `HG ≈ 0` or explained by confounds.

Reversing the sign convention after seeing results is prohibited.

### F3. Sampling-pool test
Every estimate must be computed on a well-defined observation universe: the set
of (site, time) units actually sampled — never inferred absences from missing
sampling. Specifically:

- surveyed-present, surveyed-absent, not-surveyed are three distinct states;
  not-surveyed is never coded as absent.
- Denominators (prevalence, occupancy, coverage) use sampled units only.
- Response and predictor construction must be verified against the raw sampling
  table, not assumed from data layout.

### F4. Time-aggregation test
Every claim of temporal dynamics must survive a change of temporal grain: report
the primary contrast at the native resolution AND at least one coarser
aggregation (e.g., site-level → regional, weekly → annual), or document
explicitly why aggregation is not possible.

### F5. Distance-decay (spatial structure test)
Every study must separate spatially-structured persistence from temporal
history:

- Compute the primary contrast with and without a static spatial control
  (site demeaning / site fixed effects / static suitability surface).
- State the proportion of apparent temporal signal attributable to static
  spatial structure.

### F6. Negative control
At least one negative control per study, from a fixed menu:

- future-predictor control (predicting the past / shifted labels),
- randomized spatial labels,
- simulated null data through the identical pipeline (environment-only,
  static-persistence, observation-persistence scenarios),
- unrelated-guild / placebo contrast.

### F7. Robustness classification
Every claim is labelled:

- **ROBUST** — survives all fixed checks with consistent sign/magnitude.
- **WEAK** — survives some checks, bounded by identified limits.
- **NULL** — consistent with a declared null mechanism.
- **UNSUPPORTED** — contradicted by the fixed checks.

Robustness labels are assigned by the protocol, not ad hoc per paper.

## 2. Variable items (system-specific; must be declared a priori)

| item | description | examples |
|---|---|---|
| V1. Database / data source | which survey or tracking system | BBS routes, NEON plots, Movebank GPS, FOSS trawls |
| V2. Spatial unit | the unit of analysis | BBS route, NEON grid cell, GPS fix, trawl station |
| V3. Temporal resolution | native grain of the panel | annual (BBS), monthly (NEON), GPS fixes (min–hourly) |
| V4. Observation-process correction | detection/effort/observer handling | observer covariates, imperfect-detection terms, effort offsets |
| V5. Guild definition | species grouping / inclusion rule | prevalence threshold ≥0.30 on surveyed route-years; migratory class |

Variable items may differ across systems; once declared for a given phase they
are frozen for that phase.

## 3. Process rules (fixed)

- **Pre-registration discipline**: analysis plan (models, contrasts, controls,
  GO/NO-GO thresholds) written before results are examined.
- GO/NO-GO verdicts per phase; honest nulls are valued equally with positive
  results.
- No spec changes to rescue a conclusion. Specification changes may only fix
  bugs; every bug fix triggers a pre/post impact audit.
- No fabricated data; no hardcoded results. All manuscript numbers are
  regenerated from pipeline outputs (results CSVs → docx builder).
- Forward-chaining is the primary inference for any temporal claim; random CV is
  prohibited for the primary contrast.
- Train-only preprocessing: all scaling/centring/imputation parameters estimated
  on training folds only.
- Branch-per-phase, PR-per-phase; prior phases are frozen once their PR is
  opened.

## 4. Instantiation example — Phase 9 / GEB manuscript (BBS system)

| protocol item | Phase-9 implementation | status |
|---|---|---|
| F1 primary contrast | HG = OOS(env+lag-1 state) − OOS(env); common eval asserted | done |
| F2 direction | HG > 0 = history signal | fixed pre-analysis |
| F3 sampling pool | surveyed/present/absent/not-surveyed; surveyed-denominator prevalence | done (post-bugfix) |
| F4 time aggregation | route-level → state-level regional HG (→ −0.04, not retained) | done |
| F5 distance-decay/static | 2×2 LOYO/forward × demean/none; demeaning collapses HG 0.30→0.006 | done |
| F6 negative control | simulation scenarios env-only/static/obs-persistence/true-history; observer covariates | done |
| F7 robustness | HG_D weak-positive (WEAK); occupancy hysteresis UNSUPPORTED; regional NULL | assigned |
| V1 | BBS 1966–2019 release | — |
| V2 | BBS route-year | — |
| V3 | annual | — |
| V4 | observer covariates; surveyed-only response | — |
| V5 | nz_frac ≥ 0.30 → 116 species | — |

## 5. Change control

- Protocol text may only change by a dedicated PR labelled `protocol-change`,
  with a changelog entry here and a stated reason.
- Changes that would retroactively alter a finished phase's verdict are
  prohibited; they apply to future phases only.

Changelog: v1 (2026-09-21): initial freeze; fixed items F1–F7, variable items
V1–V5, process rules, Phase-9 instantiation.

---

## 6. Instantiation — dinosaur_migration_foodweb / methodological_beta_bias

This program is a **beta-diversity contrast** system, not a forecasting system.
Where the F1 "model skill" form does not literally apply, the same protocol item
is instantiated by the closest structural equivalent, declared below.

| protocol item | Morrison/beta-diversity implementation | status | divergence from literal form |
|---|---|---|---|
| F1 primary contrast | Δβ = mean pairwise Jaccard(predator guild) − mean pairwise Jaccard(herbivore guild), same localities both guilds | done | Δβ is a structural contrast, not OOS skill; equivalence to "same evaluation sample" = identical site set |
| F2 direction | Under spatially-coupled-migration hypothesis Δβ < 0 (predators more homogeneous); observed −0.550; sign fixed in VALIDATION_HYPOTHESES.md before Stage 1c | done | none |
| F3 sampling pool | Occurrences vs absences distinguished from unvisited localities; prevalence uses sampled localities only; collection-effort model separate | done | fossil data have no true absences — recorded as "surveyed-present / not-surveyed" binary |
| F4 time aggregation | Δβ computed at member/stratigraphic grain vs fully pooled; simulated 8-slice→1-bin attenuation | done | none |
| F5 distance-decay/static | Distance-decay slopes per guild (2-D sim + empirical); stratigraphic-duration and systems-tract static controls; Allosaurus extent residual z = −0.16 | done | "static spatial control" instantiated as extent/duration adjustment, not site demeaning |
| F6 negative control | Pool-size matched null; frequency-matched null; dominant-taxon removal (Δβ −0.550 → −0.020); Nemegt external comparator; simulated Δβ_true=0 scenarios | done | multiple controls used; menu satisfied |
| F7 robustness | Structural-bias labels: STRUCTURAL / RESIDUAL / FRAGILE / INCONCLUSIVE (see methodological_beta_bias REPORTING) | assigned | label names adapted to non-forecasting domain; mapping: ROBUST↔RESIDUAL, NULL↔STRUCTURAL |
| V1 | Maidment 2024 Dryad (10.5061/dryad.6m905qg77); PBDB Nemegt | — | — |
| V2 | occurrence localities / sites | — | — |
| V3 | stratigraphic member / sub-stage | — | — |
| V4 | collection effort, stratigraphic duration, occurrence-count preservation model | — | — |
| V5 | herbivore vs large-predator guilds, a priori; Tarbosaurus preregistered for Nemegt | — | — |

Notes on process-rule applicability: forward-chaining (temporal OOS) does not
literally apply to palaeo assemblages; its structural equivalent — leave-region /
leave-formation-out checks — is used for the empirical contrast. All other
process rules (preregistration, honest nulls, no spec changes to rescue results,
no fabricated data or hardcoded numbers) apply unchanged and are already in force.
