"""Pull NOAA FOSS haul + catch tables for selected groundfish species."""
import json, time, urllib.request
import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "foss"
DATA.mkdir(parents=True, exist_ok=True)
BASE = "https://apps-st.fisheries.noaa.gov/ods/foss"

def pull(table, out, q=None, limit=10000):
    rows, off = [], 0
    while True:
        url = f"{BASE}/{table}/?offset={off}&limit={limit}"
        if q:
            url += "&q=" + urllib.request.quote(q)
        with urllib.request.urlopen(url, timeout=120) as r:
            d = json.loads(r.read())
        items = d.get("items") or []
        rows += items
        print(table, off, len(items), flush=True)
        if len(items) < limit:
            break
        off += limit
        if off > 2_000_000:
            break
        time.sleep(0.3)
    df = pd.DataFrame(rows)
    df.to_parquet(out, index=False)
    print("saved", out, len(df))

def main():
    haul_out = DATA / "haul.parquet"
    if not haul_out.exists():
        pull("afsc_groundfish_survey_haul", haul_out)
    haul = pd.read_parquet(haul_out, columns=["hauljoin", "year", "srvy",
                                            "latitude_dd_start", "longitude_dd_start",
                                            "bottom_temperature_c", "surface_temperature_c",
                                            "depth_m"])
    hj = set(haul.hauljoin)
    # prespecified common groundfish species codes
    SPP = {"21740": "walleye_pollock", "21720": "pacific_cod",
           "10210": "yellowfin_sole", "10220": "northern_rock_sole",
           "10110": "arrowtooth_flounder", "10120": "pacific_halibut"}
    for code, name in SPP.items():
        out = DATA / f"catch_{name}.parquet"
        if out.exists():
            continue
        pull("afsc_groundfish_survey_catch", out,
             q=f'{{"species_code":{code}}}')
        c = pd.read_parquet(out)
        c = c[c.hauljoin.isin(hj)]
        c.to_parquet(out, index=False)

if __name__ == "__main__":
    main()
