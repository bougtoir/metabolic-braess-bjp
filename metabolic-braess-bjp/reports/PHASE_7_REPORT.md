# Phase 7 Report — Tissue extension + drug-target mapping

## Tissue extension (scope-limited, honest)
The base reconstructions are generic-cell models without tissue-specific
constraints. We therefore probe environmental context via the condition
matrix as proxies for tissue milieus:
  aerobic        ~ normoxic, nutrient-sufficient (e.g. well-perfused tissue)
  glucose_limited~ nutrient-poor (e.g. tumour core, ischaemic margin)
  oxygen_limited ~ hypoxic (e.g. tumour interior, exercising muscle)
Interior optima persist under pFBA in all three milieus in recon3d and in
aerobic human2, but the hit identity/shape shifts: under glucose limitation
the efficiency optima vanish (substrate already scarce; restriction cannot
improve yield further) while parsimony optima remain; under oxygen
limitation the efficiency optima reappear with u*~0.7. Interpretation:
the NOPM landscape is context-dependent — the same drug target can be
monotone-damaging in one tissue milieu and NOPM in another.

## Drug-target mapping (data/drug_mapping.csv — targets only, no dose claims)
Type-II hits map to compounds used in the metabolic-inhibition literature:
  GAPDH        koningic acid, iodoacetate, 3-bromopyruvate (tool compounds)
  ENO (ENO1)   SF2312 (Leonard et al. 2016)
  PGK1         preclinical only
  PDH complex  CPI-613/devimistat (lipoylation target; cancer trials)
  complex I    rotenone; metformin/phenformin (weak, debated)
  complex III  antimycin A
  complex IV   cyanide/CO/azide (mechanistic reference, not therapeutics)
  ATP synthase oligomycin; bedaquiline (approved; mitochondrial off-target)
  LDH          oxamate, galloflavin, FX11 (preclinical)
Framing restriction: the mapping is modulation→target only. We make NO
claim that partial pharmacological inhibition reproduces the computed
optimum (dose–response coupling is a separate, kinetics-dependent question).

## Addendum — family-level replication + reaction→gene→modulator chain
Mechanistic families (data/hit_families.csv):
  mid-glycolysis   human2 5 (GAPDH/PGK/ENO/PGM/TPI) ↔ recon3d 5 (GAPD/PGK/ENO/PGM/TPI)  REPLICATES
  O2 transport     human2 1 (MAR04896)              ↔ recon3d 2 (O2t, O2tm)            REPLICATES
  oxidative phosph. human2 2 (CI MAR06921, ATPsyn MAR06916) ↔ recon3d 1 (CIII CYOR_u10mi) REPLICATES (node level differs)
  PDH complex      human2 4 (DLAT/DLD/PDH-E1/MAR20069) ↔ recon3d 0                    HUMAN2-ONLY (discordant, reported)
Gene→protein→modulator chain (targets only, no dose claims):
  GAPDH(GAPDH)→koningic acid/iodoacetate/3-BP; ENO(ENO1/2)→SF2312;
  PDH(DLAT/DLD/PDHA1)→CPI-613/devimistat; CI→rotenone/metformin(debated);
  CIII→antimycin A; ATPsyn→oligomycin/bedaquiline; O2 transport = gas
  exchange node (no direct drug target — interpret as oxygenation state).
Known partial inhibitors: SF2312 (nM ENO inhibitor), metformin (partial
CI inhibitor), oligomycin partial dosing — none have published
yield-vs-dose curves validating an interior optimum; flagged as the
testable prediction, not established evidence.
