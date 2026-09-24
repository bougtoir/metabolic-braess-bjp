"""Download ACCESS layers via GeoServer WFS (CalOOS portal, cencoos workspace)
and environmental forcing from NOAA ERDDAP.

ACCESS layers (2004-2024, Darwin Core, public):
  bird_density_2004_2024   seabird sightings, count_per_km2
  others_density_2004_2024 non-bird sightings (marine mammals etc.), count_per_km
  access_zooplankton_2024  Tucker/hoop-net zooplankton, count_per_m3
  euphasiid_geoserver      euphausiid-only zooplankton layer
Forcing:
  erdUI396hr  Bakun upwelling index 39N 125W, 6-hourly (coastwatch ERDDAP)
  ncdcOisst21Agg_LonPM180  SST, daily 0.25deg, ACCESS box 35.3-38.7N, 124-121.2W
  noaacwN20VIIRSchlaDaily  chl-a daily, same box
"""
import os
import urllib.request

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data/raw")
WFS = ("https://data.axds.co/gs/wfs?service=WFS&version=1.1.0&request=GetFeature"
       "&typeName=cencoos%3A{lyr}&outputFormat=csv")
LAYERS = ["bird_density_2004_2024", "others_density_2004_2024",
          "access_zooplankton_2024", "euphasiid_geoserver"]

os.makedirs(os.path.join(RAW, "access"), exist_ok=True)
os.makedirs(os.path.join(RAW, "forcing"), exist_ok=True)
os.makedirs(os.path.join(RAW, "erddap"), exist_ok=True)

for lyr in LAYERS:
    out = os.path.join(RAW, "access", f"{lyr}.csv")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print("exists", lyr); continue
    print("downloading", lyr)
    urllib.request.urlretrieve(WFS.format(lyr=lyr), out)
    print(" ->", os.path.getsize(out), "bytes")

def erddap_csv(dataset, constraint, out):
    url = (f"https://coastwatch.pfeg.noaa.gov/erddap/tabledap/{dataset}.csv?{constraint}")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print("exists", os.path.basename(out)); return
    print("downloading", dataset)
    urllib.request.urlretrieve(url, out)
    print(" ->", os.path.getsize(out), "bytes")

# 6-hourly upwelling index at 39N 125W (Bakun), full record
erddap_csv("erdUI396hr", "time,latitude,longitude,upwelling_index",
           os.path.join(RAW, "forcing", "upwelling_39N125W.csv"))

# SST daily over ACCESS box (griddap; LonPM180 longitudes 235.9-238.8)
sst_url = ("https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.csv"
    "?sst%5B(2004-01-01T00:00:00Z):1:(last)%5D%5B(0.0):1:(0.0)%5D"
    "%5B(35.3):1:(38.7)%5D%5B(-124.1):1:(-121.2)%5D")
out = os.path.join(RAW, "erddap", "oisst_access_box.csv")
if not (os.path.exists(out) and os.path.getsize(out) > 1000):
    print("downloading OISST box")
    urllib.request.urlretrieve(sst_url, out)
    print(" ->", os.path.getsize(out), "bytes")

print("done")
