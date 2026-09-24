#!/usr/bin/env python3
"""
Download US FARS (Fatality Analysis Reporting System) national files and build a
state-day panel of traffic-crash fatalities.

Data source: NHTSA FARS, public static files
  https://static.nhtsa.gov/nhtsa/downloads/FARS/{YEAR}/National/FARS{YEAR}NationalCSV.zip

Each row of accident.csv is one fatal crash. We aggregate FATALS by
STATE x YEAR x MONTH x DAY to get daily traffic-accident deaths per state.
We also retain crash centroid (median lat/lon per state-day) for exposure QC.
"""
import os
import io
import zipfile
import urllib.request
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
os.makedirs(RAW, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

YEARS = list(range(2016, 2023))  # 2016-2022 inclusive
URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS/{y}/National/FARS{y}NationalCSV.zip"


def fetch_year(y):
    zpath = os.path.join(RAW, f"FARS{y}.zip")
    if not os.path.exists(zpath):
        print(f"  downloading FARS {y} ...", flush=True)
        urllib.request.urlretrieve(URL.format(y=y), zpath)
    with zipfile.ZipFile(zpath) as z:
        # accident file name varies in case / nesting
        names = [n for n in z.namelist() if os.path.basename(n).lower() == "accident.csv"]
        if not names:
            raise RuntimeError(f"accident.csv not found in {zpath}: {z.namelist()[:5]}")
        with z.open(names[0]) as f:
            raw = f.read()
    # FARS files switched to a UTF-8 BOM in 2021+; decode robustly.
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1").lstrip("\ufeff")
    df = pd.read_csv(io.StringIO(text), low_memory=False)
    df.columns = [c.strip().upper().lstrip("\ufeff") for c in df.columns]
    return df


def main():
    frames = []
    for y in YEARS:
        df = fetch_year(y)
        keep = ["STATE", "YEAR", "MONTH", "DAY", "DAY_WEEK", "FATALS",
                "LATITUDE", "LONGITUD"]
        df = df[[c for c in keep if c in df.columns]].copy()
        # FARS uses 88/99/98 etc as unknown for lat/lon; drop implausible
        for c in ("LATITUDE", "LONGITUD"):
            if c in df:
                df[c] = pd.to_numeric(df[c], errors="coerce")
                df.loc[(df[c].abs() > 180), c] = np.nan
        frames.append(df)
        print(f"  {y}: {len(df):,} crashes, {int(df['FATALS'].sum()):,} fatalities", flush=True)
    allc = pd.concat(frames, ignore_index=True)

    # valid calendar dates only (FARS uses 99 for unknown day/month)
    allc = allc[(allc.MONTH.between(1, 12)) & (allc.DAY.between(1, 31))].copy()
    allc["date"] = pd.to_datetime(
        dict(year=allc.YEAR, month=allc.MONTH, day=allc.DAY), errors="coerce")
    allc = allc.dropna(subset=["date"])

    panel = (allc.groupby(["STATE", "date"], as_index=False)
             .agg(deaths=("FATALS", "sum"),
                  crashes=("FATALS", "size"),
                  lat=("LATITUDE", "median"),
                  lon=("LONGITUD", "median")))
    panel["dow"] = panel.date.dt.dayofweek
    panel["year"] = panel.date.dt.year
    panel["month"] = panel.date.dt.month
    panel["doy"] = panel.date.dt.dayofyear

    out = os.path.join(PROC, "fars_state_day.csv")
    panel.to_csv(out, index=False)
    print(f"\nSaved {out}: {len(panel):,} state-days, "
          f"{int(panel.deaths.sum()):,} total fatalities, "
          f"{panel.STATE.nunique()} state codes")


if __name__ == "__main__":
    main()
