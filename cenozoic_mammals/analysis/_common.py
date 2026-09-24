"""Shared constants and loaders for the Cenozoic mammal pipeline.

Mirrors dinosaur_migration_foodweb/analysis/_common.py — strict replication
with PBDB field names instead of the Dryad package schema.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "pbdb_cenozoic"
PROCESSED = ROOT / "data" / "processed"
METADATA = ROOT / "metadata"
TABLES = ROOT / "results" / "tables"
DIAG = ROOT / "results" / "diagnostics"
FIG_MAIN = ROOT / "figures" / "main"

RAW_OCC = RAW / "occurrences_NOA_23-5ma.csv"

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

# Terrestrial guild assignment (order-level; deviation 1 in
# protocols/cenozoic_mammals/PROTOCOL_DEVIATIONS.md).
HERBIVORE_ORDERS = {
    "Artiodactyla", "Perissodactyla", "Proboscidea", "Lagomorpha",
    "Rodentia", "Xenarthra", "Cingulata",
}
PREDATOR_ORDER = "Carnivora"
MARINE_CARNIVORE_FAMILIES = {
    "Phocidae", "Otariidae", "Odobenidae", "Enaliarctidae", "Desmatophocidae",
}
# Excluded as omnivorous/marine/ambiguous rather than silent re-mapping.
EXCLUDE_ORDERS = {
    "Cetacea", "Sirenia", "Desmostyloidea", "Desmostylia",  # marine herbivores
    "Insectivora", "Primates", "Chiroptera", "Marsupialia",
    "Didelphimorphia", "NO_ORDER_SPECIFIED",
}

# PBDB env terms treated as marine/marginal-marine and dropped (deviation —
# dinosaur input was already terrestrial-only).
MARINE_ENV_SUBSTRINGS = (
    "marine", "subtidal", "offshore", "shoreface", "lagoon", "estuar",
    "intertidal", "reef", "basinal", "foreshore", "shelf", "delta front",
    "prodelta", "coastal",
)


def assign_guild(order: str, family: str) -> str:
    if order in HERBIVORE_ORDERS:
        return "herbivore"
    if order == PREDATOR_ORDER:
        if family in MARINE_CARNIVORE_FAMILIES:
            return "marine_predator_excluded"
        return "predator"
    return "other"


def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW_OCC, low_memory=False)


def write_table(df: pd.DataFrame, name: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    out = TABLES / name
    df.to_csv(out, index=False)
    print(f"wrote {out.relative_to(ROOT)}")
    return out
