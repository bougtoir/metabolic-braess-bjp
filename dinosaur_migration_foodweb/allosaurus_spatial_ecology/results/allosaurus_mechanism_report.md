# Allosaurus mechanism report — EXPLORATORY (not confirmatory)

Question: why does *Allosaurus* generate unusually high spatial continuity
in Morrison assemblages? Gates applied in order: taxonomic pooling →
temporal averaging → preservation/sampling → generalism → (mobility
deferred). All numbers are generated from `results/tables/allo_*.csv`.

## 1. Taxonomic pooling (H_T)

| quantity | estimate | 95% CI |
|---|---|---|
| Δβ_genus (Jaccard) | -0.550 | [-0.626, -0.461] |
| Δβ_species | -0.322 | [-0.416, -0.231] |
| **L = Δβ_genus − Δβ_species** | **-0.228** | [-0.350, -0.097] |

Genus pooling accounts for ~41% of the negative Δβ; the species-level signal remains negative.

## 2. Occupancy (maps in `figures/map_*.png`)

| taxon                 |   n_occurrences |   n_collections |   occupancy_share |   max_dist_km |   hull_area_deg2 |   lat_range |
|:----------------------|----------------:|----------------:|------------------:|--------------:|-----------------:|------------:|
| Allosaurus            |             117 |             109 |         0.456067  |      1460.63  |          79.24   |    13.0934  |
| Allosaurus fragilis   |              29 |              25 |         0.104603  |       755.798 |          19.5047 |     5.25794 |
| Allosaurus jimmadseni |               8 |               8 |         0.0334728 |       720.728 |          12.6844 |     6.0669  |
| Ceratosaurus          |              13 |              13 |         0.0543933 |       886.401 |          24.8917 |     7.15389 |
| Torvosaurus           |               9 |               9 |         0.0376569 |       713.552 |          14.906  |     6.11542 |

## 3. Stratigraphic-duration / sampling model (OLS: extent ~ duration + n_occ + guild)

| term     |       coef |           p |
|:---------|-----------:|------------:|
| const    | -424.107   | 0.00905592  |
| duration |   64.2112  | 1.59052e-05 |
| n_occ    |    6.79823 | 0.000292929 |
| pred     |  -61.9653  | 0.482189    |

Allosaurus extent residual -37 km (z = -0.16,
percentile vs all dinosaur genera: 42%) — i.e., after
controlling for stratigraphic duration and occurrence count, Allosaurus's
geographic extent is what a well-sampled, long-ranging taxon would
produce.

## 4. Preservation / collection bias (H_P)

Presence of Allosaurus in a dinosaur collection is substantially
predictable from collection covariates (pseudo-R² =
0.456; environment, lithology, member, state,
systems tract, collection richness). See `allo_presence_logit.csv` for
term-level coefficients (many dummies; MLE did not fully converge —
exploratory only).

## 5. Predator comparison

| taxon         |   n_occurrences |   n_collections |   occupancy_share |   duration_ma |   env_breadth |   max_dist_km |   hull_area_deg2 |   lat_range |
|:--------------|----------------:|----------------:|------------------:|--------------:|--------------:|--------------:|-----------------:|------------:|
| Allosaurus    |             117 |             109 |         0.456067  |          18.5 |            13 |      1460.63  |         79.24    |    13.0934  |
| Ceratosaurus  |              13 |              13 |         0.0543933 |          16.2 |             8 |       886.401 |         24.8917  |     7.15389 |
| Coelurus      |              10 |               9 |         0.0376569 |          16.2 |             7 |       640.6   |         17.8005  |     5.51189 |
| Torvosaurus   |               9 |               9 |         0.0376569 |          18.5 |             6 |       713.552 |         14.906   |     6.11542 |
| Tanycolagreus |               4 |               4 |         0.0167364 |          12.3 |             3 |       753.702 |          3.89064 |     5.13411 |
| Ornitholestes |               4 |               4 |         0.0167364 |          16.2 |             4 |       613.068 |          5.03516 |     5.46829 |

## 6. Matched-taxon controls (matched on occurrence count + duration)

| taxon         | guild     |   n_occ |   duration |   extent_km |   occupancy |
|:--------------|:----------|--------:|-----------:|------------:|------------:|
| Camarasaurus  | herbivore |     117 |       18.5 |    1193.59  |   0.430962  |
| Stegosaurus   | herbivore |      72 |       18.5 |    1204.22  |   0.263598  |
| Apatosaurus   | herbivore |      59 |       16.2 |    1190.92  |   0.230126  |
| Diplodocus    | herbivore |      59 |       16.2 |    1160.23  |   0.238494  |
| Camptosaurus  | herbivore |      35 |       16.2 |     960.451 |   0.121339  |
| Nanosaurus    | herbivore |      27 |       16.2 |     836.628 |   0.0794979 |
| Barosaurus    | herbivore |      18 |       16.2 |     909.622 |   0.0711297 |
| Brachiosaurus | herbivore |      13 |       16.2 |     958.579 |   0.0543933 |
| Ceratosaurus  | predator  |      13 |       16.2 |     886.401 |   0.0543933 |
| Torvosaurus   | predator  |       9 |       18.5 |     713.552 |   0.0376569 |

Allosaurus matched extent/occupancy percentile: 100% /
100%. However its closest comparators
(Camarasaurus, Stegosaurus) reach similar occupancy; the margin over the
best-sampled herbivores is small.

## 7. Regional generalism (H_G — indirect evidence only)

| region       |   n_dino_colls |   n_herb_genera |   allo_collections |   allo_regional_share |
|:-------------|---------------:|----------------:|-------------------:|----------------------:|
| Colorado     |             77 |              18 |                 34 |              0.441558 |
| Montana      |              5 |               6 |                  2 |              0.4      |
| New Mexico   |             16 |               5 |                  7 |              0.4375   |
| Oklahoma     |              6 |               7 |                  3 |              0.5      |
| South Dakota |              8 |               4 |                  3 |              0.375    |
| Utah         |             25 |              13 |                 14 |              0.56     |
| Wyoming      |            101 |              20 |                 46 |              0.455446 |

Allosaurus occurs in 45% of
collections on average across regions spanning distinct herbivore faunas —
consistent with broad trophic generalism OR with preservational
pervasiveness; the two cannot be separated by occupancy alone.

## Classification

**MULTIFACTORIAL — taxonomic lumping (H_T) + sampling/temporal
averaging (H_L, H_P) account for most of the apparent exceptionalism;
no robust residual biological exceptionalism detected.**

- Genus→species splitting removes ~40% of the signal (H_T contribution).
- After duration and sampling adjustment Allosaurus spatial extent is
  not exceptional (H_L/H_P contribution).
- A modest residual remains (species-level Δβ stays negative; matched
  occupancy percentile = 100%), so biological generalism (H_G) is
  *plausible* but not demonstrated.
- Mobility (H_M) was not evaluated — the hierarchy gates were not all
  passed; no migration inference is made.

## Guardrails

- Exploratory labels throughout; nothing here is confirmatory.
- Broad occurrence ≠ mobility; mobility claims require independent
  evidence (isotopes, biomechanics, trackways) not yet analysed.
