"""Phase 3 pilot: scan central-carbon reactions on Human-GEM (aerobic, pFBA,
fva_informed Method B) over the coarse u grid."""
import sys, os, time
sys.path.insert(0, 'src')
import pandas as pd
from utils import load_config, load_model, apply_medium, set_objective
from scan import eligible_reactions, scan

cfg = load_config()
model, spec = load_model("human2", cfg)
apply_medium(model, cfg, "aerobic")
set_objective(model, cfg, "atp_demand")

# Pilot candidates = non-boundary reactions active under the baseline pFBA
# state (the canonical energy pathway: glycolysis -> PDH -> ETC -> ATPase).
from cobra.flux_analysis import pfba
base_fluxes = pfba(model).fluxes
rids = [rid for rid, why in eligible_reactions(model, cfg)
        if why is None and abs(base_fluxes.get(rid, 0.0)) > 1e-6]
def sub_of(r): return (r.name or "")[:30]
print("pilot candidates:", len(rids))
subs = {}
for rid in rids:
    subs.setdefault(sub_of(model.reactions.get_by_id(rid)), []).append(rid)
for s, l in subs.items(): print(" ", s, len(l))

t0 = time.time()
df, baseline = scan(model, rids, cfg, condition="aerobic",
                    state_method="pfba", mod_method="fva_informed",
                    u_grid=cfg["modulation"]["u_coarse"])
print("scan rows:", len(df), "elapsed %.0fs" % (time.time()-t0))
os.makedirs("results/scans", exist_ok=True)
df.to_csv("results/scans/pilot_human2_aerobic_pfba_fva.csv", index=False)
pd.DataFrame([baseline["metrics"]]).to_csv("results/scans/pilot_baseline_metrics.csv", index=False)
print(df[["reaction_id","modulation_fraction","feasible","objective_value","atp_demand","atp_per_glc","glc_uptake","o2_uptake"]].to_string(max_rows=80))
