"""Download NEON DP1.10072.001 (small mammal box trapping) mammal capture
records (mam_pertrapnight + mam_perplotnight for effort) via the NEON API.
Saves long-format site x month x species capture counts."""
import json, time, urllib.request
import pandas as pd
from pathlib import Path
from io import BytesIO

DATA = Path(__file__).resolve().parents[1] / "data" / "neon"
TOKEN = (DATA / "token.txt").read_text().strip()
BASE = "https://data.neonscience.org/api/v0"
HDR = {"X-API-Token": TOKEN}

def api(path):
    req = urllib.request.Request(BASE + path, headers=HDR)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def fetch(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

def main():
    (DATA / "cap_chunks").mkdir(parents=True, exist_ok=True)
    (DATA / "eff_chunks").mkdir(parents=True, exist_ok=True)
    done = ({p.name.split("_mam_")[0] for p in (DATA / "cap_chunks").glob("*.parquet")}
            | {p.name[:-12] for p in (DATA / "cap_chunks").glob("*_done.marker")})
    prod = api("/products/DP1.10072.001")["data"]
    t0 = time.time()
    n_done = 0
    for site in prod["siteCodes"]:
        for mo in site["availableMonths"]:
            tag = f"{site['siteCode']}_{mo}"
            if tag in done:
                continue
            try:
                files = api(f"/data/DP1.10072.001/{site['siteCode']}/{mo}")["data"]["files"]
            except Exception:
                continue
            for f in files:
                nm = f["name"]
                try:
                    if "mam_pertrapnight" in nm and "expanded" in nm:
                        d = pd.read_csv(BytesIO(fetch(f["url"])), low_memory=False, engine="python")
                        keep = [c for c in ["siteID", "collectDate", "taxonID",
                                            "plotID", "trapStatus"] if c in d]
                        d[keep].to_parquet(
                            DATA / "cap_chunks" / f"{site['siteCode']}_{mo}_{nm}.parquet",
                            index=False)
                    elif "mam_perplotnight" in nm and "expanded" in nm:
                        d = pd.read_csv(BytesIO(fetch(f["url"])), low_memory=False, engine="python")
                        keep = [c for c in ["siteID", "collectDate", "plotID",
                                            "trapNightCode", "numberOfTraps"] if c in d]
                        d[keep].to_parquet(
                            DATA / "eff_chunks" / f"{site['siteCode']}_{mo}_{nm}.parquet",
                            index=False)
                except Exception:
                    continue
            n_done += 1
            (DATA / "cap_chunks" / (tag + "_done.marker")).touch()
            if n_done % 50 == 0:
                print(n_done, "site-months,", round(time.time() - t0), "s",
                      flush=True)
    print("done", n_done)

if __name__ == "__main__":
    main()
