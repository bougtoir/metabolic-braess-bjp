# Paleozoic marine replication - stop-rule report

## A. Did the dinosaur effect replicate?

Pool contraction systematically LOWERED mean pairwise Jaccard beta (mean bias -0.021) and steepened the distance-decay slope (mean bias 2e-06).

## B/C. Components replicated vs not

 pool_fraction  n_replicates  n_attempted  n_invalid  bias_beta_mean  bias_beta_lo95  bias_beta_hi95  prop_bias_beta_positive  bias_decay_mean  prop_bias_decay_positive
           0.5         11630        11800        170         -0.0208         -0.0619          0.0149                   0.1088              0.0                    0.6934
           0.5         14800        14800          0         -0.0117         -0.0511          0.0126                   0.1416              0.0                    0.7385
           0.5         11449        12200        751         -0.0224         -0.0801          0.0252                   0.1381              0.0                    0.6526
           0.5         10029        10800        771         -0.0157         -0.0857          0.0357                   0.2468              0.0                    0.6529
           0.5         12366        12800        434         -0.0258         -0.0878          0.0150                   0.1068              0.0                    0.6959
           0.5         13997        14600        603         -0.0297         -0.1982          0.0482                   0.1561              0.0                    0.7462

## D. Robustness across clades

Bias_beta negative in 6/6 clades at pool_fraction=0.5.

## E. Harmonisation for cross-system synthesis

cross_system_export.csv contains only the shared schema columns; Paleozoic-only metadata are in paleozoic_extended.csv.
