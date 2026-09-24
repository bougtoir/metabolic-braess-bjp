# TOPP predator tracking modes (Task 5)

Competing mechanisms of how mobile marine predators locate productive
habitat: H1 direct environmental tracking, H2 prey-mediated trophic
tracking, H3 shared environmental forcing, H4 predictive environmental
cueing. California Current System window (30–48°N, 235–243°E).

## Reproduce
    make all        # downloads from public NOAA ERDDAP, builds tables+figures

Scripts: 01_download -> 02_process -> 03_events_env -> 04_models ->
05_lag_modes -> 06_matches_modes -> 07_figures.

See docs/TOPP_DATA_PROVENANCE.md for data sources and
docs/TOPP_MECHANISM_REPORT.md for results.
