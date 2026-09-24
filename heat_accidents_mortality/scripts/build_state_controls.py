#!/usr/bin/env python3
"""
Build US state-level annual controls:
  - population: Census Population Estimates Program (PEP) state totals
  - total VMT: FHWA Highway Statistics VM-2 state annual vehicle-miles travelled

Output: data/processed/state_controls.csv (state FIPS integer, year,
        population, vmt_millions).
"""
import os
import json
import re
import urllib.request
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
CENSUS_KEY = os.environ.get("CENSUS_API_KEY", "")


def fetch(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return path


def _state_fips_map():
    """Download the Census state FIPS lookup and return name->FIPS string."""
    url = "https://www2.census.gov/geo/docs/reference/state.txt"
    path = fetch(url, os.path.join(RAW, "census_state_fips.txt"))
    # header: STATE|STUSAB|STATE_NAME|STATENS
    df = pd.read_csv(path, sep="|")
    return dict(zip(df["STATE_NAME"].str.strip().str.title(),
                    df["STATE"].astype(str).str.zfill(2)))


def _census_pop(years=range(2016, 2023)):
    rows = []
    for y in years:
        if y <= 2019:
            name_col = "GEONAME" if y <= 2018 else "NAME"
            url = (f"https://api.census.gov/data/{y}/pep/population"
                   f"?get={name_col},POP&for=state:*&key={CENSUS_KEY}")
        else:
            url = (f"https://api.census.gov/data/2023/pep/charv"
                   f"?get=NAME,POP&for=state:*&YEAR={y}&MONTH=7&POPGROUP=001&key={CENSUS_KEY}")
        path = fetch(url, os.path.join(RAW, f"census_state_pop_{y}.json"))
        data = json.load(open(path))
        header, *body = data
        # state FIPS is the last field; population is second-to-last before state, but just index by header
        for r in body:
            d = dict(zip(header, r))
            state_name = d.get("GEONAME", d.get("NAME", "")).strip()
            if not state_name:
                continue
            rows.append({
                "state_name": state_name,
                "year": y,
                "population": int(d["POP"]),
            })
    return pd.DataFrame(rows)


def _fhwa_vmt(years=range(2016, 2023)):
    fips = _state_fips_map()
    rows = []
    for y in years:
        url = f"https://www.fhwa.dot.gov/policyinformation/statistics/{y}/xls/vm2.xls"
        path = fetch(url, os.path.join(RAW, f"fhwa_vm2_{y}.xls"))
        df = pd.read_excel(path, sheet_name="A", header=None, engine="xlrd")
        # locate header row containing 'STATE'
        header_idx = df[df[0].astype(str).str.strip().str.upper() == "STATE"].index
        if len(header_idx) == 0:
            raise ValueError(f"Could not locate header in FHWA VM-2 {y}")
        start = int(header_idx[0]) + 2
        total_col = df.shape[1] - 1
        for _, r in df.iloc[start:].iterrows():
            name = str(r[0]).strip()
            if not name or name.lower() in ("nan", "u.s. total", "total", "puerto rico", "grand total"):
                continue
            name = re.sub(r"\s+\(\d+\)$", "", name)
            if name.lower() == "district of columbia":
                name = "District Of Columbia"
            fips_str = fips.get(name.title())
            if not fips_str:
                continue
            try:
                vmt = float(r[total_col])
            except (TypeError, ValueError):
                continue
            rows.append({
                "state_fips": int(fips_str),
                "year": y,
                "vmt_millions": vmt,
            })
    return pd.DataFrame(rows)


def main():
    pop = _census_pop()
    vmt = _fhwa_vmt()
    out = (vmt
           .merge(pop.rename(columns={"state_name": "NAME"}), how="left",
                  left_on=["year"], right_on=["year"])
           .drop(columns=["NAME"]))
    # population merge is by state name -- safer to merge on fips
    # rebuild pop with fips
    fips = _state_fips_map()
    pop["state_fips"] = pop["state_name"].str.title().map(fips).astype(int)
    out = (vmt
           .merge(pop[["state_fips", "year", "population"]],
                  on=["state_fips", "year"], how="outer"))
    out = out.rename(columns={"state_fips": "state"})
    out = out[out.state <= 56].copy()
    out = out.sort_values(["state", "year"]).reset_index(drop=True)
    out = out[["state", "year", "population", "vmt_millions"]]
    os.makedirs(PROC, exist_ok=True)
    out.to_csv(os.path.join(PROC, "state_controls.csv"), index=False)
    print(f"saved state_controls.csv: {len(out)} state-years, "
          f"{out.population.notna().sum()} with population, "
          f"{out.vmt_millions.notna().sum()} with VMT")


if __name__ == "__main__":
    main()
