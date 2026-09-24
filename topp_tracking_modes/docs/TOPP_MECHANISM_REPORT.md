# TOPP: Competing mechanisms of marine predator tracking — Mechanism Report

## Setup
- Data: `gtoppAT` TOPP historical tags (public ERDDAP), 579,485 fixes;
  CCS window 30–48°N/235–243°E, ≥30 d in-box → 287 animals, 12 species,
  26,000 animal-days; outcome y = log1p(active displacement km) after
  AVISO geostrophic advection correction (residual |O−A|).
- Events: Bakun UWI pulses at 5 coastal stations (33–45°N), daily-series
  onset detection (≥3 prior days below median), 7-day separation →
  523 events, 183 in-season; 1,447 animal-days fall inside event windows.
- Prey field: SeaWiFS 8-d chl-a — **INDIRECT** proxy only; no direct prey
  layer exists in TOPP. Coverage 17,878 animal-days.
- Eligible species (≥5 animals, ≥800 model days): California Sea Lion,
  Northern Elephant Seal, Blue Whale, Salmon Shark.

## H1–H4 results (in-sample, animal-clustered SEs)
- E→predator (M_E): |coef| ≤ 0.0007, sign mixed (CASL/SS positive,
  BW/NES negative). Weak.
- prey→predator (M_K / M_EK): `K` coefficient negative in every species
  (−0.02 to −0.35 log-disp per log-chl). Direction consistent with
  residence in richer water, but the proxy is indirect and effect sizes
  small (R² gain over env-only ≤ 0.01 except NES).
- Mediation: attenuating K into M_EK leaves E coef unchanged → no
  trophic mediation detected (H2 unsupported, H3-style shared forcing
  cannot be excluded because the K-link itself is weak).
- H4 predictive cueing: env_t → chl_{t+8} CV correlations are ~0
  (CASL −0.02, NES +0.13); M_PREDICTIVE adds no robust gain, and
  Khat coefficients are unstable sign-wise. Environmental cues here do
  not carry usable information about future prey fields at this
  resolution — no support for H4.

## Event-held-out CV (§13)
Only N. elephant seal had ≥3 usable event folds. All models transfer
negatively (mean corr ≈ −0.72 to −0.81): none of the fitted mechanisms
generalizes to held-out events. Model selection on out-of-event data is
impossible → the strongest honest statement is that no mechanism is
supported at event resolution.

## Lag profiles (§14)
Peak lags scatter across −14..+14 d with no consistent ordering of
E→K < K→P or E→P (see lag_peaks.csv / lag_response.png). No cascade.

## Reverse time & placebos (§15–16)
Reverse-time check does not cleanly favor forward direction (NES
reverse association actually stronger: p=0.002 vs 0.03). Placebos:
±30 d temporal shifts of UWI exceed the observed E-coef in Blue Whale;
permuted-UWI ≈ 0; SST-as-prey placebo picks up a larger coefficient than
real chl in Blue Whale — the "prey" term is partly generic habitat
structure, not prey specifically.

## LOEO
Per-species E coef ranges are narrow with zero sign flips — but the
point estimates are near-zero, so stability ≠ signal.

## Species modes (species_tracking_mode.csv)
NES: MIXED-WEAK (negative CV transfer). Blue Whale, California Sea
Lion, Salmon Shark: INCONCLUSIVE (insufficient event folds).

## Largest validity threats
1. Prey proxy is INDIRECT (chl-a at 8-d/4-km vs animal behavior).
2. Event coverage thin: only 1,447/26,000 animal-days inside windows,
   and event×species overlap is sparse → event-level CV nearly
   unidentifiable except NES.
3. ~10 yr SeaWiFS gap after 2009 excludes later TOPP years.
4. Advection correction uses 6-day AVISO steps — submesoscale drift
   may contaminate "active" displacement.

## Classification
**System-level: MIXED-WEAK / INCONCLUSIVE.** Per species: 1×MIXED-WEAK
(NES), 3×INCONCLUSIVE. No support for pure H2; H1/H3-style direct
environmental tracking is weak in-sample and fails event-level
generalization; H4 not supported at these resolutions.

## Nature-route gate
**FAIL** — the TOPP/CCS design cannot currently discriminate the four
mechanisms with the available prey proxy and event coverage. Standards
were not relaxed.
