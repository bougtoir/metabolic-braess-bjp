"""Step C — system-level evaluation: endpoints J(v(u)) on a selected state.

Every endpoint is a linear functional of the selected flux vector v — never
re-optimized. Each metric declares orientation and interpretation in
METRIC_META. Exchange ids are resolved by exchange-name lookup so the same
code runs on Human-GEM and Recon3D.
"""
import numpy as np

from utils import is_boundary_reaction, exchange_name

METRIC_META = {
    "atp_demand":   dict(units="mmol/gDW/h", orientation="higher",
                       desc="ATP hydrolysis task flux (ATP -> ADP+Pi): cellular work capacity"),
    "atp_per_glc":  dict(units="mol/mol", orientation="higher",
                       desc="ATP produced per unit glucose taken up (energetic yield)"),
    "atp_per_o2":   dict(units="mol/mol", orientation="higher",
                       desc="ATP produced per unit O2 taken up (P/O-like efficiency)"),
    "atp_per_carbon": dict(units="mol/mol-C", orientation="higher",
                       desc="ATP produced per carbon atom taken up"),
    "glc_uptake":   dict(units="mmol/gDW/h", orientation="lower",
                       desc="Glucose uptake required by the selected state"),
    "o2_uptake":    dict(units="mmol/gDW/h", orientation="lower",
                       desc="O2 uptake required by the selected state"),
    "lac_out":      dict(units="mmol/gDW/h", orientation="lower",
                       desc="L-lactate secretion (glycolytic overflow burden)"),
    "lac_per_atp":  dict(units="mol/mol", orientation="lower",
                       desc="Lactate burden per ATP produced"),
    "total_flux":   dict(units="mmol/gDW/h", orientation="lower",
                       desc="Total absolute flux (sum|v|): metabolic traffic burden"),
}

CARBON_COUNTS = {"glucose": 6, "d-glucose": 6}


def _ex_names(name):
    """Exchange-name aliases shared across Human-GEM / Recon3D naming."""
    aliases = {
        "glucose": ("glucose", "d-glucose"),
        "o2": ("o2", "oxygen", "oxugen"),
        "l-lactate": ("l-lactate", "lactate", "l-lac"),
    }
    return aliases.get(name, (name,))


def _exchange_uptake(model, fluxes, name):
    """Uptake (>=0) on exchange `name`; boundary convention: -v = uptake, +v = secretion."""
    names = _ex_names(name)
    for r in model.reactions:
        if is_boundary_reaction(r) and exchange_name(r) in names:
            return max(-fluxes.get(r.id, 0.0), 0.0)
    return 0.0


def _exchange_secretion(model, fluxes, name):
    """Secretion (>=0) on exchange `name`; +v = secretion."""
    names = _ex_names(name)
    for r in model.reactions:
        if is_boundary_reaction(r) and exchange_name(r) in names:
            return max(fluxes.get(r.id, 0.0), 0.0)
    return 0.0


def evaluate(model, fluxes, cfg):
    """Compute all endpoints for a selected flux vector. Returns dict name->value."""
    atp = float(fluxes.get("ATPM_nopm", 0.0))
    glc = _exchange_uptake(model, fluxes, "glucose")
    o2 = _exchange_uptake(model, fluxes, "o2")
    lac = _exchange_secretion(model, fluxes, "l-lactate")
    # carbon uptake over all exchange uptakes with known C count
    carbon = 0.0
    for r in model.reactions:
        if is_boundary_reaction(r):
            nm = exchange_name(r)
            if nm in CARBON_COUNTS and CARBON_COUNTS[nm] > 0:
                carbon += CARBON_COUNTS[nm] * _exchange_uptake(model, fluxes, nm)
    tot = float(np.abs(fluxes.values).sum())
    eps = cfg.get("epsilon", 1e-9)
    return {
        "atp_demand": atp,
        "atp_per_glc": atp / max(glc, eps),
        "atp_per_o2": atp / max(o2, eps),
        "atp_per_carbon": atp / max(carbon, eps),
        "glc_uptake": glc,
        "o2_uptake": o2,
        "lac_out": lac,
        "lac_per_atp": lac / max(atp, eps),
        "total_flux": tot,
    }


def composite_score(vals):
    """Oriented Pareto-style composite for candidate ranking (not the primary J)."""
    parts = []
    for name, v in vals.items():
        meta = METRIC_META.get(name)
        if not meta or not np.isfinite(v):
            continue
        parts.append(v if meta["orientation"] == "higher" else -v)
    return parts
