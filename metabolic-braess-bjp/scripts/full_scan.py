"""Phase 4 staged full-genome scan.

Stage 1: FVA over all eligible non-boundary reactions (fraction_of_optimum
         from config) -> reactions with nonzero near-optimal span.
Stage 2: u=1 (full capacity block) single-LP test per spanned reaction ->
         reactions that change any endpoint > threshold.
Stage 3: full coarse u-grid scan on Stage-2 hits (scan.scan_reaction).
Outputs: results/scans/full_{model}_{cond}_{sel}_{mod}_stage{1,2,3}.csv
"""
import sys, os, time, json
sys.path.insert(0, 'src')
import numpy as np
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis
from utils import load_config, load_model, apply_medium, set_objective
from feasibility import feasible
from state_selection import select_state
from inhibition import apply_modulation
from metrics import evaluate, METRIC_META
from scan import eligible_reactions, scan_reaction

MODEL = sys.argv[1] if len(sys.argv) > 1 else "human2"
COND = sys.argv[2] if len(sys.argv) > 2 else "aerobic"
SEL = sys.argv[3] if len(sys.argv) > 3 else "pfba"
MOD = sys.argv[4] if len(sys.argv) > 4 else "fva_informed"
TOP_HIT_FRAC = 0.01   # >1% change in any endpoint counts as a stage-2 hit

cfg = load_config()
model, spec = load_model(MODEL, cfg)
apply_medium(model, cfg, COND)
set_objective(model, cfg, "atp_demand")
tag = f"{MODEL}_{COND}_{SEL}_{MOD}"
outdir = "results/scans"
os.makedirs(outdir, exist_ok=True)

rids = [rid for rid, why in eligible_reactions(model, cfg) if why is None]
print("eligible:", len(rids), flush=True)

# baseline
ok, status, obj = feasible(model)
assert ok, status
fluxes, _ = select_state(model, SEL, reference=None)
baseline = {"objective": obj, "fluxes": fluxes, "metrics": evaluate(model, fluxes, cfg)}
print("baseline metrics:", json.dumps(baseline["metrics"], default=float), flush=True)

# Stage 1: FVA spans (cached)
t0 = time.time()
fva_path = f"{outdir}/full_{tag}_stage1_fva.csv"
if os.path.exists(fva_path):
    fva = pd.read_csv(fva_path, index_col=0)
else:
    fva = flux_variability_analysis(model, reaction_list=rids,
                                    fraction_of_optimum=cfg["modulation"]["fva_fraction"],
                                    processes=1)
    fva.to_csv(fva_path)
spanned = [r for r in rids if (fva.loc[r, "maximum"] - fva.loc[r, "minimum"]) > cfg["scan"]["min_fva_span"]]
print(f"stage1: {len(spanned)} reactions with span > tol ({time.time()-t0:.0f}s)", flush=True)

# Stage 2: u=1 block test (single optimize per reaction; cached)
ko_path = f"{outdir}/full_{tag}_stage2_ko.csv"
hits = []
t0 = time.time()
if os.path.exists(ko_path):
    hdf = pd.read_csv(ko_path)
else:
    for i, rid in enumerate(spanned):
        r = model.reactions.get_by_id(rid)
        orig = r.bounds
        apply_modulation(model, rid, 1.0, method=MOD,
                         span=(float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"])),
                         v_ref=float(baseline["fluxes"].get(rid, 0.0)))
        sol2 = model.optimize()
        ok2 = sol2.status == "optimal"
        rec = dict(reaction_id=rid, feasible=ok2, obj_at_u1=sol2.objective_value)
        if ok2:
            vals = evaluate(model, sol2.fluxes, cfg)
            rec.update(vals)
            diffs = {m: abs(vals[m] - baseline["metrics"][m]) / max(abs(baseline["metrics"][m]), 1e-9) for m in vals}
            rec["max_rel_change"] = max(diffs.values())
            rec["metric_change"] = json.dumps({m: round(v - baseline["metrics"][m], 6) for m, v in vals.items()})
            rec["hit"] = rec["max_rel_change"] > TOP_HIT_FRAC
        else:
            rec["hit"] = True; rec["max_rel_change"] = np.inf
        hits.append(rec)
        r.bounds = orig
        if (i + 1) % 100 == 0:
            print(f"  stage2 {i+1}/{len(spanned)} ({time.time()-t0:.0f}s)", flush=True)
    hdf = pd.DataFrame(hits)
    hdf.to_csv(ko_path, index=False)

# Hit criterion (rigorous for pFBA state changes):
#  (a) KO changed the attainable objective (obj_at_u1 differs > tol), or
#  (b) the reaction participates in alternate optima -> nonzero FVA span
#      at fraction_of_optimum = 1.0 (blocking it reshapes the optimal set).
# If neither holds, blocking the reaction changes neither the objective value
# nor the set of optimal flux distributions, hence no selected-state metric.
t0 = time.time()
obj0 = float(baseline["objective"])
obj_rel = (hdf["obj_at_u1"] - obj0).abs() / max(abs(obj0), 1e-9)
obj_hits = set(hdf.loc[obj_rel > TOP_HIT_FRAC, "reaction_id"])
obj_hits |= set(hdf.loc[~hdf["feasible"], "reaction_id"])
print(f"  obj-changing KO hits: {len(obj_hits)}", flush=True)

opt_fva_path = f"{outdir}/full_{tag}_stage2_optfva.csv"
if os.path.exists(opt_fva_path):
    ofva = pd.read_csv(opt_fva_path, index_col=0)
else:
    ofva = flux_variability_analysis(model, reaction_list=rids,
                                     fraction_of_optimum=1.0, processes=1)
    ofva.to_csv(opt_fva_path)
opt_spanned = set(ofva.index[(ofva["maximum"] - ofva["minimum"]) > cfg["scan"]["min_fva_span"]])
print(f"  alternate-optimum spanned: {len(opt_spanned)} ({time.time()-t0:.0f}s)", flush=True)

hit_ids = sorted((obj_hits | opt_spanned) & set(spanned))
print(f"stage2 hits: {len(hit_ids)}", flush=True)

# Stage 2b: consistent-state screen — pFBA/MOMA state at u=1 per candidate;
# keep only reactions whose SELECTED-state metrics actually respond.
screen_path = f"{outdir}/full_{tag}_stage2_screen.csv"
if os.path.exists(screen_path):
    sdf = pd.read_csv(screen_path)
    kept_ids = sdf.loc[sdf["screen_hit"], "reaction_id"].tolist()
else:
    t0 = time.time()
    kept_ids, srows = [], []
    for i, rid in enumerate(hit_ids):
        r = model.reactions.get_by_id(rid)
        orig = r.bounds
        apply_modulation(model, rid, 1.0, method=MOD,
                         span=(float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"])),
                         v_ref=float(baseline["fluxes"].get(rid, 0.0)))
        ok2, _, _ = feasible(model)
        rec = dict(reaction_id=rid, feasible=bool(ok2), screen_hit=(not ok2))
        if ok2:
            fl, _ = select_state(model, SEL, reference=baseline["fluxes"] if SEL == "moma" else None)
            vals = evaluate(model, fl, cfg)
            rec.update(vals)
            mrc = max(abs(vals[m] - baseline["metrics"][m]) / max(abs(baseline["metrics"][m]), 1e-9) for m in vals)
            rec["max_rel_change"] = mrc
            rec["screen_hit"] = bool(mrc > TOP_HIT_FRAC)
        if rec["screen_hit"]:
            kept_ids.append(rid)
        srows.append(rec)
        r.bounds = orig
        if (i + 1) % 200 == 0:
            print(f"  screen {i+1}/{len(hit_ids)} kept={len(kept_ids)} ({time.time()-t0:.0f}s)", flush=True)
    sdf = pd.DataFrame(srows)
    sdf.to_csv(screen_path, index=False)
print(f"screen kept: {len(kept_ids)}", flush=True)

# Stage 3: full coarse grid on kept hits
t0 = time.time()
all_rows = []
for rid in kept_ids:
    span = (float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"]))
    all_rows += scan_reaction(model, rid, cfg, COND, SEL, MOD,
                              baseline, cfg["modulation"]["u_coarse"], span)
df = pd.DataFrame(all_rows)
for c, v in dict(condition=COND, state_method=SEL, mod_method=MOD, model=MODEL).items():
    df[c] = v
df.to_csv(f"{outdir}/full_{tag}_stage3_grid.csv", index=False)
print(f"stage3 rows: {len(df)} ({time.time()-t0:.0f}s) -> {outdir}/full_{tag}_stage3_grid.csv", flush=True)
