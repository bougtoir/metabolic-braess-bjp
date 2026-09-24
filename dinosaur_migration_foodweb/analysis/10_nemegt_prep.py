"""Prepare the independent Nemegt PBDB dataset for the locked validation.

Reads the raw pulls in data/raw/nemegt_pbdb/ (see
src/download/fetch_pbdb_nemegt.py), restricts to Dinosauria occurrences
identified to genus resolution, assigns guild via ancestor walk on the
PBDB taxonomy (predator = descends from 'Theropoda'; herbivore = all other
dinosaurs), and writes data/processed/nemegt_occurrences.csv.

Taphonomic fields carried through (env, lt1, ldc, tpm, tps, tpt, cct, gsc,
ccx, ccd) for the mandatory taphonomic diagnostics.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESSED, TABLES, write_table

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "nemegt_pbdb"

KEEP = [
    "oid", "cid", "tna", "tid", "rnk", "lng", "lat",
    "env", "lt1", "ldc", "tpm", "tps", "tpt", "cct", "gsc", "ccx", "ccd",
    "cnm", "aut", "pby", "oei",
]


def main() -> None:
    occ = pd.read_csv(RAW / "nemegt_occurrences.csv", dtype=str)
    colls = pd.read_csv(RAW / "nemegt_collections.csv", dtype=str)
    taxa = pd.read_csv(RAW / "dinosauria_taxa.csv", dtype=str)

    # ancestor walk structures
    name = dict(zip(taxa["oid"], taxa["nam"]))
    par = dict(zip(taxa["oid"], taxa["par"]))
    gnl = dict(zip(taxa["oid"], taxa["gnl"]))
    rnk = dict(zip(taxa["oid"], taxa["rnk"]))
    dino_oids = set(taxa["oid"])
    theropoda = {o for o, n in name.items() if n == "Theropoda"}

    def is_theropod(tid: str) -> bool:
        seen = set()
        cur = tid
        while cur in dino_oids and cur not in seen:
            if cur in theropoda:
                return True
            seen.add(cur)
            cur = par.get(cur)
        return False

    def genus_of(tid: str, tna: str) -> str | None:
        g = gnl.get(tid)
        if isinstance(g, str) and g:
            return g
        n = name.get(tid, tna)
        if rnk.get(tid) in ("genus", "species", "subgenus") or " " in str(n):
            tok = str(n).split()[0]
            return tok if tok and tok[0].isupper() else None
        return str(n) if rnk.get(tid) == "genus" else None

    occ = occ[occ["tid"].isin(dino_oids)].copy()
    # assemblage matrices use body fossils only (records with a body
    # component); pure trace/egg records are kept in the file for the
    # taphonomic comparison and excluded downstream via body_fossil flag.
    occ["body_fossil"] = occ["tpm"].fillna("").str.contains("body")
    occ["guild"] = occ["tid"].map(lambda t: "predator" if is_theropod(t) else "herbivore")
    occ["genus"] = [genus_of(t, n) for t, n in zip(occ["tid"], occ["tna"])]
    occ["collection_no"] = occ["cid"].str.replace("col:", "", regex=False)

    # fill missing occurrence coords from collection coords
    coll_xy = colls.set_index(colls["oid"].str.replace("col:", "", regex=False))[
        ["lng", "lat"]
    ]
    for ax in ("lng", "lat"):
        miss = occ[ax].isna()
        occ.loc[miss, ax] = occ.loc[miss, "collection_no"].map(coll_xy[ax])
    occ["lng"] = pd.to_numeric(occ["lng"], errors="coerce")
    occ["lat"] = pd.to_numeric(occ["lat"], errors="coerce")

    cols = [c for c in KEEP if c in occ.columns] + [
        "guild", "genus", "collection_no", "body_fossil"
    ]
    out = occ[cols]
    # ootaxa (egg parataxa: names containing 'oolith') are not skeletal
    # community members; flag for exclusion from guild matrices
    out.loc[:, "is_ootaxon"] = (
        out["genus"].fillna("").str.contains("oolith", case=False)
    )
    out.to_csv(PROCESSED / "nemegt_occurrences.csv", index=False)

    summ = pd.DataFrame(
        {
            "metric": [
                "n_occurrences_dinosaur",
                "n_occurrences_genus",
                "n_collections",
                "n_genera",
                "n_herbivore_occ",
                "n_predator_occ",
                "n_predator_genera",
                "n_herbivore_genera",
                "missing_coords",
            ],
            "value": [
                len(out),
                int(out["genus"].notna().sum()),
                int(out["collection_no"].nunique()),
                int(out["genus"].nunique()),
                int((out["guild"] == "herbivore").sum()),
                int((out["guild"] == "predator").sum()),
                int(out.loc[out["guild"] == "predator", "genus"].nunique()),
                int(out.loc[out["guild"] == "herbivore", "genus"].nunique()),
                int(out[["lng", "lat"]].isna().any(axis=1).sum()),
            ],
        }
    )
    write_table(summ, "nemegt_prep_summary.csv")
    print(summ.to_string(index=False))
    print("\nbody-fossil genus-resolved by guild:")
    b = out[out["body_fossil"] & ~out["is_ootaxon"] & out["genus"].notna()]
    print(b.groupby("guild")["genus"].count())
    print("colls:", b["collection_no"].nunique())
    print("\nPredator genera:")
    print(out[out["guild"] == "predator"].groupby("genus").size().sort_values(ascending=False))
    print("\nHerbivore genera:")
    print(out[out["guild"] == "herbivore"].groupby("genus").size().sort_values(ascending=False))


if __name__ == "__main__":
    main()
