"""Download daily environmental fields around Palmyra from NOAA CoastWatch ERDDAP
and build a daily gridded + spatially-summarized time series.

Products (all public, no auth):
  chlor_a  noaacwN20VIIRSchlaDaily (VIIRS NOAA-20 chl-a daily, ~0.0375 deg)
  sst      ncdcOisst21Agg_LonPM180 (OISST v2.1, daily, 0.25 deg)
  sla/ugos/vgos  nesdisSSH1day (daily gridded SSHA + geostrophic velocity, 0.25 deg)
  u_current/v_current  erdQAekm1day_LonPM180 (ASCAT Ekman current, daily;
                       coverage ends 2022-10-24)
  elevation  GEBCO_2020 (static bathymetry)
"""
import os
import subprocess
from urllib.parse import quote

import numpy as np
import pandas as pd
import xarray as xr

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw", "env")
os.makedirs(RAW, exist_ok=True)
ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"
ERDDAP2 = "https://coastwatch.noaa.gov/erddap/griddap"
T0, T1 = "2022-02-01T00:00:00Z", "2023-07-01T00:00:00Z"
LAT0, LAT1, LON0, LON1 = -2.0, 12.0, -170.0, -154.0


def q(constraints):
    return quote(constraints, safe=",?")


REQS = {
    "chl": None,  # chunked below (server 502s on large .nc requests)
    "sst": (f"{ERDDAP}/ncdcOisst21Agg_LonPM180.nc?sst"
            + q(f"[({T0}):1:({T1})][0][({LAT0}):1:({LAT1})][({LON0}):1:({LON1})]")),
    "ssh": None,
    "ekm": None,
    "gebco": (f"{ERDDAP}/GEBCO_2020.nc?elevation"
              + q(f"[({LAT0}):12:({LAT1})][({LON0}):12:({LON1})]")),
}

def download_chunked(name, base_url, varspec, extra_dims="",
                     end="2023-07-01"):
    path = os.path.join(RAW, f"{name}.nc")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print(name, "exists")
        return
    chunks = []
    t0 = pd.Timestamp("2022-02-01", tz="UTC")
    end = pd.Timestamp(end, tz="UTC")
    while t0 < end:
        t1 = min(t0 + pd.Timedelta(days=56), end)
        dst = os.path.join(RAW, f"{name}_{t0.date()}_{t1.date()}.nc")
        if not (os.path.exists(dst) and os.path.getsize(dst) > 1000):
            url = (f"{base_url}.nc?{varspec}"
                   + q(f"[({t0.strftime('%Y-%m-%dT%H:%M:%SZ')}):1:"
                       f"({t1.strftime('%Y-%m-%dT%H:%M:%SZ')})]{extra_dims}"
                       f"[({LAT0}):4:({LAT1})][({LON0}):4:({LON1})]"))
            print("downloading", name, t0.date(), t1.date())
            subprocess.run(["curl", "-sfL", "--retry", "5", "--retry-delay", "10",
                            "--max-time", "600", "-o", dst, url], check=True)
        chunks.append(dst)
        t0 = t1
    ds = xr.concat([xr.open_dataset(c) for c in chunks], dim="time")
    ds = ds.sortby("time").drop_duplicates("time")
    ds.to_netcdf(path)
    print(name, os.path.getsize(path))


download_chunked("chl", f"{ERDDAP2}/noaacwN20VIIRSchlaDaily", "chlor_a",
                 extra_dims="[0]")
for v in ("sla", "ugos", "vgos"):
    download_chunked(f"ssh_{v}", f"{ERDDAP}/nesdisSSH1day", v)
for v in ("u_current", "v_current"):
    download_chunked(f"ekm_{v}", f"{ERDDAP}/erdQAekm1day_LonPM180", v,
                     extra_dims="[0]", end="2022-10-24")

for name, url in REQS.items():
    if url is None:
        continue
    dst = os.path.join(RAW, f"{name}.nc")
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print(name, "exists")
        continue
    print("downloading", name)
    subprocess.run(["curl", "-sfL", "--retry", "3", "--max-time", "600",
                    "-o", dst, url], check=True)
    print(name, os.path.getsize(dst))


def load(name):
    return xr.open_dataset(os.path.join(RAW, f"{name}.nc"))


chl = load("chl")["chlor_a"].squeeze()
sst = load("sst")["sst"].squeeze()
ssh = xr.merge([load(f"ssh_{v}") for v in ("sla", "ugos", "vgos")])
ekm = xr.merge([load(f"ekm_{v}") for v in ("u_current", "v_current")]).squeeze()

lat = np.asarray(chl["latitude"])
lon = np.asarray(chl["longitude"])

daily = pd.DataFrame({"date": pd.to_datetime(chl["time"].values).date})
daily["chl_mean"] = chl.mean(dim=["latitude", "longitude"]).values
daily["chl_median"] = chl.median(dim=["latitude", "longitude"]).values
daily["chl_frac_missing"] = chl.isnull().mean(dim=["latitude", "longitude"]).values

# weight by concentration (positive); log10 weights would be negative for
# chl < 1 mg/m3 and invert the centroid toward low-concentration cells
w = chl.clip(min=0.01)
wsum = w.sum(dim=["latitude", "longitude"])
coords = {"latitude": chl["latitude"], "longitude": chl["longitude"]}
lat2 = xr.DataArray(np.broadcast_to(lat.reshape(-1, 1), (len(lat), len(lon))),
                    dims=["latitude", "longitude"], coords=coords)
lon2 = xr.DataArray(np.broadcast_to(lon.reshape(1, -1), (len(lat), len(lon))),
                    dims=["latitude", "longitude"], coords=coords)
daily["chl_centroid_lat"] = (w * lat2).sum(dim=["latitude", "longitude"]) / wsum
daily["chl_centroid_lon"] = (w * lon2).sum(dim=["latitude", "longitude"]) / wsum

lc = np.log10(chl.clip(min=0.01))
dlat = lc.differentiate("latitude")
dlon = lc.differentiate("longitude")
gradmag = np.hypot(dlat, dlon * np.cos(np.radians(6)))
daily["chl_gradient_mean"] = gradmag.mean(dim=["latitude", "longitude"]).values

sstd = sst.mean(dim=["latitude", "longitude"])
daily = daily.merge(pd.DataFrame({"date": pd.to_datetime(sst["time"].values).date,
                                  "sst_mean": sstd.values}), on="date", how="outer")

for v in ("sla", "ugos", "vgos"):
    d = ssh[v].mean(dim=["latitude", "longitude"])
    daily = daily.merge(pd.DataFrame({"date": pd.to_datetime(ssh["time"].values).date,
                                      f"{v}_mean": d.values}), on="date", how="outer")
eke = ((ssh["ugos"] ** 2 + ssh["vgos"] ** 2) / 2).mean(dim=["latitude", "longitude"])
daily = daily.merge(pd.DataFrame({"date": pd.to_datetime(ssh["time"].values).date,
                                  "eke_mean": eke.values}), on="date", how="outer")

for v in ("u_current", "v_current"):
    d = ekm[v].mean(dim=["latitude", "longitude"])
    daily = daily.merge(pd.DataFrame({"date": pd.to_datetime(ekm["time"].values).date,
                                      f"{v}_mean": d.values}), on="date", how="outer")
# NOTE: erdQAekm1day is NaN throughout the Palmyra region (equatorial mask)

daily = daily.sort_values("date").reset_index(drop=True)
daily.to_csv(os.path.join(ROOT, "data/processed/env_daily.csv"), index=False)
print(daily.describe().T[["count", "mean"]])
