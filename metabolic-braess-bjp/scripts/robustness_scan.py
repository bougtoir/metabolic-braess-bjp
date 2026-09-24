"""Phase 6: robustness matrix on confirmed candidate reactions only.

For a set of hit reaction ids, rerun the coarse+fine u-grid across:
  state-selection: pfba, moma
  conditions:      aerobic, glucose_limited, oxygen_limited
  modulation:      fva_informed, bound_scaling
Outputs: results/scans/robust_{model}_{cond}_{sel}_{mod}.csv

Usage: python3 scripts/robustness_scan.py MODEL rid1 rid2 ...
"""
import sys, os, time
sys.path.insert(0, 'src')
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis
from utils import load_config, load_model, apply_medium, set_objective
from feasibility import feasible
from state_selection import select_state
from metrics import evaluate
from scan import scan_reaction

MODEL = sys.argv[1]
HITS = sys.argv[2:]

# Type-II (NOPM) hit reactions per model — the responses MOMA must reproduce
TYPEII = {
    "human2": {"MAR04368", "MAR04373", "MAR04391", "MAR04896", "MAR06409",
               "MAR06412", "MAR06916", "MAR06921", "MAR08746", "MAR20069",
               "MAR04363", "MAR04365"},
    "recon3d": {"ENO", "PGM", "O2t", "CYOR_u10mi", "GAPD", "TPI"},
}

cfg = load_config()
model, spec = load_model(MODEL, cfg)
u_grid = sorted(set(cfg["modulation"]["u_coarse"]) | {round(0.05 * i, 2) for i in range(21)})
outdir = "results/scans"
os.makedirs(outdir, exist_ok=True)

for cond in ["aerobic", "glucose_limited", "oxygen_limited"]:
    model.solver = "glpk"  # moma leaves osqp active; LP paths need glpk
    apply_medium(model, cfg, cond)
    set_objective(model, cfg, "atp_demand")
    ok, status, obj = feasible(model)
    if not ok:
        print(f"{cond}: infeasible baseline ({status}), skipping", flush=True)
        continue
    # condition-specific FVA spans (needed by both modulation methods)
    fva_path = f"{outdir}/robust_{MODEL}_{cond}_fva.csv"
    if os.path.exists(fva_path):
        fva = pd.read_csv(fva_path, index_col=0)
    else:
        t0 = time.time()
        fva = flux_variability_analysis(model, reaction_list=HITS,
                                        fraction_of_optimum=cfg["modulation"]["fva_fraction"],
                                        processes=1)
        fva.to_csv(fva_path)
    pfba_fluxes, _ = select_state(model, "pfba", reference=None)
    for sel in ["pfba", "moma_linear"]:
        ref = pfba_fluxes if sel.startswith("moma") else None
        try:
            fluxes, _ = select_state(model, sel, reference=ref)
        except Exception as e:
            print(f"  {cond}/{sel}: selection failed ({type(e).__name__}), skipping", flush=True)
            continue
        baseline = {"objective": obj, "fluxes": fluxes, "metrics": evaluate(model, fluxes, cfg)}
        for mod in ["fva_informed", "bound_scaling"]:
            tag = f"{MODEL}_{cond}_{sel}_{mod}"
            if os.path.exists(f"{outdir}/robust_{tag}.csv"):
                continue
            t0 = time.time()
            rows = []
            # MOMA is expensive at genome scale (~40s/point): restrict to the
            # Type-II hit reactions on the coarse grid — the responses that
            # actually matter for NOPM robustness.
            moma_hits = HITS
            if sel.startswith("moma"):
                moma_hits = [r for r in HITS if r in TYPEII.get(MODEL, set())]
            grid = cfg["modulation"]["u_coarse"] if sel.startswith("moma") else u_grid
            for rid in moma_hits:
                if rid not in model.reactions:
                    continue
                span = (float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"])) if rid in fva.index else None
                rows += scan_reaction(model, rid, cfg, cond, sel, mod, baseline, grid, span)
            df = pd.DataFrame(rows)
            for c, v in dict(condition=cond, state_method=sel, mod_method=mod, model=MODEL).items():
                df[c] = v
            tag = f"{MODEL}_{cond}_{sel}_{mod}"
            df.to_csv(f"{outdir}/robust_{tag}.csv", index=False)
            print(f"robust {tag}: {len(df)} rows ({time.time()-t0:.0f}s)", flush=True)
print("done", flush=True)
