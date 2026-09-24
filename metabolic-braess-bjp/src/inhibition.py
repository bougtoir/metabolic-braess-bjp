"""Modulation implementation: apply modulation fraction u in [0,1] to a reaction.

u = 0 -> baseline; u = 1 -> maximum defined modulation. remaining = 1 - u.

Method A (bound_scaling): shrink [lb,ub] toward 0 by factor (1-u). Naive —
model bounds like +/-1000 are mathematical, not enzyme capacities.

Method B (fva_informed): shrink the reaction's *feasible* span [fmin,fmax]
(computed by FVA at the baseline objective) toward zero by factor (1-u).
This treats the feasible flux range — not the bound — as the capacity
proxy: u=1 is a full block (0 flux), u=0 leaves the span untouched.
"""
import numpy as np
from cobra.flux_analysis import flux_variability_analysis


def fva_span(model, rid, fraction=0.9):
    fva = flux_variability_analysis(model, reaction_list=[rid],
                                    fraction_of_optimum=fraction)
    return float(fva.loc[rid, "minimum"]), float(fva.loc[rid, "maximum"])


def apply_modulation(model, rid, u, method="fva_informed", span=None, v_ref=0.0):
    """Set reaction bounds for modulation u. Returns the applied (lb, ub)."""
    r = model.reactions.get_by_id(rid)
    rem = 1.0 - u
    if method == "bound_scaling":
        lb, ub = r.lower_bound, r.upper_bound
        r.bounds = (lb * rem, ub * rem)
    elif method == "fva_informed":
        fmin, fmax = span
        # Capacity restriction: the feasible span [fmin,fmax] itself is the
        # capacity proxy; u=1 collapses it to zero flux (full block),
        # u=0 leaves the native span untouched.
        r.bounds = (fmin * rem, fmax * rem)
    else:
        raise ValueError(method)
    return r.bounds


def reset_bounds(model, rid, bounds):
    model.reactions.get_by_id(rid).bounds = bounds
