#!/usr/bin/env python3
"""
Build stratified state-day death counts from FARS person-level records, for the
Lancet-Planetary-Health additional analyses:

  * hour of day (crash HOUR band)  -> time-of-day mechanism test: is the daily
    heat-anomaly excess concentrated in the hottest part of the day (afternoon)?
  * road-user type (pedestrian / cyclist / motorcyclist / vehicle occupant)
  * age band (<25 / 25-64 / 65+)   -> who bears the burden (vulnerability/equity)

Deaths are killed persons (INJ_SEV == 4) joined to their crash (accident.csv) to
recover the calendar date, state and crash hour. Output is one long CSV:

    data/processed/fars_strata_state_day.csv
    columns: state, date, dim, val, deaths

Uses the same FARS national zips downloaded by build_fars.py (nothing extra is
downloaded here if they already exist under data/raw).
"""
import os
import io
import zipfile
import urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")

YEARS = list(range(2016, 2023))
URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS/{y}/National/FARS{y}NationalCSV.zip"


def read_member(z, basename, usecols):
    names = [n for n in z.namelist() if os.path.basename(n).lower() == basename]
    if not names:
        raise RuntimeError(f"{basename} not found: {z.namelist()[:5]}")
    with z.open(names[0]) as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1").lstrip("\ufeff")
    df = pd.read_csv(io.StringIO(text), low_memory=False)
    df.columns = [c.strip().upper().lstrip("\ufeff") for c in df.columns]
    return df[[c for c in usecols if c in df.columns]].copy()


def user_type(per_typ, body_typ):
    if per_typ == 5:
        return "pedestrian"
    if per_typ == 6:
        return "cyclist"
    if per_typ in (1, 2):
        return "motorcyclist" if 80 <= body_typ <= 89 else "vehicle_occupant"
    return "other"


def age_band(a):
    if not np.isfinite(a) or a > 120:
        return None
    if a < 25:
        return "<25"
    if a < 65:
        return "25-64"
    return "65+"


def hour_band(h):
    if not np.isfinite(h) or h > 23:
        return None
    return ["00-05", "06-11", "12-17", "18-23"][int(h) // 6]


def main():
    frames = []
    for y in YEARS:
        zpath = os.path.join(RAW, f"FARS{y}.zip")
        if not os.path.exists(zpath):
            print(f"  downloading FARS {y} ...", flush=True)
            urllib.request.urlretrieve(URL.format(y=y), zpath)
        with zipfile.ZipFile(zpath) as z:
            acc = read_member(z, "accident.csv",
                              ["STATE", "ST_CASE", "YEAR", "MONTH", "DAY", "HOUR"])
            per = read_member(z, "person.csv",
                              ["STATE", "ST_CASE", "PER_TYP", "BODY_TYP", "AGE", "INJ_SEV"])
        per = per[per.INJ_SEV == 4].copy()                    # killed persons
        acc = acc[(acc.MONTH.between(1, 12)) & (acc.DAY.between(1, 31))]
        acc["date"] = pd.to_datetime(dict(year=acc.YEAR, month=acc.MONTH, day=acc.DAY),
                                     errors="coerce")
        acc = acc.dropna(subset=["date"])
        m = per.merge(acc[["STATE", "ST_CASE", "date", "HOUR"]],
                      on=["STATE", "ST_CASE"], how="inner")
        for c in ("PER_TYP", "BODY_TYP", "AGE", "HOUR"):
            m[c] = pd.to_numeric(m[c], errors="coerce")
        m["user"] = [user_type(p, b) for p, b in zip(m.PER_TYP, m.BODY_TYP)]
        m["age"] = m.AGE.map(age_band)
        m["hour"] = m.HOUR.map(hour_band)
        frames.append(m[["STATE", "date", "user", "age", "hour"]])
        print(f"  {y}: {len(m):,} killed persons", flush=True)
    allp = pd.concat(frames, ignore_index=True).rename(columns={"STATE": "state"})

    out = []
    for dim in ("user", "age", "hour"):
        g = (allp.dropna(subset=[dim])
             .groupby(["state", "date", dim]).size().reset_index(name="deaths"))
        g = g.rename(columns={dim: "val"}); g["dim"] = dim
        out.append(g[["state", "date", "dim", "val", "deaths"]])
    res = pd.concat(out, ignore_index=True)
    path = os.path.join(PROC, "fars_strata_state_day.csv")
    res.to_csv(path, index=False)
    print(f"\nSaved {path}: {len(res):,} rows; "
          f"{int(res.deaths.sum()):,} stratified death-records across "
          f"{res['dim'].nunique()} dimensions")
    print(allp.groupby("user").size())


if __name__ == "__main__":
    main()
