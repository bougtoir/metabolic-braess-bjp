"""Ingest Palmyra Bluewater Research telemetry archives into a uniform track table.

Reads data/raw/extracted/<DeploymentID>/... and emits data/processed/tracks.csv
with columns: species, individual_id, timestamp_utc, lat, lon, tracking_type,
source_file, quality.

Parser selection is by species/tag archive layout (see DATA_AUDIT.md).
"""
import glob
import os
import re

import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "extracted")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

SPECIES = {
    "CARAMB": ("Carcharhinus amblyrhynchos", "grey reef shark"),
    "CARGAL": ("Carcharhinus galapagensis", "Galapagos shark"),
    "MAKNIG": ("Makaira nigricans", "blue marlin"),
    "MOBALF": ("Mobula alfredi", "reef manta ray"),
    "THUALB": ("Thunnus albacares", "yellowfin tuna"),
    "PEPELE": ("Peponocephala electra", "melon-headed whale"),
    "TURTRU": ("Tursiops truncatus", "bottlenose dolphin"),
    "GRFR": ("Fregata minor", "great frigatebird"),
    "RFBO": ("Sula sula", "red-footed booby"),
    "SOTE": ("Onychoprion fuscatus", "sooty tern"),
}


def parse_gpe3(path):
    """MiniPAT GPE3 most-probable track (0.25-deg grid, ~12h)."""
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    hdr = next(i for i, ln in enumerate(lines) if ln.startswith("DeployID"))
    df = pd.read_csv(path, skiprows=hdr)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Most Likely Latitude": "lat",
                            "Most Likely Longitude": "lon", "Date": "ts"})
    df = df[["ts", "lat", "lon"]].dropna()
    df["timestamp_utc"] = pd.to_datetime(df["ts"].str.strip(), format="mixed",
                                         dayfirst=False, utc=True)
    df["tracking_type"] = "geolocation (GPE3)"
    df["quality"] = ""
    return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]


def parse_wc_locations(path):
    """Wildlife Computers Locations.csv (Argos + Fastloc GPS), cetacean tags."""
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["Latitude", "Longitude"])
    df["timestamp_utc"] = pd.to_datetime(
        df["Date"].str.replace(r"\.\d+ ", " ", regex=True),
        format="%H:%M:%S %d-%b-%Y", utc=True)
    df["lat"] = df["Latitude"].astype(float)
    df["lon"] = df["Longitude"].astype(float)
    df["tracking_type"] = df["Type"].astype(str).str.strip()
    df["quality"] = df["Quality"].astype(str)
    return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]


def parse_movebank_csv(path):
    """e-obs / Douglas-filter Movebank-format exports."""
    df = pd.read_csv(path, low_memory=False)
    if "algorithm-marked-outlier" in df.columns:
        df = df[df["algorithm-marked-outlier"].astype(str).str.upper() != "TRUE"]
    df = df.rename(columns={"location-long": "lon", "location-lat": "lat"})
    df = df.dropna(subset=["lat", "lon"])
    df["timestamp_utc"] = pd.to_datetime(df["timestamp"], utc=True)
    df["tracking_type"] = df.get("sensor-type", "gps")
    df["quality"] = ""
    return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]


def parse_igotu(path):
    df = pd.read_csv(path, skipinitialspace=True)
    df = df[(df["Latitude"] != 0) | (df["Longitude"] != 0)]
    df["timestamp_utc"] = pd.to_datetime(df["Date"].str.strip() + " " + df["Time"].str.strip(),
                                         format="%Y/%m/%d %H:%M:%S", utc=True)
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    df["tracking_type"] = "gps (i-gotU)"
    df["quality"] = ""
    return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]


def parse_pinpoint(path):
    df = pd.read_csv(path, encoding="latin-1")
    if "Status" not in df.columns:
        # Argos-GPS PinPoint store format: Date(dd/mm/yyyy), Time, Latitude, Longitude, Fix
        df = df.dropna(subset=["Latitude", "Longitude"])
        df = df[df["Latitude"].abs() <= 90]
        df = df[df["Fix"].astype(str).str.contains("D", na=False)]
        if "CRC" in df.columns:
            df = df[df["CRC"].astype(str).str.strip() == "OK"]
        df["timestamp_utc"] = pd.to_datetime(
            df["Date"].str.strip() + " " + df["Time"].str.strip(),
            format="%d/%m/%Y %H:%M:%S", utc=True)
        # Argos store files contain corrupt dates; deployments are 2022-2023
        df = df[(df["timestamp_utc"] >= "2022-01-01")
                & (df["timestamp_utc"] <= "2023-12-31")]
        df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
        df["tracking_type"] = "argos-gps (PinPoint)"
        df["quality"] = ""
        return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]
    df = df[df["Status"].astype(str).str.strip() == "Valid"]
    df = df.dropna(subset=["Latitude", "Longitude"])

    def fix_ts(row):
        d = pd.to_datetime(str(row["FIX-date"]).strip(), format="%y/%m/%d")
        ft = str(row["FIX-time"]).strip()          # mm:ss.s within the RTC hour
        rtc = str(row["RTC-time"]).strip()          # HH:MM:SS
        try:
            hour = int(rtc.split(":")[0])
        except Exception:
            hour = 0
        m = re.match(r"(\d+):(\d+(?:\.\d+)?)", ft)
        if m:
            minute, sec = int(m.group(1)), float(m.group(2))
        else:
            minute, sec = 0, 0.0
        return d + pd.Timedelta(hours=hour, minutes=minute, seconds=sec)

    df["timestamp_utc"] = df.apply(fix_ts, axis=1)
    df["timestamp_utc"] = df["timestamp_utc"].dt.tz_localize("UTC")
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    df["tracking_type"] = "gps (PinPoint)"
    df["quality"] = ""
    return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]


def parse_axytrek(path):
    df = pd.read_csv(path)
    df["timestamp_utc"] = pd.to_datetime(df["Date_Time_UTC"].str.replace('"', ''),
                                         format="%d/%m/%Y,%H:%M:%S", utc=True)
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    df = df.dropna(subset=["lat", "lon"])
    df["tracking_type"] = "gps (AxyTrek)"
    df["quality"] = ""
    return df[["timestamp_utc", "lat", "lon", "tracking_type", "quality"]]


def find_and_parse(deploy_dir):
    deploy = os.path.basename(deploy_dir)
    files = glob.glob(os.path.join(deploy_dir, "**", "*.csv"), recursive=True)
    base = os.path.basename
    gpe3 = [f for f in files if "GPE3" in base(f) and base(f).endswith(".csv")]
    if gpe3:
        return parse_gpe3(gpe3[0])
    daf = [f for f in files if "Douglas-Argos-Filter" in base(f)
           and base(f).endswith(".csv")]
    if daf:
        return parse_movebank_csv(daf[0])
    locs = [f for f in files if re.search(r"-\d+-Locations\.csv", base(f))]
    if locs:
        return parse_wc_locations(locs[0])
    eobs = [f for f in files if re.search(r"eobs_\d+_\d+\w*\d*\.csv", base(f))]
    if eobs:
        return parse_movebank_csv(eobs[0])
    axy = [f for f in files if "axytrek" in base(f).lower() and "geoid" not in base(f).lower()]
    if axy:
        return parse_axytrek(axy[0])
    igotu = [f for f in files if "igotu" in base(f).lower() and "geoid" not in base(f).lower()]
    if igotu:
        return parse_igotu(igotu[0])
    pp = [f for f in files if re.search(r"pinpoint_\d+\.csv", base(f))]
    if pp:
        return parse_pinpoint(pp[0])
    return None


def main():
    frames = []
    skipped = []
    for deploy_dir in sorted(glob.glob(os.path.join(RAW, "*"))):
        if not os.path.isdir(deploy_dir):
            continue
        deploy = os.path.basename(deploy_dir)
        code = deploy.split("_")[0]
        try:
            df = find_and_parse(deploy_dir)
        except Exception as e:
            print(f"PARSE FAIL {deploy}: {e}")
            df = None
        if df is None or len(df) == 0:
            skipped.append(deploy)
            continue
        df["species"] = SPECIES[code][1]
        df["species_sci"] = SPECIES[code][0]
        df["individual_id"] = deploy
        df["source_file"] = deploy
        frames.append(df)
        print(f"{deploy}: {len(df)} rows, {df['timestamp_utc'].min()} .. {df['timestamp_utc'].max()}")
    tracks = pd.concat(frames, ignore_index=True)
    tracks = tracks.dropna(subset=["timestamp_utc", "lat", "lon"])
    tracks = tracks[(tracks["lat"].between(-90, 90)) & (tracks["lon"].between(-180, 180))]
    tracks.to_csv(os.path.join(OUT, "tracks.csv"), index=False)
    print("skipped:", skipped)
    print("total", len(tracks))


if __name__ == "__main__":
    main()
