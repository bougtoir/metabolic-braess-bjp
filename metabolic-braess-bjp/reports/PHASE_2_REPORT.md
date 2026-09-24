# Phase 2 Report — Module separation, toy model, negative control

## Module separation (strictly enforced)
- (A) Feasibility  F(u): src/feasibility.py — nonempty set test only.
- (B) State selection v(u): src/state_selection.py — pFBA and MOMA(-like QP)
  solvers; independent of J.
- (C) Evaluation J(v(u)): src/metrics.py — linear functionals of the selected
  flux vector only (atp_demand, atp_per_glc, atp_per_o2, atp_per_carbon,
  glc_uptake, o2_uptake, lac_out, lac_per_atp, total_flux); never re-optimized.
- Modulation: src/inhibition.py — Method A bound_scaling; Method B
  fva_informed (feasible span shrunk toward 0; u=1 = full capacity block).
- Driver: src/scan.py (eligible_reactions + scan_reaction + scan), grid per
  config; classification: src/classify.py (Type 0/I/II/III + labels).

## Toy models (src/toy.py)
- typeII toy: efficient engine consumes cofactor C produced only by wasteful
  shunt → interior optimum in u (closed-form verifiable).
- mono toy: engine needs no cofactor → monotone response.
- Both reproduce the expected classes (unit tests).

## Unit tests — tests/test_core.py (12/12 pass)
- incl. test_negative_control_nested_sets: since F(u) ⊆ F(0), the DIRECT
  objective maximum cannot increase under modulation — the mandatory
  negative control (asserts max_u obj ≤ baseline obj + tol).
- Toy-typeII interior optimum detected; mono toy monotone; exchange sign
  conventions; modulation bound shrinkage; classifier labels.

## Interpretation guard
Interior-optimum claims require J evaluated on the SELECTED state to beat
both u=0 and u=1 (class II), not the FBA objective itself — orthogonal to
the negative control (which constrains the objective, not J).
