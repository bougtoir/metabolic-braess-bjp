"""Scan driver: u -> F(u) -> v(u) -> J(v(u)) for each candidate reaction."""
import time

import numpy as np
import pandas as pd
from cobra.flux_analysis import flux_variability_analysis

from feasibility import feasible
from state_selection import select_state
from inhibition import apply_modulation, fva_span
from metrics import evaluate, METRIC_META
from utils import is_boundary_reaction
from classify import classify


def eligible_reactions(model, cfg):
    """Auditable exclusion rules."""
    out = []
    for r in model.reactions:
        reason = None
        if cfg["scan"]["exclude_boundary"] and is_boundary_reaction(r):
            reason = "boundary"
        elif r.id == "ATPM_nopm":
            reason = "objective_sink"
        elif len(r.metabolites) == 0:
            reason = "pseudo"
        if reason:
            out.append((r.id, reason))
        else:
            out.append((r.id, None))
    return out


def scan_reaction(model, rid, cfg, condition, state_method, mod_method,
                  baseline, u_grid, span=None):
    """Scan one reaction over u grid. baseline = {'objective','fluxes','metrics'}.

    Returns (rows list of dict, fva_span). Does not restore bounds itself —
    caller restores after reading baseline bounds.
    """
    r = model.reactions.get_by_id(rid)
    orig = r.bounds
    v_ref = float(baseline["fluxes"].get(rid, 0.0))
    rows = []
    for u in u_grid:
        t0 = time.time()
        apply_modulation(model, rid, u, method=mod_method, span=span, v_ref=v_ref)
        ok, status, obj = feasible(model)
        row = dict(reaction_id=rid, reaction_name=r.name, subsystem=r.subsystem or "",
                   gene_association=r.gene_reaction_rule,
                   modulation_fraction=u, remaining_capacity_fraction=1 - u,
                   baseline_flux=v_ref, modulated_flux=np.nan,
                   feasible=ok, solver_status=status, objective_value=obj,
                   runtime=time.time() - t0)
        if ok:
            try:
                fluxes, st = select_state(model, state_method,
                                          reference=baseline["fluxes"] if state_method.startswith("moma") else None)
            except Exception as e:
                ok = False
                row["solver_status"] = f"selection_error:{type(e).__name__}"
                fluxes = None
            if ok:
                row["modulated_flux"] = float(fluxes.get(rid, np.nan))
                for m, v in evaluate(model, fluxes, cfg).items():
                    row[m] = v
        if not ok:
            for m in METRIC_META:
                row[m] = np.nan
        rows.append(row)
    r.bounds = orig
    return rows


def scan(model, rids, cfg, condition, state_method, mod_method, u_grid):
    """Full scan over rids. Returns DataFrame."""
    # Baseline
    ok, status, obj = feasible(model)
    if not ok:
        raise RuntimeError(f"baseline infeasible ({status})")
    fluxes, _ = select_state(model, state_method, reference=None)
    baseline = {"objective": obj, "fluxes": fluxes,
                "metrics": evaluate(model, fluxes, cfg)}
    all_rows = []
    if mod_method == "fva_informed":
        fva = flux_variability_analysis(model, reaction_list=rids,
                                        fraction_of_optimum=cfg["modulation"]["fva_fraction"],
                                        processes=1)
    else:
        fva = None
    for rid in rids:
        span = (float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"])) if fva is not None else None
        if span and span[1] - span[0] < cfg["scan"]["min_fva_span"]:
            continue
        all_rows += scan_reaction(model, rid, cfg, condition, state_method,
                                  mod_method, baseline, u_grid, span)
    df = pd.DataFrame(all_rows)
    df["condition"] = condition
    df["state_method"] = state_method
    df["mod_method"] = mod_method
    return df, baseline
