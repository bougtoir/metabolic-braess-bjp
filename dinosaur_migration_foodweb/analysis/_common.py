"""Shared constants and loaders for the migration-foodweb pipeline."""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "maidment2024_dryad"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
METADATA = ROOT / "metadata"
TABLES = ROOT / "results" / "tables"
DIAG = ROOT / "results" / "diagnostics"
FIG_MAIN = ROOT / "figures" / "main"
FIG_EXT = ROOT / "figures" / "extended_data"

OCC_DINOS = RAW / "Occurrence_data_with_STs_dinos.xlsx"
OCC_ALL = RAW / "Occurrence_data_with_STs.xlsx"
GENERA_LAT = RAW / "Genera_with_latitude.xlsx"

# PBDB encodes the dinosaur clade in the "class" field for this dataset.
GUILD_MAP = {"Sauropoda": "herbivore", "Ornithischia": "herbivore", "Theropoda": "predator"}

R_EARTH_KM = 6371.0


def haversine_km(lon1, lat1, lon2, lat2):
    """Vectorised great-circle distance (km)."""
    import numpy as np

    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = (
        np.sin((lat2 - lat1) / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * R_EARTH_KM * np.arcsin(np.sqrt(a))


def load_dino_occurrences() -> pd.DataFrame:
    return pd.read_excel(OCC_DINOS)


def assign_guild(clade: str) -> str:
    return GUILD_MAP.get(clade, "other")


def write_table(df: pd.DataFrame, name: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    out = TABLES / name
    df.to_csv(out, index=False)
    print(f"wrote {out.relative_to(ROOT)}")
    return out
