#!/usr/bin/env python3
"""
Build the Japan prefecture x day panel (2019-2024):

  1. Traffic deaths: National Police Agency (NPA) accident-level open data
     (honhyo_YYYY.csv). Occurrence date, prefecture code and deaths per
     accident are aggregated to prefecture-day deaths. Hokkaido's five police
     area codes (10-14) are unified to a single prefecture. Prefecture code ->
     name comes from the official NPA codebook (codebook_2022.xlsx).
     Source: https://www.npa.go.jp/publications/statistics/koutsuu/opendata/

  2. Temperature: GHCN-Daily Japan stations (IDs starting 'JA') reporting both
     TMAX and TMIN over the study window. Each prefecture is assigned its K
     nearest stations (prefecture centroid = median of its accident
     coordinates); prefecture daily mean temperature = mean of (TMAX+TMIN)/2.
     Source: https://www.ncei.noaa.gov/pub/data/ghcn/daily/

All inputs are public and traceable; nothing is hard-coded.
"""
import os
import urllib.request
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
NPA = os.path.join(RAW, "npa")
PROC = os.path.join(ROOT, "data", "processed")
os.makedirs(NPA, exist_ok=True)

YEARS = list(range(2019, 2025))
K_NEAREST = 8      # more stations per prefecture -> fewer days with no data
GHCN = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
NPA_URL = "https://www.npa.go.jp/publications/statistics/koutsuu/opendata"
LAT = "地点\u3000緯度（北緯）"
LON = "地点\u3000経度（東経）"


def download(url, path):
    if not os.path.exists(path):
        print(f"  downloading {os.path.basename(path)} ...", flush=True)
        urllib.request.urlretrieve(url, path)
    return path


def latlon_to_xyz(lat, lon):
    lat = np.radians(lat); lon = np.radians(lon)
    return np.column_stack([np.cos(lat) * np.cos(lon),
                            np.cos(lat) * np.sin(lon), np.sin(lat)])


def dms(series, deg_digits):
    """NPA packed DMS string DD(D)MMSSsss -> decimal degrees."""
    s = series.astype(str).str.zfill(deg_digits + 7)
    d = s.str[:deg_digits].astype(float)
    m = s.str[deg_digits:deg_digits + 2].astype(float)
    sec = s.str[deg_digits + 2:].astype(float) / 1000.0
    return d + m / 60.0 + sec / 3600.0


def pref_code_map():
    """code (str) -> (pref_id, pref_name) from official NPA codebook."""
    cb = download(f"{NPA_URL}/2022/codebook_2022.xlsx",
                  os.path.join(NPA, "codebook_2022.xlsx"))
    t = pd.read_excel(cb, sheet_name="都道府県", header=None, dtype=str)
    t = t[[1, 2]].dropna()
    t = t[t[1].str.fullmatch(r"\d+")]
    m = {}
    for code, name in zip(t[1], t[2]):
        base = name.split("（")[0]           # strip Hokkaido area suffix
        m[code] = base
    ids = {n: i for i, n in enumerate(dict.fromkeys(m.values()))}
    return {c: (ids[n], n) for c, n in m.items()}


def load_traffic():
    cmap = pref_code_map()
    frames = []
    for y in YEARS:
        p = download(f"{NPA_URL}/{y}/honhyo_{y}.csv",
                     os.path.join(NPA, f"honhyo_{y}.csv"))
        df = pd.read_csv(p, encoding="cp932", dtype=str,
                         usecols=["都道府県コード", "死者数",
                                  "発生日時\u3000\u3000年", "発生日時\u3000\u3000月",
                                  "発生日時\u3000\u3000日", LAT, LON])
        df["deaths"] = df["死者数"].astype(int)
        df["date"] = pd.to_datetime(dict(
            year=df["発生日時\u3000\u3000年"].astype(int),
            month=df["発生日時\u3000\u3000月"].astype(int),
            day=df["発生日時\u3000\u3000日"].astype(int)), errors="coerce")
        df["pref_id"] = df["都道府県コード"].map(lambda c: cmap.get(c, (np.nan, None))[0])
        df["pref_name"] = df["都道府県コード"].map(lambda c: cmap.get(c, (np.nan, None))[1])
        df["lat"] = dms(df[LAT], 2); df["lon"] = dms(df[LON], 3)
        frames.append(df[["pref_id", "pref_name", "date", "deaths", "lat", "lon"]])
    acc = pd.concat(frames, ignore_index=True).dropna(subset=["date", "pref_id"])
    acc["pref_id"] = acc.pref_id.astype(int)
    panel = (acc.groupby(["pref_id", "pref_name", "date"], as_index=False)
             .agg(deaths=("deaths", "sum"), crashes=("deaths", "size")))
    # prefecture centroid from plausible in-Japan accident coordinates
    good = acc[(acc.lat.between(24, 46)) & (acc.lon.between(122, 154))]
    cent = (good.groupby("pref_id")
            .agg(lat=("lat", "median"), lon=("lon", "median")).reset_index())
    print(f"  traffic: {panel.deaths.sum():,} deaths, {panel.pref_id.nunique()} prefectures, "
          f"{len(panel):,} prefecture-days observed")
    return panel, cent


def load_jp_stations():
    p = download(GHCN + "ghcnd-inventory.txt", os.path.join(RAW, "ghcnd-inventory.txt"))
    rows = []
    with open(p) as f:
        for ln in f:
            if not ln.startswith("JA"):
                continue
            rows.append((ln[0:11], float(ln[12:20]), float(ln[21:30]),
                         ln[31:35].strip(), int(ln[36:40]), int(ln[41:45])))
    inv = pd.DataFrame(rows, columns=["id", "lat", "lon", "elem", "y0", "y1"])
    cover = inv[(inv.y0 <= YEARS[0]) & (inv.y1 >= YEARS[-1])]
    ok = set(cover[cover.elem == "TMAX"].id) & set(cover[cover.elem == "TMIN"].id)
    st = cover[cover.id.isin(ok)][["id", "lat", "lon"]].drop_duplicates("id").reset_index(drop=True)
    print(f"  Japan candidate stations (TMAX+TMIN, {YEARS[0]}-{YEARS[-1]}): {len(st):,}")
    return st


def load_temps(needed):
    cols = ["id", "date", "elem", "value", "m", "q", "s", "obs"]
    frames = []
    for y in YEARS:
        gz = download(GHCN + f"by_year/{y}.csv.gz", os.path.join(RAW, f"{y}.csv.gz"))
        print(f"  parsing {y}.csv.gz ...", flush=True)
        got = []
        for chunk in pd.read_csv(gz, header=None, names=cols, compression="gzip",
                                 chunksize=2_000_000, low_memory=False,
                                 usecols=[0, 1, 2, 3, 5]):
            chunk = chunk[chunk.id.isin(needed) & chunk.elem.isin(("TMAX", "TMIN"))]
            chunk = chunk[chunk.q.isna()]
            got.append(chunk[["id", "date", "elem", "value"]])
        frames.append(pd.concat(got, ignore_index=True))
    temps = pd.concat(frames, ignore_index=True)
    wide = temps.pivot_table(index=["id", "date"], columns="elem",
                             values="value", aggfunc="mean").reset_index()
    wide["tmean"] = (wide["TMAX"] + wide["TMIN"]) / 2.0 / 10.0
    wide = wide.dropna(subset=["tmean"])
    wide["date"] = pd.to_datetime(wide["date"].astype(str), format="%Y%m%d")
    return wide[["id", "date", "tmean"]]


def main():
    panel, cent = load_traffic()
    stations = load_jp_stations()
    tree = cKDTree(latlon_to_xyz(stations.lat.values, stations.lon.values))
    _, idx = tree.query(latlon_to_xyz(cent.lat.values, cent.lon.values), k=K_NEAREST)
    idx = np.atleast_2d(idx); sid = stations.id.values
    mapping = {int(cent.pref_id.iloc[i]): [sid[j] for j in idx[i]] for i in range(len(cent))}
    needed = set(s for v in mapping.values() for s in v)
    print(f"  unique nearest stations needed: {len(needed):,}")
    temps = load_temps(needed)

    rows = [(pid, s) for pid, lst in mapping.items() for s in lst]
    ps = pd.DataFrame(rows, columns=["pref_id", "id"]).merge(temps, on="id")
    pref_day = ps.groupby(["pref_id", "date"], as_index=False).tmean.mean()

    panel.to_csv(os.path.join(PROC, "jp_pref_day.csv"), index=False)
    pref_day.to_csv(os.path.join(PROC, "jp_pref_temperature.csv"), index=False)
    print(f"\nSaved jp_pref_day.csv ({len(panel):,} rows) and "
          f"jp_pref_temperature.csv ({len(pref_day):,} rows); "
          f"temp {pref_day.tmean.min():.1f} to {pref_day.tmean.max():.1f} degC")


if __name__ == "__main__":
    main()
