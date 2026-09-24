"""Model QC: counts, boundary reactions, blocked reactions, feasibility, ATP task."""
import pandas as pd
import cobra
from cobra.flux_analysis import flux_variability_analysis, find_blocked_reactions

from utils import is_boundary_reaction, ensure_atp_demand, set_objective


def model_summary(model, spec):
    ex = [r for r in model.reactions if is_boundary_reaction(r)]
    return {
        "model": spec["name"], "version": spec["version"],
        "reactions": len(model.reactions), "metabolites": len(model.metabolites),
        "genes": len(model.genes), "compartments": len(model.compartments),
        "boundary_reactions": len(ex),
        "sha256": spec.get("sha256", ""),
    }


def dead_end_metabolites(model):
    return [m.id for m in model.metabolites
            if all(m in r.reactants for r in m.reactions) or
               all(m in r.products for r in m.reactions)]


def run_qc(model, spec, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    summ = model_summary(model, spec)
    blocked = find_blocked_reactions(model)
    summ["blocked_reactions"] = len(blocked)
    summ["dead_end_metabolites"] = len(dead_end_metabolites(model))
    pd.DataFrame([summ]).to_csv(f"{outdir}/model_summary.csv", index=False)
    pd.DataFrame({"reaction_id": blocked}).to_csv(f"{outdir}/blocked_reactions.csv", index=False)
    status, obj = "?", None
    try:
        import utils
        cfg = utils.load_config()
        utils.apply_medium(model, cfg, "aerobic")
        rid = set_objective(model, cfg, "atp_demand")
        sol = model.optimize()
        status, obj = sol.status, sol.objective_value
    except Exception as e:
        status, obj = f"error:{e}", None
    with open(f"{outdir}/qc_report.md", "w") as fh:
        fh.write(f"# QC report — {spec['name']} {spec['version']}\n\n")
        for k, v in summ.items():
            fh.write(f"- {k}: {v}\n")
        fh.write(f"- baseline objective status: {status}\n- baseline ATP task flux: {obj}\n")
    return summ
