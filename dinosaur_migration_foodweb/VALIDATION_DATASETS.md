# Candidate independent validation datasets (Stage 1c feasibility)

Survey performed 2026-09-20 via the PBDB API
(`occs/list.json?base_name=Dinosauria&formation=<F>`). Counts are
occurrences/collections at the **formation** level; theropod-bearing
collections counted via named theropod families (undercounts where family
is unspecified, so predator numbers are conservative floors).

No guild-turnover outcome was computed on any candidate dataset — only
feasibility counts and overlap estimates, per protocol.

## Option A — Independent Morrison extraction

- Fresh PBDB query (Morrison Formation, Dinosauria): 418 collections /
  1164 occurrences vs Maidment's cleansed 300 collections / 1397 tetrapod
  (651 dinosaur) occurrences.
- **Overlap: very high (~85–100%)** — Maidment's dataset IS a 2022-12 PBDB
  download; a fresh extraction adds post-2022 records and different
  cleaning/taxonomic choices but shares almost all underlying records.
- Verdict: sensitivity/reproducibility value only; **not independent**.

## Option B — Independent formations

| Formation | Age | Dino occs | Dino colls | Theropod-fam colls | Notes |
|---|---|---|---|---|---|
| Tendaguru (Tanzania) | Kimmeridgian–Tithonian | 223 | 111 | ≥12 | Closest ecological analogue (sauropod+theropod Jurassic fauna); predator collections marginal |
| Lourinhã (Portugal) | Late Jurassic | 127 | 64 | ≥12 | Morrison sister-fauna; small sample |
| Nemegt (Mongolia) | Maastrichtian | 319 | 124 | ≥53 | Good sample; Cretaceous ecology |
| Hell Creek (USA) | Maastrichtian | 767 | 285 | ≥99 | Largest sample; extreme dominance asymmetry (Triceratops/Edmontosaurus/Tyrannosaurus) — different regime |

## Recommended validation dataset

**Nemegt Formation** as primary independent validation (largest balanced
theropod+herbivore sample among non-Morrison candidates), with
**Hell Creek** as a second confirmatory system and **Tendaguru** as the
ecological-analogue sensitivity. If predator samples prove too thin after
genus-resolution filtering, combine Tendaguru+Lourinhã as a single
"non-Morrison Late Jurassic" analysis unit is a fallback (record decision
before running).

All are PBDB-sourced so the download script (`src/download/`) can be
extended with a `pbdb` source; PBDB needs no authentication for reads.
