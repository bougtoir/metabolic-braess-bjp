# Empirical decomposition — specification

The Morrison worked example is run as a single sequential diagnostic
(`analysis/07_morrison_empirical_decomposition.py`), all steps on the
primary specification (Jaccard, collection-level assemblages,
collection bootstrap CI, genus unless the step changes resolution):

| step | manipulation | diagnostic question |
|---|---|---|
| 1 | naive genus guild contrast | what does the raw record show? |
| 2 | gamma-matched null (B=10,000) | is it explained by unequal taxon pools? |
| 3 | frequency-matched null (B=10,000) | is it explained by occupancy frequencies? |
| 4 | exclude dominant taxon | does one genus carry it? |
| 5 | species-level resolution | how much was taxonomic pooling? |
| 6 | duration + occurrence-count OLS | is the dominant taxon still an outlier? |
| 7 | collection-covariate presence model | how much is sampling/preservation? |

The output table `results/tables/morrison_decomposition.csv` is the
quantitative spine of the manuscript's empirical Results sections 1–4.
