"""00: Download Paleozoic marine occurrences from PBDB.

Cambrian-Permian, envtype=marine, per candidate clade. Raw JSON is
stored unchanged; a harmonised CSV is written alongside. Every query
URL + download time is appended to data/raw/provenance.jsonl.
"""
from __future__ import annotations

import json
import time
import urllib.request

import pandas as pd

from _common import (AGE_OLD, AGE_YOUNG, CLADES, DATA_PROC, DATA_RAW,
                     log_provenance)

BASE = "https://paleobiodb.org/data1.2"
SHOW = ("coords,paleoloc,classext,strat,lithext,env,ref,acconly")
INTERVAL = "Cambrian,Permian"

KEEP = {
    "oid": "occurrence_id", "cid": "collection_id",
    "tna": "accepted_taxon", "rnk": "accepted_rank_no",
    "tid": "taxon_id", "oei": "interval_early", "eag": "early_age",
    "lag": "late_age", "lng": "lng", "lat": "lat",
    "pln": "plng", "pla": "plat", "phl": "phylum", "cll": "class",
    "odl": "order", "fml": "family", "gnl": "genus",
    "env": "environment", "lt1": "lithology1", "sfm": "formation",
    "rid": "reference_id", "idn": "identified_name",
}


def fetch(clade: str) -> dict:
    url = (f"{BASE}/occs/list.json?base_name={clade}"
           f"&interval={INTERVAL}&envtype=marine"
           f"&taxon_status=all&show={SHOW}&limit=all")
    req = urllib.request.Request(url, headers={"User-Agent": "devin-paleo"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return url, json.loads(r.read().decode())


def main() -> None:
    for clade in CLADES:
        url, js = fetch(clade)
        raw = DATA_RAW / f"occs_{clade.lower()}.json"
        raw.write_text(json.dumps(js))
        log_provenance(clade, url, raw)
        recs = js.get("records", [])
        df = pd.DataFrame(recs)
        df = df.rename(columns={k: v for k, v in KEEP.items()
                                if k in df.columns})
        df["clade"] = clade
        df.to_csv(DATA_PROC / f"occs_{clade.lower()}.csv", index=False)
        print(f"{clade}: {len(df)} occurrences")
        time.sleep(1)

    # Stage-level (and coarser) international timescale intervals
    url = f"{BASE}/intervals/list.json?scale=1&all_records"
    with urllib.request.urlopen(url, timeout=120) as r:
        js = json.loads(r.read().decode())
    raw = DATA_RAW / "intervals_scale1.json"
    raw.write_text(json.dumps(js))
    log_provenance("intervals_scale1", url, raw)
    iv = pd.DataFrame(js["records"])
    iv = iv.rename(columns={"nam": "interval", "itp": "level",
                            "eag": "max_ma", "lag": "min_ma"})
    iv = iv[(iv["max_ma"] <= AGE_OLD) & (iv["min_ma"] >= AGE_YOUNG)]
    iv.to_csv(DATA_PROC / "intervals.csv", index=False)
    print(iv.groupby("level").size())


if __name__ == "__main__":
    main()
