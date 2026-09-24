#!/usr/bin/env python3
"""
Build national driving-activity controls (confounder proxies requested to guard
against the "nice-weather -> more driving" pathway):

  - Monthly US vehicle-miles travelled (VMT): FRED series TRFVOLUSM227NFWA
    (FHWA Traffic Volume Trends, seasonally UNadjusted moving VMT).
  - Weekly US finished-motor-gasoline product supplied: EIA PET.WGFUPUS2.W
    (thousand barrels/day) -- a high-frequency proxy for on-road fuel use.

Both are national/time-varying and are merged onto the state x day panel by
period. Saved as data/processed/driving_controls.csv (one row per calendar day
in the study window with vmt and gasoline columns).
"""
import os
import io
import json
import urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
EIA_KEY = os.environ.get("EIA_API_KEY", "")
START, END = "2016-01-01", "2022-12-31"


def fetch(url, path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return path


def main():
    days = pd.date_range(START, END, freq="D")
    out = pd.DataFrame({"date": days})

    # FRED monthly VMT
    vmt_p = fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=TRFVOLUSM227NFWA",
                  os.path.join(RAW, "fred_vmt.csv"))
    vmt = pd.read_csv(vmt_p)
    vmt.columns = ["date", "vmt"]
    vmt["date"] = pd.to_datetime(vmt.date)
    vmt["ym"] = vmt.date.dt.to_period("M")
    out["ym"] = out.date.dt.to_period("M")
    out = out.merge(vmt[["ym", "vmt"]], on="ym", how="left").drop(columns="ym")

    # EIA weekly gasoline product supplied
    gas_p = fetch(f"https://api.eia.gov/v2/seriesid/PET.WGFUPUS2.W?api_key={EIA_KEY}",
                  os.path.join(RAW, "eia_gasoline.json"))
    js = json.load(open(gas_p))
    gas = pd.DataFrame(js["response"]["data"])[["period", "value"]]
    gas.columns = ["date", "gasoline"]
    gas["date"] = pd.to_datetime(gas.date)
    gas = gas.sort_values("date")
    # weekly (reported for week ending 'date'); align each day to most recent report
    out = pd.merge_asof(out.sort_values("date"), gas, on="date", direction="backward")

    out["vmt"] = out.vmt.interpolate().ffill().bfill()
    out["gasoline"] = out.gasoline.interpolate().ffill().bfill()
    out.to_csv(os.path.join(PROC, "driving_controls.csv"), index=False)
    print(f"saved driving_controls.csv: {len(out)} days; "
          f"vmt {out.vmt.min():.0f}-{out.vmt.max():.0f}, "
          f"gasoline {out.gasoline.min():.0f}-{out.gasoline.max():.0f} MBBL/D")


if __name__ == "__main__":
    main()
