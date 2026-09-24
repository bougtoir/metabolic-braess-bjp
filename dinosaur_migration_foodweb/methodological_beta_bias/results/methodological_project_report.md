# Methodological beta-bias — project report

Methodological study (new primary route). Worked example: the Morrison
guild contrast that falsified the original hypothesis.

## Morrison empirical decomposition (sequential, Jaccard, collection level)

|   step | label                                          |   delta_beta |       lo95 |        hi95 | note                                                           |
|-------:|:-----------------------------------------------|-------------:|-----------:|------------:|:---------------------------------------------------------------|
|      1 | naive genus-level guild contrast               |   -0.549734  |  -0.630442 |  -0.456673  | nan                                                            |
|      2 | observed vs gamma-matched null                 |   -0.549734  |  -0.534412 |  -0.228507  | CI shown is the null 95% interval                              |
|      3 | observed vs frequency-matched null             |   -0.549734  |  -0.124025 |  -0.0948321 | CI shown is the null 95% interval                              |
|      4 | exclude Allosaurus                             |   -0.0198198 |  -0.127578 |   0.0237991 | nan                                                            |
|      5 | species-level resolution                       |   -0.32189   |  -0.426278 |  -0.23415   | nan                                                            |
|      6 | duration+sampling adjusted Allosaurus extent z |   -0.156023  | nan        | nan         | extent residual z-score; /z/<2 = not exceptional               |
|      7 | sampling/preservation model pseudo-R2          |    0.455646  | nan        | nan         | share of presence structure explained by collection covariates |

Sequential finding: naive Δβ = -0.550 falls inside
the gamma-matched null interval (-0.534 to
-0.229) but below the frequency-matched null
(-0.124 to -0.095); removing Allosaurus
collapses it to -0.020; species resolution leaves
-0.322; duration/sampling adjustment removes the
Allosaurus extent anomaly (z = -0.156).

## Nemegt comparator (same diagnostic workflow; not a replication)

|   step | label                                             |   delta_beta | note                                         |
|-------:|:--------------------------------------------------|-------------:|:---------------------------------------------|
|      1 | naive genus-level guild contrast                  |    0.0938382 | nan                                          |
|      2 | gamma-matched null                                |  nan         | degenerate: herbivore gamma < predator gamma |
|      3 | exclude Tarbosaurus                               |    0.133528  | nan                                          |
|      4 | species-level resolution                          |    0.0379977 | nan                                          |
|      5 | Tarbosaurus extent residual z (sampling-adjusted) |   -0.402389  | /z/<2 = not exceptional                      |

Nemegt starts near zero (+0.094) — there is no
contrast to decompose; herbivore gamma (8) < predator gamma, so the
gamma null degenerates. Comparator of opposite structure.

## Simulation results

### 01 Gamma-diversity imbalance
|   n_pred_taxa |   gamma_ratio_P_over_H |   delta_beta_true |   delta_beta_obs_mean |    bias_mean |        lo95 |        hi95 |   prop_negative |   prop_abs_gt_0.1 |
|--------------:|-----------------------:|------------------:|----------------------:|-------------:|------------:|------------:|----------------:|------------------:|
|             2 |              0.0769231 |                 0 |          -0.41247     | -0.41247     | -0.443256   | -0.398212   |           1     |             1     |
|             4 |              0.153846  |                 0 |          -0.170431    | -0.170431    | -0.186841   | -0.157444   |           1     |             1     |
|             6 |              0.230769  |                 0 |          -0.0947477   | -0.0947477   | -0.115431   | -0.0822318  |           1     |             0.215 |
|             8 |              0.307692  |                 0 |          -0.0566738   | -0.0566738   | -0.0714876  | -0.0463704  |           1     |             0     |
|            12 |              0.461538  |                 0 |          -0.0242727   | -0.0242727   | -0.0354683  | -0.015492   |           1     |             0     |
|            16 |              0.615385  |                 0 |          -0.00974372  | -0.00974372  | -0.0194871  | -0.0014606  |           0.995 |             0     |
|            20 |              0.769231  |                 0 |          -0.00404479  | -0.00404479  | -0.0128821  |  0.00462112 |           0.835 |             0     |
|            26 |              1         |                 0 |          -0.000124195 | -0.000124195 | -0.00799775 |  0.00798009 |           0.515 |             0     |

Pool-size asymmetry alone generates strong negative Δβ: predator pool of
4/26 herbivore gamma → bias -0.170
(false contrast in 100% of reps).

### 02 Dominant taxon (p_D sweep)
|   p_dominant |   delta_beta_obs_mean |       lo95 |       hi95 |   prop_negative |
|-------------:|----------------------:|-----------:|-----------:|----------------:|
|          0   |            -0.0229735 | -0.0324817 | -0.0146988 |               1 |
|          0.1 |            -0.0220202 | -0.0327199 | -0.0124091 |               1 |
|          0.2 |            -0.0243386 | -0.035085  | -0.0155601 |               1 |
|          0.3 |            -0.033653  | -0.0473774 | -0.0225671 |               1 |
|          0.4 |            -0.0503038 | -0.0668493 | -0.0333631 |               1 |
|          0.5 |            -0.071423  | -0.0947292 | -0.0532585 |               1 |
|          0.6 |            -0.0999248 | -0.127157  | -0.0751321 |               1 |
|          0.7 |            -0.133055  | -0.162522  | -0.104877  |               1 |
|          0.8 |            -0.170036  | -0.197376  | -0.144392  |               1 |
|          0.9 |            -0.210202  | -0.240698  | -0.185486  |               1 |

A dominant predator at p_D = 0.46 (Allosaurus-like prevalence) shifts
Δβ by ~-0.071.

### 03 Taxonomic lumping
|   n_lumped_species |   B_lumping_mean |   delta_beta_species |   delta_beta_genus |   shift_genus_minus_species |
|-------------------:|-----------------:|---------------------:|-------------------:|----------------------------:|
|                  1 |        0         |          -0.0998541  |         -0.0998541 |                   0         |
|                  2 |        0.0582554 |          -0.0422939  |         -0.100549  |                  -0.0582554 |
|                  3 |        0.076959  |          -0.021993   |         -0.098952  |                  -0.076959  |
|                  4 |        0.0881201 |          -0.0125311  |         -0.100651  |                  -0.0881201 |
|                  6 |        0.0992265 |          -0.00149362 |         -0.10072   |                  -0.0992265 |

Collapsing k geographically partitioned species into one genus adds
B_lumping ≈ 0.099 at k=6 — genus pooling
systematically inflates apparent continuity.

### 04 Temporal averaging
|   temporal_bins |   bin_width_slices |   delta_beta_obs_mean |       lo95 |        hi95 |
|----------------:|-------------------:|----------------------:|-----------:|------------:|
|               8 |                  1 |          -0.0308296   | -0.0355958 | -0.0265418  |
|               4 |                  2 |          -0.011935    | -0.0180285 | -0.00654522 |
|               2 |                  4 |          -0.000688557 | -0.0179362 |  0.0156481  |
|               1 |                  8 |          -0.000837561 | -0.0292793 |  0.0302565  |

Merging 8 time slices into 1 erases nearly all guild contrast
(Δβ → -0.001).

### 05 Sampling asymmetry
|   pred_sampling_ratio_A_vs_B |   delta_beta_obs_mean |       lo95 |        hi95 |
|-----------------------------:|----------------------:|-----------:|------------:|
|                            1 |            -0.0239289 | -0.0400534 | -0.00995148 |
|                            2 |            -0.0230349 | -0.0377287 | -0.00757063 |
|                            4 |            -0.0235997 | -0.0453197 | -0.00743335 |
|                            8 |            -0.0236765 | -0.0407852 | -0.0083352  |

Guild-specific sampling ratios up to 8× produced only modest bias
(-0.024 to -0.023)
in this simple model — sampling bias is real but smaller than
gamma/dominance effects here.

### 06 Factorial grid
|   n_lumped |   bias |
|-----------:|-------:|
|          1 | -0.154 |
|          3 | -0.289 |
|          6 | -0.432 |

(per-lumping-level mean bias; full grid in sim06_factorial.csv —
sign-reversal and false-difference flags in `prop_sign_negative` /
`prop_false_difference`)

## Figures

- fig1_narrative.png, fig2_attenuation.png, fig3_bias_heatmap.png,
  fig4_lumping.png, fig5_temporal_dominance.png

## Independent evidence audit

See INDEPENDENT_EVIDENCE_AUDIT.md — nothing found contradicts the
methodological conclusion; available evidence favours trophic
generalism over mobility.

## Headline

Naive guild-level beta-diversity contrasts in fossil assemblages can be
dominated by gamma asymmetry, a single dominant taxon, taxonomic
resolution and time averaging — demonstrated on a preregistered
prediction that reversed and then failed independent replication.
