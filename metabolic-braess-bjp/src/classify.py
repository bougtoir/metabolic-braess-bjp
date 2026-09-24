"""Response classification (Section 13 of the design)."""
import numpy as np


def classify(J, u, cfg):
    """J: endpoint values (higher=better) on grid u. Returns (cls, u_opt, info).

    0   no meaningful benefit
    I   optimum at/near maximal modulation
    II  NOPM: interior optimum better than both J(0) and J(1)
    III plateau / broad near-optimal interval
    """
    J = np.asarray(J, float); u = np.asarray(u, float)
    tol = cfg["classification_tolerance"]
    eps = cfg.get("epsilon", 1e-9)
    valid = np.isfinite(J)
    info = {"n_feasible": int(valid.sum())}
    if valid.sum() < 3:
        return "infeasible", np.nan, info
    uv, Jv = u[valid], J[valid]
    i = int(np.argmax(Jv))
    u_opt, J_opt = float(uv[i]), float(Jv[i])
    J0 = float(Jv[np.argmin(np.abs(uv))]) if (uv == 0).any() else np.nan
    J1 = float(Jv[np.argmax(uv)]) if (uv == 1).any() else np.nan
    scale = max(abs(J_opt), abs(J0) if np.isfinite(J0) else 0.0, eps)
    gain0 = (J_opt - J0) / scale if np.isfinite(J0) else np.inf
    gain1 = (J_opt - J1) / scale if np.isfinite(J1) else np.inf
    info.update(J0=J0, J1=J1, J_opt=J_opt, gain0=gain0, gain1=gain1)

    interior = tol < u_opt < 1 - tol
    better_both = gain0 > tol and gain1 > tol
    flat_frac = float(np.mean(np.abs(Jv - J_opt) <= tol * scale))

    if not (np.isfinite(J0) and np.isfinite(J1)):
        return "insufficient_endpoints", u_opt, info
    # NOPM requires both endpoints defined: J(u*)>J(0) and >J(1)
    if interior and better_both:
        return "II", u_opt, info
    if u_opt >= 1 - tol and better_both:
        return "I", u_opt, info
    if flat_frac >= 0.5 and (gain0 > tol or gain1 > tol):
        return "III", u_opt, info
    return "0", u_opt, info
