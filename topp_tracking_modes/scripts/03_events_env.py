"""Environmental fields + independent upwelling events + per-animal-day
exposure and response metrics.

Events: upwelling pulses at each UWI station (33-45N): daily UWI > seasonal
75th pct after >=3 days below daily median; >=7d separation; end on first day
below median. Also SST-anomaly events (cold anomalies) — sensitivity only.

Per animal-day env exposure: local UWI at nearest station, local SST anomaly,
local chl (8-day composite, INDIRECT prey proxy), geostrophic current u/v.

Outputs: outputs/tables/independent_events.csv,
         data/processed/animal_day_env.parquet
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data/raw")
OUT = os.path.join(ROOT, "outputs/tables")
PROC = os.path.join(ROOT, "data/processed")

STATIONS = {33: (-119.5, 33), 36: (-121.9, 36), 39: (-125.0, 39),
            42: (-125.6, 42), 45: (-124.4, 45)}

# ---------------- events per station ----------------
events = []
for lat, (lon, y0) in STATIONS.items():
    f = os.path.join(RAW, "forcing", f"uwi_{lat}N.csv")
    uw = pd.read_csv(f, skiprows=[1])
    uw["time"] = pd.to_datetime(uw["time"], utc=True)
    uw["uwi"] = pd.to_numeric(uw["upwelling_index"], errors="coerce")
    d = uw.set_index("time")["uwi"].resample("1D").mean()
    med = d.median()
    thr = d[(d.index.month >= 4) & (d.index.month <= 10)].quantile(0.75)
    v = d.values; idx = d.index; i = 3
    k = 0
    st_events = []  # this station's events only
    while i < len(v):
        if (not np.isnan(v[i]) and v[i] > thr
                and not np.isnan(v[i - 3:i]).any()
                and (v[i - 3:i] < med).all()):
            j = i + 1
            while j < len(v) and not np.isnan(v[j]) and v[j] >= med:
                j += 1
            # separation rule per station (7d between onsets)
            if (not st_events
                    or (idx[i] - st_events[-1]["start_date"]).days >= 7):
                seg = d.iloc[i:j].dropna()
                seg7 = d.rolling(7, min_periods=3).mean().loc[idx[i]:idx[max(i, j - 1)]].dropna()
                pk = seg7.idxmax() if len(seg7) else seg.idxmax()
                inten = seg7.max() if len(seg7) else seg.max()
                events.append({"event_id": f"uwi{lat}_{k:03d}", "station_lat": lat,
                               "lon": lon, "start_date": idx[i],
                               "end_date": idx[max(i, j - 1)],
                               "peak_date": pk, "intensity": inten,
                               "duration_d": (idx[max(i, j - 1)] - idx[i]).days,
                               "event_type": "upwelling_pulse",
                               "environmental_source": f"Bakun UWI {lat}N"})
                st_events.append(events[-1])
                k += 1
            i = j
        else:
            i += 1
ev = pd.DataFrame(events)
ev["in_season"] = (ev["start_date"].dt.month >= 4) & (ev["start_date"].dt.month <= 10)
ev.to_csv(os.path.join(OUT, "independent_events.csv"), index=False)
print("events:", len(ev), "| in-season:", ev["in_season"].sum())

# ---------------- env fields ----------------
# UWI daily per station -> long table
uwi_long = []
for lat in STATIONS:
    f = os.path.join(RAW, "forcing", f"uwi_{lat}N.csv")
    uw = pd.read_csv(f, skiprows=[1])
    uw["time"] = pd.to_datetime(uw["time"], utc=True)
    s = uw.set_index("time")["upwelling_index"].resample("1D").mean()
    uwi_long.append(s.rename(lat))
uwi_wide = pd.concat(uwi_long, axis=1)

sst = pd.read_csv(os.path.join(RAW, "erddap", "oisst_ccs.csv"), skiprows=[1])
sst["time"] = pd.to_datetime(sst["time"], utc=True)
sst["sst"] = pd.to_numeric(sst["sst"], errors="coerce")
sst["date"] = sst["time"].dt.floor("D")
clim = sst.groupby([sst["date"].dt.dayofyear, sst["latitude"],
                    sst["longitude"]])["sst"].mean().rename("sst_clim")
sst = sst.merge(clim, left_on=[sst["date"].dt.dayofyear, "latitude", "longitude"],
                right_index=True)
sst["sst_anom"] = sst["sst"] - sst["sst_clim"]
sst_grid = sst[["date", "latitude", "longitude", "sst", "sst_anom"]].dropna()
sst_grid["key"] = sst_grid["date"]

chl = pd.read_csv(os.path.join(RAW, "erddap", "seawifs_chl_ccs.csv"))
chl["time"] = pd.to_datetime(chl["time"], utc=True)
chl["chl"] = pd.to_numeric(chl["chlorophyll"], errors="coerce")
chl = chl.dropna(subset=["chl"])
chl["chl_date"] = chl["time"].dt.floor("D")

cur = pd.read_csv(os.path.join(RAW, "erddap", "ssh_currents_ccs.csv"),
                  skiprows=[1])
cur["time"] = pd.to_datetime(cur["time"], utc=True)
cur["u"] = pd.to_numeric(cur["u_current"], errors="coerce")
cur["v"] = pd.to_numeric(cur["v_current"], errors="coerce")
cur["lon180"] = cur["longitude"].where(cur["longitude"] <= 180,
                                       cur["longitude"] - 360)
cur["date"] = cur["time"].dt.floor("D")

# ---------------- animal-day env ----------------
ad = pd.read_csv(os.path.join(PROC, "topp_daily.csv"), parse_dates=["date"])
ad = ad[(ad["date"] >= "2000-01-01") & (ad["date"] <= "2010-12-31")]

# nearest-station UWI
def nearest_station(lat, lon360):
    d = {lat2: abs(lat - lat2) + abs(((lon360 % 360) - (STATIONS[lat2][0] % 360))) / 111
         for lat2 in STATIONS}
    return min(d, key=d.get)

ad["station"] = [nearest_station(r.lat, r.lon360) for r in ad.itertuples()]
for lat in STATIONS:
    ad[f"uwi_{lat}"] = ad["date"].map(uwi_wide[lat])
ad["uwi"] = [getattr(r, f"uwi_{r.station}") for r in ad.itertuples()]

# nearest grid cell via searchsorted on each grid's unique coordinate axes
def nearest_axis(vals, x):
    arr = np.sort(np.asarray(pd.unique(vals)))
    i = np.clip(np.searchsorted(arr, x), 1, len(arr) - 1)
    return arr[np.where(np.abs(arr[i] - x) < np.abs(arr[i - 1] - x), i, i - 1)]

# SST: nearest cell per (date, lat, lon360)
sg = sst_grid.rename(columns={"latitude": "slat", "longitude": "slon"})
sg["slon"] = sg["slon"] % 360
ad["g_slat"] = nearest_axis(sg["slat"], ad["lat"].values)
ad["g_slon"] = nearest_axis(sg["slon"], ad["lon360"].values)
sg["slon"] = sg["slon"].astype(float)
ad = ad.merge(sg[["date", "slat", "slon", "sst", "sst_anom"]],
              left_on=["date", "g_slat", "g_slon"],
              right_on=["date", "slat", "slon"], how="left")

# chl: nearest cell of nearest 8-day composite within +-10d
chl["clat"] = chl["latitude"]
chl["clon360"] = chl["longitude"] % 360
ad["g_clat"] = nearest_axis(chl["clat"], ad["lat"].values)
ad["g_clon"] = nearest_axis(chl["clon360"], ad["lon360"].values)
chl_by = chl.groupby(["chl_date", "clat", "clon360"])["chl"].first()
chl_dates = pd.DatetimeIndex(sorted(chl["chl_date"].unique())).values
def chl_lookup(row):
    d0 = chl_dates[np.argmin(np.abs(chl_dates - np.datetime64(row.date.tz_localize(None))))]
    v = chl_by.get((pd.Timestamp(d0, tz="UTC"), row.g_clat, row.g_clon))
    if pd.isna(v):
        for dlat in (0.33, -0.33, 0.66, -0.66):
            for dlon in (0.33, -0.33, 0.66, -0.66):
                v = chl_by.get((pd.Timestamp(d0, tz="UTC"), row.g_clat + dlat,
                                row.g_clon + dlon))
                if pd.notna(v):
                    break
            if pd.notna(v):
                break
    return v
ad["chl"] = [chl_lookup(r) for r in ad.itertuples()]

# currents: nearest cell + nearest ~6-day time step
cur["clat"] = cur["latitude"]
cur["clon360"] = cur["longitude"] % 360
cur_by = cur.groupby(["date", "clat", "clon360"])[["u", "v"]].first()
cur_dates = pd.DatetimeIndex(sorted(cur["date"].unique())).values
ad["g_ulat"] = nearest_axis(cur["clat"], ad["lat"].values)
ad["g_ulon"] = nearest_axis(cur["clon360"], ad["lon360"].values)
def cur_lookup(row):
    d0 = cur_dates[np.argmin(np.abs(cur_dates - np.datetime64(row.date.tz_localize(None))))]
    key = (pd.Timestamp(d0, tz="UTC"), row.g_ulat, row.g_ulon)
    if key in cur_by.index:
        r = cur_by.loc[key]
        return r["u"], r["v"]
    return np.nan, np.nan
uv = [cur_lookup(r) for r in ad.itertuples()]
ad[["u_cur", "v_cur"]] = pd.DataFrame(uv, index=ad.index)

# event flag: animal-day within [start, start+21d] of in-season event at its
# nearest station
ad["event_id"] = pd.NA
for _, e in ev[ev["in_season"]].iterrows():
    m = (ad["station"] == e["station_lat"]) & \
        (ad["date"] >= e["start_date"]) & \
        (ad["date"] <= e["start_date"] + pd.Timedelta(days=21))
    ad.loc[m, "event_id"] = e["event_id"]

ad.to_parquet(os.path.join(PROC, "animal_day_env.parquet"), index=False)
print("animal-days:", len(ad), "| with chl:", ad["chl"].notna().sum(),
      "| with uwi:", ad["uwi"].notna().sum(), "| in event:",
      ad["event_id"].notna().sum())
