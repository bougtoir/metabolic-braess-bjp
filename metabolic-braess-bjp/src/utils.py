"""Shared utilities: config, model loading, exchange identification."""
import hashlib
import os
import re

import cobra
import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")


def load_config(path=None):
    with open(path or os.path.join(ROOT, "config", "config.yaml")) as fh:
        return yaml.safe_load(fh)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_model(cfg_key="human2", cfg=None):
    cfg = cfg or load_config()
    spec = cfg["models"][cfg_key]
    model = cobra.io.read_sbml_model(os.path.join(ROOT, spec["file"]))
    model.solver = cfg.get("solver", "glpk")
    return model, spec


def is_boundary_reaction(r):
    """Exchange/demand/sink: a reaction with only reactants or only products."""
    return len(r.reactants) == 0 or len(r.products) == 0


def exchange_name(r):
    """Short metabolite-ish name of an exchange reaction ('Exchange of glucose' -> 'glucose')."""
    name = (r.name or "").strip()
    m = re.match(r"(?i)^exchange of\s+(.*)$", name)
    return (m.group(1) if m else name).lower()


def build_exchange_table(model):
    rows = []
    for r in model.reactions:
        if is_boundary_reaction(r):
            rows.append({"id": r.id, "name": r.name, "ex_name": exchange_name(r),
                         "lb": r.lower_bound, "ub": r.upper_bound})
    return pd.DataFrame(rows)


def apply_medium(model, cfg, condition="aerobic"):
    """Minimal medium: close all uptakes except the configured set.

    Boundary convention (both exchange orientations): negative flux = uptake
    from medium, positive flux = secretion to medium. Only secretion_names
    may carry positive flux (unless secretion_open).
    """
    cond = cfg["conditions"][condition]
    allowed = {n.lower() for n in cfg["medium"]["uptake_names"]}
    open_sec = cfg["medium"]["secretion_open"]
    sec_names = {n.lower() for n in cfg["medium"].get("secretion_names", [])}
    for r in model.reactions:
        if not is_boundary_reaction(r):
            continue
        name = exchange_name(r)
        cap = cond["uptake_caps"].get(name, cfg["medium"]["default_uptake_cap"]) \
            if name in allowed else 0.0
        sec_ok = open_sec or name in sec_names
        # Convention (both boundary forms): negative flux = uptake (medium->cell),
        # positive flux = secretion (cell->medium).
        r.lower_bound = -cap
        r.upper_bound = 1000.0 if sec_ok else 0.0
    return model


def ensure_atp_demand(model, cfg):
    """Add the Human-GEM metabolic-task ATP hydrolysis demand if absent.

    Task: ATP[c] + H2O[c] -> ADP[c] + Pi[c] + H+[c]  (metabolicTasks_Essential).
    Documented as the physiological work sink; part of the environment, never
    modulated. Returns the reaction id.
    """
    rid = "ATPM_nopm"
    if rid in [r.id for r in model.reactions]:
        return rid
    def mid(base):
        # Human-GEM MAM ids; fall back to name lookup for Recon3D
        return base
    try:
        atp = model.metabolites.get_by_id("MAM01371c")
        adp = model.metabolites.get_by_id("MAM01285c")
        pi = model.metabolites.get_by_id("MAM02751c")
        h2o = model.metabolites.get_by_id("MAM02040c")
        h = model.metabolites.get_by_id("MAM02039c")
    except KeyError:
        def find(biggs, pred):
            for bid in biggs:
                try:
                    return model.metabolites.get_by_id(bid)
                except KeyError:
                    continue
            for met in model.metabolites:
                if pred((met.name or "").lower()) and met.compartment in ("c", "C"):
                    return met
            raise KeyError(biggs)
        atp = find(("atp[c]",), lambda n: "adenosine triphosphate" in n or n == "atp")
        adp = find(("adp[c]",), lambda n: "adenosine diphosphate" in n or n == "adp")
        pi = find(("pi[c]",), lambda n: n in ("pi", "phosphate", "phosphate[c]"))
        h2o = find(("h2o[c]",), lambda n: n in ("h2o", "water"))
        h = find(("h[c]",), lambda n: n in ("h+", "h", "proton"))
    r = cobra.Reaction(rid)
    r.name = "ATP maintenance (NOPM task demand)"
    r.lower_bound, r.upper_bound = 0.0, 1000.0
    r.add_metabolites({atp: -1.0, h2o: -1.0, adp: 1.0, pi: 1.0, h: 1.0})
    model.add_reactions([r])
    return rid


def set_objective(model, cfg, name=None):
    name = name or cfg["objective"]["primary"]
    if name == "atp_demand":
        rid = ensure_atp_demand(model, cfg)
        model.objective = model.reactions.get_by_id(rid)
        return rid
    if name == "biomass":
        for cand in ("MAR13082", "biomass_reaction", "biomass"):
            try:
                model.objective = model.reactions.get_by_id(cand)
                return cand
            except KeyError:
                continue
        for r in model.reactions:
            if "biomass" in (r.name or "").lower():
                model.objective = r
                return r.id
        raise KeyError("no biomass reaction found")
    model.objective = model.reactions.get_by_id(name)
    return name


def subsystem_of(r):
    return r.subsystem or ""
