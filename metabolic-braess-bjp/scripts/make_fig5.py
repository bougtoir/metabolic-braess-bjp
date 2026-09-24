import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
df = pd.read_csv('results/robustness_matrix.csv')
df[['cond','sel','mod']] = df['config'].str.extract(r'(aerobic|glucose_limited|oxygen_limited)_(pfba|moma_linear)_(fva_informed|bound_scaling)'.replace('()','()'), expand=True)
df = df.dropna(subset=['cond'])
piv = df.pivot_table(index=['model','cond','mod'], columns='sel', values='n_interior', aggfunc='first')
fig, ax = plt.subplots(figsize=(4.6, 3.4))
labels = [f"{r.model}\n{r.cond.replace('_',' ')}\n{r.mod.replace('_',' ')}" for r in piv.reset_index().itertuples()]
M = piv[['pfba','moma_linear']].fillna(0).values
im = ax.imshow(M, cmap='YlOrRd', vmin=0, vmax=12, aspect='auto')
ax.set_xticks([0,1]); ax.set_xticklabels(['pFBA','L1-MOMA'])
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=5.5)
for i in range(M.shape[0]):
    for j in range(2):
        ax.text(j, i, int(M[i,j]), ha='center', va='center', fontsize=7)
ax.set_title('Interior-optimum combos per cell')
fig.colorbar(im, shrink=0.8)
fig.tight_layout(); fig.savefig('figures/fig5_robustness.png', dpi=200)
print('saved fig5')
