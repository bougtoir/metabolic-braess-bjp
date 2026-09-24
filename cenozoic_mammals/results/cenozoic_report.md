# Cenozoic mammals — strict replication report

## Primary contrast (Delta-beta, predator - herbivore)
- Simpson: -0.028 [-0.040, -0.018], P(delta>0)=0.000
- Sorensen: -0.026 [-0.034, -0.021]
- n collections: herbivore 1661, predator 809

## Distance decay (Mantel Spearman r)
- herbivore: r=0.0867 (p=0.0001)
- predator: r=0.1027 (p=0.0001)

## Sampling-pool sensitivity (delta_beta under each correction)
           correction  delta_beta_mean      lo95      hi95  prop_gt0  n_rep
                  raw        -0.028379 -0.028379 -0.028379  0.000000      1
 no_dominant_quarries        -0.025158 -0.025158 -0.025158  0.000000      1
        no_singletons        -0.010360 -0.010360 -0.010360  0.000000      1
equalized_collections        -0.028254 -0.033846 -0.022523  0.000000    999
spatial_thinning_1deg        -0.026333 -0.050381 -0.004517  0.001001    999

## Temporal aggregation sensitivity
binning  delta_beta  delta_vs_pooled
 pooled   -0.028379         0.000000
  epoch   -0.087343        -0.058964
    ma5   -0.080743        -0.052365
    ma1   -0.078403        -0.050024

## Genus-pool null models
              null  observed  null_mean   null_lo  null_hi  quantile  n_rep                                               notes
size_matched_split -0.028379  -0.028824 -0.080502 0.003677  0.341341    999                         random 131/378 genus splits
     label_shuffle -0.028379  -0.027836 -0.080490 0.003024  0.327327    999 permute guild labels across genera, keep pool sizes

## Comparison to dinosaur reference
- dinosaur Morrison: Delta-beta_Simpson = -0.543 [-0.623, -0.452], P(>0)=0; Mantel r~0 both guilds (see docs/DINOSAUR_PROTOCOL_CANONICAL.md)
- Robustness class assignment: see protocols/cenozoic_mammals/ and results/common_metrics/common_metrics_cenozoic.csv