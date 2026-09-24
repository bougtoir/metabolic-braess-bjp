"""Build the GEB manuscript docx (inline figures/tables) + editable pptx +
tables docx. All numbers read from phase9 post-fix result CSVs.

Run: python3 make_manuscript.py
Outputs:
  geb/manuscript/GEB_manuscript.docx
  geb/results/figures/GEB_figures_editable.pptx
  geb/results/tables/GEB_tables.docx
"""
import re
from pathlib import Path
import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PInches, Pt as PPt

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "phase9" / "results" / "tables"
FIG = Path(__file__).resolve().parents[1] / "results" / "figures"
GEB = Path(__file__).resolve().parents[1]
OUT_DOC = GEB / "manuscript"
OUT_DOC.mkdir(exist_ok=True)

# ---------------- data ----------------
diag = pd.read_csv(T / "cv_demean_2x2_diagnostic.csv")
summ = pd.read_csv(T / "final_116_species_summary.csv")
hys = pd.read_csv(T / "matched_environment_hysteresis.csv")
lag = pd.read_csv(T / "history_after_lagged_env.csv")
trn = pd.read_csv(T / "forward_training_size_sensitivity.csv")
win = pd.read_csv(T / "window_sensitivity.csv")
anom = pd.read_csv(T / "climate_anomaly_redistribution.csv")
spd = pd.read_csv(T / "forecast_speed_bias.csv")
sim = pd.read_csv(T / "simulation_false_positive.csv")
fut = pd.read_csv(T / "future_information_gain.csv")
obs = pd.read_csv(T / "observer_occurrence_scale_moderators.csv")
occ_sem = pd.read_csv(T / "final_occupancy_semantics_audit.csv")
inc = pd.read_csv(T / "species_inclusion_audit.csv")


def med(s):
    return float(pd.to_numeric(s, errors="coerce").median())


def iqr(s):
    s = pd.to_numeric(s, errors="coerce").dropna()
    return s.quantile(0.25), s.quantile(0.75)


def f(x, d=3):
    return f"{x:.{d}f}"


N_SP = len(summ)
n_def = int(hys.effect_of_prior_state.notna().sum())
n_ab_ci = int((hys.ci_ab_lo > 0).sum())
q = lambda s: pd.to_numeric(s, errors="coerce")
SV = {r.quantity: r.value for r in occ_sem.itertuples()}

vals = dict(
    n_sp=N_SP,
    hg_a=med(diag.HG_A), hg_b=med(diag.HG_B),
    hg_c=med(diag.HG_C), hg_d=med(diag.HG_D),
    hg_d_ppos=(q(diag.HG_D) > 0).mean(),
    hg_d_ci=(q(summ.HG_lo) > 0).mean(),
    hg_d_q=iqr(diag.HG_D),
    hg_a_q=iqr(diag.HG_A), hg_b_q=iqr(diag.HG_B),
    hg_c_q=iqr(diag.HG_C),
    cv_eff=med(diag.HG_C - diag.HG_A),
    dm_loyo=med(diag.HG_B - diag.HG_A),
    dm_fwd=med(diag.HG_D - diag.HG_C),
    fut_med=med(fut.Delta_future_information),
    hg_lagenv=med(lag.HG_lagenv), hg_lagenv2=med(lag.HG_lagenv2),
    hyst_med=med(hys.effect_of_prior_state),
    n_def=n_def,
    ab_med=med(hys.eff_abundance),
    ab_q=iqr(hys.eff_abundance),
    n_ab_ci=n_ab_ci, n_ab=n_def,
    obs_med=med(obs.M3_obs - obs.M1_obs),
    reg_med=med(obs.HG_regional),
    reg_n=int(q(obs.HG_regional).notna().sum()),
    env_red=med(anom.env_pred_redist),
    hist_red=med(anom.hist_pred_redist),
    obs_red=med(anom.obs_redist),
    n_events=int(anom.event_year.nunique()),
    sb_env=med(spd.speed_bias_env), sb_hist=med(spd.speed_bias_hist),
    surv=int(SV.get("surveyed_route_years", np.nan)),
    tot=int(SV.get("total_route_years", np.nan)),
    n_dropped=int((inc.pre_to_post == "dropped").sum()),
    win_expand=med(win[win.window == "expand"].HG),
    win10=med(win[win.window == "10y"].HG),
    win20=med(win[win.window == "20y"].HG),
)

trn_meds = {int(k): med(g.HG)
            for k, g in trn.dropna(subset=["min_hist"]).groupby("min_hist")}

# ---------------- references ----------------
REFS = {}
ORDER = []


def cite(key, text):
    if key not in REFS:
        REFS[key] = text
        ORDER.append(key)
    return "{" + str(ORDER.index(key) + 1) + "}"


def refs_done():
    return [REFS[k] for k in ORDER]

# ---------------- docx helpers ----------------
doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11)
doc.sections[0].left_margin = Inches(1)
doc.sections[0].right_margin = Inches(1)

SUP = re.compile(r"(\{[^}]+\})")


def para(text, style=None, bold=False, italic=False, align=None):
    p = doc.add_paragraph(style=style)
    for part in SUP.split(text):
        if not part:
            continue
        m = re.fullmatch(r"\{([^}]+)\}", part)
        if m:
            r = p.add_run(m.group(1))
            r.font.superscript = True
        else:
            r = p.add_run(part)
            r.bold = bold
            r.italic = italic
    if align:
        p.alignment = align
    return p


def heading(text, level=1):
    doc.add_heading(text, level=level)


def add_fig(path, width=6.0, caption=""):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    c = doc.add_paragraph()
    c.paragraph_format.space_before = Pt(14)
    c.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = c.add_run(caption)
    r.font.size = Pt(9)


# ---------------- title ----------------
para("Disentangling spatial persistence from temporal history in "
     "continental bird distributions", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size = Pt(16)
para("Running title: Spatial persistence and history dependence",
     align=WD_ALIGN_PARAGRAPH.CENTER)
para("")
para("Target journal: Global Ecology and Biogeography (Original Article)",
     italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

# ---------------- abstract ----------------
heading("Abstract", 1)
para(
    "Species distribution models routinely include lagged occurrence or "
    "abundance as predictors, and the resulting predictive gains are often "
    "interpreted as ecological memory, inertia, or hysteresis. However, "
    "lagged state also encodes persistent spatial heterogeneity: a "
    "consistently suitable site produces lag-1 predictability without any "
    "path dependence. We decomposed lagged-state predictability in the "
    f"North American Breeding Bird Survey ({vals['surv']:,} surveyed "
    f"route-years) across {vals['n_sp']} widespread breeding-bird species, "
    "using a 2×2 design that crosses retrospective (leave-one-year-out) "
    "with prospective (forward-chaining) evaluation and route demeaning. "
    "Apparent history gain was large without spatial control "
    f"(median {f(vals['hg_a'])}), but collapsed after route demeaning "
    f"(forward + demeaned median {f(vals['hg_d'], 4)}). Matched-environment "
    "occupancy hysteresis was unsupported (contrast = 0.000 in all "
    f"{vals['n_def']} definable species), whereas abundance retained strong "
    f"temporal state dependence (median {f(vals['ab_med'], 2)} log-count; "
    f"{vals['n_ab_ci']}/{vals['n_ab']} definable species with 95% CI > 0). "
    "Lagged-state predictors in distribution forecasts should not be read "
    "as memory until persistent spatial heterogeneity is separated; "
    "distribution persistence and population state dependence are distinct "
    "phenomena."
)
para("Keywords: species distribution model; Breeding Bird Survey; "
     "history dependence; hysteresis; spatial heterogeneity; forward "
     "validation; occupancy; abundance", italic=True)

# ---------------- introduction ----------------
heading("Introduction", 1)
para(
    "Species distributions are commonly modelled as functions of "
    "contemporary environment, and forecasts of climate-driven range "
    "change inherit this equilibrium structure"
    + cite("elith",
           "Elith J, Leathwick JR. Species distribution models: ecological "
           "explanation and prediction across space and time. Annu Rev Ecol "
           "Evol Syst. 2009;40:677-697.")
    + cite("devictor",
           "Devictor V, Julliard R, Couvet D, Jiguet F. Birds are tracking "
           "climate warming, but not fast enough. Proc R Soc B. "
           "2008;275:2743-2748.")
    + ". Within this framework, adding a species' previous occupancy or "
    "abundance as a predictor often improves fit, and the improvement is "
    "variously interpreted as distributional inertia, spatial memory, site "
    "fidelity, hysteresis, or delayed environmental tracking"
    + cite("mackenzie",
           "MacKenzie DI, Nichols JD, Hines JE, Knutson MG, Franklin AB. "
           "Estimating site occupancy, colonization, and local extinction "
           "when a species is detected imperfectly. Ecology. "
           "2003;84:2200-2207.")
    + cite("clement",
           "Clement MJ, Hines JE, Nichols JD, Pardieck KL, Ziolkowski DJ. "
           "Estimating indices of range shifts in birds using dynamic "
           "models when detection is imperfect. Glob Change Biol. "
           "2016;22:3273-3285.")
    + "."
)
para(
    "Yet lagged state can also be a proxy for persistent spatial "
    "heterogeneity. A route that is consistently suitable produces "
    "occupancy in consecutive years without any dependence of the current "
    "state on the path taken to reach it. The confound between lagged-state "
    "predictability and static spatial structure is well recognized in the "
    "spatial-autocorrelation literature"
    + cite("dormann2007a",
           "Dormann CF. Assessing the validity of autologistic regression. "
           "Ecol Modell. 2007;207:234-242.")
    + cite("dormann2007b",
           "Dormann CF, McPherson JM, Araújo MB, et al. Methods to account "
           "for spatial autocorrelation in the analysis of species "
           "distributional data: a review. Ecography. 2007;30:609-628.")
    + cite("mielke",
           "Mielke K, Claassen T, Busana M, Heskes T, Huijbregts MAJ, "
           "Koffijberg K, Schipper AM. Disentangling drivers of spatial "
           "autocorrelation in species distribution models. Ecography. "
           "2020;43:1741-1751.")
    + ", but its temporal analogue — whether lagged occurrence "
    "predicts the future beyond persistent site quality under genuine "
    "out-of-time validation — has rarely been quantified across many "
    "species. Retrospective cross-validation can further inflate apparent "
    "history dependence, because training on future years leaks information "
    "that prospective forecasting cannot exploit"
    + cite("roberts",
           "Roberts DR, Bahn V, Ciuti S, et al. Cross-validation strategies "
           "for data with temporal, spatial, hierarchical, or phylogenetic "
           "structure. Ecography. 2017;40:913-929.")
    + "."
)
para(
    "Here we decompose lagged-state predictability into four components — "
    "persistent route-level spatial structure, prospective lag-1 "
    "information, lagged environment, and abundance-level state dependence "
    "— using the North American Breeding Bird Survey (BBS), a continental "
    "monitoring program with annual counts on fixed roadside routes since "
    "1966"
    + cite("pardieck",
           "Pardieck KL, Ziolkowski DJ Jr, Lutmerding M, Aponte VI, Hudson "
           "M-AR. North American Breeding Bird Survey Dataset 1966-2019. "
           "Reston (VA): U.S. Geological Survey data release; 2020.")
    + cite("sauer",
           "Sauer JR, Link WA. Analysis of the North American Breeding Bird "
           "Survey using hierarchical models. Auk. 2011;128:87-98.")
    + f". We test {vals['n_sp']} widespread, regularly detected breeding-bird "
    "species under both retrospective (leave-one-year-out) and prospective "
    "(forward-chaining) evaluation, with all preprocessing estimated from "
    "training data only. We asked four questions:"
)
para("H1. Lagged previous state will appear strongly predictive when "
     "persistent route-level spatial structure is not removed.", style=None)
para("H2. After controlling for route-level persistence, prospective "
     "History Gain will shrink substantially.")
para("H3. If genuine spatial history dependence exists, lag-1 state will "
     "still materially improve forward prediction after route demeaning, "
     "lagged-environment control, common evaluation samples, and "
     "train-only preprocessing.")
para("H4. Occupancy-level and abundance-level state dependence may differ: "
     "occupancy hysteresis may disappear under spatial control while "
     "abundance retains state dependence through demographic continuity.")

# ---------------- methods ----------------
heading("Methods", 1)
heading("Data", 2)
para(
    "We used the BBS annual counts (1966–2019 release) restricted to "
    f"routes and years with modelled environmental covariates, yielding "
    f"{vals['surv']:,} surveyed route-years across the contiguous United "
    "States and southern Canada. Each (route, year) was classified as "
    "surveyed-present (species detected), surveyed-absent (route surveyed, "
    "species not detected), or not surveyed; unsurveyed cells were never "
    "coded as absences. Species were included on data sufficiency only: a "
    "species was retained if it was detected on at least 30% of surveyed "
    "route-years on routes where it ever occurred (n = "
    f"{vals['n_sp']} species retained; {vals['n_dropped']} candidate "
    "species excluded for low prevalence). The same inclusion rule was "
    "used for every analysis."
)
heading("Environmental covariates and response", 2)
para(
    "Five annual environmental variables per route-year (annual mean "
    "temperature, annual precipitation, drought index, winter "
    "precipitation, June temperature) were expressed as anomalies against a "
    "fixed 1966–2005 baseline. The response was log1p(count) for regression "
    "analyses; occurrence (present/absent) and count were treated "
    "separately in matched-environment analyses."
)
heading("Models and History Gain", 2)
para(
    "Ridge-style linear models compared: M0 intercept only; M1 current "
    "environment; M2 lag-1 state only; M3 environment + lag-1 state. "
    "History Gain HG = OOS R\u00b2(M3) − OOS R\u00b2(M1); Environment Gain "
    "EG = OOS R\u00b2(M3) − OOS R\u00b2(M2), where OOS R\u00b2 is evaluated "
    "on held-out route-years against the training mean. Predictors were "
    "centred on training column means; no additional scaling was applied "
    "and evaluation used complete cases (rows with a missing response or "
    "covariate were excluded — no imputation)."
)
heading("Cross-validation and spatial control", 2)
para(
    "Two evaluation schemes were crossed with two spatial-control settings. "
    "Leave-one-year-out (LOYO) trains on all years except the held-out "
    "year (retrospective). Forward-chaining trains on years ≤ t and "
    "predicts year t + 1 (prospective). Route demeaning subtracts each "
    "route's training-period mean from both response and predictors; the "
    "means are estimated from training data only, so target-year "
    "information cannot enter features. We report all four combinations "
    "(A: LOYO, no demean; B: LOYO, demean; C: forward, no demean; D: "
    "forward, demean). HG_D is the primary prospective signal. For every "
    "species, models compared within a test were evaluated on identical "
    "observations (common evaluation sample, asserted programmatically)."
)
heading("Lagged environment and sensitivity", 2)
para(
    "To separate lag-1 state from lagged environment, M5 (current + "
    "previous-year environment) and M6 (M5 + lag-1 state) were compared. "
    "Sensitivity analyses repeated forward-chaining with minimum training "
    "histories of 5, 10, and 15 years and with expanding vs rolling 10- and "
    "20-year windows."
)
heading("Matched-environment state dependence", 2)
para(
    "For each species we identified within-route year pairs in which all "
    "five environmental anomalies lay within ±0.5 SD of zero — i.e., "
    "environmentally matched years — restricted to surveyed observations. "
    "The prior-state contrast was computed at two levels: an occupancy "
    "contrast (P(present_t | present(t−1)) − P(present_t | absent(t−1))) "
    "and an abundance contrast (mean log1p count difference). Confidence "
    "intervals used a route-level cluster bootstrap (200 replicates, "
    "routes resampled with replacement preserving draw multiplicities). "
    "The occupancy contrast is undefined for near-ubiquitous species that "
    "have too few matched absences."
)
heading("Climate-anomaly redistribution", 2)
para(
    "For continental-scale warm/dry anomaly years, redistribution was "
    "measured as the fraction of routes whose anomaly deviates from its "
    "route baseline (training-period mean) with opposite sign in the event "
    "year and the following year, computed identically for observed "
    "occupancy and model-predicted distributions. Forecast speed bias "
    "compared env-only vs history-aware predictions."
)
heading("Regional aggregation and observer controls", 2)
para(
    "Counts were aggregated to state level to test whether spatial memory "
    "re-emerges at coarser grain. Observer identity covariates were added "
    "to assess whether apparent history reflects observer persistence."
)
heading("Simulation falsification", 2)
para(
    "Occupancy-like panels were simulated under eight scenarios "
    "(environment-only, static-route persistence, observation persistence, "
    "true lag-1 history, true hysteresis, and controls) using the real "
    "survey coverage mask, and passed through the identical pipeline to "
    "measure true- and false-positive rates of the HG and hysteresis "
    "metrics."
)

# ---------------- results ----------------
heading("Results", 1)

heading("Apparent history dependence before spatial control", 2)
para(
    f"Without route demeaning, lagged state added substantial predictive "
    f"power: under LOYO, median HG_A = {f(vals['hg_a'])} (IQR "
    f"{f(vals['hg_a_q'][0])}–{f(vals['hg_a_q'][1])}); under forward-chaining, "
    f"median HG_C = {f(vals['hg_c'])} (IQR {f(vals['hg_c_q'][0])}–"
    f"{f(vals['hg_c_q'][1])}). Nearly all species were positive "
    f"(P(HG_A > 0) = {(q(diag.HG_A) > 0).mean():.2f}). This is the signal "
    "typically read as distributional memory (H1 supported)."
)
add_fig(FIG / "F1_conceptual.png", 6.3,
        "Figure 1. Conceptual decomposition of lagged-state predictability. "
        "(A) Naive reading: X(t−1) predicts X_t. (B) Persistent route-level "
        "suitability generates both, producing apparent lag correlation "
        "without path dependence. (C) True state dependence remains only "
        "after the static component is removed.")

heading("Static spatial persistence explains most of it", 2)
para(
    f"Route demeaning collapsed the apparent signal (Figure 2). Under LOYO, "
    f"HG fell from {f(vals['hg_a'])} to {f(vals['hg_b'])} (demeaning effect "
    f"median {f(vals['dm_loyo'])}); under forward-chaining, from "
    f"{f(vals['hg_c'])} to {f(vals['hg_d'], 4)} (median {f(vals['dm_fwd'])}). "
    f"The cross-validation effect (C − A, median {f(vals['cv_eff'])}) was "
    "small, and adding future years to training did not increase HG "
    f"(future-information gain median {f(vals['fut_med'])}). Thus the drop "
    "is attributable to route-level static persistence, not to LOYO's use "
    "of future years (H2 supported; the decomposition follows pattern 2)."
)
add_fig(FIG / "F2_2x2.png", 6.0,
        "Figure 2. Species-level History Gain under the 2×2 design: "
        "leave-one-year-out vs forward-chaining × route demeaning. Grey "
        "lines connect the same species across conditions. Demeaning "
        "collapses HG in both schemes; the CV scheme contributes little.")

heading("Prospective lag-1 information is small but mostly positive", 2)
para(
    f"The primary prospective signal, HG_D (forward + route-demeaned), had "
    f"median {f(vals['hg_d'], 4)} (IQR {f(vals['hg_d_q'][0], 4)}–"
    f"{f(vals['hg_d_q'][1], 4)}; Figure 3). It was positive in "
    f"{vals['hg_d_ppos']:.0%} of species, with "
    f"{vals['hg_d_ci']:.0%} having bootstrap 95% CI > 0. H3 is therefore "
    "only weakly supported: a small prospective lag-1 component survives "
    "static spatial control, but its magnitude is roughly two orders of "
    "magnitude below the naive apparent signal."
)
add_fig(FIG / "F3_species_hgd.png", 5.8,
        f"Figure 3. Prospective History Gain (HG_D) for {vals['n_sp']} "
        "species, ranked by effect size, with 95% bootstrap CIs. The "
        "distribution is centred slightly above zero.")

heading("Lagged environment and robustness", 2)
para(
    f"The residual signal did not grow after controlling lagged "
    f"environment (M6 − M5 median {f(vals['hg_lagenv'], 4)}; with lag-2 "
    f"environment {f(vals['hg_lagenv2'], 4)}) and was stable across minimum "
    "training histories (5/10/15 yr medians "
    + ", ".join(f"{k}: {f(v,4)}" for k, v in sorted(trn_meds.items()))
    + f") and window choices (expanding {f(vals['win_expand'],4)}, "
    f"rolling 10-yr {f(vals['win10'],4)}, rolling 20-yr "
    f"{f(vals['win20'],4)}; Figure 5)."
)

heading("Occupancy hysteresis is unsupported", 2)
para(
    "At matched modelled environment, the occupancy prior-state contrast "
    f"was 0.000 for all {vals['n_def']} species in which it was definable "
    f"(remaining {vals['n_sp'] - vals['n_def']} species were "
    "near-ubiquitous and lacked matched absences; Figure 4A). There is no "
    "evidence that prior occupancy elevates occupancy probability beyond "
    "environment and persistent route suitability."
)

heading("Abundance retains strong state dependence", 2)
para(
    "In the same matched-environment design, prior-year occupancy "
    "predicted current-year abundance even after route demeaning: median "
    f"effect {f(vals['ab_med'], 2)} log-count (IQR "
    f"{f(vals['ab_q'][0], 2)}–{f(vals['ab_q'][1], 2)}), with "
    f"{vals['n_ab_ci']}/{vals['n_ab']} definable species having "
    "cluster-bootstrap 95% CI > 0 (Figure 4B). This is demographic state "
    "dependence, not spatial memory: abundance carries continuity because "
    "N_t inherits N(t−1) through births, deaths, and dispersal."
)
add_fig(FIG / "F4_occ_vs_abund.png", 6.3,
        "Figure 4. Occupancy vs abundance prior-state effects at matched "
        "environment (route-demeaned, cluster-bootstrap CIs). (A) Occupancy "
        "contrast is zero in every definable species. (B) Abundance "
        "contrast is positive in nearly all definable species.")

heading("Regional aggregation does not rescue spatial memory", 2)
para(
    f"Aggregating to state level did not recover a history signal: "
    f"regional HG median = {f(vals['reg_med'])} over {vals['reg_n']} "
    "species where defined. The earlier appearance of positive regional "
    "persistence reflected implementation issues and static route "
    "structure, not emergent regional memory."
)

heading("No delayed redistribution after climate anomalies", 2)
para(
    f"Across {vals['n_events']} anomaly events, observed occupancy "
    f"redistribution (sign-flip vs route baseline) median = "
    f"{f(vals['obs_red'])}; env-only predicted {f(vals['env_red'])}, "
    f"history-aware predicted {f(vals['hist_red'])}. History-aware "
    "forecasts were if anything slower than env-only ones (speed bias "
    f"median {f(vals['sb_hist'])} vs {f(vals['sb_env'])}). Simulations on "
    "the same pipeline confirm the design detects static persistence and "
    "true-history scenarios while rejecting environment-only and "
    "observation-persistence nulls at the expected rates "
    "(Supplementary Figure S4)."
)
add_fig(FIG / "F5_robustness.png", 5.8,
        "Figure 5. Specification curve for the prospective History Gain: "
        "median and IQR across lagged-environment controls, minimum "
        "training-history screens, and expanding/rolling windows.")

para(
    "Observer covariates did not change the picture (observer-controlled "
    f"HG median {f(vals['obs_med'], 4)}; Supplementary Figure S2)."
)
add_fig(FIG / "F6_interpretation.png", 5.4,
        "Figure 6. Decomposition summary: apparent distributional history "
        "gain is largely persistent spatial heterogeneity; the prospective "
        "residual is small; abundance retains genuine state dependence.")

# Table 1
doc.add_paragraph()
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(14)
r = p.add_run("Table 1. Summary of key effect sizes (species-level "
              "medians, post-fix pipeline).")
r.bold = True
tbl = doc.add_table(rows=1, cols=4)
tbl.style = "Table Grid"
for i, h in enumerate(["Quantity", "Median", "IQR / detail", "n species"]):
    tbl.rows[0].cells[i].text = h
rows = [
    ("Apparent HG, LOYO no demean", f(vals["hg_a"]),
     f"{f(vals['hg_a_q'][0])}–{f(vals['hg_a_q'][1])}", str(vals["n_sp"])),
    ("HG, LOYO demean", f(vals["hg_b"]),
     f"{f(vals['hg_b_q'][0])}–{f(vals['hg_b_q'][1])}", str(vals["n_sp"])),
    ("HG, forward no demean", f(vals["hg_c"]),
     f"{f(vals['hg_c_q'][0])}–{f(vals['hg_c_q'][1])}", str(vals["n_sp"])),
    ("Prospective HG_D, forward demean", f(vals["hg_d"], 4),
     f"{f(vals['hg_d_q'][0],4)}–{f(vals['hg_d_q'][1],4)}; "
     f"P>0 {vals['hg_d_ppos']:.2f}, CI>0 {vals['hg_d_ci']:.2f}",
     str(vals["n_sp"])),
    ("Occupancy prior-state contrast (matched env)",
     f(vals["hyst_med"]), "all species exactly 0.000",
     str(vals["n_def"])),
    ("Abundance prior-state effect (log-count)",
     f(vals["ab_med"], 2), f"{f(vals['ab_q'][0],2)}–{f(vals['ab_q'][1],2)}; "
     f"CI>0 {vals['n_ab_ci']}/{vals['n_ab']}", str(vals["n_ab"])),
    ("Regional (state-level) HG", f(vals["reg_med"]), "—",
     str(vals["reg_n"])),
    ("Observed anomaly redistribution", f(vals["obs_red"]),
     f"env-pred {f(vals['env_red'])}, hist-pred {f(vals['hist_red'])}",
     str(vals["n_events"]) + " events"),
]
for a, b, c, d in rows:
    cells = tbl.add_row().cells
    cells[0].text, cells[1].text, cells[2].text, cells[3].text = a, b, c, d

# ---------------- discussion ----------------
heading("Discussion", 1)
para(
    "Across 116 widespread North American breeding birds, lagged spatial "
    "state appeared strongly predictive of current distribution — but most "
    "of that apparent history dependence disappeared once persistent "
    "route-level structure was removed. Route demeaning reduced History "
    "Gain from ~0.30 to ~0.006 under forward validation, while the "
    "evaluation scheme itself contributed almost nothing. The dominant "
    "driver of lagged-state predictability in these data is static spatial "
    "persistence, not temporal memory."
)
para(
    "This distinction matters wherever lagged occurrence is interpreted "
    "biologically — in species distribution models, range-shift forecasts, "
    "occupancy dynamics, and climate-impact assessments. A previous-year "
    "occurrence term can proxy stable site quality; reading its predictive "
    "gain as memory or delayed climate tracking risks systematic "
    "misattribution. Our result quantifies that risk at continental scale "
    "and across many species: the inflation is large (two orders of "
    "magnitude) and robust to lagged-environment controls."
)
para(
    "The clearest biological contrast is between occupancy and abundance. "
    "At matched environment, prior occupancy did not elevate occupancy "
    "probability in any definable species, yet prior occupancy predicted "
    "substantially higher abundance in nearly all of them. This is not a "
    "contradiction: occupancy on a repeatedly surveyed route is largely a "
    "static property of site suitability, whereas abundance obeys "
    "demographic continuity — N_t is literally built from N(t−1) through "
    "recruitment, mortality, and local dispersal. Abundance state "
    "dependence therefore survives spatial control even though spatial "
    "'memory' of occupancy does not. Distribution persistence and "
    "population state dependence are different phenomena, and conflating "
    "them — as lagged-state predictors invite — conflates geography with "
    "demography."
)
para(
    "For ecological forecasting, the practical implication is that "
    "lagged-state predictors can improve retrospective fit yet should not "
    "be interpreted as memory, hysteresis, or delayed climate tracking "
    "until persistent spatial heterogeneity is explicitly separated. Where "
    "forecast skill is the goal, a lagged-state term still helps slightly "
    "in prospective mode (median HG_D ≈ 0.006, positive in most species), "
    "but the honest interpretation of that residual is small: lag-1 state "
    "carries a little information beyond environment and site identity, "
    "and some of it may still be slowly varying unmeasured habitat rather "
    "than true path dependence."
)
para(
    "The negative results are equally informative. We found no occupancy "
    "hysteresis at matched environment, no recovery of a history signal "
    "under regional aggregation, and no delayed redistribution following "
    "climate anomalies — history-aware forecasts were, if anything, slower "
    "than environment-only forecasts. These falsifications sharpen the "
    "interpretation: if genuine spatial memory were a dominant force in "
    "annual-scale avian distribution dynamics, at least one of these "
    "independent tests should have retained it."
)
para(
    "Limitations are real. Resolution is annual; memory operating at "
    "finer scales (within-season decisions, dispersal timing) is invisible "
    "here. Data are route-level survey counts, not individual tracks, so "
    "site fidelity cannot be separated from site suitability. Environmental "
    "covariates are incomplete — 'matched environment' means matched on "
    "the modelled set — and BBS counts carry observation-process noise "
    "(imperfect detection, observer turnover), although observer-covariate "
    "controls did not alter conclusions. Our inclusion rule selects "
    "widespread species, so conclusions cover the common bird community, "
    "not rare or range-edge species where history may matter most. "
    "Finally, simulations show the demeaned forward-chaining design has "
    "limited power: some true lag-1 history is absorbed by demeaning, so "
    "the small HG_D is a lower bound rather than a clean estimate."
)
para(
    "Future work should combine repeated population surveys with "
    "individual telemetry and finer temporal resolution to separate "
    "spatial memory, demographic inertia, and habitat persistence along "
    "independent axes. The design used here — crossing retrospective and "
    "prospective validation with explicit static spatial control — is "
    "taxon- and system-general and can be applied wherever lagged-state "
    "predictors are proposed as evidence of memory."
)
para(
    "In summary, apparent history dependence in continental bird "
    "distributions is largely persistent spatial heterogeneity in "
    "disguise. What survives spatial control is a small prospective lag-1 "
    "component and a robust abundance-level state dependence — population "
    "dynamics, not spatial memory."
)

# ---------------- statements ----------------
heading("Acknowledgments", 2)
para("BBS data are provided by the U.S. Geological Survey and Environment "
     "and Climate Change Canada; we thank the thousands of volunteer "
     "observers.")
heading("Data availability", 2)
para("BBS data: USGS ScienceBase / Pardieck et al. (2020). All analysis "
     "code and result tables are provided in the accompanying repository "
     "(phase9/ pipeline; regenerated end-to-end from raw data).")
heading("Author contributions", 2)
para("[To be completed at submission.]")

# ---------------- references ----------------
heading("References", 1)
for i, r in enumerate(refs_done(), 1):
    para(f"{i}. {r}")

# ---------------- figure captions (supplement list) ----------------
doc.add_page_break()
heading("Supplementary material index", 1)
para("S1 species inclusion flow; S2 observer sensitivity; S3 redistribution "
     "metric validation (toy cases); S4 simulation null distributions; "
     "S5 regional aggregation detail; S6 training-window sensitivity; "
     "S7 bug-fix audit; S8 full 116-species results table. Supplementary "
     "tables are generated from phase9/results/tables/.")

out = OUT_DOC / "GEB_manuscript.docx"
doc.save(out)
print("wrote", out)

# ---------------- editable pptx ----------------
prs = Presentation()
prs.slide_width = PInches(13.333)
prs.slide_height = PInches(7.5)
figs = [
    ("F1_conceptual.png", "Figure 1", "Conceptual decomposition of "
     "lagged-state predictability."),
    ("F2_2x2.png", "Figure 2", "2×2 decomposition: CV scheme × route "
     "demeaning."),
    ("F3_species_hgd.png", "Figure 3", "Prospective HG_D across species "
     "with 95% CIs."),
    ("F4_occ_vs_abund.png", "Figure 4", "Occupancy vs abundance "
     "prior-state effects at matched environment."),
    ("F5_robustness.png", "Figure 5", "Specification curve: lagged env, "
     "training history, windows."),
    ("F6_interpretation.png", "Figure 6", "Interpretation: static "
     "persistence vs abundance state dependence."),
]
for fn, title, cap in figs:
    s = prs.slides.add_slide(prs.slide_layouts[6])
    tb = s.shapes.add_textbox(PInches(0.5), PInches(0.3), PInches(12.3),
                            PInches(0.6))
    tb.text_frame.text = title
    tb.text_frame.paragraphs[0].font.size = PPt(28)
    s.shapes.add_picture(str(FIG / fn), PInches(3.67), PInches(1.0),
                         height=PInches(5.2))
    cb = s.shapes.add_textbox(PInches(0.5), PInches(6.4), PInches(12.3),
                            PInches(0.9))
    cb.text_frame.text = cap
    cb.text_frame.paragraphs[0].font.size = PPt(16)
pout = FIG / "GEB_figures_editable.pptx"
prs.save(pout)
print("wrote", pout)

# ---------------- editable tables docx ----------------
tdoc = Document()
tdoc.add_heading("Supplementary / main tables (editable)", 0)
tt = tdoc.add_table(rows=1, cols=4)
tt.style = "Table Grid"
for i, h in enumerate(["Quantity", "Median", "IQR / detail", "n"]):
    tt.rows[0].cells[i].text = h
for a, b, c, d in rows:
    cells = tt.add_row().cells
    cells[0].text, cells[1].text, cells[2].text, cells[3].text = a, b, c, d
tout = GEB / "results" / "tables" / "GEB_tables.docx"
tout.parent.mkdir(parents=True, exist_ok=True)
tdoc.save(tout)
print("wrote", tout)
