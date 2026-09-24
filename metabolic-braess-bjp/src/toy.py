"""Transparent toy network for the Braess-like/NOPM concept and unit tests.

Topology:
  S enters via EX_S (<=10); S -> X freely.
  ENG_E  : X + C -> P, yields 2 ATPd, capacity 4   (efficient engine)
  SHUNT_R: X -> W + L + C, yields 0.2 ATPd         (wasteful shunt; sole C source)
  RESCUE : X -> P, yields 0.5 ATPd                 (low-yield fallback)
  P/W/L/ATPd drain through sinks.

Mechanism: C is produced only by the wasteful shunt and consumed 1:1 by the
efficient engine. A wasteful physiological reference (SHUNT_R over-used)
sees J improve when the shunt is restricted toward the cofactor-sufficient
level and collapse when it is fully closed (engine starved) -> interior u*.

Toy B ('mono'): engine needs no C -> shunt restriction is monotonically good.
"""
import cobra
import pandas as pd


def _m(id_):
    return cobra.Metabolite(id_, compartment="c")


def build_toy(kind="typeII"):
    model = cobra.Model(f"toy_{kind}")
    S = _m("S"); X = _m("X"); P = _m("P"); W = _m("W")
    L = _m("L"); C = _m("C"); ATPd = _m("ATPd")

    exS = cobra.Reaction("EX_S"); exS.bounds = (0, 10); exS.add_metabolites({S: 1})
    s2x = cobra.Reaction("S2X"); s2x.bounds = (0, 1000); s2x.add_metabolites({S: -1, X: 1})
    E = cobra.Reaction("ENG_E"); E.bounds = (0, 4)
    if kind == "mono":
        E.add_metabolites({X: -1, P: 1, ATPd: 2})
    else:
        E.add_metabolites({X: -1, C: -1, P: 1, ATPd: 2})
    R = cobra.Reaction("SHUNT_R"); R.bounds = (0, 8)  # biological capacity ~8
    R.add_metabolites({X: -1, W: 1, L: 1, C: 1, ATPd: 0.2})
    P2 = cobra.Reaction("RESCUE"); P2.bounds = (0, 1000)
    P2.add_metabolites({X: -1, P: 1, ATPd: 0.5})
    sinkW = cobra.Reaction("EX_W"); sinkW.bounds = (0, 1000); sinkW.add_metabolites({W: -1})
    sinkP = cobra.Reaction("EX_P"); sinkP.bounds = (0, 1000); sinkP.add_metabolites({P: -1})
    sinkL = cobra.Reaction("EX_L"); sinkL.bounds = (0, 1000); sinkL.add_metabolites({L: -1})
    sinkC = cobra.Reaction("EX_C"); sinkC.bounds = (0, 1000); sinkC.add_metabolites({C: -1})
    atpd = cobra.Reaction("ATPM_nopm"); atpd.bounds = (0, 1000); atpd.add_metabolites({ATPd: -1})
    model.add_reactions([exS, s2x, E, R, P2, sinkW, sinkP, sinkL, sinkC, atpd])
    model.objective = atpd
    return model


def modulate_toy(model, u):
    r = model.reactions.get_by_id("SHUNT_R")
    r.bounds = (0, 8 * (1 - u))
    return r.bounds


def wasteful_reference(model):
    """A feasible suboptimal reference: shunt over-used beyond cofactor needs."""
    ref = pd.Series(0.0, index=[r.id for r in model.reactions])
    # X balance: 10 in = 6 (R) + 4 (E); C: 6 produced, 4 used (2 accumulate? no) ->
    # use R=4 for C, plus extra 2 through R anyway (wasteful): R=6,E=4.
    ref["EX_S"] = 10.0; ref["S2X"] = 10.0
    ref["SHUNT_R"] = 6.0; ref["ENG_E"] = 4.0
    ref["EX_W"] = 6.0; ref["EX_L"] = 6.0; ref["EX_P"] = 4.0; ref["EX_C"] = 2.0
    ref["ATPM_nopm"] = 6 * 0.2 + 4 * 2.0  # 9.2
    return ref
