"""Environmental events from upwelling index + SST anomaly; attach exposures
to matched trophic units.

Primary exposure: Bakun upwelling index at 39N 125W (6-hourly, physical
forcing independent of animals). Event = upwelling pulse: UWI 24h-mean
crosses above the Apr-Oct 75th percentile after >=3 consecutive days below,
with >=7-day minimum separation between onsets. Robustness at 3d and 14d.

Outputs: outputs/tables/independent_events.csv,
         data/processed/units_with_env.parquet (units + env cols + event flags)
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "outputs/tables")
os.makedirs(OUT, exist_ok=True)

uw = pd.read_csv(os.path.join(ROOT, "data/raw/forcing/upwelling_39N125W.csv"),
                 skiprows=[1])
uw["time"] = pd.to_datetime(uw["time"], utc=True)
uw["uwi"] = pd.to_numeric(uw["upwelling_index"], errors="coerce")
uw = uw.set_index("time").sort_index()
uwi_daily = uw["uwi"].resample("1D").mean().rename("uwi_day")
uwi_7d = uwi_daily.rolling(7, min_periods=3).mean()

season = uwi_7d[(uwi_7d.index.month >= 4) & (uwi_7d.index.month <= 10)]
thr = season.quantile(0.75)

# onset detection on the DAILY series (7d-mean is too smooth for a 3-day
# prior-baseline condition); event intensity/peak measured on 7d-mean
MED = uwi_daily.median()
thr_d = uwi_daily[(uwi_daily.index.month >= 4) & (uwi_daily.index.month <= 10)].quantile(0.75)

def events_from(sep_days):
    # onset: daily UWI > seasonal 75th pct after >=3 consecutive non-null days
    # below the daily median; event ends on first day below median; peak within
    # [start, end] measured on the 7-day mean
    vals = uwi_daily
    ev = []
    i = 3
    idx = vals.index
    while i < len(vals):
        v = vals.iloc[i]
        if (pd.notna(v) and v > thr_d
                and vals.iloc[i - 3:i].notna().all()
                and (vals.iloc[i - 3:i] < MED).all()):
            if ev and (idx[i] - ev[-1]["start_date"]).days < sep_days:
                i += 1
                continue
            # find end: first day below median after onset
            j = i + 1
            while j < len(vals) and pd.notna(vals.iloc[j]) and vals.iloc[j] >= MED:
                j += 1
            seg = uwi_7d.loc[idx[i]:idx[j - 1]].dropna()
            if len(seg) == 0:
                seg = uwi_daily.loc[[idx[i]]].dropna()
            ev.append({"start_date": idx[i],
                       "end_date": idx[j - 1] if j > i + 1 else idx[i],
                       "peak_date": seg.idxmax(), "intensity": seg.max()})
            i = j
        else:
            i += 1
    out = pd.DataFrame(ev)
    if len(out):
        out["duration_d"] = (out["end_date"] - out["start_date"]).dt.days
    return out

ev7 = events_from(7)
ev7.insert(0, "event_id", ["uwi_%04d" % i for i in range(len(ev7))])
ev7["in_season"] = (ev7["start_date"].dt.month >= 4) & (ev7["start_date"].dt.month <= 10)
ev7.to_csv(os.path.join(OUT, "independent_events.csv"), index=False)

# SST box mean + climatology anomaly
sst = pd.read_csv(os.path.join(ROOT, "data/raw/erddap/oisst_access_box.csv"),
                  skiprows=[1])
sst["time"] = pd.to_datetime(sst["time"], utc=True)
sst["sst"] = pd.to_numeric(sst["sst"], errors="coerce")
sst_d = sst.groupby(sst["time"].dt.floor("D"))["sst"].mean()
clim = sst_d.groupby(sst_d.index.dayofyear).transform("mean")
sst_anom = sst_d - clim
sst_anom.index = sst_d.index

env = pd.DataFrame({"uwi": uwi_7d, "uwi_day": uwi_daily, "sst": sst_d,
                    "sst_anom": sst_anom})
env.index.name = "date"

# attach to units
u = pd.read_parquet(os.path.join(ROOT, "data/processed",
                                 "ecomega_matched_trophic_units.parquet"))
u["date"] = pd.to_datetime(u["date"], utc=True)
u = u.merge(env, left_on="date", right_index=True, how="left")
# event membership: tow falls within [start, start+21d] of an event onset
u["event_id"] = pd.NA
for _, e in ev7[ev7["in_season"]].iterrows():
    mask = (u["date"] >= e["start_date"]) & (u["date"] <= e["start_date"] + pd.Timedelta(days=21))
    u.loc[mask, "event_id"] = e["event_id"]

u.to_parquet(os.path.join(ROOT, "data/processed/units_with_env.parquet"),
             index=False)
n_ev_cov = u.dropna(subset=["krill_m3", "bird_km2"]).dropna(subset=["event_id"])["event_id"].nunique()
print("events total:", len(ev7), "| in-season:", ev7["in_season"].sum(),
      "| events w/ full trophic coverage:", n_ev_cov)
print("units:", len(u), "| matched predator+prey+env:",
      u.dropna(subset=["krill_m3", "bird_km2", "uwi"]).shape[0])
for sep in (3, 14):
    print(f"separation {sep}d -> {len(events_from(sep))} events")
