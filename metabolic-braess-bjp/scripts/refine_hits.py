"""Phase 5 refinement: fine-grid (0.05) rescan of Stage-3 hits that showed
any non-flat response, plus mechanism annotation (flux reroute table at u*).
Usage: python3 scripts/refine_hits.py <stage3_csv> <model> <cond> <sel> <mod>
"""
import sys, os, json, time
sys.path.insert(0, 'src')
import numpy as np
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis
from utils import load_config, load_model, apply_medium, set_objective
from feasibility import feasible
from state_selection import select_state
from metrics import evaluate
from scan import scan_reaction

path, MODEL, COND, SEL, MOD = (sys.argv + ["human2", "aerobic", "pfba", "fva_informed"])[1:6]
cfg = load_config()
df = pd.read_csv(path)
# hits = reactions whose objective or any metric varies across u
hits = []
for rid, g in df.groupby("reaction_id"):
    if (g[["atp_demand", "atp_per_glc", "glc_uptake", "lac_out", "total_flux"]]
            .max() - g[["atp_demand", "atp_per_glc", "glc_uptake", "lac_out", "total_flux"]].min()).max() > 1e-4:
        hits.append(rid)
print("refining", len(hits), "reactions on fine grid", flush=True)

model, _ = load_model(MODEL, cfg)
apply_medium(model, cfg, COND)
set_objective(model, cfg, "atp_demand")
ok, st, obj = feasible(model)
fluxes, _ = select_state(model, SEL, reference=None)
baseline = {"objective": obj, "fluxes": fluxes, "metrics": evaluate(model, fluxes, cfg)}

fva = flux_variability_analysis(model, reaction_list=hits,
                                fraction_of_optimum=cfg["modulation"]["fva_fraction"], processes=1)
fine = sorted(set(list(cfg["modulation"]["u_coarse"]) +
                  list(np.arange(0, 1.001, cfg["modulation"]["u_fine_step"]))))
t0 = time.time()
rows = []
for rid in hits:
    span = (float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"]))
    rows += scan_reaction(model, rid, cfg, COND, SEL, MOD, baseline, fine, span)
out = pd.DataFrame(rows)
for c, v in dict(condition=COND, state_method=SEL, mod_method=MOD, model=MODEL).items():
    out[c] = v
tag = f"{MODEL}_{COND}_{SEL}_{MOD}"
outp = f"results/scans/fine_{tag}.csv"
out.to_csv(outp, index=False)
print(f"fine rows: {len(out)} ({time.time()-t0:.0f}s) -> {outp}")
