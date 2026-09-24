# Allosaurus spatial ecology — EXPLORATORY NEW PROJECT

**Status: exploratory. This project does NOT inherit confirmatory status
from `dinosaur_migration_foodweb`.** The original cross-formation
predator-continuity hypothesis was falsified then failed preregistered
replication in Nemegt (`dinosaur_migration_foodweb/PROJECT_OUTCOME_ORIGINAL.md`,
`NATURE_GO_NO_GO.md` — NO-GO). This project asks a narrower question.

## Central question

Why does *Allosaurus* generate unusually high spatial continuity in
Morrison fossil assemblages — i.e., how did a single large theropod
lineage remain geographically pervasive across a Morrison herbivore fauna
with substantially greater spatial turnover?

Explicitly NOT assumed: migration.

## Candidate mechanisms (to be discriminated)

| code | mechanism |
|---|---|
| H_T | taxonomic lumping (genus-level pooling inflates apparent continuity) |
| H_G | dietary / ecological generalism across distinct prey communities |
| H_M | high mobility / large home range |
| H_P | preservation or collecting bias |
| H_L | long stratigraphic/temporal duration |
| H_C | combination of mechanisms |

## Hierarchy of inference (ordered gates)

broad occurrence → rule out taxonomic pooling (H_T) → rule out time
averaging (H_L) → rule out preservation bias (H_P) → evaluate generalism
(H_G) → only then evaluate mobility (H_M)

Mobility is never inferred from broad geographic occurrence alone.

## Data

Reuses the Maidment et al. 2024 Morrison dataset already pulled with
sha256 provenance in `../` (the parent `dinosaur_migration_foodweb`
project; CC0; DOI 10.5061/dryad.6m905qg77). All analysis inputs are
derived from `../data/processed/occurrences_clean.csv` and the raw
occurrence workbook (collection-level lithology/environment/sampling
fields).

## Outputs

`results/allosaurus_mechanism_report.md` — generated from
`results/tables/allo_*.csv`; no hardcoded numbers.
