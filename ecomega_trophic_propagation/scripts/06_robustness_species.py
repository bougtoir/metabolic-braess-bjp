"""LOEO stability, species-level heterogeneity, mobility test.

Outputs: outputs/tables/LOEO_results.csv, species_response_results.csv,
         metadata/species_mobility.csv, figures.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "outputs/tables")
FIG = os.path.join(ROOT, "outputs/figures")

u = pd.read_parquet(os.path.join(ROOT, "data/processed/units_with_env.parquet"))
d = u.dropna(subset=["krill_m3", "bird_km2", "uwi"]).copy()
d["P"] = np.log1p(d["bird_km2"])
d["K"] = np.log1p(d["krill_m3"])
d["E"] = d["uwi"]
d["month"] = d["time"].dt.month
d["year"] = d["time"].dt.year
d["cruise"] = d["cruise"].astype(str)
CTRL = " + C(month) + C(year)"

# ---------------- LOEO (leave-one-cruise-out, the independent sampling unit)
def head_coefs(dd):
    out = {}
    for tag, f, key in [
        ("E->P", "P ~ E" + CTRL, "E"),
        ("E->K", "K ~ E" + CTRL, "E"),
        ("K->P|E", "P ~ E + K" + CTRL, "K"),
    ]:
        try:
            m = smf.ols(f, data=dd).fit()
            out[tag] = m.params[key]
        except Exception:
            out[tag] = np.nan
    return out

full = head_coefs(d)
loeo_rows = []
cruises = d["cruise"].unique()
for c in cruises:
    est = head_coefs(d[d["cruise"] != c])
    est["left_out"] = c
    loeo_rows.append(est)
loeo = pd.DataFrame(loeo_rows)
summ = []
for tag in full:
    s = loeo[tag].dropna()
    summ.append({"estimate": tag, "full": full[tag], "loeo_min": s.min(),
                 "loeo_max": s.max(), "loeo_median": s.median(),
                 "sign_reversals": int((np.sign(s) != np.sign(full[tag])).sum()),
                 "largest_influence": loeo.loc[s.sub(full[tag]).abs().idxmax(), "left_out"]
                 if len(s) else np.nan})
loeo_df = pd.DataFrame(summ)
loeo_df.to_csv(os.path.join(OUT, "LOEO_results.csv"), index=False)
loeo.to_csv(os.path.join(OUT, "LOEO_per_cruise.csv"), index=False)

# ---------------- species-level responses ----------------
b = pd.read_csv(os.path.join(ROOT, "data/raw/access/bird_density_2004_2024.csv"),
                low_memory=False)
b["time"] = pd.to_datetime(b["eventDate"], errors="coerce", utc=True)
b["density"] = pd.to_numeric(b["count_per_km2"], errors="coerce")
b = b.dropna(subset=["time", "decimalLatitude", "decimalLongitude", "density"])
top_sp = b["vernacularName"].value_counts().head(12).index.tolist()

# tow-event matched env: map each bird event to same-day UWI
uw = pd.read_csv(os.path.join(ROOT, "data/raw/forcing/upwelling_39N125W.csv"),
                 skiprows=[1])
uw["time"] = pd.to_datetime(uw["time"], utc=True)
uw["uwi"] = pd.to_numeric(uw["upwelling_index"], errors="coerce")
uwi7 = (uw.set_index("time")["uwi"].resample("1D").mean()
          .rolling(7, min_periods=3).mean())
b["uwi"] = b["time"].dt.floor("D").map(uwi7)
b["month"] = b["time"].dt.month
b["year"] = b["time"].dt.year
b["cruise"] = (b["time"].dt.floor("D")
               .map(dict(zip(sorted(b["time"].dt.floor("D").unique()),
                             (pd.Series(sorted(b["time"].dt.floor("D").unique()))
                              .diff().dt.days > 4).cumsum()))))

MOB = {  # approximate independent mobility: typical daily range proxy (km)
    "Common Murre": 40, "Cassin's Auklet": 60, "Rhinoceros Auklet": 60,
    "Sooty Shearwater": 300, "Pink-footed Shearwater": 300,
    "Northern Fulmar": 250, "Western Gull": 40, "Brandt's Cormorant": 20,
    "Black-footed Albatross": 400, "Red-necked Phalarope": 200,
    "California Gull": 50, "Pigeon Guillemot": 10,
}
TL = {  # approximate trophic levels (fish-eaters ~4+, krill-feeders ~3.5)
    "Common Murre": 4.1, "Cassin's Auklet": 3.5, "Rhinoceros Auklet": 3.9,
    "Sooty Shearwater": 4.0, "Pink-footed Shearwater": 4.0,
    "Northern Fulmar": 3.8, "Western Gull": 3.9, "Brandt's Cormorant": 4.1,
    "Black-footed Albatross": 4.2, "Red-necked Phalarope": 3.4,
    "California Gull": 3.9, "Pigeon Guillemot": 4.0,
}
sp_rows = []
for sp in top_sp:
    sub = b[b["vernacularName"] == sp].groupby(
        ["cruise", "month", "year"]).agg(
        P=("density", "mean"), uwi=("uwi", "first")).reset_index().dropna()
    if len(sub) < 30:
        continue
    sub["P"] = np.log1p(sub["P"])
    m = smf.ols("P ~ uwi + C(month) + C(year)", data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["cruise"]})
    sp_rows.append({"species": sp, "n_cruise": len(sub),
                    "E_coef": m.params["uwi"], "E_p": m.pvalues["uwi"],
                    "mobility_km": MOB.get(sp, np.nan), "trophic_level": TL.get(sp, np.nan)})
spdf = pd.DataFrame(sp_rows)
spdf.to_csv(os.path.join(OUT, "species_response_results.csv"), index=False)

pd.DataFrame([{"species": s, "mobility_km_day": MOB[s], "trophic_level": TL[s],
               "source": "literature estimate (approximate)", "confidence": "LOW"}
              for s in MOB]).to_csv(
    os.path.join(ROOT, "metadata/species_mobility.csv"), index=False)

# mobility beyond trophic level
mm = spdf.dropna(subset=["mobility_km", "trophic_level"])
mm["lresp"] = mm["E_coef"]
m_mob = smf.ols("lresp ~ np.log(mobility_km) + trophic_level", data=mm).fit()
print(m_mob.summary().tables[1])

# LOEO figure
fig, ax = plt.subplots(figsize=(6, 4))
x = np.arange(len(loeo_df))
ax.errorbar(x, loeo_df["full"], fmt="ks", label="full")
ax.vlines(x, loeo_df["loeo_min"], loeo_df["loeo_max"], color="grey")
ax.axhline(0, color="r", lw=0.5)
ax.set_xticks(x); ax.set_xticklabels(loeo_df["estimate"])
ax.legend(); ax.set_title("LOEO stability")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "LOEO_mechanism.png"), dpi=130)

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(mm["mobility_km"], mm["E_coef"])
for _, r in mm.iterrows():
    ax.annotate(r["species"][:12], (r["mobility_km"], r["E_coef"]), fontsize=7)
ax.set_xscale("log"); ax.set_xlabel("mobility (km/day)"); ax.set_ylabel("E coef")
ax.set_title("Species env response vs mobility")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "species_mobility_response.png"), dpi=130)
print(loeo_df.to_string(index=False))
print(spdf.to_string(index=False))
