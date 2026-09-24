# Figure audit (Figures 1–5)

| figure | plotted values vs manuscript_values.csv | sign convention | zero reference | extreme vs representative labelled | caption states conditions | status |
|---|---|---|---|---|---|---|
| Fig.1 narrative | bars use dec.csv values (−0.550, −0.020, +0.094…) | y-axis = Δβ(P−H) labelled | yes (hline 0) | n/a | yes | OK; schematic to be redrawn |
| Fig.2 gamma+dominance | matches sim01/sim02 | negative = apparent predator continuity, stated in caption | yes | pool4 highlighted as representative; pool2 extreme labelled in caption | N_H=26, sweep, Δβ_true=0 | OK after caption revision |
| Fig.3 lumping+temporal | matches sim03/sim04 | B_lumping defined as β_species−β_genus; Δβ shift annotated | yes | k sweep | 8 slices→bins | OK |
| Fig.4 factorial heatmap | matches sim06; colorbar −0.5..+0.5 symmetric | Bias = Δβ_obs−Δβ_true | diverging cmap centred at 0 | grid annotated | n_pred × p_D × k | OK |
| Fig.5 attenuation | matches morrison_decomposition.csv; null intervals shown as shaded bands (distinct from observed CIs) | Δβ axis labelled | yes | — | primary spec stated | OK |

Actions taken:
- Fig.2 caption revised: pool-4 identified as the representative case,
  pool-2 as the most extreme tested condition.
- Fig.5 caption revised: shaded bands explicitly labelled "null
  simulation intervals", distinct from bootstrap CIs of the observed
  statistic.
- All figures carry a y-axis sign note ("negative Δβ = predators more
  spatially homogeneous than herbivores").
