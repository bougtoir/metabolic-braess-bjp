"""Shared data loading and constants for the demographic-transition universality re-analysis.

Data source: Gapminder (https://www.gapminder.org/data/), the same primary source used by
Itao (2024/2026), "Two universal pathways in demographic transition", arXiv:2402.15697 /
Evol. Hum. Sci. (DOI 10.1017/ehs.2026.10054). The two long-run series used here are:
  - crude_birth_rate_births_per_1000_population.csv  (lambda, births per 1,000 population)
  - life_expectancy_years.csv                        (e0, period life expectancy at birth)
Auxiliary series (child mortality, GDP, population) are used only for descriptive context.

All downstream results are recomputed from these CSVs; no numeric result is hard-coded.
"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")
RESULTS_DIR = os.path.join(ROOT, "results")
FIGS_DIR = os.path.join(ROOT, "figs")

# Constant in the Phase II conserved quantity lambda * exp(e0 / TAU_E0) used by the
# published EHS version of the paper (the arXiv preprint uses 18).
TAU_E0 = 17.0


def _read_wide(name):
    """Read a Gapminder wide CSV (country x year) into a long tidy frame."""
    path = os.path.join(DATA_DIR, name)
    df = pd.read_csv(path)
    df = df.rename(columns={df.columns[0]: "country"})
    long = df.melt(id_vars="country", var_name="year", value_name="value")
    long["year"] = pd.to_numeric(long["year"], errors="coerce")
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    long = long.dropna(subset=["year"])
    long["year"] = long["year"].astype(int)
    return long


def load_panel(year_max=2015):
    """Build the country-year panel of crude birth rate (lambda) and life expectancy (e0).

    year_max caps the observation window (the preprint uses observed data up to 2015; later
    Gapminder life-expectancy values are forward projections and are excluded).
    """
    cbr = _read_wide("crude_birth_rate_births_per_1000_population.csv").rename(
        columns={"value": "lambda"}
    )
    e0 = _read_wide("life_expectancy_years.csv").rename(columns={"value": "e0"})
    panel = cbr.merge(e0, on=["country", "year"], how="inner")
    panel = panel[(panel["year"] >= 1800) & (panel["year"] <= year_max)]
    panel = panel.dropna(subset=["lambda", "e0"])
    panel = panel[(panel["lambda"] > 0) & (panel["e0"] > 0)]
    panel = panel.sort_values(["country", "year"]).reset_index(drop=True)
    return panel


def load_series(name, value_name):
    return _read_wide(name).rename(columns={"value": value_name})


def ensure_dirs():
    for d in (RESULTS_DIR, FIGS_DIR):
        os.makedirs(d, exist_ok=True)
