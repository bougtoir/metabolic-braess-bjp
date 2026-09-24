"""Step A — feasibility: is F(u) nonempty? Independent of state selection."""
import cobra
import numpy as np


def feasible(model):
    """Return (is_feasible, solver_status, objective_value).

    Solves the model once with the current objective; 'optimal' means F(u)
    nonempty. Feasibility answers the set question only — a feasible but
    poor-performing state is not the same thing as an infeasible problem.
    """
    try:
        sol = model.slim_optimize(error_value=None)
        if sol is not None:
            return True, "optimal", sol
        sol = model.optimize()
    except Exception as e:  # solver failure (time/iteration limit etc.)
        return False, f"solver_error:{type(e).__name__}", np.nan
    ok = sol.status == "optimal"
    return ok, sol.status, sol.objective_value


def max_objective(model):
    sol = model.optimize()
    return sol.status, sol.objective_value
