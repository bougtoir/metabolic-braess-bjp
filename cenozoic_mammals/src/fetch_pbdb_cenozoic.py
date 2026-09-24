"""Fetch Cenozoic terrestrial mammal occurrences from PBDB (strict-replication input).

One call via the PBDB 1.2 JSON API (no auth):
occs/list?cc=NOA&base_name=Mammalia&max_ma=23&min_ma=5&show=full,coords,phylo&limit=all

Window and continent are configurable via CLI flags; defaults follow
protocols/cenozoic_mammals/config.yaml (North America, 23-5 Ma).

Writes raw CSV under data/raw/pbdb_cenozoic/ and appends a sha256 provenance
row to metadata/sources.csv.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "pbdb_cenozoic"
SOURCES = ROOT / "metadata" / "sources.csv"
BASE = "https://paleobiodb.org/data1.2"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cc", default="NOA")
    ap.add_argument("--max-ma", type=float, default=23.0)
    ap.add_argument("--min-ma", type=float, default=5.0)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    SOURCES.parent.mkdir(parents=True, exist_ok=True)

    url = (
        f"{BASE}/occs/list.json?cc={args.cc}&base_name=Mammalia"
        f"&max_ma={args.max_ma}&min_ma={args.min_ma}"
        "&show=full,coords,phylo&limit=all"
    )
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=600) as r:
        recs = json.load(r)["records"]
    print(f"occurrences: {len(recs)}")

    df = pd.DataFrame(recs)
    out = OUT / f"occurrences_{args.cc}_{args.max_ma:g}-{args.min_ma:g}ma.csv"
    df.to_csv(out, index=False)

    row = {
        "file": str(out.relative_to(ROOT)),
        "sha256": sha256(out),
        "url": url,
        "retrieved": pd.Timestamp.utcnow().isoformat(),
        "n_records": len(recs),
    }
    write_header = not SOURCES.exists()
    with SOURCES.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if write_header:
            w.writeheader()
        w.writerow(row)
    print(f"wrote {out.relative_to(ROOT)} sha256={row['sha256'][:12]}...")


if __name__ == "__main__":
    main()
