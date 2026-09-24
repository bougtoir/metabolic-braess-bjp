#!/usr/bin/env python3
"""
Japan analysis: does ambient heat raise daily traffic-crash mortality?

Quasi-Poisson distributed-lag models on a prefecture x day panel (2019-2024)
using NPA accident open data and GHCN-Daily Japan temperature, adjusting for
prefecture fixed effects, region-specific season (natural spline of day of
year), long-term trend and day of week. Primary model uses the local seasonal
temperature ANOMALY, decomposed over lag windows (same-day, 1-3 d, 4-10 d).

All numbers derive from the NPA + GHCN inputs; nothing is hard-coded.
"""
import os
import numpy as np
import pandas as pd
from patsy import dmatrix
from model import fit_model, cumulative_curve, bin_response, attributable, BINS, VAR_DF

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

REGION = {
    "北海道": "Hokkaido",
    "青森": "Tohoku", "岩手": "Tohoku", "宮城": "Tohoku", "秋田": "Tohoku",
    "山形": "Tohoku", "福島": "Tohoku",
    "茨城": "Kanto", "栃木": "Kanto", "群馬": "Kanto", "埼玉": "Kanto",
    "千葉": "Kanto", "東京": "Kanto", "神奈川": "Kanto",
    "新潟": "Chubu", "富山": "Chubu", "石川": "Chubu", "福井": "Chubu",
    "山梨": "Chubu", "長野": "Chubu", "岐阜": "Chubu", "静岡": "Chubu", "愛知": "Chubu",
    "三重": "Kinki", "滋賀": "Kinki", "京都": "Kinki", "大阪": "Kinki",
    "兵庫": "Kinki", "奈良": "Kinki", "和歌山": "Kinki",
    "鳥取": "Chugoku", "島根": "Chugoku", "岡山": "Chugoku", "広島": "Chugoku", "山口": "Chugoku",
    "徳島": "Shikoku", "香川": "Shikoku", "愛媛": "Shikoku", "高知": "Shikoku",
    "福岡": "Kyushu", "佐賀": "Kyushu", "長崎": "Kyushu", "熊本": "Kyushu",
    "大分": "Kyushu", "宮崎": "Kyushu", "鹿児島": "Kyushu", "沖縄": "Kyushu",
}


def load_panel():
    dth = pd.read_csv(os.path.join(PROC, "jp_pref_day.csv"), parse_dates=["date"])
    temp = pd.read_csv(os.path.join(PROC, "jp_pref_temperature.csv"), parse_dates=["date"])
    names = dth[["pref_id", "pref_name"]].drop_duplicates()
    prefs = sorted(set(dth.pref_id) & set(temp.pref_id))
    dates = pd.date_range(dth.date.min(), dth.date.max(), freq="D")
    grid = pd.MultiIndex.from_product([prefs, dates], names=["pref_id", "date"]).to_frame(index=False)
    df = grid.merge(dth[["pref_id", "date", "deaths"]], on=["pref_id", "date"], how="left")
    df["deaths"] = df.deaths.fillna(0).astype(int)
    df = df.merge(temp[["pref_id", "date", "tmean"]], on=["pref_id", "date"], how="left")
    df = df.merge(names, on="pref_id", how="left")
    df["region"] = df.pref_name.map(REGION)
    df = df.sort_values(["pref_id", "date"]).reset_index(drop=True)
    df["unit"] = df.pref_id
    df["dow"] = df.date.dt.dayofweek
    df["doy"] = df.date.dt.dayofyear
    df["t_index"] = (df.date - df.date.min()).dt.days
    n0 = len(df); df = df.dropna(subset=["tmean"]).reset_index(drop=True)
    parts = []
    for _, g in df.groupby("pref_id"):
        g = g.sort_values("date").copy()
        B = np.asarray(dmatrix("cc(doy, df=6)", g, return_type="dataframe"))
        g["clim"] = B @ np.linalg.lstsq(B, g.tmean.values, rcond=None)[0]
        parts.append(g)
    df = pd.concat(parts).sort_values(["pref_id", "date"]).reset_index(drop=True)
    df["anom"] = df.tmean - df.clim
    print(f"panel: {len(df):,} pref-days ({n0-len(df):,} dropped for missing temp), "
          f"{df.pref_id.nunique()} prefectures, {int(df.deaths.sum()):,} deaths")
    return df


def confounders(df, season_df=6):
    nyears = df.date.dt.year.nunique()
    return dmatrix("C(pref_id) + C(region):cr(doy, df=%d) + cr(t_index, df=%d) + C(dow)"
                   % (season_df, 3 * nyears), df, return_type="dataframe")


def main():
    df = load_panel()

    mabs = fit_model(df, "tmean", confounders, group="unit"); mabs["expname"] = "tmean"
    tgrid = np.linspace(*np.percentile(df.tmean, [0.5, 99.5]), 200)
    lo, hi = np.percentile(df.tmean, [1, 99])
    raw = np.array([mabs["cb"].cumulative_basis([t])[0] @ mabs["beta"] for t in tgrid])
    inr = (tgrid >= lo) & (tgrid <= hi)
    mmt = float(tgrid[np.where(inr)[0][np.argmin(raw[inr])]])
    cumulative_curve(mabs, tgrid, mmt).rename(columns={"x": "tmean"}).to_csv(
        os.path.join(PROC, "jp_exposure_response_abs.csv"), index=False)

    m = fit_model(df, "anom", confounders, group="unit"); m["expname"] = "anom"
    agrid = np.linspace(*np.percentile(df.anom, [0.5, 99.5]), 200)
    cumulative_curve(m, agrid, 0.0).rename(columns={"x": "anom"}).to_csv(
        os.path.join(PROC, "jp_anomaly_response.csv"), index=False)
    br = bin_response(m, 9.0, 0.0)
    br.to_csv(os.path.join(PROC, "jp_lag_response.csv"), index=False)

    an_hot, sims_hot = attributable(m, "anom", ref=0.0, only="hot")
    y = m["d"].deaths.values; total = int(y.sum()); nyears = m["d"].date.dt.year.nunique()
    rr9 = cumulative_curve(m, [9.0], 0.0).iloc[0]; rr_same = br.iloc[0]

    res = {
        "total_deaths": total, "years": nyears,
        "mmt_abs_degC": round(mmt, 2), "dispersion_phi": round(float(m["phi"]), 3),
        "cumRR_anom+9C": round(float(rr9.rr), 3), "cumRR_anom+9C_lo": round(float(rr9.lo), 3),
        "cumRR_anom+9C_hi": round(float(rr9.hi), 3),
        "sameday_RR_anom+9C": round(float(rr_same.rr), 3),
        "sameday_RR_anom+9C_lo": round(float(rr_same.lo), 3),
        "sameday_RR_anom+9C_hi": round(float(rr_same.hi), 3),
        "net_heat_attributable_deaths": round(float(an_hot.sum()), 1),
        "net_heat_attributable_lo": round(float(np.percentile(sims_hot, 2.5)), 1),
        "net_heat_attributable_hi": round(float(np.percentile(sims_hot, 97.5)), 1),
        "net_heat_attributable_per_year": round(float(an_hot.sum() / nyears), 1),
        "net_heat_attributable_fraction_pct": round(float(100 * an_hot.sum() / total), 3),
    }
    for a in (3, 6, 9, 12):
        c = cumulative_curve(m, [float(a)], 0.0).iloc[0]
        res[f"net_cumRR_anom+{a}C"] = f"{c.rr:.3f} ({c.lo:.3f}-{c.hi:.3f})"

    dfy = m["d"].assign(an=an_hot, year=m["d"].date.dt.year)
    per_year = dfy.groupby("year").agg(deaths=("deaths", "sum"), heat_an=("an", "sum")).reset_index()
    per_year["heat_af_pct"] = 100 * per_year.heat_an / per_year.deaths
    per_year.to_csv(os.path.join(PROC, "jp_attributable_by_year.csv"), index=False)
    pd.DataFrame([res]).to_csv(os.path.join(PROC, "jp_attributable.csv"), index=False)

    with open(os.path.join(OUT, "jp_model_summary.txt"), "w") as f:
        f.write(f"Japan temperature-anomaly distributed-lag model, bins={BINS}, var_df={VAR_DF}\n")
        f.write(f"observations: {len(y):,}  deaths: {total:,}  prefectures: {m['d'].pref_id.nunique()}\n")
        f.write(f"quasi-Poisson dispersion phi = {m['phi']:.3f}\n\n")
        f.write("Lag-window RR for a +9C anomaly vs seasonal norm:\n")
        for _, r in br.iterrows():
            f.write(f"  {r.window:9s}: {r.rr:.3f} ({r.lo:.3f}-{r.hi:.3f})\n")
        f.write("\n")
        for k, v in res.items():
            f.write(f"{k}: {v}\n")
    print(open(os.path.join(OUT, "jp_model_summary.txt")).read())


if __name__ == "__main__":
    main()
