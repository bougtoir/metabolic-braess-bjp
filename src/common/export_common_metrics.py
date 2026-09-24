"""Export each system's committed result tables into the common metric schema.

Reads ONLY committed result tables — never re-runs raw analysis and never
overwrites system-specific outputs. Writes
results/common_metrics/common_metrics_<system>.csv conforming to
results/common_metrics/schema.yaml.

Usage:
    python3 src/common/export_common_metrics.py [--system NAME ...]

Systems without committed result tables (quaternary, ancient_marine as of
this branch) are skipped with a notice — their CSV is produced when their
pipeline lands.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "results" / "common_metrics"

COLUMNS = [
    "system", "era", "environment_type", "data_type", "region",
    "time_interval", "lower_trophic_definition", "higher_trophic_definition",
    "metric", "effect_estimate", "effect_scale", "lower_ci", "upper_ci",
    "p_value", "sample_size", "effect_direction", "standardized_effect",
    "sampling_pool_sensitivity", "time_aggregation_sensitivity",
    "distance_decay_effect", "temporal_lag", "observation_bias_score",
    "robustness_class", "analysis_script", "data_source", "notes",
]

NA = "NA"


def row(system, era, environment_type, data_type, region, time_interval,
        lower_trophic_definition, higher_trophic_definition, metric,
        est=NA, scale=NA, lo=NA, hi=NA, p=NA, n=NA, direction=NA,
        std=NA, pool=NA, agg=NA, decay=NA, lag=NA, bias=NA,
        robust=NA, script=NA, source=NA, notes=NA):
    return dict(zip(COLUMNS, [system, era, environment_type, data_type,
                              region, time_interval, lower_trophic_definition,
                              higher_trophic_definition, metric, est, scale,
                              lo, hi, p, n, direction, std, pool, agg, decay,
                              lag, bias, robust, script, source, notes]))


def direction_from_delta(delta, lo, hi):
    if pd.isna(delta):
        return NA
    if pd.notna(lo) and pd.notna(hi) and lo <= 0 <= hi:
        return "no detectable contrast"
    return "lower<higher" if delta > 0 else "lower>higher"


def load_series(path: Path) -> pd.Series:
    df = pd.read_csv(path, index_col=0)
    return df.iloc[:, 0]


# ---------------------------------------------------------------- dinosaur
def export_dinosaur() -> pd.DataFrame:
    base = dict(system="dinosaur", era="Late Jurassic",
                environment_type="terrestrial", data_type="fossil_occurrence",
                region="Morrison Formation (western North America)",
                time_interval="156.3-146.8 Ma",
                lower_trophic_definition="Sauropoda + Ornithischia", higher_trophic_definition="Theropoda")
    tables = ROOT / "dinosaur_migration_foodweb" / "results" / "tables"
    rows = []

    s = load_series(tables / "stage1_beta_summary.csv")
    for metric in ("simpson", "sorensen"):
        d = float(s[f"delta_beta_{metric}_overall"])
        lo, hi = float(s[f"delta_beta_{metric}_boot_lo"]), float(s[f"delta_beta_{metric}_boot_hi"])
        n_h = int(s[f"herbivore_{metric}_n_collections"])
        n_p = int(s[f"predator_{metric}_n_collections"])
        # standardized: delta / pooled within-guild sd proxy (mean beta pooled sd)
        denom = np.nanmean([s[f"herbivore_{metric}_mean_pairwise_beta"],
                            s[f"predator_{metric}_mean_pairwise_beta"]])
        rows.append(row(**base, metric=f"delta_beta_{metric}", est=d,
                        scale=f"{'Simpson' if metric=='simpson' else 'Sorensen'} turnover diff (predator - herbivore)",
                        lo=lo, hi=hi, p=float(s[f"delta_beta_{metric}_boot_p_gt0"]),
                        n=f"{n_h} herbivore / {n_p} predator collections",
                        direction=direction_from_delta(-d, -hi, -lo),  # flip to lower-higher axis
                        std=d / denom if denom else NA,
                        decay=f"mantel r herbivore={s[f'herbivore_{metric}_mantel_r']:.4f}; predator={s[f'predator_{metric}_mantel_r']:.4f}",
                        robust="A" if metric == "simpson" else NA,
                        script="dinosaur_migration_foodweb/analysis/05_beta_diversity.py",
                        source="Maidment et al. 2024 Dryad 10.5061/dryad.6m905qg77",
                        notes="H1 (predator>herbivore) falsified; reverse signal documented Stage 1b"))
    # sampling-pool sensitivity rows
    sens = pd.read_csv(tables / "stage1_sampling_sensitivity.csv")
    raw = float(sens.loc[sens.correction == "raw", "delta_beta_mean"].iloc[0])
    for _, r in sens.iterrows():
        if r["correction"] == "raw":
            continue
        rows.append(row(**base, metric="sampling_pool_sensitivity",
                        est=NA, scale="delta_beta_simpson under correction",
                        lo=r["lo95"], hi=r["hi95"], p=r["prop_gt0"],
                        pool=r["delta_beta_mean"] - raw,
                        direction=direction_from_delta(-r["delta_beta_mean"], -r["hi95"], -r["lo95"]),
                        script="dinosaur_migration_foodweb/analysis/06_sampling_bias.py",
                        source=base["region"], notes=f"correction={r['correction']}"))
    # Nemegt validation = null/negative-control row
    nem = tables / "nemegt_delta_beta.csv"
    if nem.exists():
        nd = pd.read_csv(nem)
        v = nd.iloc[0]
        est = float(v.get("delta_beta", v.get("delta_beta_full", np.nan)))
        lo = v.get("lo95", v.get("ci_lo", NA))
        hi = v.get("hi95", v.get("ci_hi", NA))
        rows.append(row(**{**base, "region": "Nemegt Formation (Mongolia)",
                           "time_interval": "Maastrichtian"},
                        metric="null_validation_nemegt", est=est,
                        scale="delta_beta_simpson (full)",
                        lo=lo, hi=hi, direction="no detectable contrast",
                        robust="D",
                        script="dinosaur_migration_foodweb/analysis/11_nemegt_validation.py",
                        source="PBDB 1.2 API", notes="preregistered independent validation; Outcome D"))
    return pd.DataFrame(rows, columns=COLUMNS)


# ------------------------------------------------------------- cenozoic
def export_cenozoic() -> pd.DataFrame | None:
    tables = ROOT / "cenozoic_mammals" / "results" / "tables"
    summ = tables / "beta_summary.csv"
    if not summ.exists():
        print("cenozoic: no results tables yet — skipped")
        return None
    base = dict(system="cenozoic", era="Cenozoic (Miocene-Pliocene)",
                environment_type="terrestrial", data_type="fossil_occurrence",
                region="North America (PBDB cc=NOA)", time_interval="23-5 Ma",
                lower_trophic_definition="herbivorous mammal orders (see protocols/cenozoic_mammals/config.yaml)",
                higher_trophic_definition="Carnivora (terrestrial)")
    s = load_series(summ)
    rows = []
    for metric in ("simpson", "sorensen"):
        d = float(s[f"delta_beta_{metric}_overall"])
        lo, hi = float(s[f"delta_beta_{metric}_boot_lo"]), float(s[f"delta_beta_{metric}_boot_hi"])
        rows.append(row(**base, metric=f"delta_beta_{metric}",
                        robust="B" if metric == "simpson" else NA,
                        est=d,
                        scale="Simpson turnover diff (predator - herbivore)" if metric == "simpson" else "Sorensen turnover diff",
                        lo=lo, hi=hi, p=float(s[f"delta_beta_{metric}_boot_p_gt0"]),
                        n=f"{int(s[f'herbivore_{metric}_n_collections'])} herbivore / {int(s[f'predator_{metric}_n_collections'])} predator collections",
                        direction=direction_from_delta(-d, -hi, -lo),
                        decay=f"mantel r herbivore={s[f'herbivore_{metric}_mantel_r']:.4f}; predator={s[f'predator_{metric}_mantel_r']:.4f}",
                        script="cenozoic_mammals/analysis/03_beta_diversity.py",
                        source="PBDB 1.2 API",
                        notes="sign replicates dinosaur (predator turnover lower) but magnitude is within the genus-pool null (quantile ~0.33) — PARTIAL" if metric == "simpson" else NA))
    sens_p = tables / "sampling_sensitivity.csv"
    if sens_p.exists():
        sens = pd.read_csv(sens_p)
        raw = float(sens.loc[sens.correction == "raw", "delta_beta_mean"].iloc[0])
        for _, r in sens.iterrows():
            if r["correction"] == "raw":
                continue
            rows.append(row(**base, metric="sampling_pool_sensitivity",
                            est=NA, scale="delta_beta_simpson under correction",
                            lo=r["lo95"], hi=r["hi95"], p=r["prop_gt0"],
                            pool=r["delta_beta_mean"] - raw,
                            direction=direction_from_delta(-r["delta_beta_mean"], -r["hi95"], -r["lo95"]),
                            script="cenozoic_mammals/analysis/04_sampling_bias.py",
                            source="PBDB 1.2 API", notes=f"correction={r['correction']}"))
    agg_p = tables / "aggregation_sensitivity.csv"
    if agg_p.exists():
        agg = pd.read_csv(agg_p)
        for _, r in agg.iterrows():
            rows.append(row(**base, metric="time_aggregation_sensitivity",
                            est=r.get("delta_beta", NA),
                            scale="delta_beta_simpson per binning",
                            agg=r.get("delta_vs_pooled", NA),
                            direction=direction_from_delta(-r.get("delta_beta", np.nan), np.nan, np.nan),
                            script="cenozoic_mammals/analysis/05_aggregation.py",
                            source="PBDB 1.2 API", notes=f"binning={r['binning']}"))
    null_p = tables / "pool_null.csv"
    if null_p.exists():
        nl = pd.read_csv(null_p)
        for _, r in nl.iterrows():
            rows.append(row(**base, metric=f"null_{r.get('null', 'pool')}",
                            est=r.get("observed", NA), scale="observed vs null quantile",
                            p=r.get("quantile", NA),
                            script="cenozoic_mammals/analysis/06_pool_null.py",
                            source="PBDB 1.2 API", notes=str(r.get("notes", NA))))
    return pd.DataFrame(rows, columns=COLUMNS)


# ------------------------------------------------------ modern terrestrial
def export_modern_terrestrial() -> pd.DataFrame | None:
    tables = ROOT / "phase9" / "results" / "tables"
    summ_p = tables / "final_116_species_summary.csv"
    if not summ_p.exists():
        print("modern_terrestrial: phase9 tables missing — skipped")
        return None
    base = dict(system="modern_terrestrial", era="modern",
                environment_type="terrestrial", data_type="survey_panel",
                region="North America (BBS)", time_interval="annual panel",
                lower_trophic_definition="not guild-coded natively", higher_trophic_definition="not guild-coded natively")
    rows = []
    summ = pd.read_csv(summ_p)
    med = summ["HG"].median()
    lo, hi = summ["HG_lo"].median(), summ["HG_hi"].median()
    rows.append(row(**base, metric="occupancy_persistence_residual",
                    est=med, scale="median History Gain after route demeaning (forward)",
                    lo=lo, hi=hi, n=len(summ),
                    direction="no detectable contrast",
                    script="phase9/src/species_hg.py",
                    source="USGS BBS",
                    notes="raw no-demean median HG_A≈0.30 collapses to ≈0.006; spatial persistence ≠ temporal memory"))
    hyst_p = tables / "matched_environment_hysteresis.csv"
    if hyst_p.exists():
        h = pd.read_csv(hyst_p)
        ab = h["eff_abundance"]
        rows.append(row(**base, metric="abundance_state_dependence",
                        est=ab.median(), scale="log-count prior-state effect (matched environment)",
                        lo=ab.quantile(0.025) if len(ab) else NA,
                        hi=ab.quantile(0.975) if len(ab) else NA,
                        n=int(h["species"].nunique()),
                        direction=NA, lag="lag-1 (1 yr)",
                        script="phase9/src/matched.py", source="USGS BBS",
                        notes="occupancy hysteresis=0 in all definable species; abundance retains state dependence"))
        rows.append(row(**base, metric="occupancy_hysteresis",
                        est=0.0, scale="matched-environment contrast",
                        n=int(h["species"].nunique()), direction="no detectable contrast",
                        script="phase9/src/matched.py", source="USGS BBS",
                        notes="falsified in all definable species"))
    return pd.DataFrame(rows, columns=COLUMNS)


# ---------------------------------------------------------- modern marine
def export_modern_marine() -> pd.DataFrame | None:
    eco = ROOT / "ecomega_trophic_propagation" / "outputs" / "tables"
    lag_p = eco / "lag_estimates.csv"
    if not lag_p.exists():
        print("modern_marine: ecomega tables missing — skipped")
        return None
    base = dict(system="modern_marine", era="modern",
                environment_type="marine", data_type="matched_survey",
                region="California Current (ACCESS)", time_interval="event-based",
                lower_trophic_definition="krill/zooplankton", higher_trophic_definition="seabirds/whales (predator sightings)")
    rows = []
    lag = pd.read_csv(lag_p)
    for _, r in lag.iterrows():
        rows.append(row(**base, metric=f"trophic_path_{str(r['link']).replace('>', '_')}",
                        est=r["coef"], scale="lag-curve coefficient", p=r["p"], n=r["n"],
                        lag=r["lag"], direction=NA,
                        script="ecomega_trophic_propagation/scripts/05_lag_placebo.py",
                        source="ACCESS surveys + NOAA ERDDAP",
                        notes="Type A (common env) vs Type B (trophic propagation) discrimination"))
    comp_p = eco / "typeA_typeB_model_comparison.csv"
    if comp_p.exists():
        comp = pd.read_csv(comp_p)
        for _, r in comp.iterrows():
            rows.append(row(**base, metric=f"model_comparison_{r['model']}",
                            est=r.get("r2", NA), scale="R2 (AIC in notes)",
                            n=r.get("n", NA),
                            script="ecomega_trophic_propagation/scripts/04_models.py",
                            source="ACCESS + ERDDAP",
                            notes=f"AIC={r.get('aic', NA)}; verdict: common-environment dominated"))
    return pd.DataFrame(rows, columns=COLUMNS)


EXPORTERS = {
    "dinosaur": export_dinosaur,
    "cenozoic": export_cenozoic,
    "modern_terrestrial": export_modern_terrestrial,
    "modern_marine": export_modern_marine,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", action="append", choices=sorted(EXPORTERS))
    args = ap.parse_args()
    systems = args.system or sorted(EXPORTERS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in systems:
        df = EXPORTERS[name]()
        if df is None or df.empty:
            continue
        out = OUT_DIR / f"common_metrics_{name}.csv"
        df.to_csv(out, index=False)
        print(f"wrote {out.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
