# FEASIBILITY — event-based test of trophic-mobility perturbation propagation

Verdict up front: **WEAK GO** — usable for a case study / hypothesis-generating
analysis, not (yet) a standalone confirmatory paper.

Answers below refer to the primary definition **B_percentile** (Δlog10
regional chl-a beyond 5th/95th percentile, 7-day independence); robustness
across definitions A–D is in `outputs/tables/event_independence.csv`.

**Q1. How many genuinely independent events?**
22 independent events at 7-day separation (31/22/18 at 3/7/14 d). Definition A
gives 14, C gives 18, D gives 6. So 6–22 depending on strictness; ~14–22 under
non-persistent definitions.

**Q2. How many overlap ≥ 2 guilds?**
16 of 22 B events have ≥ 2 guilds with ≥ 1 tracked individual-day in the event
window; **~10 events (Jun–Nov 2022) have ≥ 2 guilds with meaningful coverage**
(≥ 5 individual-days per guild). After Nov 2022 coverage collapses to
shark + manta.

**Q3. Sufficient individuals simultaneously tracked?**
Marginally. Max individuals per guild per event is 5–11 in mid-2022, dropping
to ~2 in 2023. Cetaceans (19–27 d tags) and sooty terns (19 d) cover only
June 2022 events. Sample-size information is retained everywhere
(`n_individuals` columns); raw fixes are never pooled.

**Q4. Can environmental fields be matched at useful resolution?**
Yes for regional-scale exposure: daily chl-a / SST / SLA / geostrophic currents
on 0.04–0.25° grids around Palmyra. Caveats: chl-a is ~67 % cloud-masked
per day (region-mean metrics remain estimable); Ekman product is equatorially
masked and unusable; sub-mesoscale matching to individual tracks is not
feasible — exposure must be regional, not pointwise.

**Q5. Advection vs active displacement?**
Active displacement is identifiable. Daily displacement vectors vs
co-located geostrophic current vectors (`outputs/tables/advection_alignment.csv`):
median alignment ≈ 0 for most species; vector residual
|observed − advected| / |observed| ≥ ~1 — animals are not passively drifting.
Melon-headed whales show median alignment 0.75 but on small n — flagged, not
trusted.

**Q6. Any tentative trophic-mobility gradient?**
No consistent one. Per-event slope of log10 centroid-shift vs mobility rank is
median **−0.018** (≈ 0); event fixed-effects OLS slope −0.032
(clustered p = 0.33). Raw
median shifts are large for mobile predators (249 km) but scale with baseline
mobility, i.e. compatible with ordinary ranging rather than event-associated
redistribution.

**Q7. Robust to leave-one-event-out?**
Yes — trivially, because the effect is ~0. LOEO median slopes span
−0.021 to −0.015; no single event dominates
(`outputs/tables/leave_one_event_out.csv`).

**Q8. Distinguishable from seasonal/placebo responses?**
No. Season-matched placebos (±30–60 d offsets) give median slope −0.020;
50 % of valid placebo slopes exceed the observed median. The event-level response
signal is **not distinguishable from background variability**.

**Q9. Serious pseudoreplication issues?**
Contained but real. Raw event-days (50 for B) shrink to 22 independent events;
dense bird fixes (135k–152k) are aggregated to individual-days before any
summary; species-day responses use per-species medians with n retained. The
binding constraint is few individuals per guild per event (often ≤ 5).

**Q10. What can this dataset support?**
A **case study / methods-demonstration**, not a standalone confirmatory paper:
public multi-species telemetry + public environmental grids + reproducible
event framework is a solid template, but contemporaneous multi-guild coverage
is ~6 months and no event-associated mobility gradient emerges above placebo.

## Decision

**WEAK GO.** Meets ≥ 10 independent events and ≥ 2 guilds for ~10 events, but
fails the GO criterion "preliminary movement response exceeds seasonal placebo
patterns". Not NO-GO: events are numerous, exposure is reliably estimable, and
no single event dominates. A case study ("event-associated redistribution is
compatible with ranging variability; power is limited by contemporaneous
coverage") is feasible and honest.
