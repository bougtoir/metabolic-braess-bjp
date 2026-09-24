"""Cenozoic pipeline smoke/regression tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
PROCESSED = ROOT / "data" / "processed"


def test_clean_outputs_exist():
    for f in ("occurrences_clean.csv", "collections_clean.csv"):
        assert (PROCESSED / f).exists(), f"run analysis/02_clean.py first"


def test_no_marine_envs():
    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv", low_memory=False)
    env = occ["env"].fillna("").str.lower()
    assert not env.str.contains("marine").any()


def test_guild_sets_nonempty():
    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv", low_memory=False)
    g = occ[(occ.resolution == "genus")]
    assert g.loc[g.guild == "herbivore", "genus"].nunique() > 0
    assert g.loc[g.guild == "predator", "genus"].nunique() > 0
    # no pinniped families inside predator guild
    marine_fams = {"Phocidae", "Otariidae", "Odobenidae", "Enaliarctidae", "Desmatophocidae"}
    assert not set(g.loc[g.guild == "predator", "family"].dropna()) & marine_fams


@pytest.mark.skipif(not (TABLES / "beta_summary.csv").exists(),
                    reason="run analysis/03_beta_diversity.py first")
def test_beta_summary_keys():
    s = pd.read_csv(TABLES / "beta_summary.csv", index_col=0).iloc[:, 0]
    for k in ("delta_beta_simpson_overall", "delta_beta_simpson_boot_lo",
              "delta_beta_simpson_boot_hi", "herbivore_simpson_mantel_r",
              "predator_simpson_mantel_r"):
        assert k in s.index and pd.notna(s[k])
    assert -1 <= s["delta_beta_simpson_overall"] <= 1


@pytest.mark.skipif(not (TABLES / "sampling_sensitivity.csv").exists(),
                    reason="run analysis/04_sampling_bias.py first")
def test_all_five_corrections():
    s = pd.read_csv(TABLES / "sampling_sensitivity.csv")
    assert set(s["correction"]) == {
        "raw", "no_dominant_quarries", "no_singletons",
        "equalized_collections", "spatial_thinning_1deg"}


@pytest.mark.skipif(not (TABLES / "aggregation_sensitivity.csv").exists(),
                    reason="run analysis/05_aggregation.py first")
def test_aggregation_ladder():
    a = pd.read_csv(TABLES / "aggregation_sensitivity.csv")
    assert set(a["binning"]) == {"pooled", "epoch", "ma5", "ma1"}
