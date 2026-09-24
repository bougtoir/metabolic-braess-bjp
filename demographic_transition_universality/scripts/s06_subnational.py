"""Sub-national test of the 'universal' law: does one lambda-e0 curve hold *within* countries?

If the two pathways were a genuine macroscopic law, regions of the same country observed in the
same year - at nearly identical e0 - should sit on the same lambda-e0 curve. We assemble
sub-national (region-level) crude birth rate lambda and life expectancy at birth e0 for
decentralised / federal states and measure how far apart same-country regions sit on the curve.

Sources (all open):
  * Eurostat regional database (NUTS2): life expectancy at birth demo_r_mlifexp (age Y_LT1,
    sex T) and crude birth rate demo_r_gind3 (indic_de GBIRTHRT). Covers Spain, Italy and
    Germany (and other EU states). Fetched live from the Eurostat dissemination API and cached
    under data/eurostat/.
  * Human Mortality Database sub-population series (East vs West Germany; New Zealand Maori vs
    non-Maori), used by the target paper's own bundle but *excluded* from its main analysis. We
    derive annual e0 (period life table) and crude birth rate (births / exposure) and store the
    aggregated indicators (not the raw HMD micro-files, which HMD asks users not to redistribute)
    in results/subnational_hmd.csv.

Outputs: results/subnational_points.csv (one row per region-year used) and
results/subnational_summary.json (within-country dispersion of lambda at matched e0).
"""
import json
import os
import urllib.request

import numpy as np
import pandas as pd

from common import DATA_DIR, RESULTS_DIR, ensure_dirs

EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
EU_COUNTRIES = {"ES": "Spain", "IT": "Italy", "DE": "Germany", "FR": "France"}
YEAR = 2019  # most recent pre-COVID year with wide NUTS2 coverage
HMD_ROOT = os.environ.get("HMD_ROOT", "/tmp/DemographicTransition/data/hmd_countries_20251110")
US_CACHE = os.path.join(DATA_DIR, "us_states_2019.csv")
HMD_CACHE = os.path.join(RESULTS_DIR, "subnational_hmd.csv")
HMD_SPLITS = {"DEUTE": ("Germany", "East Germany"), "DEUTW": ("Germany", "West Germany"),
              "NZL_MA": ("New Zealand", "Maori"), "NZL_NM": ("New Zealand", "non-Maori")}


# ----------------------------- Eurostat ------------------------------------
def _eurostat_json(dataset, params):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{EUROSTAT}/{dataset}?{q}"
    cache = os.path.join(DATA_DIR, "eurostat", f"{dataset}_{YEAR}.json")
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    if not os.path.exists(cache):
        with urllib.request.urlopen(url, timeout=90) as r:
            data = r.read()
        with open(cache, "wb") as f:
            f.write(data)
    with open(cache, "rb") as f:
        return json.load(f)


def _jsonstat_to_frame(d, value_name):
    ids = d["id"]
    sizes = d["size"]
    geo_cat = d["dimension"]["geo"]["category"]["index"]
    geo_lab = d["dimension"]["geo"]["category"]["label"]
    inv_geo = {v: k for k, v in geo_cat.items()}
    geo_pos = ids.index("geo")
    strides = np.ones(len(sizes), dtype=int)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    rows = []
    for flat, val in d["value"].items():
        flat = int(flat)
        gi = (flat // strides[geo_pos]) % sizes[geo_pos]
        code = inv_geo[gi]
        rows.append({"geo": code, "region": geo_lab[code], value_name: val})
    return pd.DataFrame(rows)


def eurostat_subnational():
    le = _jsonstat_to_frame(
        _eurostat_json("demo_r_mlifexp",
                       {"format": "JSON", "sex": "T", "age": "Y_LT1",
                        "geoLevel": "nuts2", "time": YEAR}), "e0")
    cbr = _jsonstat_to_frame(
        _eurostat_json("demo_r_gind3",
                       {"format": "JSON", "indic_de": "GBIRTHRT",
                        "geoLevel": "nuts2", "time": YEAR}), "lambda")
    df = le.merge(cbr, on=["geo", "region"], how="inner")
    df["cc"] = df["geo"].str[:2]
    df = df[df["cc"].isin(EU_COUNTRIES)].copy()
    df["country"] = df["cc"].map(EU_COUNTRIES)
    df["unit"] = df["region"]
    df["year"] = YEAR
    df["source"] = "Eurostat NUTS2"
    return df[["country", "unit", "year", "e0", "lambda", "source"]].dropna()


# ------------------------------- USA ---------------------------------------
def usa_states():
    """US states: life expectancy at birth (NCHS/CDC, 2019) + crude birth rate (US Census
    Bureau Population Estimates component RBIRTH, 2019). Both are open; Census needs a free key."""
    key = os.environ.get("CENSUS_API_KEY")
    le_url = "https://data.cdc.gov/resource/ncvk-7amm.json?$limit=200&sex=Total"
    try:
        with urllib.request.urlopen(le_url, timeout=60) as r:
            le = pd.DataFrame(json.load(r))
    except Exception as exc:
        print("US life-expectancy fetch failed:", exc)
        return None
    le = le[["state", "leb"]].rename(columns={"state": "unit", "leb": "e0"})
    le["e0"] = pd.to_numeric(le["e0"], errors="coerce")
    le = le[le["unit"] != "United States"]

    cbr_url = "https://api.census.gov/data/2019/pep/components?get=NAME,RBIRTH&for=state:*"
    if key:
        cbr_url += f"&key={key}"
    try:
        with urllib.request.urlopen(cbr_url, timeout=60) as r:
            rows = json.load(r)
    except Exception as exc:
        print("US birth-rate fetch failed:", exc)
        return None
    cbr = pd.DataFrame(rows[1:], columns=rows[0]).rename(columns={"NAME": "unit", "RBIRTH": "lambda"})
    cbr["lambda"] = pd.to_numeric(cbr["lambda"], errors="coerce")
    df = le.merge(cbr[["unit", "lambda"]], on="unit", how="inner").dropna()
    df["country"] = "United States"
    df["year"] = YEAR
    df["source"] = "CDC/NCHS + US Census PEP"
    df = df[["country", "unit", "year", "e0", "lambda", "source"]]
    df[["unit", "e0", "lambda"]].to_csv(US_CACHE, index=False)  # refresh public cache
    return df


def usa_states_cached():
    """Offline fallback: read the committed US aggregate (CDC life expectancy + Census PEP birth
    rate, 2019) so the public repository reproduces without a Census API key or network."""
    if not os.path.exists(US_CACHE):
        return None
    df = pd.read_csv(US_CACHE)
    df["country"] = "United States"
    df["year"] = YEAR
    df["source"] = "CDC/NCHS + US Census PEP"
    return df[["country", "unit", "year", "e0", "lambda", "source"]]


# ------------------------------- HMD ---------------------------------------
def _read_hmd(path, has_age=False):
    df = pd.read_csv(path, sep=r"\s+", skiprows=2, na_values=".", engine="python")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    return df


def _total_by_year(df, cols):
    low = {c.lower(): c for c in cols}
    key = low.get("total") or low.get("both")
    if key:
        return df.groupby("Year")[key].sum()
    return df.groupby("Year")[cols].sum().sum(axis=1)


def hmd_subnational():
    if not os.path.isdir(HMD_ROOT):
        # Offline fallback: the committed derived aggregates (not the raw HMD micro-files, which
        # HMD asks users not to redistribute) let the public repository reproduce these numbers.
        if os.path.exists(HMD_CACHE):
            return pd.read_csv(HMD_CACHE)
        return None
    frames = []
    for code, (country, unit) in HMD_SPLITS.items():
        stats = os.path.join(HMD_ROOT, code, "STATS")
        try:
            births = _read_hmd(os.path.join(stats, "Births.txt"))
            expo = _read_hmd(os.path.join(stats, "Exposures_1x1.txt"), has_age=True)
            e0 = _read_hmd(os.path.join(stats, "E0per.txt"))
        except FileNotFoundError:
            continue
        b = births.rename(columns={[c for c in births.columns if c.lower() in ("total", "both")][0]: "births"})
        b = b[["Year", "births"]]
        expo_year = _total_by_year(expo, [c for c in expo.columns if c not in ("Year", "Age")]).rename("exposure").reset_index()
        e0col = [c for c in e0.columns if c.lower() in ("total", "both")][0]
        e0y = e0[["Year", e0col]].rename(columns={e0col: "e0"})
        m = b.merge(expo_year, on="Year").merge(e0y, on="Year")
        m["lambda"] = m["births"] / m["exposure"] * 1000.0
        m["country"] = country
        m["unit"] = unit
        m["source"] = "HMD sub-population"
        m = m.rename(columns={"Year": "year"})
        frames.append(m[["country", "unit", "year", "e0", "lambda", "source"]])
    if not frames:
        return None
    out = pd.concat(frames, ignore_index=True).dropna()
    out["year"] = out["year"].astype(int)
    out.to_csv(os.path.join(RESULTS_DIR, "subnational_hmd.csv"), index=False)
    return out


def within_country_dispersion(points, e0_tol=1.0):
    """For each country and year, how much does lambda vary across regions at (near-)equal e0?
    We report the mean within-country SD of lambda among regions whose e0 lies within a narrow
    band, and the residual SD around the national Phase-II isocline."""
    res = {}
    for country, g in points.groupby("country"):
        g = g.copy()
        # spread of lambda across regions in the latest common year
        yr = g["year"].max()
        gy = g[g["year"] == yr]
        if len(gy) < 3:
            continue
        # regions within a 3-year e0 window of the country median e0 (matched maturity)
        med = gy["e0"].median()
        near = gy[(gy["e0"] - med).abs() <= 3.0]
        res[country] = {
            "year": int(yr),
            "n_regions": int(len(gy)),
            "e0_min": float(gy["e0"].min()), "e0_max": float(gy["e0"].max()),
            "lambda_min": float(gy["lambda"].min()), "lambda_max": float(gy["lambda"].max()),
            "lambda_range": float(gy["lambda"].max() - gy["lambda"].min()),
            "lambda_cv_across_regions": float(gy["lambda"].std() / gy["lambda"].mean()),
            "lambda_cv_matched_e0": (float(near["lambda"].std() / near["lambda"].mean())
                                     if len(near) >= 3 else None),
            "e0_spread_matched": float(near["e0"].max() - near["e0"].min()) if len(near) >= 3 else None,
        }
    return res


def hmd_matched_contrast(hmd):
    """For each country's two HMD sub-populations, quantify how differently they sit on the
    lambda-e0 plane by comparing lambda at matched e0 (linear interpolation over the shared e0
    range). Returns the mean absolute lambda gap and its ratio to the mean lambda."""
    out = {}
    pairs = {"Germany": ("East Germany", "West Germany"),
             "New Zealand": ("Maori", "non-Maori")}
    for country, (u1, u2) in pairs.items():
        g1 = hmd[(hmd.country == country) & (hmd.unit == u1)].sort_values("e0")
        g2 = hmd[(hmd.country == country) & (hmd.unit == u2)].sort_values("e0")
        if len(g1) < 3 or len(g2) < 3:
            continue
        lo = max(g1.e0.min(), g2.e0.min())
        hi = min(g1.e0.max(), g2.e0.max())
        if hi <= lo:
            continue
        grid = np.linspace(lo, hi, 40)
        l1 = np.interp(grid, g1.e0.values, g1["lambda"].values)
        l2 = np.interp(grid, g2.e0.values, g2["lambda"].values)
        gap = np.abs(l1 - l2)
        out[country] = {
            "units": [u1, u2],
            "e0_overlap": [float(lo), float(hi)],
            "mean_abs_lambda_gap": float(gap.mean()),
            "max_abs_lambda_gap": float(gap.max()),
            "mean_rel_gap": float((gap / ((l1 + l2) / 2)).mean()),
        }
    return out


def main():
    ensure_dirs()
    parts = []
    try:
        eu = eurostat_subnational()
        parts.append(eu)
        print(f"Eurostat: {len(eu)} region-year points across {eu['country'].nunique()} countries")
    except Exception as exc:  # network / API issues are reported, not fatal
        print("Eurostat fetch failed:", exc)
    try:
        us = usa_states()
    except Exception as exc:
        print("US fetch failed:", exc)
        us = None
    if us is None:
        us = usa_states_cached()
        if us is not None:
            print("US states: using committed cache")
    if us is not None:
        parts.append(us)
        print(f"US states: {len(us)} states/DC")
    hmd = hmd_subnational()
    if hmd is not None:
        parts.append(hmd)
        print(f"HMD splits: {hmd['unit'].nunique()} sub-populations, "
              f"{hmd['year'].min()}-{hmd['year'].max()}")
    else:
        print("HMD sub-national skipped (HMD_ROOT not available)")

    points = pd.concat(parts, ignore_index=True)
    points.to_csv(os.path.join(RESULTS_DIR, "subnational_points.csv"), index=False)

    cross = points[points["source"].isin(["Eurostat NUTS2", "CDC/NCHS + US Census PEP"])]
    disp = within_country_dispersion(cross)
    with open(os.path.join(RESULTS_DIR, "subnational_summary.json"), "w") as f:
        json.dump(disp, f, indent=2)
    print(json.dumps(disp, indent=2))

    if hmd is not None:
        contrast = hmd_matched_contrast(hmd)
        with open(os.path.join(RESULTS_DIR, "subnational_hmd_contrast.json"), "w") as f:
            json.dump(contrast, f, indent=2)
        print(json.dumps(contrast, indent=2))


if __name__ == "__main__":
    main()
