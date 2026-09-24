#!/usr/bin/env python3
"""
Stratified US temperature-anomaly distributed-lag analyses (Lancet-Planetary-
Health additional analyses). For each stratum we refit the SAME primary model
(state fixed effects, division-specific season, long-term trend, day of week;
quasi-Poisson) on that stratum's daily death counts and report the same-day and
cumulative rate ratio for a +9C anomaly vs the local seasonal norm.

  * time-of-day (crash hour band)  -> mechanism: heat impairment should
    concentrate the anomaly excess in the hottest hours (early afternoon),
    whereas a pure driving-activity confounder would not.
  * road-user type and age band    -> who bears the burden (vulnerability).

Outputs:
  data/processed/us_timeofday_response.csv
  data/processed/us_subgroup_response.csv
"""
import os
import numpy as np
import pandas as pd
from analyze_us import load_panel, confounders
from model import fit_model, cumulative_curve, bin_response

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "data", "processed")


def fit_stratum(base, strata, val):
    s = strata[strata.val == val][["state", "date", "deaths"]]
    df = base.drop(columns="deaths").merge(s, on=["state", "date"], how="left")
    df["deaths"] = df.deaths.fillna(0).astype(int)
    df = df.sort_values(["state", "date"]).reset_index(drop=True)
    m = fit_model(df, "anom", confounders, group="unit")
    same = bin_response(m, 9.0, 0.0).iloc[0]
    cum = cumulative_curve(m, [9.0], 0.0).iloc[0]
    return {
        "deaths": int(df.deaths.sum()),
        "sameday_RR_+9C": round(float(same.rr), 3),
        "sameday_lo": round(float(same.lo), 3),
        "sameday_hi": round(float(same.hi), 3),
        "cumRR_+9C": round(float(cum.rr), 3),
        "cum_lo": round(float(cum.lo), 3),
        "cum_hi": round(float(cum.hi), 3),
        "dispersion_phi": round(float(m["phi"]), 3),
    }


def main():
    base = load_panel()
    st = pd.read_csv(os.path.join(PROC, "fars_strata_state_day.csv"),
                     parse_dates=["date"])
    st["state"] = st.state.astype(int)

    plans = {
        "hour": (["00-05", "06-11", "12-17", "18-23"], "us_timeofday_response.csv"),
    }
    rows = []
    for val in plans["hour"][0]:
        r = fit_stratum(base, st[st.dim == "hour"], val)
        r = {"hour_band": val, **r}
        rows.append(r)
        print(f"hour {val}: same-day RR+9C = {r['sameday_RR_+9C']} "
              f"({r['sameday_lo']}-{r['sameday_hi']}), n={r['deaths']:,}")
    pd.DataFrame(rows).to_csv(os.path.join(PROC, plans["hour"][1]), index=False)

    sub = []
    order = [("user", ["vehicle_occupant", "motorcyclist", "pedestrian", "cyclist"]),
             ("age", ["<25", "25-64", "65+"])]
    for dim, vals in order:
        for val in vals:
            r = fit_stratum(base, st[st.dim == dim], val)
            r = {"dimension": dim, "group": val, **r}
            sub.append(r)
            print(f"{dim} {val}: same-day RR+9C = {r['sameday_RR_+9C']} "
                  f"({r['sameday_lo']}-{r['sameday_hi']}), n={r['deaths']:,}")
    pd.DataFrame(sub).to_csv(os.path.join(PROC, "us_subgroup_response.csv"), index=False)


if __name__ == "__main__":
    main()
