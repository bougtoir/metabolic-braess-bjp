"""Spatial coupling documentation figure.

The Dryad dataset covers a single ~10 km2 foraging area; there are no
within-study spatial coordinates for capelin shoals vs seabirds, so a
distance-to-prey-centroid analysis is not feasible. This figure documents
the study-area geometry and the survey-level (not spatially resolved)
nature of the data.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")

fig, ax = plt.subplots(figsize=(7, 5))
# approximate location: Funk Island / Notre Dame Bay region, NE Newfoundland
ax.plot([-55.5], [49.75], "r^", ms=12, label="study area (10 km2)")
ax.set_xlim(-57.5, -53.5); ax.set_ylim(49.0, 51.0)
ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
ax.set_title("Single-site design: capelin + seabirds surveyed in one ~10 km2 area")
ax.text(-57.2, 49.15, "No within-study spatial resolution:\n"
        "distance-to-prey-centroid analysis not feasible with this dataset.",
        fontsize=9)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/spatial_coupling_example.png"),
            dpi=150)
print("done")
