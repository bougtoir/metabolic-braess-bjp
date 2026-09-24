"""Fetch the independent Nemegt Formation validation dataset from PBDB.

Three calls, all via the PBDB 1.2 JSON API (no auth; CC0/CC-BY data):

1. Collections: colls/list, cc=MN, interval=Maastrichtian, show=full —
   filtered to formation name containing "Nemegt" (captures Nemegt and
   Nemegtian stratigraphic labels). Carries depositional environment
   (env), lithology (lt1/la1/ldc), collection type (cct/gsc/ccx) and
   taphonomy fields used for the mandatory taphonomic diagnostics.
2. Occurrences: occs/list for exactly those collection ids, show=full +
   coords + phylo, limit=all. All taxa retained; dinosaur/guild filtering
   happens in analysis/10_nemegt_prep.py.
3. Taxonomy: taxa/list base_name=Dinosauria rel=all_children show=phylo —
   parent-linked classification used to assign Theropoda ancestry.

Writes raw JSON->CSV under data/raw/nemegt_pbdb/ and appends sha256
provenance rows to metadata/sources.csv.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "nemegt_pbdb"
SOURCES = ROOT / "metadata" / "sources.csv"

BASE = "https://paleobiodb.org/data1.2"


def get(url: str) -> dict:
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    colls_url = f"{BASE}/colls/list.json?cc=MN&interval=Maastrichtian&show=full"
    colls = get(colls_url)["records"]
    nem = [c for c in colls if "emegt" in str(c.get("sfm", ""))]
    print(f"collections: {len(colls)} total, {len(nem)} Nemegt")
    coll_ids = [c["oid"].replace("col:", "") for c in nem]

    occ_url = (
        f"{BASE}/occs/list.json?coll_id={','.join(coll_ids)}"
        "&show=full,coords,phylo&limit=all"
    )
    occs = get(occ_url)["records"]
    print(f"occurrences: {len(occs)}")

    taxa_url = f"{BASE}/taxa/list.json?base_name=Dinosauria&rel=all_children&show=phylo"
    taxa = get(taxa_url)["records"]
    print(f"dinosaur taxa: {len(taxa)}")

    paths = {}
    for name, rows, url in (
        ("nemegt_collections", nem, colls_url),
        ("nemegt_occurrences", occs, occ_url),
        ("dinosauria_taxa", taxa, taxa_url),
    ):
        df = pd.DataFrame(rows)
        p = OUT / f"{name}.csv"
        df.to_csv(p, index=False)
        paths[name] = (p, url)

    SOURCES.parent.mkdir(parents=True, exist_ok=True)
    exists = SOURCES.exists()
    with SOURCES.open("a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["file", "source", "url", "sha256", "retrieved"])
        for name, (p, url) in paths.items():
            w.writerow(
                [
                    str(p.relative_to(ROOT)),
                    "PBDB 1.2 API",
                    url,
                    sha256(p),
                    pd.Timestamp.utcnow().isoformat(),
                ]
            )
            print(f"wrote {p.relative_to(ROOT)} sha256={sha256(p)[:12]}...")


if __name__ == "__main__":
    sys.exit(main())
