"""Phase 5: classify each (reaction, endpoint) response curve -> Type labels,
NOPM candidates, mechanism annotations."""
import sys, os, json
sys.path.insert(0, 'src')
import numpy as np
import pandas as pd
from utils import load_config
from metrics import METRIC_META
from classify import classify

cfg = load_config()
path = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(path).rsplit('.', 1)[0]
df = pd.read_csv(path)
rows = []
for (rid, name, sub), g in df.groupby(["reaction_id", "reaction_name", "subsystem"], dropna=False):
    g = g.sort_values("modulation_fraction")
    u = g["modulation_fraction"].values
    for met, meta in METRIC_META.items():
        J = g[met].values.astype(float)
        Ji = -J if meta["orientation"] == "lower" else J
        cls, u_opt, info = classify(Ji, u, cfg)
        rows.append(dict(reaction_id=rid, reaction_name=name, subsystem=sub,
                         metric=met, orientation=meta["orientation"],
                         type=cls, u_opt=u_opt, J0=info.get("J0"), J1=info.get("J1"),
                         J_opt=info.get("J_opt"), gain0=info.get("gain0"),
                         gain1=info.get("gain1"), n_feasible=info.get("n_feasible")))
out = pd.DataFrame(rows)
out.to_csv(f"results/scans/class_{tag}.csv", index=False)
nopm = out[out["type"] == "II"]
print("classified:", len(out), "NOPM candidates:", len(nopm))
if len(nopm):
    print(nopm[["reaction_id", "reaction_name", "metric", "u_opt", "J0", "J_opt", "J1"]].to_string(index=False))
print("\ntype counts:")
print(out["type"].value_counts())
