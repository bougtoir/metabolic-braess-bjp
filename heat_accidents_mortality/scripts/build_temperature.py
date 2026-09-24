#!/usr/bin/env python3
"""
Build a population-weighted daily mean-temperature series for each US state from
GHCN-Daily, 2016-2022.

Method (standard population-weighted exposure for climate-health studies):
  1. Candidate stations = US GHCN-Daily stations reporting both TMAX and TMIN
     continuously over 2016-2022 (from ghcnd-inventory.txt).
  2. Each US county (Census 2023 Gazetteer centroid) is assigned its K nearest
     candidate stations. County daily mean temperature Tc = mean over available
     stations of (TMAX+TMIN)/2.
  3. State daily temperature = county-population-weighted mean of Tc, using
     Census 2019 Population Estimates.

Sources:
  - GHCN-Daily: https://www.ncei.noaa.gov/pub/data/ghcn/daily/
  - Census Gazetteer 2023 counties + Census PEP 2019 populations (API key).
All inputs are public and traceable; nothing is hard-coded.
"""
import os
import io
import gzip
import zipfile
import urllib.request
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
os.makedirs(RAW, exist_ok=True)
os.makedirs(PROC, exist_ok=True)

YEARS = list(range(2016, 2023))
K_NEAREST = 3
GHCN = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
GAZ = ("https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
       "2023_Gazetteer/2023_Gaz_counties_national.zip")
CENSUS_KEY = os.environ.get("CENSUS_API_KEY", "")


def download(url, path):
    if not os.path.exists(path):
        print(f"  downloading {os.path.basename(path)} ...", flush=True)
        urllib.request.urlretrieve(url, path)
    return path


def latlon_to_xyz(lat, lon):
    lat = np.radians(lat); lon = np.radians(lon)
    return np.column_stack([np.cos(lat) * np.cos(lon),
                            np.cos(lat) * np.sin(lon),
                            np.sin(lat)])


def load_stations():
    p = download(GHCN + "ghcnd-inventory.txt", os.path.join(RAW, "ghcnd-inventory.txt"))
    rows = []
    with open(p) as f:
        for ln in f:
            sid = ln[0:11]
            if not sid.startswith("US"):
                continue
            lat = float(ln[12:20]); lon = float(ln[21:30])
            elem = ln[31:35].strip(); y0 = int(ln[36:40]); y1 = int(ln[41:45])
            rows.append((sid, lat, lon, elem, y0, y1))
    inv = pd.DataFrame(rows, columns=["id", "lat", "lon", "elem", "y0", "y1"])
    cover = inv[(inv.y0 <= YEARS[0]) & (inv.y1 >= YEARS[-1])]
    ok = set(cover[cover.elem == "TMAX"].id) & set(cover[cover.elem == "TMIN"].id)
    st = (cover[cover.id.isin(ok)][["id", "lat", "lon"]]
          .drop_duplicates("id").reset_index(drop=True))
    print(f"  candidate stations (TMAX+TMIN, {YEARS[0]}-{YEARS[-1]}): {len(st):,}")
    return st


def load_counties():
    zp = download(GAZ, os.path.join(RAW, "gaz_counties.zip"))
    with zipfile.ZipFile(zp) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            gaz = pd.read_csv(f, sep="\t", dtype={"GEOID": str}, encoding="latin-1")
    gaz.columns = [c.strip() for c in gaz.columns]
    gaz = gaz.rename(columns={"INTPTLAT": "lat", "INTPTLONG": "lon"})
    gaz["lat"] = pd.to_numeric(gaz["lat"], errors="coerce")
    gaz["lon"] = pd.to_numeric(gaz["lon"], errors="coerce")
    gaz["state_fips"] = gaz.GEOID.str[:2]
    gaz["county_fips"] = gaz.GEOID.str[2:5]

    url = (f"https://api.census.gov/data/2019/pep/population?"
           f"get=POP,NAME&for=county:*&key={CENSUS_KEY}")
    pop_raw = download(url, os.path.join(RAW, "county_pop_2019.json"))
    js = pd.read_json(pop_raw)
    pop = pd.DataFrame(js.values[1:], columns=js.iloc[0])
    pop["state_fips"] = pop["state"].str.zfill(2)
    pop["county_fips"] = pop["county"].str.zfill(3)
    pop["POP"] = pd.to_numeric(pop["POP"], errors="coerce")
    gaz = gaz.merge(pop[["state_fips", "county_fips", "POP"]],
                    on=["state_fips", "county_fips"], how="left")
    # Connecticut switched to planning-region GEOIDs in 2022; the 2023 Gazetteer
    # GEOIDs no longer match the 2019 county FIPS used for population.  Fall back
    # to land area (sq mi) weighting for any county whose population is missing.
    fallback = gaz["POP"].isna() & gaz["ALAND_SQMI"].notna()
    gaz.loc[fallback, "POP"] = gaz.loc[fallback, "ALAND_SQMI"]
    if fallback.any():
        print(f"  area-weighted fallback for {int(fallback.sum()):,} counties"
              f" ({gaz.loc[fallback, 'NAME'].tolist()[:3]} ...)")
    df = gaz.dropna(subset=["lat", "lon", "POP"])
    # keep only 50 states + DC (state fips 01-56, exclude territories >= 60)
    df = df[df.state_fips.astype(int) <= 56]
    print(f"  counties with centroid+population: {len(df):,}")
    return df[["GEOID", "state_fips", "lat", "lon", "POP"]].reset_index(drop=True)


def assign_stations(counties, stations):
    tree = cKDTree(latlon_to_xyz(stations.lat.values, stations.lon.values))
    _, idx = tree.query(latlon_to_xyz(counties.lat.values, counties.lon.values),
                        k=K_NEAREST)
    idx = np.atleast_2d(idx)
    sid = stations.id.values
    mapping = {counties.GEOID.iloc[i]: [sid[j] for j in idx[i]]
               for i in range(len(counties))}
    needed = set(s for lst in mapping.values() for s in lst)
    print(f"  unique nearest stations needed: {len(needed):,}")
    return mapping, needed


def load_temps(needed):
    frames = []
    cols = ["id", "date", "elem", "value", "m", "q", "s", "obs"]
    for y in YEARS:
        gz = download(GHCN + f"by_year/{y}.csv.gz", os.path.join(RAW, f"{y}.csv.gz"))
        print(f"  parsing {y}.csv.gz ...", flush=True)
        got = []
        for chunk in pd.read_csv(gz, header=None, names=cols, compression="gzip",
                                 chunksize=2_000_000, low_memory=False,
                                 usecols=[0, 1, 2, 3, 5]):
            chunk = chunk[chunk.elem.isin(("TMAX", "TMIN", "PRCP")) & chunk.id.isin(needed)]
            chunk = chunk[chunk.q.isna()]  # drop QC-flagged
            got.append(chunk[["id", "date", "elem", "value"]])
        frames.append(pd.concat(got, ignore_index=True))
    temps = pd.concat(frames, ignore_index=True)
    wide = temps.pivot_table(index=["id", "date"], columns="elem",
                             values="value", aggfunc="mean").reset_index()
    wide["tmean"] = (wide["TMAX"] + wide["TMIN"]) / 2.0 / 10.0  # tenths degC -> degC
    # PRCP is daily total precipitation in tenths of mm
    if "PRCP" in wide.columns:
        wide["prcp"] = wide["PRCP"] / 10.0
    wide = wide.dropna(subset=["tmean"])
    wide["date"] = pd.to_datetime(wide["date"].astype(str), format="%Y%m%d")
    print(f"  station-days with tmean: {len(wide):,}")
    return wide[["id", "date", "tmean", "prcp"]]


def main():
    stations = load_stations()
    counties = load_counties()
    mapping, needed = assign_stations(counties, stations)
    temps = load_temps(needed)

    # long county-station table
    rows = []
    for geoid, sids in mapping.items():
        for sid in sids:
            rows.append((geoid, sid))
    cs = pd.DataFrame(rows, columns=["GEOID", "id"])
    cs = cs.merge(temps, on="id", how="inner")
    # county-day = mean over its assigned stations
    county_day = (cs.groupby(["GEOID", "date"], as_index=False)
                  .agg(tmean=("tmean", "mean"), prcp=("prcp", "mean")))
    county_day = county_day.merge(counties[["GEOID", "state_fips", "POP"]], on="GEOID")

    # state-day pop-weighted mean
    def wavg(g, col):
        v = g[col]
        ok = v.notna()
        if ok.any():
            return np.average(v[ok], weights=g.POP[ok])
        return np.nan

    state_day = (county_day.groupby(["state_fips", "date"])
                 .apply(lambda g: pd.Series({
                     "tmean": wavg(g, "tmean"),
                     "prcp": wavg(g, "prcp"),
                     "pop_cov": g.POP.sum()}))
                 .reset_index())

    out = os.path.join(PROC, "state_day_temperature.csv")
    state_day.to_csv(out, index=False)
    print(f"\nSaved {out}: {len(state_day):,} state-days, "
          f"{state_day.state_fips.nunique()} states, "
          f"temp range {state_day.tmean.min():.1f} to {state_day.tmean.max():.1f} degC, "
          f"prcp range {state_day.prcp.min():.1f} to {state_day.prcp.max():.1f} mm")


if __name__ == "__main__":
    main()
