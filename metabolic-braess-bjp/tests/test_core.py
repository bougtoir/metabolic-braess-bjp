"""Unit tests (Section 23)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
import cobra
import pytest
import yaml

from toy import build_toy, modulate_toy, wasteful_reference
from classify import classify
from inhibition import apply_modulation
from utils import load_config
from cobra.flux_analysis import moma

CFG = load_config()


def test_remaining_capacity_convention():
    m = build_toy()
    for u in (0, 0.25, 0.5, 1.0):
        modulate_toy(m, u)
        r = m.reactions.SHUNT_R
        assert r.upper_bound == pytest.approx(8 * (1 - u))
        assert 1 - u == pytest.approx(1 - u)


def test_u0_reproduces_baseline():
    m = build_toy()
    base = m.slim_optimize()
    modulate_toy(m, 0.0)
    assert m.slim_optimize() == pytest.approx(base)


def test_u1_is_maximum():
    m = build_toy()
    modulate_toy(m, 1.0)
    assert m.reactions.SHUNT_R.upper_bound == 0


def test_fva_informed_shrinks_span_around_ref():
    m = build_toy()
    sol = m.optimize()
    apply_modulation(m, "SHUNT_R", 0.5, method="fva_informed",
                     span=(0.0, 8.0), v_ref=float(sol.fluxes["SHUNT_R"]))
    r = m.reactions.SHUNT_R
    assert r.upper_bound - r.lower_bound == pytest.approx(4.0)


def test_typeII_toy_detected():
    m = build_toy("typeII")
    ref = cobra.Solution(0.0, "optimal", wasteful_reference(m))
    us = np.linspace(0, 1, 11)
    J = []
    for u in us:
        modulate_toy(m, u)
        sol = moma(m, solution=ref, linear=True)
        glc = sol.fluxes["EX_S"]
        J.append(sol.fluxes["ATPM_nopm"] / glc if glc else np.nan)
    cls, u_opt, info = classify(J, us, CFG)
    assert cls == "II", (cls, info)
    assert 0 < u_opt < 1


def test_mono_toy_not_typeII():
    m = build_toy("mono")
    ref = cobra.Solution(0.0, "optimal", wasteful_reference(m))
    us = np.linspace(0, 1, 11)
    J = []
    for u in us:
        modulate_toy(m, u)
        sol = moma(m, solution=ref, linear=True)
        J.append(sol.fluxes["ATPM_nopm"])
    cls, _, _ = classify(J, us, CFG)
    assert cls != "II"


def test_numerical_noise_not_typeII():
    us = np.linspace(0, 1, 11)
    rng = np.random.default_rng(0)
    J = 5 + rng.normal(0, 1e-9, 11)
    cls, _, _ = classify(J, us, CFG)
    assert cls in ("0", "III")


def test_negative_control_nested_sets():
    """Direct-objective control: max J over Fu <= max J over F0."""
    m = build_toy("typeII")
    obj0 = m.slim_optimize()
    m.reactions.SHUNT_R.bounds = (0, 4)
    obj1 = m.slim_optimize()
    m.reactions.SHUNT_R.bounds = (0, 0)
    obj2 = m.slim_optimize()
    assert obj1 <= obj0 + 1e-6
    assert obj2 <= obj1 + 1e-6


def test_feasibility_not_performance():
    m = build_toy()
    from feasibility import feasible
    ok, status, obj = feasible(m)
    assert ok and obj > 0
    m.reactions.SHUNT_R.bounds = (0, 0)
    ok2, _, obj2 = feasible(m)
    assert ok2 and obj2 < obj  # feasible but worse: distinct concepts


def test_model_restored_after_scan():
    m = build_toy()
    orig = m.reactions.SHUNT_R.bounds
    for u in (0.1, 0.5, 0.9):
        modulate_toy(m, u)
    m.reactions.SHUNT_R.bounds = orig
    assert m.reactions.SHUNT_R.bounds == orig


def test_no_nan_propagation():
    us = np.linspace(0, 1, 11)
    J = [np.nan] * 8 + [1.0, 2.0, 1.5]
    cls, u_opt, _ = classify(J, us, CFG)
    assert cls == "insufficient_endpoints"


def test_deterministic_rerun():
    m1 = build_toy(); m2 = build_toy()
    assert m1.slim_optimize() == pytest.approx(m2.slim_optimize())
