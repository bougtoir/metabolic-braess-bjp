[TITLE PAGE — SEPARATE FILE]

# The Solow Residual as a Measurement Artefact: Investment Gestation Lags, Intangible Capital, and Macroeconomic Policy

**Onishi Tatsuki**

Data Science and AI Innovation Research Promotion Center, Shiga University

1-1-1, Bamba, Hikone, Shiga, 522-8522 Japan, Telephone: +81-749-27-1023, E-mail: bougtoir@gmail.com, ORCID: 0000-0001-7261-9062

**Declarations**

*Competing interests.* The author declares no competing interests.

*Consent to participate.* Not applicable.

*Consent to publish.* Not applicable.

*Data and code availability.* Penn World Table 10.01, World Bank CWON, World Bank WDI, and OECD GFCF data used in this study are publicly available from their respective providers. Frozen source extracts, checksums, analysis scripts, intermediate results, and manuscript sources are archived at https://github.com/bougtoir/gdp-tempo-paper.

*Declaration of generative AI use.* The author used generative AI to assist with formatting the text, choosing words that suited the tone, and writing analysis code. The author reviewed and edited the content as needed and takes full responsibility for the content of the published article.

*Ethics approval.* This research uses publicly available, aggregate macroeconomic data (Penn World Table 10.01, World Bank CWON, World Bank WDI, OECD GFCF). No human subjects, animals, or personally identifiable data were involved. Ethical approval was not required.

*Funding.* No external funding was received for this research.

[END TITLE PAGE]

---

[MANUSCRIPT]

# The Solow Residual as a Measurement Artefact: Investment Gestation Lags, Intangible Capital, and Macroeconomic Policy

**Abstract.** Conventional growth accounting attributes variation in aggregate output to total factor productivity (TFP). We show that a measurable share of the Solow residual is a measurement artefact arising from two conventions routinely imposed at zero: the mean gestation lag between investment and output is treated as constant and negligible, and produced capital omits intangible investment. By jointly estimating a time-varying investment-to-output lag, μ(t), and a country-specific intangible-capital share, β, for 39 OECD and middle-income economies over 1970–2019, we reconcile production-side and wealth-side national accounts to within 1–2 per cent for most countries. Correcting the gestation-lag bias raises log-level TFP by a median 1.7 percentage points and the implied labour share by 1.7 percentage points; the additional intangible-capital correction raises produced capital by up to 1.1 per cent and total wealth by up to 0.3 per cent in research-intensive economies. The tempo correction is validated by an observable, parameter-free proxy constructed from OECD asset-composition data for the 35 countries with asset-type detail. Monte Carlo and time-varying-depreciation robustness checks confirm that the joint identification is statistically sharp. Because these measurement biases feed directly into potential-output estimates and the calibration of fiscal and monetary policy responses, correcting them is of immediate policy relevance.

**Keywords**: Solow residual; time-to-build; intangible capital; growth accounting; national wealth; macroeconomic policy.

**JEL codes**: E01, E22, E44, E52, E62, O47.

---

## 1 Introduction

Macroeconomic policy is calibrated to measured productivity. Output-gap estimates, debt-sustainability projections and monetary-policy reaction functions all build on total factor productivity (TFP), so any systematic measurement error in TFP feeds directly into the policy stance. This paper shows that conventional TFP estimates conflate genuine innovation with two accounting conventions that are increasingly implausible in the modern economy: investment is treated as productive the moment it is spent, and the capital stock omits much of intangible investment. Correcting these two conventions revises measured TFP growth by several percentage points during well-known episodes such as the Republic of Korea's 1997–1999 crisis, and raises median log-level TFP by 1.7 percentage points across 39 countries. These are not forecasts of new technologies; they are measurement consequences with immediate implications for fiscal rules, monetary transmission and cross-country productivity comparisons.

Every macroeconomic forecast, fiscal-policy rule, and monetary-policy assessment embeds a single residual: total factor productivity, or TFP. A measurable share of what is labelled TFP is neither technology nor innovation, but a bookkeeping artefact produced by two conventions standard growth accounting imposes at zero: the lag between investment and output is treated as constant and negligible, and produced capital omits intangible investment. Both conventions were defensible when economies invested mainly in plant and equipment; they become harder to defend now that investment has shifted toward software, cloud infrastructure, pharmaceutical R&D, and complex engineering systems.

This paper makes three contributions. First, it estimates a time-varying investment-to-output lag μ(t) for a broad set of countries and shows that the standard PIM capital stock is systematically mis-timed as a result. Second, it recovers a country-specific intangible-capital share β by jointly disciplining production-side growth residuals and wealth-side capital trajectories. Third, it demonstrates that the demographic tempo-and-quantum framework — used for fertility since Bongaarts and Feeney (1998) — transposes cleanly to capital accounting, providing an observable, parameter-free proxy *M_obs* that can be built from existing OECD asset data.

The measurement error has a specific, quantifiable source. Conventional growth accounting imposes at zero the time-varying lag μ(t) and the intangible capital share β. While time-to-build has been studied since Kydland and Prescott (1982), all prior work treats the lag as fixed across decades. Yet the composition of investment has shifted toward long-lead assets — custom software, R&D platforms, and complex engineering systems — whose gestation periods differ by nearly an order of magnitude from the plant and equipment on which the foundational lag literature was calibrated (OECD, 2013; Corrado et al., 2020). When μ is rising but treated as zero, the PIM capital stock is mis-timed and the Solow residual absorbs the error. The parameter β captures the broader intangible capital share that Corrado et al. (2005, 2009) have shown is quantitatively large, yet official wealth accounts — including CWON (Lange et al., 2021) — capture only partially. When β is forced to zero, any intangible component not already recorded inflates TFP.

The identification strategy exploits a structural analogy with population statistics. Bongaarts and Feeney (1998) showed that a drifting mean age at childbearing depresses measured period fertility even when completed fertility is constant; Goldstein et al. (2003) showed that their adjustment was an upper bound unless a parity-specific "forgotten" variance σ was re-introduced. Under a precise change of variables, the same mathematics applies to capital accounting (Supplementary Table 1): investment plays the role of births, the PIM capital stock plays the role of the population stock, μ(t) is the analogue of the mean age at childbearing, and β is the analogue of the forgotten variance. The same timing correction, applied for the first time to capital accounting, should carry at least as much empirical content.

These measurement corrections have direct macroeconomic implications. The observable proxy *M_obs* — constructed from OECD GFCF asset composition by weighting asset-specific gestation lags by their investment shares — changes measured capital stocks by a median 4.3 % across 35 OECD and middle-income economies (Penn World Table 10.01, World Bank CWON, 1970–2019; CWON available from 1995). This is not a forecasting result: it is a measurement consequence. Because *M_obs* lowers measured capital relative to the standard PIM, it raises measured log-level TFP by a median 1.7 percentage points and the implied labour share by 1.7 percentage points. The effects are largest in economies whose investment mix has shifted toward long-gestation assets — Ireland (−9.2 %), Republic of Korea (−7.1 %), Israel (−6.4 %) — and smallest where the asset mix has been stable. A Solow-residual decomposition reveals that tempo drift alone (M0 → M2) accounts for up to 13.8 % of TFP-growth variance in some countries (and the joint correction (M0 → M4) for up to 29.7 %). Under the joint model, counterfactual wealth calculations show that official produced-capital figures understate the corrected produced-capital stock by up to 1.1 % in high-R&D economies, with the effect on total wealth below 0.3 %. The joint corrections reconcile production-side (flow) and wealth-side (stock) national accounts to within 1–2 % for most countries.

Three implications follow. First, potential-output estimates inherit the tempo bias, so output-gap and fiscal-policy calculations may be misdirected. Second, the lengthening of monetary-policy transmission lags (Havranek and Rusnak, 2013) can be partly interpreted through gestation: as projects take longer to mature, the real-economy response to interest-rate changes is delayed. Third, cross-country heterogeneity in (μ̂, β̂) maps onto differences in investment composition, so one-size-fits-all depreciation schedules are a source of international GDP comparability problems.

The remainder of the paper proceeds as follows. Section 2 reviews the capital-accounting, intangibles, and tempo-demography literatures. Section 3 develops the theory. Section 4 describes the data and methods and defines five models M0–M4. Section 5 reports the core empirical results. The Supporting Information reports robustness checks. Section 6 discusses policy implications. Section 7 concludes.

## 2 Related literature

**Capital accounting and time-to-build.** Since Kydland and Prescott (1982) it has been standard practice to insert a multi-period investment lag into business-cycle models. Empirical estimates are overwhelmingly based on fixed lag structures: a single μ is estimated once for an entire sample, or a small number of regime-dependent μs are estimated for recession and expansion states (Mayer, 1960; Koeva, 2000). Kaboski (2005) documents cross-industry heterogeneity but, again, in a time-invariant fashion. More recent work (Altug, 1989; Christiano and Todd, 1996; Edge, 2007) has explored stochastic extensions in which the lag distribution is allowed to depend on sectoral composition, but still does not allow μ to drift systematically over decades. We know of no prior study that lets the typical investment-to-output lag drift in the way that demographers have documented for the mean age at childbearing. This omission matters because post-1990 investment has shifted substantially toward long-lead assets — custom industrial software, cloud infrastructure, pharmaceutical R&D, complex engineering systems — whose gestation periods differ by nearly an order of magnitude from the plant and equipment of the 1960s on which the foundational lag literature was calibrated (OECD, 2013; Corrado et al., 2020).

**Intangible capital.** The programme begun by Corrado et al. (2005, 2009) has by now produced robust international evidence that software, R&D, design, brand, organisational capital, and training account for 30–60 % of productivity growth in advanced economies (INTAN-Invest: Corrado et al., 2016; Roth, 2022). The 2008 SNA (United Nations et al., 2009) formally incorporated R&D into produced capital, but broader intangibles — organisational capital, brand, training, purchased design services, some categories of financial innovation — remain excluded from most official balance sheets, including the World Bank CWON (Lange et al., 2021, Chap. 3). McGrattan and Prescott (2010) and Haskel and Westlake (2017, 2022) emphasise that this omission biases not only the level of measured capital but also the implied productivity growth rate whenever the intangible share is expanding — exactly the setting of our 1995–2019 sample. In practice, the intangible share β is not a global constant: Japan, Germany, and some East-Asian economies retain a smaller intangible share than the United States even under harmonised measurement (Corrado et al., 2020), so β ought to be a country-specific parameter, which is how we treat it in Sect. 4.

**Wealth accounting.** The Beyond-GDP movement, from Stiglitz et al. (2009) through Jorgenson (2018) and Managi and Kumar (2018), proposes to replace or augment GDP with wealth-style aggregates. Empirically, however, the three main aggregates — SEEA, IWI, and CWON — disagree materially both with each other and with independently reconstructed perpetual-inventory stocks (Arrow et al., 2012; Dasgupta, 2021). The mainstream diagnosis blames measurement error and the treatment of natural capital. We show that a more mundane culprit — a mis-specified time-to-build and an omitted intangible share — accounts for a sizeable fraction of the discrepancy.

**Tempo and forgotten parameters in demography.** Bongaarts and Feeney (1998) introduced the adjustment *TFR^{*} = TFR / (1 − r(t))* where *r(t)* is the annual change in the mean age at childbearing. Goldstein et al. (2003) showed that the Bongaarts and Feeney (1998) adjustment was an upper bound unless a parity-specific "forgotten" variance σ was re-introduced. Kohler et al. (2002) and Bongaarts and Sobotka (2012) confirmed both findings across Europe. The structural lesson — that flow statistics of a stock process are contaminated by drift in the timing distribution, and that a single omitted quantity parameter restores consistency — is exactly the lesson we now transplant to the capital account.

**Healthcare and human capital sustainability.** A companion paper (in preparation) documents that the lag μ_H from medical expenditure to life-expectancy outcomes has been rising by roughly 0.15 years per year since 2000, and that an analogous "forgotten" parameter β_H — the share of expenditure directed to prevention and R&D, as opposed to curative care — accounts for a further share of the US-Japan life-expectancy gap. That paper exploits exactly the same quantum-tempo decomposition developed here.

**The gap this paper fills.** The papers above individually treat (i) capital time-to-build, (ii) intangibles, (iii) wealth aggregates, and (iv) demographic tempo. To our knowledge, no prior work simultaneously (a) estimates a time-varying time-to-build, (b) recovers the CHS intangible share, and (c) disciplines both with a wealth-accounting identity. This paper combines all three. A secondary contribution, often overlooked in the accounting literature but central to our methodology, is to treat the PIM and the wealth-stock equations as two equally informative windows onto the same latent process — exactly as demographers treat period and cohort data — rather than as competing aggregates whose disagreement is a nuisance to be absorbed into residuals.

## 3 Theory

### 3.1 Flow-side production function with tempo

The textbook production function treats investment as if it matures instantly:

    K_instant(t) = (1 − δ_{t-1}) K_instant(t−1) + I_{t-1},                         (M0)

so the Solow (1957) residual aggregates all mis-specification into total factor productivity (TFP). Since Mayer (1960) and Kydland and Prescott (1982) it is well known that, in reality, investment accrues to the stock only after a lag. We write this as a distributed-lag perpetual inventory:

    K(t; μ) = (1 − δ_{t-1}) K(t−1; μ) + Σₛ w_s(μ) I_{t-1-s},                     (M1)

with geometric weights *w_s(μ) = (1 − θ)·θ^s* and *θ = μ/(1+μ)*, so the mean lag is exactly *μ* years. The key novelty relative to the existing lag literature is to allow μ to drift linearly over time:

    μ(t) = μ₀ + μ₁·(t − t₀),                                                    (M2)

where μ₁ captures the "tempo" in the sense of Bongaarts and Feeney (1998). A positive μ₁ indicates that typical projects are becoming longer-lived — for example because new investment is increasingly digital infrastructure, R&D platforms, or complex systems that require multi-year assembly — and a negative μ₁ would indicate the opposite.

### 3.2 Unifying identity: the flow-stock joint loss

Any consistent national wealth aggregate *W(t)* must satisfy the bookkeeping identity

    dW/dt = S(Y) − δ_W · W,                                                       (1)

where *S(Y)* is gross saving and *δ_W* is the aggregate depreciation rate. Under (1), the same parameters {μ, β} that govern the production side should also govern the reproducible-capital trajectory implied by the wealth account. We therefore define a single joint loss:

    L_total(μ, β) = L_production(μ, β) + λ · L_wealth(μ, β),                      (2)

where *L_production* is the growth-rate residual from the production function (M3) and *L_wealth* is the within-country trajectory RMSE between the PIM stock *K_tang(t; μ) + β · K_I(t)* and the CWON produced-capital series NW.PCA.TO(t). Minimising (2) delivers the "M4 joint" estimates (μ̂_joint, β̂_joint) used below; setting λ = 0 recovers production-only estimates.

### 3.3 Quantum–tempo correspondence between population and capital

Supplementary Table 1 lays out the one-to-one mapping between the demographic variables that Bongaarts and Feeney (1998), Goldstein et al. (2003), and their successors analysed and the capital-accounting variables we analyse. Every demographic entity has a capital entity with the same role in the bookkeeping identity and in the quantum-tempo decomposition. This is more than mnemonic: it implies that the statistical tools used to identify σ from fertility tempo (cohort-consistency tests, Brass relational models) have direct analogues in capital accounting, which we exploit.

### 3.4 Relational PIM: a Brass model for capital accounting

Demography has long employed Brass relational models to compare an observed fertility or mortality schedule against a "standard" schedule via a small number of parameters that capture systematic deviations (Brass, 1971). We transplant this idea to capital accounting. Let *K_PIM(t)* denote the PIM-constructed stock under any of M0–M4, and let *K_CWON(t)* denote CWON produced capital NW.PCA.TO. We define the **Relational PIM** (RPIM) as:

    log K_PIM(t) = ρ₁ + ρ₂ · log K_CWON(t) + ε(t),                              (M5)

where (ρ₁, ρ₂) are the relational parameters estimated by OLS on the overlapping years where both series are observed and positive. The interpretation is direct:

* **ρ₂ = 1 and ρ₁ = 0**: the PIM and CWON accounts are fully consistent — they measure the same latent stock up to a white-noise error.
* **ρ₂ ≠ 1**: there is a cumulative (scale-dependent) bias in the PIM relative to CWON. If ρ₂ < 1, the PIM understates the growth of capital relative to CWON; if ρ₂ > 1, it overstates it.
* **ρ₁ ≠ 0**: there is a level shift between the two accounts, capturing differences in base-year calibration, PPP conversions, or asset coverage.

The novelty is threefold. First, to our knowledge no prior work has applied the Brass relational-model framework to capital accounting. Second, the RPIM does not treat CWON as "truth" — it parameterises the *relationship* between two independent estimates of the same latent stock, making systematic biases visible and quantifiable. Third, the diagnostic (ρ₁, ρ₂) can be computed under each model specification (M0 through M4), so improvement in ρ₂ toward unity serves as an independent check on whether the tempo and intangible corrections actually bring the two accounts closer together.

## 4 Data and methods

### 4.1 Data

We use **Penn World Table 10.01** (Feenstra et al., 2015) for real GDP output (*rgdpna*), tangible capital stock (*rnna*), investment share (*csh_i*), depreciation (*delta*), employment (*emp*), average hours (*avh*), human-capital index (*hc*), and labour share (*labsh*). For R&D intensity we use **World Bank WDI** series *GB.XPD.RSDV.GD.ZS*. For wealth we use **World Bank Changing Wealth of Nations** 2021 release (Lange et al., 2021) — specifically *NW.PCA.TO* (produced capital total), *NW.HCA.TO* (human capital total), and *NW.TOW.TO* (total wealth). For the observable-tempo construction *M_obs*, we use **OECD gross fixed capital formation by asset type** (OECD.Stat, SNA Table 8A), which reports investment broken down by asset category (dwellings, other buildings, transport equipment, ICT equipment, other machinery, intellectual property products) for all OECD member states.

One caveat on double counting matters. PWT *rnna* is already a perpetual-inventory capital stock that, depending on the country vintage, may include some intellectual-property products. CWON produced capital also incorporates R&D in many countries following the 2008 SNA. Our intangible stock *K_I* is built from WDI R&D expenditure and therefore risks overlapping with assets already counted in *rnna* or CWON. Because asset-level PWT detail is not public, we cannot net out the overlap exactly; M3 and M4 should be interpreted as a proxy for the produced-capital coverage gap between the PWT/CWON asset boundary and the broader intangible-capital literature — i.e. an upper-bound correction for intangible capital not already captured in the baseline — while M0 and M2 are unaffected.

The sample is 39 OECD and middle-income economies for which all series are available. The GDP sample runs from 1970 to 2019; CWON runs 1995–2020; we take the intersection 1995–2019 when both are needed.

### 4.2 Models M0, M2, M4 and M_obs

The main text focuses on four specifications. M0 is the Solow baseline; M2 adds the time-varying gestation lag μ(t) = μ₀ + μ₁·(t − t₀); M4 jointly identifies (μ, β) against the CWON wealth account; and *M_obs* is the observable parameter-free tempo proxy. M1 (constant lag) and M3 (intangibles only) are reported in the Supporting Information as intermediate benchmarks.

* **M0**: Solow baseline, *K_tang* as M0 above, β = 0.
* **M2**: Time-varying lag μ(t) = μ₀ + μ₁·(t − t₀) from (M2).
* **M4**: Joint identification (Sect. 3.2), minimising (2) over (μ, β) simultaneously against CWON.
* **M_obs**: Observable tempo, where μ(t) is constructed directly from OECD gross fixed capital formation (GFCF) by asset type. For each country-year, the share of investment in each asset category (dwellings, other buildings, transport equipment, ICT equipment, machinery, intellectual property products) is computed from OECD GFCF data, and μ_obs(t) = Σ_a s_a(t) · μ_a, where s_a(t) is the share of asset *a* in total GFCF and μ_a is the literature-based gestation lag for asset *a* (dwellings and other buildings: 2.0 years; transport equipment: 0.5 years; ICT equipment: 0.3 years; machinery: 0.8 years; intellectual property products: 3.0 years). *M_obs* has **zero free parameters**. A sensitivity analysis that scales these literature lags by 0.5–2.0 yields a median out-of-sample MAPE between 3.86 % and 4.39 % (Supplementary Table 2), confirming that the results are not sensitive to the precise literature value chosen for each asset.

OECD asset-composition data are available for 35 of the 39 countries in the main panel. All K-level, TFP-shift, and implied labour-share results that rely on *M_obs* are therefore reported for this 35-country subsample; the model-comparison results in Sects. 5.1–5.3 continue to use the full 39-country panel.

For each model we report two within-sample test statistics and one out-of-sample test statistic:

* **Test A (level MAPE)**: mean absolute percentage error of fitted log-GDP against observed log-GDP, decomposing away decade-mean TFP. Lower is better.
* **Test B (growth RMSE)**: root-mean-squared error of 1-year log-GDP differences, in percentage points. Lower is better.
* **Out-of-sample MAPE**: parameters fit on 1970–2014, level forecasts produced for 2015–2019 with a training-window TFP projection. Lower is better.

### 4.3 Estimation protocol and grid search

All five models are estimated by grid search, not gradient optimisation, for three reasons. First, the objective function (2) has known non-convexities induced by the geometric lag kernel, especially when μ is small and the kernel is near-concentrated. Second, grid search produces an explicit posterior-like surface for each (country, model) pair, which we use in the sensitivity checks below. Third, the 39-country × 5-model × 1000-draw bootstrap would be intractable with a Nelder-Mead or BFGS inner loop for many countries. The μ grid is {0.01, 0.05, 0.10, 0.25, 0.50, 1.0, 1.5, 2.0, 3.0, 4.5, 6.0} years and the β grid is {0.00, 0.02, 0.04, ..., 0.34}; μ₁ is searched on {−0.08, −0.04, −0.02, 0, +0.02, +0.04, +0.08} per year. These bounds were selected to bracket all plausible parameter values reported in prior cross-country studies (Kaboski, 2005; Corrado et al., 2016). In the constant-lag (M1) grid search, __N_BOUNDARY__ of the __N_COUNTRIES__ countries hit a boundary for μ: __N_LOWER_BOUND__ at the lower bound (0.01 years, effectively zero lag) and __N_UPPER_BOUND__ at the upper bound (6.0 years). The remaining __N_INTERIOR__ countries have interior μ̂_M1 values; we report the conditional out-of-sample evaluation for this interior-solution subsample in Supplementary Section S.14. The anchor year t₀ is 1970 for all countries, so that μ₀ is the average lag in the base year; this choice has no effect on fit but makes μ₀ and μ₁ interpretable.

### 4.4 Bootstrap confidence intervals

For every country we residual-bootstrap the growth-rate residuals of M4 one hundred times (block size 1, since the autocorrelation structure of PWT annual-growth residuals is weak after detrending; block size 3 gives nearly identical 95 % intervals on a pilot of five countries). Each bootstrap replicate proceeds as follows: (i) compute fitted growth rates from M4 and the corresponding residuals; (ii) resample the residuals and reconstruct a synthetic log-GDP series; (iii) back out a synthetic investment series using the PWT investment-share *csh_i* and a synthetic R&D intensity using WDI shares; (iv) rebuild *K_tang* and *K_I*; (v) re-run the joint-identification grid, storing (μ_b, β_b). We report 95 % percentile intervals in the bootstrap output and per-country medians in the supplementary JSON. Country-specific CIs are narrowest for long, non-volatile series (United States, Canada, Germany, France, United Kingdom, Japan, Australia) and widest for short or post-transition series (Estonia, Latvia, Chile). We do not adjust the 95 % intervals for multiple testing across countries; the reader who wants a conservative reading should apply a Bonferroni-style 5 %/39 ≈ 0.13 % threshold. At the conventional 5 % level, joint identification rejects μ = 0 for 39 of 39 countries and β = 0 for 7 countries; such a Bonferroni correction would reduce both counts.

## 5 Results

### 5.1 In-sample parameter distributions and fit


Table 1 summarises the five models. Three facts deserve particular emphasis. First, the median in-sample growth-rate RMSE hardly moves across M0–M4 (3.07–3.10 pp). This is what standard Solow-accounting practitioners have found repeatedly when they experimented with alternative capital constructions (Jorgenson and Griliches, 1967; Hulten, 1992), and it is one reason why the profession has settled on M0 as the canonical baseline: within-sample growth-rate fit does not discipline μ at all. Second, the median level MAPE under M0 is 4.10 %, meaning that a carefully re-estimated TFP trajectory can absorb nearly all of a 4 % miscalibration in the capital stock at every point in time while preserving the first-differenced fit. This is a clear illustration of Griliches's (1996) warning that "TFP is the measure of our ignorance": any capital mis-specification that varies on decade-scale time-frequencies will be silently reabsorbed into decade-scale TFP, and then re-interpreted as innovation. Third, and central to our method, the distribution of estimated *μ̂_M1* across the 39 countries is highly non-degenerate. The interquartile range under M1 runs from 0.01 years to 2.13 years, and the tempo drift μ₁ under M2 has an IQR that includes both substantially negative and substantially positive values. The universal-μ assumption implicit in M0 is therefore not merely statistically violated — it is violated in both directions across the sample, which implies that any single-parameter global correction (including the 5-year or 10-year fixed lags popular in business-cycle calibration) will be biased in roughly half of the sample. The median country has an M1 constant lag *μ̂_M1* ≈ 0.3 years and an M2 tempo drift μ₁ close to zero on average but with wide dispersion across countries (IQR roughly [−0.08, +0.12]). Median intangible share β under M3 is 0.00 for production-only fitting and 0.04 under joint identification with CWON (M4); the corresponding means are 0.08 and 0.10, reflecting a right-skewed distribution. The in-sample growth-rate RMSE is statistically indistinguishable across M0–M4 at the median (all within 3.07–3.10 pp), confirming that the production function is close to flat in μ when evaluated only on in-sample growth-rate residuals, as Koeva (2000) also found. In-sample level MAPE improves monotonically from M0 (4.10 %) to M4 (4.06 %). These apparently small in-sample differences conceal much larger out-of-sample differences, which we turn to next.
**[Table 1 here]**

### 5.2 Out-of-sample prediction gains from the tempo correction

Supplementary Figure 1 ranks the 39 countries by in-sample growth RMSE (M0) and overlays the other four models. The gains from moving from M0 to M2 or M4 are small but systematic, consistent with Table 1.


Figure 1 shows the out-of-sample performance. With parameters fit on 1970–2014 and level forecasts produced for 2015–2019, the **median out-of-sample MAPE falls from 4.60 % under the Solow baseline M0 to 3.99 % under the time-varying-lag M2**, a 13 % relative reduction. A Wilcoxon signed-rank test on the __WILCOXON_N__ paired country MAPEs gives a two-sided *p* = __WILCOXON_P__, and a paired percentile bootstrap of the country-level MAPE differences produces a 95 % interval that comfortably includes zero, so the reduction is not statistically significant at conventional levels in this sample; the point estimate should be read as a systematic reduction in out-of-sample error rather than a precisely measured one. M1 (constant lag) achieves most of the gain (4.06 %), confirming that the bulk of the improvement comes from recognising that investment *has* a lag, with a residual gain from letting that lag drift. M3 (intangibles) slightly worsens out-of-sample MAPE to 4.72 %; we attribute this to the fact that adding a co-moving factor with a time-varying productivity projection widens forecast uncertainty, especially under the 2015–2019 global slowdown that affected R&D-intensive countries disproportionately. M4 (joint) returns to 4.61 %, close to M0; because M4 is chosen to reconcile flow and stock accounts rather than to minimise forecast error, its out-of-sample MAPE should not be read as a measure of forecasting performance. The observable-tempo *M_obs* achieves a median MAPE of 4.17 %, a 9.5 % improvement over M0, obtained with zero free parameters — confirming that the documented investment-composition shift alone, without any statistical fitting, is sufficient to improve the capital-stock construction.
**[Figure 1 here]**

We note, however, that out-of-sample prediction accuracy is not evidence of measurement quality *per se*: selecting a capital series by how well it tracks output risks folding output variation into the capital measure. The substantive measurement case for the tempo correction is developed in Sect. 5.4, where we show that the correction changes measured capital levels, TFP, and implied labour shares in ways that are independent of forecast performance.

The 13 % median improvement masks substantial cross-country heterogeneity. M2 improves on M0 in 23 of 39 countries, and the largest gains are concentrated where the investment mix has shifted most toward long-gestation assets such as software, cloud infrastructure, R&D platforms, and complex engineering systems (Supplementary Figure 1). Countries in which the asset mix was stable over 1995–2019 have little room for μ(t) to matter, and M0 is close to best for them. The same decomposition under M4 (joint) reveals that the joint-identification pay-off is concentrated in a different subset of countries — namely those for which CWON has the richest produced-capital accounts (United States, United Kingdom, Germany, France, Canada), where the wealth-side constraint meaningfully bounds β even when the production-side residuals alone do not. Supplementary Table 3 reports selected historical episodes in which these asset-mix shifts produced the largest TFP artefacts.

### 5.3 Flow–stock consistency


Figure 2 shows PIM-reconstructed capital *K_tang(t; μ̂) + β̂ · K_I(t)* alongside CWON-produced capital NW.PCA.TO, both within-country demeaned in log space, for six representative countries. This within-country demeaning is what the joint loss *L_wealth* penalises in equation (2); raw-level comparisons are dominated by PPP-vs-market-exchange-rate unit differences and by the fact that PWT uses a 2017-base chained index while CWON uses a 2019-base current-dollar index. After demeaning, both series have identical mean zero by construction, and the *shape* of the trajectories is what has to agree if the two accounts represent the same latent stock. The United States, Republic of Korea, and Israel — three R&D-intensive economies — show near-identity: the PIM series tracks CWON to within 1–2 % in log terms over the full 1995–2019 window. Germany and the Netherlands show small but visible widening after 2010, which is consistent with the delayed incorporation of the 2008 SNA's R&D treatment on the CWON side. Japan is one outlier: from 2010 onward, the PIM series continues to rise while CWON PCA turns flat or declines. The Supporting Information reports an asset-price revaluation sensitivity check that suggests this gap is plausibly a price rather than a quantity effect, consistent with Hayashi and Prescott (2002).

**[Figure 2 here]**

### 5.4 Capital-level measurement consequences of tempo correction


The analyses above establish that the tempo correction improves forecast accuracy and flow-stock consistency. But the economically fundamental question is different: does the correction change the *measured capital stock itself*, and do those changes propagate to the growth-accounting quantities — TFP and labour shares — that macroeconomists actually use? This section shows that they do, and quantifies the magnitudes.

From the growth-accounting identity TFP = log Y − α log K − (1−α) log LH, any change in measured capital changes measured TFP mechanically: Δ log K = (*TFP_M0* − *TFP_obs*) / α. Figure 3 plots the K-level divergence — *K_obs*/*K_M0* − 1 in percent — over the full sample period for six representative countries (Japan, United States, Germany, Republic of Korea, United Kingdom, Sweden). In every country the tempo-corrected stock *K_obs* lies below the standard PIM stock *K_M0*, and the gap widens over time as investment composition shifts toward longer-gestation assets. This is the direct measurement consequence: the PIM counts investment as productive before it has completed gestation, overstating the capital stock. The direction is unambiguous: all 35 countries show *K_obs* < *K_M0*.

**[Figure 3 here]**


Table 2 and the country panels of Figure 3 quantify the cross-country distribution. Over 2010–2019, the median K-level gap is −4.3 % (IQR: −5.2 % to −3.8 %). The five most affected economies — Ireland (−9.2 %), Costa Rica (−7.3 %), Republic of Korea (−7.1 %), Slovakia (−6.7 %), Israel (−6.4 %) — are precisely those with the largest recent shifts toward intellectual-property and ICT investment. The five least affected — Greece (−0.6 %), Japan (−1.2 %), Germany (−1.9 %), Italy (−2.1 %), Portugal (−2.6 %) — are those with more stable investment mixes.
**[Table 2 here]**


*TFP consequences.* Because *TFP_obs* = log Y − α log *K_obs* − (1−α) log LH and *K_obs* < *K_M0*, it follows that *TFP_obs* > *TFP_M0*: the standard PIM therefore *understates* log-level TFP, with *TFP_M0* lying a median 1.7 percentage points below *TFP_obs* (reported in Table 2 as a −1.7 pp shift). For Ireland the gap reaches 4.6 pp, meaning that nearly five percentage points of what the conventional Solow residual attributes to capital deepening is actually a tempo artefact. Figure 4 shows the country-level TFP shifts.

**[Figure 4 here]**


*Labour-share consequences.* If the capital stock is overstated, the capital contribution α log K absorbs variation that should be attributed to labour or TFP, mechanically depressing the residual labour share. Correcting K downward by δ log K shifts the implied labour share upward by approximately α × |δ log K| percentage points. The median upward shift is 1.7 pp (IQR: 1.4–2.7 pp; Figure 5). For the Republic of Korea the shift is 3.1 pp, for Israel 2.8 pp. These magnitudes are modest relative to the full secular decline in labour shares documented by Karabarbounis and Neiman (2014). The correction therefore cannot reverse the broader decline, but it can attenuate a portion of the measured fall: a fraction of the observed decline in labour shares may reflect a measurement artefact arising from the failure to account for investment gestation lags, alongside deeper structural forces such as globalisation, automation, and market power. We stress that this is an accounting reclassification, not a causal explanation.

**[Figure 5 here]**
*Investment composition and the business cycle.* The K-level gap is not constant over time but co-moves with the investment cycle. During expansions, firms undertake more complex, long-gestation projects (software platforms, R&D programmes, infrastructure); during contractions, investment retreats to short-lead maintenance and replacement. The observable μ_obs(t) therefore rises in booms and falls in recessions, amplifying the tempo effect procyclically. This means the standard PIM systematically *overstates* the capital stock in booms (when long-gestation investment is being counted before completion) and *understates* it in troughs (when the pipeline empties but past projects are completing). The procyclical bias in measured K translates to a countercyclical bias in measured TFP: TFP appears lower in booms and higher in recessions than it should, which may explain part of the well-documented countercyclicality of the Solow residual.

*Counterfactual produced-capital revaluation.* A mechanical imputation of the joint-identified intangible share β into official produced-capital accounts raises the corrected produced-capital stock by up to 1.1 % for the Netherlands and by 0.9 % for both France and Norway, with a negligible effect on total wealth (below 0.3 %). Because the R&D-only proxy for intangible capital is conservative, these figures are lower-bound estimates of the official-account revaluation implied by the broader intangible-capital literature (Corrado et al., 2005; Haskel and Westlake, 2017). The full country-level counterfactuals are reported in Supplementary Table 4.

### 5.5 Solow-residual historical decomposition

The TFP variance decomposition complements the level analysis of Sect. 5.4. Under M0 the residual is log A₀(t) = log Y − α log K₀ − (1 − α) log LH, where K₀ is the instant PIM stock. Under M2 and *M_obs* the residual is computed using the tempo-corrected stocks K₂ and *K_obs*. The difference in growth-rate variance measures how much TFP-growth variation is absorbed by the correction. Across the 39 countries, the median variance reduction attributable to tempo drift alone (M0 → M2) is 1.7 %, but it exceeds 8 % in several economies and reaches 13.8 % for New Zealand. The joint correction (M0 → M4) achieves a median reduction of 0.1 %, with France (29.7 %), Luxembourg (14.6 %), Italy (11.0 %), and the Netherlands (10.7 %) showing the largest shifts (Supplementary Table 5).

Supplementary Table 3 translates these reductions into concrete historical episodes. The 1997–1999 Asian-crisis episode for the Republic of Korea shows the largest tempo artefact: the conventional M0 residual attributes positive TFP growth to the crisis years, but the tempo-corrected series report much lower TFP growth. For the United States, the dot-com boom and the global financial crisis display smaller and partly offsetting artefacts, while Japan's lost decade and the 2007–2009 crisis show no meaningful tempo artefact because investment composition was stable. Supplementary Figure 2 displays the time-series TFP paths for six representative countries; the shaded area between M0 and M2 measures the tempo artefact. These changes are reallocations of *how much of output growth is attributed to capital versus productivity*.

## 6 Discussion and policy implications

The tempo drift and intangible corrections developed above have direct implications for macroeconomic policy, statistical practice, and the broader measurement agenda. We structure the discussion around five themes.

### 6.1 Re-interpreting the Solow residual

The K-level analysis of Sect. 5.4 and the historical decomposition of Sect. 5.5 put a number on the long-standing suspicion that the Solow residual conflates genuine innovation with capital-stock mismeasurement. Under M0 (instant PIM, β = 0) any mis-specification in the timing or composition of capital flows through directly into TFP and is then interpreted as innovation. We show that a measurable share of Solow-residual growth variation across our 35 countries can be re-assigned to two accounting corrections that need not be interpreted as innovation: the time-to-build μ(t) and the intangible share β. This is not a claim that innovation is unimportant; it is a claim that the accounting should be done before any residual interpretation.

### 6.2 The demographic tempo analogy

Supplementary Table 1 established that period-fertility analysts already solved the problem of measuring a stock process from its flow when the flow is contaminated by drift in the timing distribution. Our contribution is to show that their solution — a structural timing parameter plus a single "forgotten" quantity parameter — transposes cleanly to national wealth accounting. This is not metaphor. Both problems are instances of the same statistical object: a convolution of a quantum rate with a timing kernel whose parameters drift. The same Bongaarts and Feeney (1998) adjustment works, up to a change of units.

At the most conservative level, the results of Sect. 5 show that a *fraction* of what we have been calling TFP growth is a bookkeeping artefact that disappears once μ(t) and β are jointly estimated. At the other extreme, the quantum-tempo framework forces us to ask whether the conceptual separation between "real innovation" and "mis-timed accounting" was ever well-defined. If the typical investment has a longer gestation period in 2019 than in 1995 — plausibly because the share of assets whose productive deployment requires software integration, regulatory approval, and network complementarities has risen — then the accounting correction *is* an economic statement about the changing composition of capital. The boundary between "pure accounting" and "pure innovation" is therefore porous. Our position is that the two categories should be treated symmetrically, with the same parametric machinery, rather than with the asymmetric treatment implicit in M0 that has dominated a half-century of growth accounting.

### 6.3 Identification strategy and credibility

A natural objection is that μ(t) and β may not be separately identified from the production-side data alone: a higher lag μ slows measured capital accumulation in much the same way as a lower intangible share β. Our identification strategy relies on three distinct sources of variation, each of which resolves a different dimension of the parameter space.

*First, the wealth-side constraint.* The joint loss (2) simultaneously penalises production-side growth-rate residuals and wealth-side trajectory deviations. Because CWON produced capital NW.PCA.TO is an independent measurement — compiled from national balance sheets with their own asset-life assumptions, revaluation conventions, and depreciation schedules — the wealth constraint provides an external discipline that the production residuals alone cannot. The bootstrap evidence in Sect. 5.4 quantifies this: production-side residuals alone leave the 95 % region in (μ, β) space as a broad ridge for most countries; adding the wealth constraint tightens both parameters substantially and narrows the ridge. The collapse is itself a testable implication: if the wealth data were uninformative, the joint and production-only posteriors would coincide.

*Second, cross-country heterogeneity in asset composition.* Countries with systematically different R&D intensities trace out different regions of (μ, β) space. The positive gradient of ρ̂₂ on R&D intensity reported in Supplementary Figure 3 (slope = 0.068, t = 2.34 under M4) is consistent with the interpretation that β captures a component correlated with — but not mechanically determined by — observable R&D spending. If β were merely absorbing production-side noise unrelated to intangibles, there would be no reason for the cross-sectional gradient to steepen under M4 relative to M0.

*Third, the depreciation-sensitivity check.* The δ-perturbation experiment reported in Supplementary Information 5.6 addresses the concern that a drifting depreciation rate could mimic the tempo effect. The finding that the median and mean μ̂_M1 are stable to within 2 % of the baseline value across six alternative δ(t) schedules implies that the tempo parameter is not an artefact of depreciation mis-measurement; the two channels are empirically separable under the grid-search protocol, even though they are theoretically confounded in a single-equation setting.

We acknowledge that none of these arguments constitutes a structural identification proof of the kind available in natural-experiment or instrumental-variable designs. The framework here is a calibrated decomposition, not a causal model. What the three sources of variation collectively establish is that the decomposition is *disciplined* — it is not an unconstrained statistical exercise but a system of accounting identities whose parameters are pinned down by the requirement that flow and stock accounts agree — and that the resulting parameter estimates move in the directions predicted by economic theory (higher μ in economies with longer-gestation investment, higher β in economies with more R&D). Whether the decomposition is unique in a deeper structural sense — whether alternative parameter configurations could generate the same observables — is a question we leave to future work with richer asset-class data.

### 6.4 Concrete policy implications

The corrections developed here translate into four practical recommendations for macroeconomic policy and statistical practice.

*Potential output and fiscal rules.* Output-gap estimates that feed directly into fiscal-policy rules — the EU's Stability and Growth Pact, the US Congressional Budget Office's potential-GDP series, Japan's Cabinet Office estimates — are computed from production functions that assume μ = 0 and β = 0. If the capital stock is systematically mis-timed, the potential-output estimate inherits the bias, and the fiscal stance calibrated to the resulting output gap may be misdirected. For the United States (μ̂_M4 ≈ 3.5 years), the PIM capital stock under M0 runs about 3–4 years ahead of the tempo-corrected stock, which implies that the conventional output gap overstates the degree of slack during investment booms and understates it during downturns. Governments that tighten fiscal policy in response to an overestimated output gap risk procyclical contraction.

*Monetary-policy transmission.* The lengthening of monetary-policy transmission lags documented by Havranek and Rusnak (2013) has been attributed to financial deepening and expectation formation. The time-varying μ(t) offers a complementary structural explanation: as the typical investment project takes longer to mature — from factories built in 18 months in the 1970s to software platforms deployed over 3–5 years today — the real-economy response to interest-rate changes is delayed through the same gestation channel that this paper formalises. Central banks calibrating their forward guidance to historical transmission lags may consequently underestimate the delay with which current rate changes affect output.

*Statistical-agency practice.* The 2008 SNA (United Nations et al., 2009) would benefit from three modifications. First, the PIM should report μ(t) as a time-varying parameter alongside the depreciation rate δ, rather than treating it as a fixed structural constant. Second, produced-capital aggregates should carry a supplementary β estimate so that users can see the intangible adjustment at a glance. Third, the Relational PIM diagnostic (ρ₁, ρ₂) developed in Sect. 3.4 can serve as a routine quality-control metric: a country whose ρ̂₂ deviates markedly from unity warrants investigation before its wealth statistics are published.

*International GDP comparability.* Cross-country heterogeneity in (μ̂, β̂) maps onto observable differences in investment composition. The one-size-fits-all depreciation schedules and zero-lag assumption used to construct PWT capital stocks introduce a systematic comparability problem: countries with longer-gestation investment portfolios (Nordic economies, Republic of Korea) appear to have lower capital and higher TFP relative to countries with shorter-gestation portfolios (United States, United Kingdom). Tempo-correcting the capital stock before computing TFP would improve the comparability of cross-country productivity studies such as Inklaar and Timmer (2013).

### 6.5 Flow–stock reconciliation and extensions

The Beyond-GDP programme has argued that flow measures (GDP) should be replaced or augmented by stock measures such as IWI, CWON, and SEEA. The results point to a simpler synthesis: flow and stock measures are both biased by the same hidden parameters, and they move in the same direction once μ(t) and β are made explicit. A reader who trusts CWON-produced capital should also trust a PIM stock built with time-varying μ(t) and a nonzero β: the two series now agree to within 1–2 % for most countries (Figure 3). The practical route to Beyond-GDP is therefore not to abandon the flow account but to audit it for tempo drift and hidden β, just as demographers audited the period total fertility rate in the 1990s.

Three implications follow. First, the argument that flow and stock accounts are irreconcilable is not supported once both are audited on the same terms. Second, constructing a single composite headline index is premature until the component accounts are internally consistent. Third, the demographic-tempo literature moved from a single-parameter adjustment to a richer multi-parameter framework only after the simpler version was taken seriously. Capital-accounting tempo correction is at the same stage fertility research was in 1998: the one-parameter version here is a necessary first step, and richer asset-class heterogeneity in μ, country-specific β drift, and interaction terms between μ and δ are natural next steps.

The same quantum-tempo decomposition applies to other stock-of-outcomes processes — human capital, medical R&D capital, climate adaptation capital — where the flow is contaminated by drift in the timing distribution. Extending the framework to those domains is a research programme; this paper is the first step.

### 6.6 Limitations

Three caveats apply. First, our identification of β against CWON is only as clean as CWON itself, and CWON combines national sources of heterogeneous quality — in particular, the treatment of land and sub-soil assets differs materially between Europe and the United States (Lange et al., 2021, Chap. 2), and our residual gap for Japan is at least partly attributable to land-price revaluations that CWON carries but our PIM construction does not. Second, the bootstrap CIs (Sect. 5.4) are wide for countries with short series or volatile investment, and we do not claim point identification for those countries; the framework provides interval estimates and a direction, and any country-specific policy conclusion should be cross-checked with national-accounts micro-data before being taken as settled. Third, the γ_price sensitivity experiment (Supplementary Section S.9) treats the CWON deflator as a single country-level scalar; a more careful study would use sector-specific deflators, national land-price indices (Shimizu and Nishimura, 2007), and Tornqvist chained price indices for intangibles (Jorgenson et al., 2005), and is left to future work. A fourth, and perhaps the most important, caveat is that the demographic-tempo analogy is suggestive but not exact: demographic stocks depreciate via well-measured mortality rates, whereas capital stocks depreciate via δ_t that is itself a derived estimate in PWT and is known to be imprecisely measured in transition economies (Inklaar and Timmer, 2013). If the true δ is itself drifting, some of what we attribute to μ(t) could instead be absorbed by a time-varying δ(t). Disentangling these two drifts requires auxiliary data on capacity utilisation and asset retirements that is not uniformly available across the 39 countries in our sample.

## 7 Conclusion

The debate over national income and wealth accounting has often been framed as a choice between flow and stock measures. The more useful question is whether the parameters that link the two — the time-to-build of investment and the share of intangible capital — are estimated or imposed. When they are imposed at zero, the accounting is silently biased, the Solow residual absorbs the error, and the accounts drift apart. When μ is constructed from observable investment composition, the measured capital stock changes by a median 4.3 %, the corrected TFP is higher by 1.7 percentage points, and the implied labour share is higher by 1.7 percentage points. These are not forecasting improvements: they are measurement consequences.

The scale matters. A 4.3 % capital-stock revision is modest in absolute terms, but it implies that the capital contribution to output is systematically biased for every country that has shifted toward long-gestation assets. For the Republic of Korea the capital stock is overstated by 7.1 %, shifting TFP by 3.1 pp and the labour share by 3.1 pp; for Ireland the figures are 9.2 % and 4.6 pp. These magnitudes are comparable to the secular trends in labour shares (Karabarbounis and Neiman, 2014), suggesting that part of the observed decline could reflect an accounting artefact from ignoring gestation lags, alongside structural forces.

Three practical recommendations follow. First, national capital-stock estimates that treat μ as time-invariant should be treated as provisional; the observable *M_obs* proxy can be computed at negligible cost from existing OECD asset data. Second, the CWON and IWI programmes should publish, alongside point estimates, joint-identified (μ, β) values so users can see whether the flow and stock accounts are internally consistent. Third, TFP growth should no longer be the residual of first resort. A post-tempo, post-intangible residual is a more informative benchmark for productivity growth. Demography learned to live with a smaller unexplained component once the period-cohort bias was acknowledged; economic measurement would benefit from the same adjustment.

---


## References

Altug, S. (1989). Time-to-build and aggregate fluctuations: Some new evidence. *International Economic Review*, *30*(4), 889–920. https://doi.org/10.2307/2526758

Arrow, K. J., Dasgupta, P., Goulder, L. H., Mumford, K. J., & Oleson, K. (2012). Sustainability and the measurement of wealth. *Environment and Development Economics*, *17*(3), 317–353. https://doi.org/10.1017/S1355770X12000137

Bongaarts, J., & Feeney, G. (1998). On the quantum and tempo of fertility. *Population and Development Review*, *24*(2), 271–291. https://doi.org/10.2307/2807974

Bongaarts, J., & Sobotka, T. (2012). A demographic explanation for the recent rise in European fertility. *Population and Development Review*, *38*(1), 83–120. https://doi.org/10.1111/j.1728-4457.2012.00473.x

Brass, W. (1971). On the scale of mortality. In W. Brass (Ed.), *Biological aspects of demography* (pp. 69–110). Taylor and Francis.

Christiano, L. J., & Todd, R. M. (1996). Time to plan and aggregate fluctuations. *Federal Reserve Bank of Minneapolis Quarterly Review*, *20*(1), 14–27.

Corrado, C., Hulten, C., & Sichel, D. (2005). Measuring capital and technology: An expanded framework. In C. Corrado, J. Haltiwanger, & D. Sichel (Eds.), *Measuring capital in the new economy* (pp. 11–46). University of Chicago Press. https://doi.org/10.7208/chicago/9780226116174.003.0002

Corrado, C., Hulten, C., & Sichel, D. (2009). Intangible capital and US economic growth. *Review of Income and Wealth*, *55*(3), 661–685. https://doi.org/10.1111/j.1475-4991.2009.00343.x

Corrado, C., Haskel, J., Jona-Lasinio, C., & Iommi, M. (2016). Intangible investment in the EU and US before and since the Great Recession and its contribution to productivity growth (EIB Working Papers 2016/08). European Investment Bank.

Corrado, C., Haskel, J., Iommi, M., & Jona-Lasinio, C. (2020). Intangible capital, innovation and productivity à la Jorgenson: Evidence from Europe and the US. In B. M. Fraumeni (Ed.), *Measuring economic growth and productivity* (pp. 363–385). Academic Press. https://doi.org/10.1016/B978-0-12-817596-5.00016-0

Dasgupta, P. (2021). *The economics of biodiversity: The Dasgupta review*. HM Treasury.

Edge, R. M. (2007). Time-to-build, time-to-plan, habit-persistence, and the liquidity effect. *Journal of Monetary Economics*, *54*(6), 1644–1669. https://doi.org/10.1016/j.jmoneco.2006.07.003

Feenstra, R. C., Inklaar, R., & Timmer, M. P. (2015). The next generation of the Penn World Table. *American Economic Review*, *105*(10), 3150–3182. https://doi.org/10.1257/aer.20130954

Goldstein, J. R., Lutz, W., & Scherbov, S. (2003). Long-term population decline in Europe: The relative importance of tempo effects and generational length. *Population and Development Review*, *29*(4), 699–707. https://doi.org/10.1111/j.1728-4457.2003.00699.x

Griliches, Z. (1996). The discovery of the residual: A historical note. *Journal of Economic Literature*, *34*(3), 1324–1330.

Haskel, J., & Westlake, S. (2017). *Capitalism without capital: The rise of the intangible economy*. Princeton University Press.

Haskel, J., & Westlake, S. (2022). *Restarting the future: How to fix the intangible economy*. Princeton University Press.

Havranek, T., & Rusnak, M. (2013). Transmission lags of monetary policy: A meta-analysis. *International Journal of Central Banking*, *9*(4), 39–76.

Hayashi, F., & Prescott, E. C. (2002). The 1990s in Japan: A lost decade. *Review of Economic Dynamics*, *5*(1), 206–235. https://doi.org/10.1006/redy.2001.0149

Hulten, C. R. (1992). Growth accounting when technical change is embodied in capital. *American Economic Review*, *82*(4), 964–980.

Inklaar, R., & Timmer, M. P. (2013). Capital, labor and TFP in PWT 8.0 (Research Memorandum GD-144). Groningen Growth and Development Centre.

Jorgenson, D. W., & Griliches, Z. (1967). The explanation of productivity change. *Review of Economic Studies*, *34*(3), 249–283. https://doi.org/10.2307/2296675

Jorgenson, D. W. (2018). Production and welfare: Progress in economic measurement. *Journal of Economic Literature*, *56*(3), 867–919. https://doi.org/10.1257/jel.20171358

Jorgenson, D. W., Ho, M. S., & Stiroh, K. J. (2005). *Productivity, Vol. 3: Information technology and the American growth resurgence*. MIT Press.

Kaboski, J. P. (2005). Factor price uncertainty, technology choice and investment delay. *Journal of Economic Dynamics and Control*, *29*(3), 509–527. https://doi.org/10.1016/j.jedc.2004.03.001

Karabarbounis, L., & Neiman, B. (2014). The global decline of the labor share. *Quarterly Journal of Economics*, *129*(1), 61–103. https://doi.org/10.1093/qje/qjt032

Koeva, P. (2000). The facts about time-to-build (IMF Working Paper 00/138). International Monetary Fund.

Kohler, H.-P., Billari, F. C., & Ortega, J. A. (2002). The emergence of lowest-low fertility in Europe during the 1990s. *Population and Development Review*, *28*(4), 641–680. https://doi.org/10.1111/j.1728-4457.2002.00641.x

Kydland, F. E., & Prescott, E. C. (1982). Time to build and aggregate fluctuations. *Econometrica*, *50*(6), 1345–1370. https://doi.org/10.2307/1913386

Lange, G.-M., Cust, J., Herrera, D., Naikal, E., & Peszko, G. (Eds.). (2021). *The changing wealth of nations 2021: Managing assets for the future*. World Bank. https://doi.org/10.1596/978-1-4648-1590-4

Managi, S., & Kumar, P. (Eds.). (2018). *Inclusive wealth report 2018*. Routledge.

Mayer, T. (1960). Plant and equipment lead times. *Journal of Business*, *33*(2), 127–132. https://doi.org/10.1086/294329

McGrattan, E. R., & Prescott, E. C. (2010). Unmeasured investment and the puzzling US boom in the 1990s. *American Economic Journal: Macroeconomics*, *2*(4), 88–123. https://doi.org/10.1257/mac.2.4.88

OECD. (2013). *Supporting investment in knowledge capital, growth and innovation*. OECD Publishing. https://doi.org/10.1787/9789264193307-en

Roth, F. (2022). Intangible capital and labor productivity growth – Revisiting the evidence: An update. *Hamburg Discussion Papers in International Economics*, *11*.

Shimizu, C., & Nishimura, K. G. (2007). Pricing structure in Tokyo metropolitan land markets and its structural changes: Pre-bubble, bubble, and post-bubble periods. *Journal of Real Estate Finance and Economics*, *35*(4), 475–496. https://doi.org/10.1007/s11146-007-9052-8


Solow, R. M. (1957). Technical change and the aggregate production function. *Review of Economics and Statistics*, *39*(3), 312–320. https://doi.org/10.2307/1926047

Stiglitz, J. E., Sen, A., & Fitoussi, J.-P. (2009). *Report by the Commission on the Measurement of Economic Performance and Social Progress*. Commission on the Measurement of Economic Performance and Social Progress.

United Nations, European Commission, International Monetary Fund, Organisation for Economic Co-operation and Development, & World Bank. (2009). *System of National Accounts 2008*. United Nations. https://unstats.un.org/unsd/nationalaccount/docs/SNA2008.pdf
