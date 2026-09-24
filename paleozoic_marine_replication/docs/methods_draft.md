# Methods draft (skeleton)

## Data

Occurrence data were downloaded from the Paleobiology Database (PBDB
API v1.2) on the dates recorded in `data/raw/provenance.jsonl`. We
retrieved all marine occurrences (`envtype=marine`) assigned to six
candidate clades — Brachiopoda, Trilobita, Bivalvia, Gastropoda,
Cephalopoda and Crinoidea — with early/late ages intersecting the
Cambrian–Permian interval (538.8–251.9 Ma). Fields retained include
occurrence and collection identifiers, accepted and genus-level
taxonomy, early/late numeric ages and interval names, present-day and
rotated paleocoordinates (PBDB `gplates`/`mid` models), environment,
lithology and stratigraphic metadata. Raw API responses are preserved
unchanged in `data/raw/`.

## Temporal units

Two parallel temporal schemes were implemented. (A) Stratigraphic:
PBDB international stage-level bins (scale-1 `age` level) and merged
two-stage pairs. (B) Absolute-duration bins of 5, 10 and 20 Myr
anchored at the Cambrian base. Occurrences were assigned by the
midpoint of their early–late age range. The realised duration of every
bin is recorded in `time_bins.csv`.

## Spatial units

Analyses use rotated paleocoordinates. Sites are equal-angle
paleolatitude/paleolongitude grid cells at 5, 10 and 20 degree
resolutions (10 degrees primary; the others are sensitivity analyses).
Minimum sampling thresholds were predefined: >= 5 occupied sites, >= 5
genera per dataset, and >= 10 site pairs for distance-decay
estimation. No threshold was tuned post hoc.

## Community matrices

For every time bin x clade x spatial unit we built presence/absence
matrices of sites x genera and recorded number of sites, collections,
occurrences, regional gamma diversity, median alpha diversity, median
taxon occupancy, and collection/occurrence intensity
(`dataset_summary.csv`).

## Beta-diversity metrics

Core metrics replicate the dinosaur protocol exactly: mean pairwise
Jaccard dissimilarity, plus Sorensen dissimilarity and its Baselga
partition into turnover (Simpson) and nestedness components.

## Distance decay

For every eligible dataset we estimated distance decay as the OLS
slope of pairwise Jaccard dissimilarity against great-circle distance
(km) between site centroids — the same linear model family as the
dinosaur analysis.

## Perturbation experiments

Following the dinosaur pool-size experiment, we contracted the
observable regional genus pool to 75%, 50% and 25% (200 Monte Carlo
draws each) while holding the spatial framework fixed, and recorded
Bias_beta = beta_perturbed - beta_reference and Bias_decay =
slope_perturbed - slope_reference for every replicate. Sampling
perturbation subsampled collections to the same fractions; the two
factors were crossed in a full factorial design (50 replicates per
cell). Temporal aggregation was assessed by progressively merging
adjacent bins (stage -> 2-stage; 5 -> 10 -> 20 Myr) and computing
Bias_time = metric_aggregated - metric_fine.

## Simulation engine

The shared 2-D simulation engine is the dinosaur lattice model
(`13_2d_robustness.py`) imported unchanged: square lattice, disc-shaped
taxon ranges, fixed occupancy probability. Only the reference gamma
parameter differs (60, the typical stage-level clade gamma, vs 26);
all differences are logged in `parameter_registry.csv`.

## Replication criterion

The primary replication test is qualitative: whether pool contraction
shifts mean beta, between-group contrasts and decay slopes in the same
direction as in the dinosaur system, and whether it interacts with
sampling intensity and temporal aggregation. Effect sizes are not
expected to match.
