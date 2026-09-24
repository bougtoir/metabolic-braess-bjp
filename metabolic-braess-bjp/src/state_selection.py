"""Step B — physiological state selection: choose v(u) from F(u).

Selection rule is deliberately separate from the performance metrics J.
Implemented: pFBA (min sum|v| at optimal objective) and MOMA-like
(min squared distance to a reference flux, via QP).
"""
import numpy as np
import cobra
from cobra.flux_analysis import pfba


def select_state(model, method, reference=None):
    """Return (fluxes pd.Series, status). method in {'pfba','moma'}."""
    if method == "pfba":
        sol = pfba(model)
        if sol is None or sol.status != "optimal":
            sol = model.optimize()
        return sol.fluxes, sol.status
    if method in ("moma", "moma_linear"):
        if reference is None:
            raise ValueError("MOMA needs a reference flux vector")
        ref_sol = cobra.Solution(objective_value=0.0, status="optimal", fluxes=reference)
        if method == "moma_linear":
            # linear (L1) MOMA: LP-solvable at genome scale; cobra already
            # rolls the model back internally
            sol = cobra.flux_analysis.moma(model, solution=ref_sol, linear=True)
        else:
            # quadratic MOMA on a copy: the QP pollutes the model's solver
            # state and breaks subsequent LPs on the original
            mc = model.copy()
            sol = cobra.flux_analysis.moma(mc, solution=ref_sol, linear=False)
        return sol.fluxes, sol.status
    raise ValueError(method)
