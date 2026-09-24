# Phase 0 Report — Audit and Environment

## 0.1 Repository audit
- Project repo: `bougtoir/wip` subdir `metabolic-braess-bjp/`, branch `devin/1790204771-metabolic-braess-bjp`.
- Prescribed module layout implemented: feasibility.py (Step A), state_selection.py (Step B),
  metrics.py (Step C), inhibition.py (modulation), scan.py (driver), classify.py (Type 0–V),
  model_qc.py, toy.py (closed-form validation model), utils.py (config/model IO).
- Reproducibility: config/config.yaml holds every numerical assumption; Makefile-less driver
  scripts under scripts/; tests in tests/test_core.py (12 tests, all passing).

## 0.2 Journal guidelines (BJP) — to verify before Phase 9
- British Journal of Pharmacology (Wiley). Expected limits to confirm live at submission:
  ~4,000-word main text, ~60 references, <=10 display items, Discussion ~1,500 words,
  3–7 keywords, bullet-point summary statements, CRediT + AI-use declarations.
  URL: https://bpspubs.onlinelibrary.wiley.com/journal/14765381 — MUST be re-verified
  in Phase 11 before finalisation.

## 0.3 Prior-art audit (searched 2026-09-23)
| # | Work | Relation |
|---|------|----------|
| 1 | Schäffner, Smith, Tampé & Grubmüller (2026) "Braess' Paradox in Enzyme Kinetics" J Chem Theory Comput 22:1982–1999 (ABCE1 Markov models) | Braess-like effect at the *molecular* (Markov-state enzyme kinetics) level, single enzyme ABCE1. Not a network/FBA phenomenon — cited as closest name-neighbour. |
| 2 | Motter (2010) "Improved network performance via antagonism" (synthetic rescues) | Full gene/reaction knockouts that *restore* performance of already-suboptimal networks; antagonistic drug pairs. Closest conceptual ancestor — but ON/OFF perturbations and rescue of damaged networks, not interior optima under partial modulation of a healthy network. |
| 3 | "Partial inhibition and bilevel optimization in FBA" BMC Bioinformatics 2013 | Methodological: continuous partial inhibition inside bilevel FBA (E. coli drug design). Tooling precedent; no claim of interior optima. |
| 4 | Chemical-network Braess (New Haven faculty pub) | Small artificial chemical networks with diminished product rate on added capacity. |
| 5 | Braess-TASEP transport-network literature | Original domain (traffic/user equilibria), cited for analogy framing only. |

### Novelty assessment
- No prior work identified that systematically scans a genome-scale human metabolic
  reconstruction for reactions whose *partial* restriction improves an
  *independent* system-level endpoint (interior optimum in u in (0,1)).
- Nearest neighbours (synthetic rescue; bilevel partial inhibition) differ on:
  perturbation type (ON/OFF vs graded), network state (damaged vs healthy),
  objective independence (FBA objective vs separate evaluation functional J).
- We therefore describe the phenomenon provisionally as Network-Optimal Partial
  Modulation (NOPM) and explicitly do NOT claim discovery priority beyond this
  formulation ("Braess-like" is used as an analogy, not a taxonomy claim).
  Any stronger priority claim would violate the no-first-claims rule.

## 0.4 Environment and data provenance
- Models: Human-GEM v2.0.1 (commit 93e8d29) 12,877 rxns; Recon3DModel v301
  (commit 967ff51) 10,600 rxns. SHA-256 recorded in results/qc/*/model_summary.csv.
- Key environment decision (documented, not silent): boundary-flux convention
  `-v = uptake, +v = secretion` for both models; curated secretion list
  (canonical wastes only); uptakes = glucose/O2/NH3/Pi/H2O/H+. This is the ONLY
  medium found consistent with canonical ATP production AND no fuel-import or
  disproportionation artifacts; the debugging trail is in this report's appendix.
- Known limitation: Human-GEM ATP synthase flux is not stoichiometrically locked
  to a physiological P/O ratio (baseline atp_per_o2 = 6); reported as a model
  property, not edited.
