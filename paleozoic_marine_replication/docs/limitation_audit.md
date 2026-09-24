# Limitation audit

1. **Age assignment by midpoint.** Occurrences spanning multiple stages
   are placed by range midpoint; long-ranging occurrences (e.g. poorly
   resolved Cambrian material) may be mis-binned. The two-stage scheme
   partly absorbs this.

2. **Equal-angle grid.** Grid cells at fixed paleolat/paleolon degree
   resolutions are not equal-area; high paleolatitude cells cover less
   seafloor. Distance decay uses great-circle distances, so decay
   estimates are unaffected, but site definition is not.

3. **PBDB paleocoordinate models.** Rotated positions derive from
   PBDB's `gplates`/`mid` models; model choice can shift cell
   membership. Results are conditional on PBDB rotations.

4. **Genus-level primary resolution.** Species-level sensitivity was
   not run in this pass; identification completeness is high (>85% of
   occurrences carry a species-ranked accepted name) but species pools
   are thinner per bin.

5. **Coverage heterogeneity.** Trilobites and brachiopods dominate
   Cambrian–Devonian bins; bivalves and gastropods only become
   well-sampled later, so cross-clade replication is strongest for
   Ordovician–Devonian (the pilot emphasis).

6. **Decay slopes are shallow.** Reference Jaccard decay slopes are
   small (~1e-6/km); bias on the slope is correspondingly small in
   absolute terms, though directionally consistent (>65% of replicates
   steepen under pool contraction in every clade).

7. **No environment stratification yet.** Spec section 15 sensitivity
   (environmental breadth restriction / stratification) is deferred;
   the factorial and decay results pool all marine environments.

8. **Extinction/diversification extensions deferred.** Sections 16-17
   require the core replication to be accepted first (stop rule).
