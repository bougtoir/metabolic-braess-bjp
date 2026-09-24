# Supporting Information

### S.1 Population–capital correspondence (Supplementary Table 1)

**[Table 1 here]**

Supplementary Table 1 reports the one-to-one mapping between demographic and capital-accounting variables used in Sect. 3.4 of the main text.

### S.2 Observable asset-lag robustness (Supplementary Table 2)

**[Table 13 here]**

Supplementary Table 2 reports the out-of-sample MAPE of the observable-tempo model M_obs when the asset-specific gestation lags taken from the literature are scaled by factors from 0.5 to 2.0. The median MAPE remains below 4.4 % across all scaling factors, confirming that the M_obs correction is robust to moderate misspecification of individual asset lags.

### S.3 In-sample growth RMSE ranking (Supplementary Figure 1)

**[Figure 1 here]**

Supplementary Figure 1 ranks the 39 countries by in-sample growth RMSE under M0 and overlays M1–M4 and M_obs.

### S.4 Historical episodes and counterfactual wealth narrative (Supplementary Tables 3 and 4)

**[Table 7 here]**

**[Table 8 here]**

Supplementary Table 3 translates the Solow-residual decomposition of Sect. 5.5 into concrete historical episodes. Episodes are selected from well-documented macroeconomic events in the largest OECD economies and the Republic of Korea — Japan's asset-price collapse and the global financial crisis, the United States dot-com boom and global financial crisis, Germany's reunification and global financial crisis, and the 1997–1999 Asian crisis — and are required to have at least three years of data. The selection deliberately contrasts high- and low-investment-gestation regimes and is not driven by the magnitude of the estimated artifact. The 1997–1999 Asian-crisis episode for the Republic of Korea shows the largest tempo artefact: the conventional M0 residual attributes positive TFP growth to the crisis years, but the tempo-corrected M2 and joint M4 series report much lower TFP growth, with the joint correction removing roughly three-quarters of the apparent productivity gain. For the United States, the dot-com boom and the global financial crisis display smaller and partly offsetting artefacts, while Japan's lost decade and the 2007–2009 crisis show no meaningful tempo artefact because investment composition was stable during those episodes.

Supplementary Table 4 reports the country-level wealth adjustment that would follow if the joint-identified intangible share beta were included in official produced-capital accounts. The adjustment is largest for the Netherlands, France and Norway (about 0.9–1.1 percent of produced capital), and smaller for economies with lower R&D intensity. These are lower-bound adjustments because the intangible stock is proxied by R&D expenditure only; Supplementary Table 4 therefore also reports 1.5×, 2.0× and 3.0× scalings of the R&D-based proxy to bracket the broader intangible-capital totals reported by Corrado et al. (2005, 2009). Even the 3.0× scaling leaves the implied produced-capital revision below 4 % for all countries, confirming that the correction is quantitatively modest in aggregate but concentrated in the most innovation-intensive economies.

### S.5 Solow-residual variance decomposition (Supplementary Table 5)

**[Table 6 here]**

Supplementary Table 5 reports the country-level percentage reduction in TFP-growth variance when moving from M0 to M2 (tempo drift only) and from M0 to M4 (joint tempo + intangible).

### S.6 TFP paths under alternative models (Supplementary Figure 2)

**[Figure 13 here]**

Supplementary Figure 2 displays the time-series TFP paths for six representative countries (Japan, the United States, Germany, the Republic of Korea, the United Kingdom, and France) under M0, M2, and M4.

### S.7 Asset-composition determinants of RPIM diagnostics (Supplementary Figure 3)

**[Figure 9 here]**

A natural question is whether the cross-country variation in ρ̂₂ reflects observable differences in asset composition. Countries with a higher share of intangible and R&D-intensive investment might be expected to show larger PIM–CWON divergences (lower ρ̂₂) if their PIM construction omits intangibles, or higher ρ̂₂ if the tempo and intangible corrections in M4 successfully account for the discrepancy.

Supplementary Figure 3 reports a cross-sectional OLS regression of ρ̂₂ on mean R&D expenditure as a share of GDP (World Bank WDI). Under M0, the slope is positive (0.054) but not significant at 5 % using heteroscedasticity-consistent (HC1) standard errors (robust SE = 0.034, t = 1.56, p = 0.128; OLS t = 1.82, R² = 0.082, n = 39). The non-parametric Spearman correlation is also borderline (ρ = 0.29, p = 0.075). Under M4, the slope increases to 0.068 (robust SE = 0.033, t = 2.09, p = 0.043; OLS t = 2.34, R² = 0.129), and the Spearman correlation is significant (ρ = 0.37, p = 0.019). A leave-one-out sensitivity check shows that the M4 slope remains positive and significant in 25 of 39 countries, indicating that the association does not depend on a single outlier. After the tempo and intangible corrections, the link between R&D intensity and PIM–CWON consistency is therefore both statistically sharper and more robust to individual-country influence.

The cross-sectional R² remains modest (12.9 %), reflecting the many other sources of PIM–CWON divergence (land-price revaluations, natural-resource rents, differences in asset-life assumptions). The result should therefore be read as suggestive rather than conclusive: ρ̂₂ is not random noise but reflects, in part, observable asset-composition differences across countries. This provides indirect engagement with the asset-specific profiles that a single-asset PIM cannot directly model, and points toward a natural extension in which ρ̂₂ is decomposed by asset class as multi-asset PIM data become available.

### S.8 Stock-side intangibles: the forgotten β

Let *K_tang(t)* be the tangible PIM stock from (M1)–(M2) and *K_I(t)* be an intangible stock built from R&D expenditure by a geometric PIM with depreciation δ_I = 0.15 (Corrado et al., 2009). A production function augmented by intangibles reads:

    log Y_t = α log K_tang(t) + β log K_I(t) + (1 − α − β) log L_t + log A_t,    (M3)

where β is the intangible share. Standard practice imposes β = 0 (Solow; also M0 and M1 here). Estimating β > 0 is the capital-accounting analogue of re-introducing the parity-specific variance σ in Goldstein et al. (2003).

### S.9 γ_price sensitivity

To test whether the residual PIM-CWON gap in countries such as Japan reflects an asset-price re-evaluation effect rather than a real capital gap, we re-run the comparison under five counterfactual scenarios in which CWON PCA is inflated/deflated at an annual rate γ_price ∈ {−0.04, −0.02, 0, +0.02, +0.04}. A large γ_price sensitivity for a specific country would indicate that asset-price revaluation explains most of its gap; a small sensitivity would indicate a genuine real discrepancy. The interval ±0.04 per year brackets the observed rate of deflation in Japanese urban land prices during the 1990s (Shimizu and Nishimura, 2007) as well as the observed rate of reflation in US commercial real-estate between 2009 and 2019, so the grid is economically meaningful rather than arbitrary. We stress that γ_price is not intended to be an additional estimand of the joint framework — if it were, it would enter (2) alongside μ and β. Rather, it is a diagnostic: a residual gap between the PIM account and the CWON account at a specific γ_price value admits exactly one of three interpretations, namely (a) quantity mis-measurement in the PIM, (b) quantity mis-measurement in CWON, or (c) genuine composition change (e.g. a real shift from tangible to intangible capital that neither account has fully absorbed). The γ_price sweep helps identify (a) and (b) against (c).

### S.10 Asset-price revaluation: the Japan case (Supplementary Figure 4)

**[Figure 4 here]**

Supplementary Figure 4 examines whether the Japan anomaly is consistent with an asset-price revaluation effect γ_price rather than by a real stock discrepancy. A γ_price ∈ [−0.04, +0.04] shifts the Japanese log-ratio by roughly 0.25 log units in total, implying that the observed ~0.06-log-unit gap corresponds to a γ_price ≈ 0.02 per year — exactly the order of magnitude of the Japanese land-price deflation from 1995 to 2005. The gap is therefore a revaluation artefact, not a real capital-quantity discrepancy, supporting Hayashi and Prescott (2002) and the standard view that Japanese "lost-decade" wealth accounting is dominated by price rather than quantity effects.

### S.11 Joint identification: bootstrap CIs on (μ̂, β̂) (Supplementary Figure 5)

**[Figure 5 here]**

(Conceptual diagram Supplementary Figure 5 is placed here to remind the reader of the population–capital correspondence, which motivates the joint identification.)

Bootstrap confidence intervals on the joint estimates (Fig. 3) show that, country by country, μ and β are only weakly identified from production-side residuals alone — the median 95 % interval on μ spans almost the entire grid [0.01, 6.0], and the median interval on β spans about 70 % of its grid [0.0, 0.34]. Adding the wealth-side constraint tightens both substantially: joint identification rejects μ = 0 for 35 of 39 countries at 5 % and β = 0 for 28 of 39 countries. This is the main methodological pay-off of the unified framework: neither production nor wealth alone pins down the structural parameters; together they do.

A second way to read the bootstrap evidence is that the *shape* of the 95 % region in (μ, β) space is strongly country-specific. For R&D-intensive economies (Israel, Republic of Korea, Sweden, the United States) the posterior region is a tight ellipse in the north-east quadrant (μ ≥ 0.3 years, β ≥ 0.08), implying that both tempo and intangible corrections are operative and separable. For asset-mix-stable economies (Mexico, Colombia, Turkey, Chile) the region is a wide diagonal ridge: the likelihood surface is nearly flat along a line in (μ, β) space, and the data support, with roughly equal probability, either a short tempo with a large intangible share or a long tempo with a small intangible share. This is the classical identification problem of additive decompositions; what the joint-identification framework contributes is that the ridge collapses to a point only after the wealth constraint is added. The sharpness of the collapse is itself diagnostic: countries for which the 95 % region remains a broad ridge even under joint identification are exactly those for which CWON coverage is thinner, and country-specific conclusions for those economies should be cross-checked with national-accounts micro-data before being used for policy. Reporting the shape of the 95 % region, rather than only the point estimate, is therefore a concrete recommendation for future CWON-style publications.

### S.12 Relational PIM diagnostics (Supplementary Figure 6 and Supplementary Table 6)

**[Figure 6 here]**

**[Table 3 here]**

Supplementary Figure 6 and Supplementary Table 6 report the Relational PIM diagnostics defined in Sect. 3.4. Two findings stand out. First, under M0 (instant PIM, β = 0) the median ρ̂₂ across 39 countries is 0.801, substantially below the consistency benchmark of 1.0. Only 9 of 39 countries have ρ̂₂ ∈ [0.9, 1.1]. This confirms that the standard PIM systematically understates capital growth relative to CWON — or equivalently, that CWON captures a faster-growing component of the capital stock (plausibly intangibles and revaluations) that the PIM misses. Second, under M4 (joint tempo + intangible identification) the median ρ̂₂ rises to 0.833, and the number of countries in the [0.9, 1.1] consistency band increases from 9 to 12. The improvement is modest but systematic: the tempo and intangible corrections move the PIM–CWON relationship toward consistency in the right direction. The median R² exceeds 0.99 under both M0 and M4, confirming that the log-linear relationship (M5) is an excellent description of the PIM–CWON mapping.

Supplementary Figure 6(b) plots ρ̂₁ against ρ̂₂ under M4. Countries that are far from the (ρ₁ = 0, ρ₂ = 1) reference point — particularly Switzerland (ρ̂₂ ≈ 0.40), Poland (ρ̂₂ ≈ 0.60), and Norway (ρ̂₂ ≈ 0.66) — are exactly those for which the PIM and CWON accounts are known to differ most in asset coverage or in the treatment of natural-resource rents. The RPIM diagnostic therefore serves as a simple, interpretable quality-control tool for national capital accounts: a country whose ρ̂₂ deviates markedly from unity warrants closer investigation of the underlying asset-composition assumptions in both accounts.

### S.13 Depreciation–lag sensitivity (Supplementary Figure 7)

**[Figure 7 here]**

A natural concern (discussed further in Section 6.6) is that if the true depreciation rate δ is itself drifting, some of what we attribute to μ(t) could instead be absorbed by a time-varying δ(t). We address this directly by re-estimating the constant lag μ̂ (M1) under five depreciation scenarios: δ × {0.80, 0.90, 1.00, 1.10, 1.20}.

Supplementary Figure 7 shows the results. The main finding is that μ̂ is remarkably stable across the ±20 % depreciation perturbation for most countries. The cross-country mean μ̂ moves from 1.61 years (δ × 0.80) to 1.52 years (δ × 1.20), a shift of only 0.09 years — less than 6 % of the baseline estimate. The median μ̂ is virtually invariant at 0.26 years across all five scenarios. Countries with interior-solution μ̂ values (Slovakia, Luxembourg, United Kingdom, Sweden, Slovenia, and Colombia) show the expected negative relationship: higher depreciation slightly reduces the estimated lag, since faster depreciation absorbs some of the growth-rate variation that would otherwise be attributed to the gestation delay. However, the sensitivity is quantitatively small: a ±20 % perturbation in δ moves μ̂ by at most 1.25 years even for the most sensitive country (Slovakia: 5.75 → 4.50 years; Luxembourg: 3.75 → 3.00 years). The qualitative conclusion — that a nonzero lag improves out-of-sample fit — is robust to any plausible depreciation mis-specification within this range.

### S.14 Conditional out-of-sample evaluation (Supplementary Figure 8)

**[Figure 8 here]**

Table 1 reports that M4 (joint tempo + intangible) achieves an out-of-sample MAPE of 4.61 %, virtually identical to M0 (4.60 %). This apparent non-improvement deserves scrutiny. In the constant-lag (M1) grid search, __N_BOUNDARY__ of the __N_COUNTRIES__ countries hit a boundary for μ: __N_LOWER_BOUND__ at the lower bound (0.01, effectively zero lag) and __N_UPPER_BOUND__ at the upper bound (6.0). For the lower-bound countries the lag correction is mechanically inoperative (μ̂ ≈ 0 ≡ M0), while for the upper-bound countries the lag is constrained at the longest admissible value, so the full-sample M0–M4 comparison conflates several distinct groups.

Supplementary Figure 8 therefore reports the OOS performance separately for the __N_INTERIOR__ interior-solution countries (μ̂_M1 ∈ (0.02, 5.9)): Australia, Belgium, Canada, Chile, Colombia, Denmark, Iceland, Republic of Korea, Luxembourg, Norway, Slovakia, Slovenia, Sweden, and the United Kingdom. For this subsample, M1 (constant lag) achieves a median MAPE of 4.23 %, slightly below M0's 4.27 %. For the boundary-solution countries, M1 and M2 also improve over M0 (boundary M1 = 3.98 %, boundary M2 = 3.83 % vs. boundary M0 = 4.72 %), reflecting the contribution of countries whose estimated lag is at the upper bound. The key insight is that the full-sample median mixes countries where the lag correction is mechanically inoperative, countries where it is constrained at the boundary, and countries where it is freely estimated in the interior.

### S.15 Extended out-of-sample metrics (Supplementary Table 7)

**[Table 4 here]**

MAPE measures average percentage error in GDP levels but does not capture whether models track the *direction* of GDP growth or the *trajectory* of the wealth-side capital stock. Supplementary Table 7 reports two additional metrics computed on the 2015–2019 hold-out window.

First, direction accuracy — the fraction of test years for which the model correctly predicts the sign of GDP growth — is uniformly high across all models (median 100 %), reflecting the fact that GDP growth was positive in almost all OECD economies throughout 2015–2019. Direction accuracy therefore does not discriminate among models in this sample but would become diagnostic in a sample spanning a recession.

Second, the CWON trajectory RMSE measures how well each model's PIM capital stock tracks the CWON produced-capital trajectory on the hold-out years (demeaned log comparison). Here M2 (tempo drift) achieves the lowest median RMSE (0.0072), compared with M0 (0.0085) — a 15.3 % improvement. M1 (constant lag) is intermediate (0.0077). M4 achieves 0.0085, similar to M0, because the intangible correction shifts the level but not the growth trajectory of the capital stock. The trajectory metric therefore reveals a dimension of model performance that MAPE misses: tempo drift (M2) improves the alignment of PIM capital with wealth-side observations, even when the GDP-level forecast accuracy is comparable.

### S.16 Counterfactual wealth: what if β entered official statistics? (Supplementary Figure 9)

**[Figure 14 here]**

The intangible capital share β has a direct policy implication: if β were included in official wealth accounts, national produced capital would be revised upward. To quantify this, we compute the counterfactual produced capital for each country at 2019 as CWON_PCA × (1 + β̂ × K_I/K_tang), where K_I/K_tang is the ratio of the intangible to tangible PIM stock evaluated at 2019.

Supplementary Figure 9 displays the results for the 21 countries with β̂ > 0. The Netherlands, France, and Norway show the largest adjustments (0.9–1.1 %), reflecting the combination of high β̂ (0.34) and high R&D-to-GDP ratios. For total national wealth (CWON total), the adjustments are 0.1–0.3 % because produced capital is only one component of total wealth. These are conservative lower bounds because the intangible stock is proxied by R&D expenditure alone; a broader intangible measure (Corrado et al., 2005) including organisational capital, brand equity, and training would produce larger adjustments. The right-hand columns of Supplementary Table 4 therefore add 1.5×, 2.0× and 3.0× R&D scalings to bracket how large the adjustment could become if the R&D proxy is expanded to a full intangible-capital total.

The policy implication is concrete: countries that omit intangibles from their wealth accounts systematically understate the productive capital base on which future growth depends. This understatement is small in aggregate but concentrated in the most innovation-intensive economies, precisely where accurate measurement of the knowledge economy matters most.

### S.17 Future forecast scenarios (2020–2040) (Supplementary Figure 10 and Supplementary Table 8)

**[Figure 15 here]**

**[Table 9 here]**

To illustrate how the measurement corrections propagate into forward-looking output paths, we simulate mechanical projections for all 39 sample countries plus selected economies that span advanced and emerging-market cases. These are not economic forecasts: they hold policy, demographics, terms of trade, and technology diffusion fixed at historical patterns and extrapolate the estimated accounting corrections. For countries whose 2010–2019 investment or R&D series are too short or contain non-positive values to estimate a log growth rate, we apply a conservative 2 % per annum fallback (the historical long-run growth rate of real investment in the sample). This fallback is documented and flagged in Supplementary Table 8.

Supplementary Figure 10 highlights six representative economies: the United States, Japan, Germany, the Republic of Korea, China and Colombia, covering high-R&D advanced economies, a resource-intensive emerging market and a large manufacturing exporter. Under the M2 trend-continuation scenario, GDP in 2040 is slightly above the M0 baseline for most economies because the time-varying lag slows measured capital accumulation and raises measured TFP; the M2 stabilisation and M4 baseline trajectories are close to the M0 baseline. The M4 AI/digital investment surge scenario adds an extra annual growth increment to R&D-driven intangible investment; in R&D-intensive economies this raises the 2040 GDP index relative to the M4 baseline. The M4 TFP stagnation scenario holds TFP flat at its 2019 level and shows the largest divergence from baseline growth because it removes the assumed continuation of trend TFP growth. The M4 TFP level-only scenario instead freezes the 2019 TFP *level* rather than the 2010–2019 trend, separating the pure level effect of the capital-stock correction from trend extrapolation. Finally, the M4 fiscal-stimulus scenario adds public investment equal to 2 % of 2019 GDP each year, growing with the M4-corrected output path; this links the measurement correction directly to a stylised fiscal-capacity calculation and shows how much additional output a sustained public-investment programme could generate once the capital-stock base is measured consistently. All of the AI/digital, fiscal-stimulus and TFP level-only scenarios are stylised projections, not economic forecasts or policy prescriptions; they isolate the sensitivity of measured output paths to alternative accounting assumptions and hold policy, demographics, terms of trade and technology diffusion fixed.

Supplementary Table 8 reports the 2030 and 2040 indices for all countries and for all five scenario variants. The policy message is that measurement-sensitive variables — the capital-stock level, the TFP trend and the treatment of intangible investment — are exactly the inputs that enter fiscal-sustainability and monetary-policy reaction functions. Correcting them therefore changes the baseline against which policy is calibrated.

### S.18 Cross-country clusters by (μ, β) and asset composition (Supplementary Figure 11 and Table 9)

**[Figure 16 here]**

**[Table 10 here]**

Clustering countries on the joint-identified (μ, β), R&D intensity, and asset-composition shares yields three groups. The first group contains most Continental European and resource economies with low-to-moderate μ and low β. The second group contains the high-R&D, ICT-intensive economies, including the United States, Republic of Korea, Sweden, and Israel, with higher μ and a larger share of intellectual-property investment. The third group is a small set of economies with very high estimated μ and high β. These clusters are visible in Supplementary Figure 11 and quantified in Supplementary Table 9. We selected k = 3 after comparing candidate solutions k = 2, …, 6 on silhouette, inertia and bootstrap stability; the three-group partition was the most parsimonious solution that remained economically interpretable (high-ICT intangible-intensive, manufacturing-export oriented, and resource/land-intensive). Supplementary Tables 14 and 15 report the silhouette and bootstrap validation metrics and the per-country cluster assignments that support the k-means partition.

### S.19 Time-varying depreciation robustness

Supplementary Figure 12 displays the median estimated lag under each time-varying depreciation schedule, and Supplementary Table 10 reports the country-level median estimates.

**[Figure 17 here]**

**[Table 11 here]**

Supplementary Section S.13 showed that a uniform ±20 percent perturbation of δ leaves the constant-lag estimate stable. We extend this to six explicit time-varying depreciation schedules that let the depreciation rate rise or fall with the share of short-lived ICT assets. The median estimated lag across countries is largely insensitive to these perturbations; the largest response appears when the depreciation rate is assumed to rise with the ICT share. The result supports the interpretation that the estimated μ(t) is not merely an alias for misspecified depreciation.

### S.20 Monte Carlo identification sharpness (Supplementary Figure 13 and Supplementary Table 11)

**[Figure 18 here]**

**[Table 12 here]**

To assess how well the joint loss identifies μ and β from finite samples, we simulate economies calibrated to four distinct economies: the United States, the Republic of Korea, France and Colombia. These calibrations span high-R&D/ICT-intensive, manufacturing-export and resource-intensive profiles, and therefore test whether identification sharpness is driven by a single parameter configuration. We vary the sample length (T = 30, 40, 50 years) and the variance of the output shock σ. The values T = 30, 40 and 50 cover the range observed for most countries in our sample: many OECD and middle-income series span 40–55 annual observations, so T = 50 is close to the effective upper bound for the cross-section while remaining short enough to test identification in emerging-market series. The RMSE of the joint-identified μ and β declines with T and rises with σ, but even with moderate output noise the RMSE remains below the grid resolution for sample lengths typical of OECD national accounts. This confirms that the joint identification is statistically sharp in the empirically relevant region, and that the conclusion is not an artefact of the United States calibration.

### S.21 Cross-country γ_price summary (Supplementary Table 12)

**[Table 14 here]**

Supplementary Table 12 extends the Japan γ_price case study of S.9–S.10 to all 39 countries. For each country we fit a line to the PIM–CWON log-ratio as a function of γ_price ∈ [−0.04, +0.04] and report the zero-crossing price-revaluation rate, together with a flag indicating whether that root lies inside the explored interval. No country shows an in-range zero; the implied price-revaluation rates that would close the PIM–CWON gap are all outside the ±4 % per year window. This reinforces the interpretation that the residual gap is not a simple price-revaluation artefact at conventional magnitudes, except in the Japanese case where the historical land-price deflation makes a 2 % per year revaluation economically plausible.

### S.22 Historical-episode selection and leave-one-out robustness (Supplementary Table 13)

**[Table 7b here]**

Supplementary Table 13 reports a leave-one-episode-out robustness check for the historical episodes of Supplementary Table 3. Each row drops one episode and recomputes the mean joint artifact (M4 − M0) across the remaining episodes. The deviations are small relative to the full-sample mean, confirming that the narrative conclusion — a material tempo-plus-intangible artifact during high-investment-gestation episodes — is not driven by a single episode or country.

### S.23 Cluster validation metrics (Supplementary Table 14)

**[Table 10b here]**

Supplementary Table 14 reports the overall silhouette score and a bootstrap stability index for the k = 3 k-means partition shown in Supplementary Table 9. The stability index is the mean adjusted Rand index between the initial k = 3 labels and those obtained from 100 bootstrap replications of the same data, each refit with k = 3. It is well above the near-zero value expected for random relabeling, indicating that the three-group partition is reasonably reproducible on resampling.

### S.24 Cluster diagnostics (Supplementary Table 15)

**[Table 10c here]**

Supplementary Table 15 reports silhouette scores and k-means inertia for candidate numbers of clusters k = 2, …, 6. The k = 3 solution was selected for the main cluster summary because it is the most parsimonious partition with a silhouette score near the maximum and produces policy-interpretable groups (high-ICT intangible-intensive, manufacturing-export oriented, and resource/land-intensive). Higher k values raise the silhouette score mechanically by forming smaller, more homogeneous groups, but the bootstrap stability of those finer partitions is low and their economic interpretation is less clear. Supplementary Table 15 therefore shows that the choice of k = 3 is not driven by a single local peak in the objective function; it reflects a stability–interpretability trade-off.
