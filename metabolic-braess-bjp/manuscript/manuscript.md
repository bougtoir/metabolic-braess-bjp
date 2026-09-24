# Maximum local effect does not imply optimal system effect: selection-rule-dependent interior modulation optima in human metabolic networks

**Article type:** Original Research Article — British Journal of Pharmacology

**Keywords (3–7):** systems pharmacology; flux balance analysis; partial inhibition; metabolic networks; dose–response; network optima

**Bullet-point summary** (each ≤15 words):
- Partial, not maximal, restriction of glycolytic enzymes maximizes ATP yield per glucose consumed.
- Interior optima recur across two independent human genome-scale metabolic reconstructions.
- All interior optima localize to the glycolytic–oxidative energetic core of the network.
- Optima depend on the parsimonious-flux selection rule, largely disappearing under minimal-deviation states.
- Mechanism: restriction redirects substrate from low-yield toward near-complete oxidation.

---

**Abstract (structured, BJP format):**

*Background and Purpose.* Pharmacological dose–response is commonly
assumed monotone: more target engagement yields more effect. Whether
*partial* restriction of a metabolic reaction can outperform both the
unperturbed and the fully blocked state on an independent system-level
endpoint has not been mapped at genome scale.

*Experimental Approach.* We scanned every reaction of two independent
human genome-scale metabolic models (Human-GEM v2.0.1, Recon3D v301)
for endpoints with an interior optimum in modulation intensity u∈[0,1]
— Network-Optimal Partial Modulation (NOPM). Post-perturbation states
were selected by parsimonious FBA or minimal-deviation (L1-MOMA) rules
across three media, two modulation methods and grid refinements.

*Key Results.* Twelve reaction–endpoint pairs in Human-GEM and eight in
Recon3D qualify; all localize to the glycolytic–oxidative energetic
core, and three mechanistic families (mid-glycolysis, oxygen transport,
oxidative phosphorylation) replicate across models. Partial restriction
of glycolytic enzymes raises ATP yield per glucose ~12→~30 while ATP
throughput falls — a rate–yield trade-off. Optima recur under
parsimonious selection in multiple (but not all) media and largely
disappear under minimal-deviation selection.

*Conclusion and Implications.* Interior optima are cross-model
reproducible yet contingent on the state-selection rule — a testable
adaptation-state hypothesis, with no dose-translation claim.

---

## 1. Introduction

Dose–response thinking in pharmacology defaults to monotone logic: more
target engagement produces more effect, and the maximally potent
concentration is treated as an upper endpoint to be approached, not
exceeded.  Yet constraint-based metabolic models represent stoichiometric
coupling and rerouting without explicit kinetic feedback regulation,
and real metabolic networks share resources; in such networks, maximal local intervention need not be optimal for a
system-level objective.  Analogous phenomena are documented elsewhere:
in traffic assignment, adding capacity can worsen total travel time
(Braess' paradox [1]); in enzyme kinetics, disabling
one of two symmetric catalytic sites can increase turnover ten-fold
[2]; and at the network level, partially damaging
an antifungal's target can rescue flux by rerouting around the lesion
[3].  Whether *partial* restriction of a metabolic reaction
can exceed both the unperturbed and the fully blocked state on an
independent, system-level performance measure — across the entire
reaction catalogue of a human genome-scale model — has not been mapped.

We therefore ask three concrete questions.  First, over all reactions
of two independently curated human metabolic reconstructions (Human-GEM
v2.0.1 and Recon3D v301), how often does a scalar endpoint J exhibit an
*interior optimum* in modulation intensity u ∈ [0, 1] — that is, a u*
with J(u*) strictly larger than both J(0) and J(1)?  We call such a
response Network-Optimal Partial Modulation (NOPM), a Braess-like
phenomenon restricted to optimum-location rather than capacity-addition
form.  Second, where in the network do such optima localize?  Third, how
sensitive are they to the two unavoidable modelling choices — the
flux-state selection rule (parsimony FBA vs. minimal-adjustment MOMA)
and the nutrient environment?

Our answers are deliberately conservative.  NOPM exists and is
recurrent: restricting central glycolytic enzymes to ~15–40 % residual
capacity raises ATP yield per glucose from ~12 to ~30 in both models.
But the effect is *conditional*: it arises when the post-perturbation
state is selected by flux parsimony, and largely disappears when the
state is selected by minimal deviation from the pre-perturbation flux
map.  The non-monotonicity is thus a property of the network-plus-
selection rule, not of stoichiometry alone — a qualification we argue
is itself pharmacologically informative.

## 2. Methods

### 2.1 Pipeline and separation of concerns

All computations follow a strict three-stage pipeline.  (A) Feasibility:
restricting reaction i to fraction u of its original span defines a
sub-feasible region F_i(u) ⊆ F(0); infeasible states are reported, never
extrapolated.  (B) State selection: within F_i(u) a flux vector v(u) is
selected by parsimonious FBA (pFBA [4]) or, for
robustness, by the linear (L1) minimal-adjustment rule MOMA
[5].  (C) Evaluation: an independent scalar endpoint
J(v(u)) — a linear functional of the selected state — is reported.  The
endpoint is *never* re-optimized; the three stages use disjoint
objectives, enforced in code and unit tests.

### 2.2 Models, media, and endpoints

Human-GEM v2.0.1 (12,877 reactions [6]) and Recon3D
v301 (10,600 reactions [7]) were frozen by SHA-256
checksum (acquisition ledger, Supplementary Data S1).  A curated minimal
aerobic medium (glucose 10, O2 20 mmol·gDW⁻¹·h⁻¹, mineral/trace
essentials, canonical secretion sinks) was validated on both models,
which reproduce canonical respiration (≈12 ATP per glucose, ≈6 ATP per
O2 — retained as a diagnostic endpoint only, see Limitations — no
disproportionation artefacts).  Endpoints are raw, never
composite: ATP production rate, ATP per glucose, ATP per O2, ATP per
total carbon, glucose and O2 uptake, lactate efflux, lactate/ATP ratio,
and total |flux| (parsimony proxy).  The maintenance objective
(ATPM ≈ 120 mmol·gDW⁻¹·h⁻¹) fixes the production-rate scale.

### 2.3 Modulation and scanning

Modulation method B (FVA-informed capacity restriction) is primary: at
intensity u the reaction's feasible span, computed by flux variability
analysis [8], is contracted to (1−u) of its
width around its midpoint; method A (uniform bound scaling) is the
robustness alternative.  u grids: coarse {0, .1, .25, .5, .75, .9, 1}
plus fine 0.05.  Genome scan is staged and exact: FVA at fraction of
optimum fo = 0.9 over all reactions, a knockout/objective-change test
plus alternate-optimum FVA at fo = 1.0 (a reaction can alter the
selected pFBA state only if it changes the optimum or has nonzero span
at fo = 1), and a consistent-state pFBA screen at u = 1; only
responders receive the full u-grid.  This cut 2,494 candidates to 22
(Recon3D) and 2,254 to 27 (Human-GEM).  Classification: Type II
(NOPM) requires an interior u* with J(u*) > J(0) and J(u*) > J(1) at
tolerance 1e-4; Types 0/I/III/V cover monotone, endpoint-maximal, and
infeasible cases.  Negative control: because F(u) ⊆ F(0), the modulated
reaction's own objective cannot increase — verified in unit tests
(12/12 pass).  Software: COBRA/cobrapy, GLPK; all reported numbers are
regenerated into `manuscript_values.csv` from result CSVs, never
hardcoded.

### 2.4 Robustness matrix

Every Type II hit was re-scanned over: model × selector {pFBA, L1-MOMA}
× medium {aerobic, glucose-limited (glc 2), oxygen-limited (O2 4)} ×
modulation method {A, B} × grid resolution.  Quadratic MOMA did not
converge reliably at genome scale (OSQP iteration-limit); the linear
MOMA problem was solved as an LP instead — a documented limitation
(Section 4.4).

## 3. Results

### 3.1 A sparse, recurrent set of interior optima

Of ~10–13k scanned reactions, 12 reaction–endpoint combinations in
Human-GEM and 8 in Recon3D satisfy Type II under the primary
configuration (pFBA, method B, aerobic).  Every hit lies in the
glycolytic–oxidative energetic core (Figure 1; Table 1).  Grouped into
mechanistic reaction families, three families replicate across the
reconstructions: mid-glycolysis (5 hits in each model — GAPDH, PGK,
ENO, PGM, TPI), oxygen transport (Human-GEM MAR04896; Recon3D O2t,
O2tm), and oxidative phosphorylation (Human-GEM complex I/ATP-synthase
nodes; Recon3D complex III node CYOR_u10mi).  The pyruvate
dehydrogenase complex contributes 4 hits in Human-GEM but none in
Recon3D — a discordance reported transparently rather than reconciled.
No peripheral-pathway reaction qualified in either model: family-level
replication, not raw hit identity, is the reproducible signal. A
reaction-level crosswalk (Human-GEM hit → Recon3D analogue → family →
replication status) is given in Supplementary Table S1.

### 3.2 Efficiency NOPM: partial restriction raises ATP yield

Partial restriction of mid-glycolytic enzymes produces a genuine
interior optimum in ATP per glucose: in Human-GEM, GAPDH
(MAR04373) reaches J(u*) = 30.05 ATP/glc at u* = 0.90 versus
J(0) = 12 and J(1) = 29; PGK (MAR04368) reaches 21 at u* = 0.75.
Recon3D reproduces the phenomenon at the analogous nodes (ENO, PGM:
u* ≈ 0.75, J ≈ 31.5 vs 12.15) — two independently curated
reconstructions converging on the same mechanism (Figure 2).  The effect is
large in magnitude yet bounded: yield approaches but cannot exceed the
~30–32 ATP/glucose aerobic ceiling. We stress that efficiency NOPM lies
on a rate–yield trade-off: ATP yield per glucose rises as ATP
throughput falls (Figure 4). NOPM does not mean every desirable output
improves simultaneously — at each glycolytic hit, u* improves yield
while reducing ATP production rate, i.e. it is Pareto-superior only on
the yield axis and sits on the efficiency side of the rate–yield
frontier.

### 3.3 Parsimony NOPM: interior minima in total flux

A second, distinct class appears on the parsimony endpoint: total
|flux| has an interior *minimum* at intermediate restriction of PDH
complex subunits (DLAT u* ≈ 0.9, DLD ≈ 0.85, PDH-E1 ≈ 0.85), complex I
(u* ≈ 0.1–0.15), TPI (u* ≈ 0.7), and oxygen transport (u* ≈ 0.25–0.3)
(Figure 3).  The cell's most flux-economic state is thus achieved at
partial, not zero, catalytic capacity.

### 3.4 Mechanism: rerouting toward complete oxidation

Inspection of the u-resolved flux maps (Figure 4) shows the mechanism
is the same in both NOPM classes.  Restriction suppresses glucose
uptake roughly 2–3-fold faster than the ATP production rate; the
remaining glucose is consequently routed away from overflow (lactate)
and toward complete oxidation, so yield climbs toward the aerobic
ceiling — until u approaches 1, where the pathway cannot sustain the
flux and yield collapses again.  The interior optimum exists precisely
because low-yield and high-yield route usage trade off monotonically
with restriction while throughput falls.

### 3.5 Robustness: a selection-rule-conditional phenomenon

Across the full matrix (Table 4; Figure 5), interior optima recur under
pFBA in multiple — but not all — media, under both modulation
methods (hit counts 0–11 per cell; the empty pFBA cell is Human-GEM
under glucose limitation, where even parsimony optima vanish), with u* locations shifting modestly with method
(method A optima sit ~0.1–0.3 lower).  Under L1-MOMA the picture
inverts: the efficiency optima vanish (e.g. in Recon3D aerobic,
ENO 12.2→8.2, PGM 12.2→9.2, GAPD 12.2→8.2, all monotone decreasing),
while one parsimony optimum survives (complex III node,
total-flux minimum across conditions).  We treat the MOMA discordance
not as a failed replication but as a result: NOPM is cross-model
reproducible and condition-robust *under parsimonious selection*, and
its disappearance under minimal-deviation selection identifies the
state-selection rule — not network topology alone — as the contingent
mechanistic variable: Braess-like metabolic optima depend on both
network structure and the rule by which the post-perturbation state is
selected.  This is structurally apt for the Braess analogy:
Braess-like behaviour depends not only on network topology and capacity
but on the rule by which the system selects a state.  We therefore do
not claim universality: maximum is not optimum, under the rerouting
rule, and that qualifier is the finding.

## 4. Discussion

### 4.1 Existence

We have shown that, at genome scale in two independent human metabolic
reconstructions, partial restriction of a small set of energetic-core
reactions can outperform both zero and complete restriction on
system-level endpoints.  The phenomenon is structurally distinct from
Braess' paradox (which concerns adding capacity, not scaling it) and
from enzyme-kinetic population effects (single-molecule Markov
mechanics); it is a stoichiometric network property of route
reallocation.  Continuous partial inhibition has previously been
implemented inside bilevel FBA for drug-design tasks [21],
but as an optimisation tool, not as a survey of interior optima; we
name the phenomenon Network-Optimal Partial Modulation descriptively
and make no priority claim beyond this formulation (Table 3).

### 4.2 Cross-model replication

Replication is at the level of mechanistic families, not reaction
identity: mid-glycolysis, oxygen transport and oxidative
phosphorylation replicate across Human-GEM and Recon3D
(Supplementary Table S1), while the PDH-complex hits are
Human-GEM-specific — a discordance we report rather than reconcile.
Family-level rather than reaction-level agreement is the expected
signature for independently curated reconstructions whose compartment
and subsystem granularity differ.

### 4.3 The rate–yield trade-off

Efficiency NOPM does not mean every desirable output improves
simultaneously.  At each glycolytic hit, ATP yield per glucose rises
while ATP production rate falls — the optimum sits on the yield side of
a rate–yield frontier (Figure 4).  A pharmacological reading must
therefore specify *which* currency is valued: yield, throughput, or
flux economy.  Claims that partial inhibition is "better" are
endpoint-dependent; what is endpoint-independent is that the
response is non-monotone.

### 4.4 State-selection dependence — a result, not a caveat

Braess-like metabolic optima depend on both network structure and the
rule by which the post-perturbation state is selected.  pFBA selects
the most parsimonious — most extensively adapted — attainable
post-perturbation state; L1-MOMA selects the minimal-deviation state
constrained near the pre-perturbation flux map.  These are
state-selection abstractions, not time models: we deliberately do not
equate pFBA with chronic adaptation or MOMA with acute inhibition.
What the data show is that the interior optima exist under parsimonious
selection and largely disappear under minimal-deviation selection —
the disappearance under MOMA is itself a positive result about which
system property carries the effect.

### 4.5 Pharmacological interpretation — framed conservatively

Dose–response monotonicity is an assumption, not a theorem.  Our
results demonstrate a computationally concrete counterexample: for
yield- and parsimony-valued objectives, an inhibitor of intermediate
strength achieves more than a saturating one.  Hit targets map onto
recognizable modulators (Table 2): GAPDH (koningic acid, iodoacetate,
3-bromopyruvate), ENO (SF2312 [9]), PDH complex
(devimistat/CPI-613 [10]), complex I (metformin —
weak and debated [11]), ATP synthase (oligomycin,
bedaquiline), LDH (oxamate, FX11).  The classification is deliberately
conservative — approved agents, preclinical compounds, tool compounds
and toxins are labelled as such, and directionality conflicts are
flagged (e.g. dichloroacetate activates PDH upstream rather than
inhibiting it).  We stress the framing: this is a modulation→target
map, not a dose translation.  A pharmacological dose–response curve
couples target occupancy to efficacy through kinetics these
stoichiometric models do not contain; the NOPM claim is that the
*optimal intensity is interior in principle*, not that any clinical
dose realizes it.

### 4.6 Limitations

(i) Stoichiometric steady-state models contain no kinetics, regulation,
or metabolite concentrations; real optima can shift or vanish.
(ii) The state-selection assumption drives the result, as shown.
(iii) Human-GEM does not constrain the ATP-synthase P/O stoichiometry
(our ATP/O2 = 6), so ATP/O2 is used only as a diagnostic endpoint and
is excluded from headline claims; we report it rather than silently
patch the model.  (iv) Quadratic MOMA was not
solver-robust at genome scale; linear MOMA was substituted.
(v) Medium choice changes the hit set (efficiency optima vanish under
glucose limitation), so conclusions are environment-specific.
(vi) No statistical sampling of uncertainty was performed; optima are
deterministic statements about the frozen models.

### 4.7 A testable adaptation-state hypothesis

The conditional structure suggests — but does not prove — an
experimental hypothesis: if parsimonious state selection approximates a
post-perturbation state the cell has had time to adapt into, interior
optima should be more evident under *slow* restrictions (genetic,
transcriptional, chronic low-dose) than under *acute* inhibition, where
the state stays near the pre-perturbation map.  This is a hypothesis
about adaptation states, not a demonstrated acute-versus-chronic
distinction.  Specific falsifiable predictions:

1. In controlled minimal medium, graded inhibition of GAPDH/PGK/ENO
   should produce an inverted-U ATP-yield curve with an interior
   maximum near 15–40 % residual activity.
2. Such an interior optimum should be more readily detectable under
   slowly imposed restriction than under abrupt inhibition.
3. Glucose-poor environments should suppress the efficiency optimum
   while preserving parsimony optima.

### 4.8 Conclusion

Across two independently reconstructed human metabolic networks, a
sparse set of energetic-core reactions exhibits interior optima in
modulation intensity: maximum local restriction is not system-optimal.
The optima are contingent on parsimonious state selection — a
qualification that is itself experimentally testable.  Non-monotone
dose–response is therefore a network property that pharmacology can
exploit, with the caveat that the exploitable regime depends on how the
cell settles after intervention.

## References (Vancouver, numbered by appearance)

1. Braess D, Nagurney A, Wakolbinger T. On a paradox of traffic planning. Transportation Science. 2005;39(4):446–450.
2. Schäffner M, Smith CA, Tampé R, Grubmüller H. Braess' paradox in enzyme kinetics: asymmetry from population balance without direct cooperativity. J Chem Theory Comput. 2026;22(4):1982–1999.
3. Motter AE. Improved network performance via antagonism: from synthetic rescues to multi-drug combinations. BioEssays. 2010;32(3):236–245.
4. Lewis NE, Hixson KK, Conrad TM, et al. Omic data from evolved E. coli are consistent with computed optimal growth from genome-scale models. Mol Syst Biol. 2010;6:390.
5. Segre D, Vitkup D, Church GM. Analysis of optimality in natural and perturbed metabolic networks. Proc Natl Acad Sci USA. 2002;99(23):15112–15117.
6. Robinson JL, Kocabaş P, Wang H, et al. An atlas of human metabolism. Sci Adv. 2020;6(13):eaaz1482.
7. Brunk E, Sahoo S, Zielinski DC, et al. Recon3D enables a three-dimensional view of gene variation in human metabolism. Nat Biotechnol. 2018;36(3):272–281.
8. Mahadevan R, Schilling CH. The effects of alternate optimal solutions in constraint-based genome-scale metabolic models. Metab Eng. 2003;5(4):264–276.
9. Leonard PG, Satani N, Maxwell D, et al. SF2312 is a natural phosphonate inhibitor of enolase. Nat Chem Biol. 2016;12(12):1053–1058.
10. Pardee TS, Anderson RG, Pladna KM, et al. A phase I study of CPI-613 in combination with high-dose cytarabine and mitoxantrone for relapsed or refractory acute myeloid leukemia. Clin Cancer Res. 2018;24(9):2060–2073.
11. Owen MR, Doran E, Halestrap AP. Evidence that metformin exerts its anti-diabetic effects through inhibition of complex 1 of the mitochondrial respiratory chain. Biochem J. 2000;348 Pt 3:607–614.
12. Zheng J. Energy metabolism of cancer: glycolysis versus oxidative phosphorylation (review). Oncol Lett. 2012;4(6):1151–1157.
13. Orth JD, Thiele I, Palsson BØ. What is flux balance analysis? Nat Biotechnol. 2010;28(3):245–248.
14. Ebrahim A, Lerman JA, Palsson BØ, Hyduke DR. COBRApy: constraints-based reconstruction and analysis for Python. BMC Syst Biol. 2013;7:74.
15. Warburg O. On the origin of cancer cells. Science. 1956;123(3191):309–314.
16. Heiden MGV, Cantley LC, Thompson CB. Understanding the Warburg effect: the metabolic requirements of cell proliferation. Science. 2009;324(5930):1029–1033.
17. Cascante M, Boros LG, Comin-Anduix B, de Atauri P, Centelles JJ, Lee PW-N. Metabolic control analysis in drug discovery and disease. Nat Biotechnol. 2002;20(3):243–249.
18. Simeonidis E, Price ND. Model-based engineering of biological systems: advances, challenges, and applications. Curr Opin Biotechnol. 2015;36:90–96.
19. Grüning N-M, Ralser M. Cancer: sacrifice for survival. Nature. 2010;463(7277):38–39.
20. Bailey JE. Toward a science of metabolic engineering. Science. 1991;252(5013):1668–1675.
21. Facchetti G, Altafini C. Partial inhibition and bilevel optimization in flux balance analysis. BMC Bioinformatics. 2013;14:344.

## Tables

- Table 1: Type II hits (model, reaction, endpoint, u*, J(0), J(u*), J(1)).
- Table 2: hit → representative modulators (data/drug_mapping.csv).
- Table 3: prior-art comparison (Phase 0 audit).
- Table 4: robustness matrix — interior-optimum counts per cell (results/robustness_matrix.csv).
- Supplementary Table S1: cross-model reaction crosswalk (manuscript/tableS1_crosswalk.csv).

## Figures

- Fig 1: pipeline & modulation scheme (schematic). figures/fig1_pipeline.png
- Fig 2: efficiency NOPM curves, both models. figures/fig2_efficiency_nopm.png
- Fig 3: parsimony NOPM (total-flux) curves, both models. figures/fig3_parsimony_nopm.png
- Fig 4: rate–yield trade-off — ATP production rate vs ATP yield per glucose for GAPDH (u* sits on the yield side of the frontier). figures/fig4_pareto_gapdh.png
- Fig 5: robustness matrix — interior-optimum counts by model × medium × selection rule × modulation method (pFBA vs L1-MOMA). figures/fig5_robustness.png
