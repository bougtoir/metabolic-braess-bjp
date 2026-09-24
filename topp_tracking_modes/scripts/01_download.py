"""Download TOPP tracks + environmental fields.

Sources:
- TOPP Historical Tagged Animals: oceanview.pfeg.noaa.gov ERDDAP gtoppAT
  (SSM/Argos/GPS positions, species, TOPP ID, 2000-2010). Open, no auth.
- Upwelling index: coastwatch ERDDAP erdUI{lat}6hr at 33/36/39/42/45N.
- SST: ncdcOisst21Agg_LonPM180 daily, CCS box 30-48N, 235-243E, stride 4.
- Geostrophic currents: nesdisSSH1day ugos/vgos, same box, stride 2.
- Chlorophyll: erdSW2018chla8day (SeaWiFS 8-day 4km, covers 1997-2010),
  same box, stride 4. INDIRECT prey proxy.
"""
import os
import urllib.request
import urllib.parse

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data/raw")
os.makedirs(os.path.join(RAW, "forcing"), exist_ok=True)
os.makedirs(os.path.join(RAW, "erddap"), exist_ok=True)

def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print("exists:", path); return
    print("downloading", path)
    urllib.request.urlretrieve(url, path)
    print("  ->", os.path.getsize(path) // 1024, "KB")

# 1) TOPP tracks (fetched as csv0 = no header units row)
get("https://oceanview.pfeg.noaa.gov/erddap/tabledap/gtoppAT.csv0"
    "?commonName,project,toppID,serialNumber,yearDeployed,isDrifter,"
    "time,latitude,longitude",
    os.path.join(RAW, "topp_gtoppAT.csv"))

# 2) Upwelling indices at multiple latitudes (6-hourly)
for lat in (33, 36, 39, 42, 45):
    get(f"https://coastwatch.pfeg.noaa.gov/erddap/tabledap/erdUI{lat}6hr.csv"
        f"?time,upwelling_index",
        os.path.join(RAW, "forcing", f"uwi_{lat}N.csv"))

# 3) SST box 30-48N 235-243E, 2000-01-01..2010-12-31, stride 4 (~1 deg)
get("https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv"
    "?sst[(2000-01-01T00:00:00Z):1:(2010-12-31T00:00:00Z)][(0.0):1:(0.0)]"
    "[(30.0):4:(48.0)][(-125.0):4:(-117.0)]",
    os.path.join(RAW, "erddap", "oisst_ccs.csv"))

# 4) geostrophic currents u/v (TOPEX/AVISO erdTAgeo1day, ~6-day, 1992-2012,
#    longitude 0-360), stride 1 in time, stride 2 in space
get("https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdTAgeo1day.csv"
    "?u_current[(2000-01-01T00:00:00Z):1:(2010-12-31T00:00:00Z)]"
    "[(0.0):1:(0.0)][(30.0):2:(48.0)][(235.0):2:(243.0)],"
    "v_current[(2000-01-01T00:00:00Z):1:(2010-12-31T00:00:00Z)]"
    "[(0.0):1:(0.0)][(30.0):2:(48.0)][(235.0):2:(243.0)]",
    os.path.join(RAW, "erddap", "ssh_currents_ccs.csv"))

# 5) SeaWiFS chl-a 8-day, stride 8 (~0.35 deg) — per-year chunks (ERDDAP
#    request-size limit)
chl_parts = []
for y in range(2003, 2011):
    p = os.path.join(RAW, "erddap", f"seawifs_chl_ccs_{y}.csv")
    try:
        get("https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdSW2018chla8day.csv"
            f"?chlorophyll[({y}-01-01T00:00:00Z):1:({y}-12-31T00:00:00Z)]"
            "[(30.0):8:(48.0)][(-125.0):8:(-117.0)]",
            p)
        chl_parts.append(p)
    except Exception as ex:
        print("chl year failed:", y, ex)
import pandas as pd
frames = []
for p in chl_parts:
    if os.path.exists(p):
        df = pd.read_csv(p, skiprows=[1])
        frames.append(df)
pd.concat(frames).drop_duplicates(
    subset=["time", "latitude", "longitude"]).to_csv(
    os.path.join(RAW, "erddap", "seawifs_chl_ccs.csv"), index=False)
print("done")
