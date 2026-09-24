"""Load Davoren et al. 2024 Dryad workbook -> data/processed/surveys.csv.

Dataset DOI: 10.5061/dryad.jq2bvq8k8 (CC0). SHA-256 verified against the
Dryad API file digest. One capelin spawning onset per year (DateSpawn,
ordinal) defines the prey event; surveys are ~weekly July-August.

Note: Dryad file downloads are behind Anubis bot protection; if the raw file
is missing, scripts/download_data.py explains how to fetch it via a real
browser session.
"""
import hashlib
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
XLSX = os.path.join(ROOT, "data/raw/dryad/Davoren_et_al._2024_DRYAD.xlsx")
EXPECTED_SHA256 = "0063605dc827a77c1ac2738941b6199fac811fb1d207a9d6505e8778b0f24236"

h = hashlib.sha256(open(XLSX, "rb").read()).hexdigest()
assert h == EXPECTED_SHA256, f"checksum mismatch: {h}"

d = pd.read_excel(XLSX, sheet_name="Raw Data")
d.columns = [c.strip() for c in d.columns]
d["date"] = pd.to_datetime(d["Date"], format="%d-%m-%Y")
d["year"] = d["date"].dt.year
d = d.rename(columns={
    "Ordinal Date": "doy", "DateSpawn": "spawn_doy", "DiffSpawn": "tau",
    "no.bins": "n_bins", "Ave.survey.g.m2": "fish_g_m2",
    "No.Schools": "n_schools", "AveShoalBiomass": "shoal_biomass",
    "Ave.Area.Shoal..h.w..m2": "shoal_area",
    "TOTAL.BIRDS": "birds_total", "TOTAL.ALCID": "alcids",
    "TOTAL LARUS": "larus", "NOGA": "gannets", "GRSH&SOSH": "shearwaters",
})
d["birds_per_bin"] = d["birds_total"] / d["n_bins"]
d["fish_per_bin"] = d["fish_g_m2"]  # already an average across bins
d.to_csv(os.path.join(ROOT, "data/processed/surveys.csv"), index=False)
print(d.groupby("year").agg(n=("date", "size"), spawn=("spawn_doy", "first")))
