"""Regression baselines: refactoring must not change committed key outputs.

Compares committed result tables to tests/regression/baselines.json captured
at refactor time (see docs/EXISTING_PROTOCOL_AUDIT.md). Tolerances are loose
enough for float formatting only — any real drift fails.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE = json.loads((Path(__file__).parent / "baselines.json").read_text())
TOL = 1e-6


def dino_summary():
    return pd.read_csv(
        ROOT / "dinosaur_migration_foodweb/results/tables/stage1_beta_summary.csv",
        index_col=0).iloc[:, 0]


@pytest.mark.parametrize("key", [
    "herbivore_simpson_mean_pairwise_beta",
    "predator_simpson_mean_pairwise_beta",
    "delta_beta_simpson_overall",
    "delta_beta_simpson_boot_lo",
    "delta_beta_simpson_boot_hi",
    "delta_beta_sorensen_overall",
    "herbivore_simpson_mantel_r",
    "predator_simpson_mantel_r",
])
def test_dinosaur_key_values(key):
    assert abs(float(dino_summary()[key]) - BASE[key]) < TOL


def test_dinosaur_sampling_raw():
    sens = pd.read_csv(
        ROOT / "dinosaur_migration_foodweb/results/tables/stage1_sampling_sensitivity.csv")
    raw = float(sens.loc[sens.correction == "raw", "delta_beta_mean"].iloc[0])
    assert abs(raw - BASE["sampling_raw_delta"]) < TOL


def test_dinosaur_collection_counts():
    s = dino_summary()
    assert int(s["herbivore_simpson_n_collections"]) == 206
    assert int(s["predator_simpson_n_collections"]) == 114


def test_phase9_modern_terrestrial():
    h = pd.read_csv(ROOT / "phase9/results/tables/final_116_species_summary.csv")
    assert len(h) == BASE["phase9_n_species"]
    assert abs(h["HG"].median() - BASE["phase9_HG_median"]) < TOL
    hyst = pd.read_csv(
        ROOT / "phase9/results/tables/matched_environment_hysteresis.csv")
    assert abs(hyst["effect_of_prior_state"].abs().max()
               - BASE["phase9_hysteresis_max_abs"]) < TOL
    assert abs(hyst["eff_abundance"].median()
               - BASE["phase9_abundance_median"]) < TOL
