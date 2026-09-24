#!/usr/bin/env python3
"""
Build population-weighted daily humidity/heat-stress metrics for each US state
from GHCN-Daily, 2016-2022.

GHCN-Daily elements:
  ADPT = average dew point temperature (tenths of degC)
  RHAV = average relative humidity (%)
  AWBT = average wet-bulb temperature (tenths of degC)

Computed at the station-day level:
  dewpoint_C = ADPT / 10
  rh         = RHAV
  wetbulb_C  = AWBT / 10
  humidex_C  = air T_C + 0.5555*(e - 10), where e = 6.11*exp(5417.7530*(1/273.16 - 1/(273.15+dewpoint_C)))
  heat_index_C = NOAA heat index converted back to degC, from T_C and RHAV

State values are county-population-weighted means of the station metrics using
the same K-nearest-station assignment as the temperature build.

Output: data/processed/state_day_humidity.csv
"""
import os
import gzip
import zipfile
import urllib.request
import math
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")

YEARS = list(range(2016, 2023))
K_NEAREST = 3
GHCN = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
GAZ = ("https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
       "2023_Gazetteer/2023_Gaz_counties_national.zip")


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

    import json
    key = os.environ.get("CENSUS_API_KEY", "")
    url = (f"https://api.census.gov/data/2019/pep/population?"
           f"get=POP,NAME&for=county:*&key={key}")
    pop_raw = download(url, os.path.join(RAW, "county_pop_2019.json"))
    js = pd.read_json(pop_raw)
    pop = pd.DataFrame(js.values[1:], columns=js.iloc[0])
    pop["state_fips"] = pop["state"].str.zfill(2)
    pop["county_fips"] = pop["county"].str.zfill(3)
    pop["POP"] = pd.to_numeric(pop["POP"], errors="coerce")
    gaz = gaz.merge(pop[["state_fips", "county_fips", "POP"]],
                    on=["state_fips", "county_fips"], how="left")
    # Connecticut planning-region GEOIDs do not match 2019 county FIPS; fall back
    # to land area (sq mi) weighting when population is unavailable.
    fallback = gaz["POP"].isna() & gaz["ALAND_SQMI"].notna()
    gaz.loc[fallback, "POP"] = gaz.loc[fallback, "ALAND_SQMI"]
    if fallback.any():
        print(f"  area-weighted fallback for {int(fallback.sum()):,} counties")
    df = gaz.dropna(subset=["lat", "lon", "POP"])
    df = df[df.state_fips.astype(int) <= 56]
    print(f"  counties with centroid+population: {len(df):,}")
    return df[["GEOID", "state_fips", "lat", "lon", "POP"]].reset_index(drop=True)


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
    ok = (set(cover[cover.elem == "TMAX"].id) &
          set(cover[cover.elem == "TMIN"].id) &
          set(cover[cover.elem == "ADPT"].id) &
          set(cover[cover.elem == "RHAV"].id) &
          set(cover[cover.elem == "AWBT"].id))
    st = (cover[cover.id.isin(ok)][["id", "lat", "lon"]]
          .drop_duplicates("id").reset_index(drop=True))
    print(f"  candidate humidity stations (TMAX/TMIN/ADPT/RHAV/AWBT, "
          f"{YEARS[0]}-{YEARS[-1]}): {len(st):,}")
    return st


def assign_stations(counties, stations):
    tree = cKDTree(latlon_to_xyz(stations.lat.values, stations.lon.values))
    _, idx = tree.query(latlon_to_xyz(counties.lat.values, counties.lon.values),
                        k=K_NEAREST)
    idx = np.atleast_2d(idx)
    sid = stations.id.values
    mapping = {counties.GEOID.iloc[i]: [sid[j] for j in idx[i]]
               for i in range(len(counties))}
    needed = set(s for lst in mapping.values() for s in lst)
    print(f"  unique nearest humidity stations needed: {len(needed):,}")
    return mapping, needed


def _heat_index_f(t_f, rh):
    """NOAA heat index in degF; simplified (no low-RH adjustment)."""
    if t_f < 80 or rh <= 0:
        return t_f
    hi = (-42.379 + 2.04901523 * t_f + 10.14333127 * rh
          - 0.22475541 * t_f * rh - 6.83783e-3 * t_f**2
          - 5.481717e-2 * rh**2 + 1.22874e-3 * t_f**2 * rh
          + 8.5282e-4 * t_f * rh**2 - 1.99e-6 * t_f**2 * rh**2)
    return hi


def _fahrenheit_to_celsius(f):
    return (f - 32.0) * 5.0 / 9.0


def _humidex(t_c, dew_c):
    e = 6.11 * math.exp(5417.7530 * (1.0 / 273.16 - 1.0 / (273.15 + dew_c)))
    return t_c + 0.5555 * (e - 10.0)


def _wbgt_approx(t_c, wet_c):
    # simple approximation: 70% wet-bulb + 30% air temperature
    return 0.7 * wet_c + 0.3 * t_c


def load_humidity(needed):
    frames = []
    cols = ["id", "date", "elem", "value", "m", "q", "s", "obs"]
    for y in YEARS:
        gz = download(GHCN + f"by_year/{y}.csv.gz", os.path.join(RAW, f"{y}.csv.gz"))
        print(f"  parsing {y}.csv.gz for humidity ...", flush=True)
        got = []
        for chunk in pd.read_csv(gz, header=None, names=cols, compression="gzip",
                                 chunksize=2_000_000, low_memory=False,
                                 usecols=[0, 1, 2, 3, 5]):
            chunk = chunk[chunk.elem.isin(("TMAX", "TMIN", "ADPT", "RHAV", "AWBT")) &
                         chunk.id.isin(needed)]
            chunk = chunk[chunk.q.isna()]
            got.append(chunk[["id", "date", "elem", "value"]])
        frames.append(pd.concat(got, ignore_index=True))
    hum = pd.concat(frames, ignore_index=True)
    wide = hum.pivot_table(index=["id", "date"], columns="elem",
                           values="value", aggfunc="mean").reset_index()
    wide["tmean"] = (wide["TMAX"] + wide["TMIN"]) / 2.0 / 10.0
    wide["dewpoint"] = wide["ADPT"] / 10.0
    wide["rh"] = wide["RHAV"]
    wide["wetbulb"] = wide["AWBT"] / 10.0
    wide = wide.dropna(subset=["tmean", "dewpoint", "rh", "wetbulb"])
    wide["date"] = pd.to_datetime(wide["date"].astype(str), format="%Y%m%d")

    wide["humidex"] = wide.apply(lambda r: _humidex(r["tmean"], r["dewpoint"]), axis=1)
    wide["heat_index"] = wide.apply(
        lambda r: _fahrenheit_to_celsius(_heat_index_f(r["tmean"] * 9.0 / 5.0 + 32.0,
                                                          r["rh"])), axis=1)
    wide["wbgt_est"] = wide.apply(lambda r: _wbgt_approx(r["tmean"], r["wetbulb"]), axis=1)
    print(f"  station-days with humidity metrics: {len(wide):,}")
    return wide[["id", "date", "tmean", "dewpoint", "rh", "wetbulb",
                 "humidex", "heat_index", "wbgt_est"]]


def main():
    stations = load_stations()
    counties = load_counties()
    mapping, needed = assign_stations(counties, stations)
    hum = load_humidity(needed)

    rows = []
    for geoid, sids in mapping.items():
        for sid in sids:
            rows.append((geoid, sid))
    cs = pd.DataFrame(rows, columns=["GEOID", "id"])
    cs = cs.merge(hum, on="id", how="inner")
    # county-day mean over assigned stations
    county_day = (cs.groupby(["GEOID", "date"], as_index=False)
                  .agg({c: "mean" for c in ["tmean", "dewpoint", "rh", "wetbulb",
                                             "humidex", "heat_index", "wbgt_est"]}))
    county_day = county_day.merge(counties[["GEOID", "state_fips", "POP"]], on="GEOID")

    def wavg(g, col):
        v = g[col]
        ok = v.notna()
        if ok.any():
            return np.average(v[ok], weights=g.POP[ok])
        return np.nan

    outcols = ["tmean_hum", "dewpoint", "rh", "wetbulb", "humidex", "heat_index", "wbgt_est"]
    def agg(g):
        return pd.Series({c: wavg(g, c) for c in ["tmean", "dewpoint", "rh", "wetbulb",
                                                    "humidex", "heat_index", "wbgt_est"]}
                         | {"pop_cov": g.POP.sum()})
    state_day = (county_day.groupby(["state_fips", "date"])
                 .apply(lambda g: agg(g))
                 .reset_index())
    state_day = state_day.rename(columns={"tmean": "tmean_hum"})

    os.makedirs(PROC, exist_ok=True)
    out = os.path.join(PROC, "state_day_humidity.csv")
    state_day.to_csv(out, index=False)
    print(f"\nSaved {out}: {len(state_day):,} state-days, "
          f"{state_day.state_fips.nunique()} states")


if __name__ == "__main__":
    main()
