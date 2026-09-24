# TOP10_MARINE_SYSTEMS — scored shortlist with qualitative evaluation

Scores in `outputs/tables/marine_candidate_ranking.csv`. Scoring is a
screening aid; this section evaluates causal separability (advection vs
resource-following; common-environmental vs trophic propagation) and
event-definition circularity for each.

## 1. TOPP — Tagging of Pacific Predators (E. N. Pacific) — score 14

- Chain: upwelling/chl → forage fish (survey indices) → tunas/sharks/pinnipeds/turtles/seabirds.
- Data: OBIS-SEAMAP doi:10.82144/d127533f, open; ~2000–2010, daily SSM positions, hundreds of individuals.
- Events: ≥20 (annual upwelling pulses, eddy passages, marine-heatwave onsets); onsets defined from wind/SST/SSH — not from predators.
- Advection: daily geostrophic + OSCAR-era currents — estimable.
- Confounders: prey layer is survey indices, not concurrent biomass along tracks; migratory seasonality.
- Improves on Palmyra: ~10 years not 1.3; real prey layer exists (even if coarse); many more individuals.
- vs capelin: far more events and predators, but exposure resolution coarser than direct acoustic biomass.
- Biggest risk: prey-patch mismatch — may only distinguish "env→predator" (type A), not env→prey→predator (type B).
- Circularity: none — events from environmental indices.

## 2. SEATRACK + ICES sandeel (NE Atlantic) — score 16

- Chain: sandeel acoustic/dredge (DATRAS, open API) → kittiwake/puffin/fulmar GPS tracks (SEATRACK open download), >10 yr, ~30–60 min fixes.
- Events: ~10–15 annual sandeel/breeding windows; also sandeel collapse episodes.
- Advection: currents available; flight-dominated anyway.
- Confounders: colony site fidelity; sandeel resolved annually, not per-event.
- Improves on capelin: hourly predator fixes + colony replication vs weekly counts.
- Biggest risk: prey granularity (annual biomass) limits event coupling.
- Circularity: none (survey-defined prey + breeding-season windows).

## 3. CalCOFI / NOAA CPS surveys + TOPP fusion (California Current) — score 15

- Chain: upwelling pulses (BEUTI indices) → anchovy/sardine acoustic-trawl biomass → predators via TOPP tracks.
- Events: ≥20 repeated upwelling pulses; objectively wind-defined.
- Advection: currents estimable.
- Confounders: two archives must be fused; contemporaneity at event scale must be verified.
- Improves on both pilots: most events + direct prey acoustics + daily predator fixes.
- Biggest risk: fusion misalignment (surveys quarterly/annual vs daily tracks).
- Circularity: none.

## 4. California ecomega at-sea surveys — score 14

- Chain: krill/forage acoustics + simultaneous seabird/mammal visual counts on same transects — a true 3-layer contemporaneous design.
- Events: ~10–15 survey windows; upwelling events external.
- Advection: estimable; confounders: annual scale, raw counts via NOAA request.
- Best Type-B evidence potential (all layers same day).
- Biggest risk: access friction for raw counts.

## 5. South Georgia krill–penguin/seal (BAS PDC + CCAMLR) — score 13

- Chain: chl → krill (acoustic) → macaroni/chinstrap penguin + fur seal GPS/PTT.
- Events: ~10 annual breeding-season krill arrival/ice-edge episodes.
- Telemetry is hourly-grade; individualed; open PDC downloads (e.g. 10.5285/459597b2-…).
- Biggest risk: krill acoustics episodic — simultaneity must be verified year by year.
- Circularity: none.

## 6. Antarctic Peninsula gentoo (Dryad 10.5061/dryad.5x69p8d20) — score 13

- Chain: sea-ice/chl → (krill inferred) → gentoo GPS/TDR.
- High-resolution tracks, CC0, but **no measured prey layer** → supports Type-A only.
- Biggest risk: cannot separate common-env tracking from trophic propagation.

## 7. Scotia Sea krill–penguin — score 12

Similar to #5; larger geographic spread, sparser concurrent krill acoustics.

## 8. MEOP elephant-seal CTD (Southern Ocean) — score 11

Hourly in-situ oceanography + predator movement; many eddy/front events — but no prey measurement → Type-A only.

## 9. Benguela sardine–gannet — score 10

High-res gannet GPS + annual sardine acoustics; ~8–10 annual episodes. Prey granularity annual.

## 10. Davoren capelin–seabird (pilot B) — score 9

Reference point: weekly simultaneous prey+predator, 10 events, prey-defined onsets — WEAK positive control already measured.

## Notable exclusions (score high but fail trophic criterion)

- **eddy-tuna** (8) and **imos-aatams** (3): no observable prey/resource layer → cannot distinguish trophic propagation from direct environmental response.
- **krillbase-whale** (3): prey net-haul database (1920s–2008) and whale telemetry are mostly non-contemporaneous.

## Finalists

- **Finalist A (best repeated-event system): TOPP.** Hundreds of tracked predators, daily env fields, ≥20 candidate perturbations; risk is prey-layer granularity.
- **Finalist B (best true 3-level chain): California ecomega at-sea surveys.** Krill+forage acoustics and predator counts measured on the same transect-day — uniquely separates Type B from Type A.
- **Finalist C (best high-frequency telemetry): South Georgia krill–penguin/seal.** Hourly GPS/PTT + 3 trophic layers + open PDC data.

Next-step plans: A — detect ≥20 upwelling/eddy onsets from wind/SSH, event-window predator centroid/RoG response (Palmyra machinery re-usable), prey-side check vs CalCOFI indices. B — pooled event-model within survey windows, placebo on survey-free dates, LOEO across years. C — per-event distance-to-krill-survey-area and dive behaviour shifts, ice-edge events, LOEO across seasons.
