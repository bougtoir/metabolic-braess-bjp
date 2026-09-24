# Phase-9 — BBS spatial hysteresis / delayed redistribution

Does the Phase-8B BBS history signal represent genuine prospective path
dependence rather than delayed environmental response, static geography, or
observation structure? See docs/PHASE9_ANALYSIS_PLAN.md, LOYO_FORWARD_
DIAGNOSTIC.md, PHASE9_GO_NO_GO.md.

Run order: see Makefile (env_fetch → species_hg → matched → anomaly → sim9 →
observers_mod → reg_occ_fix → loyo_compare → figures9 → report9).
Data: BBS routes (RunType==1) + Open-Meteo/NASA POWER env; data/ is
gitignored.
