## Introduction (GEB revision)

Beta diversity — the compositional variation of assemblages across space — is a
foundational currency of macroecology and biogeography (Whittaker, 1960;
Tuomisto, 2010a; Anderson et al., 2011). Pairwise dissimilarity, multiple-site
metrics and the decay of similarity with distance are used to infer connectivity,
dispersal limitation, environmental filtering and biogeographic differentiation
(Nekola & White, 1999; Soininen et al., 2007; Morlon et al., 2008; Baselga,
2010). Comparative studies increasingly apply these measures across taxonomic
or functional groups — asking, for example, whether one guild is more spatially
homogeneous than another — because such contrasts promise inference about
group-specific spatial ecology (Heino et al., 2015). All of these applications
are scale-dependent: turnover varies with the spatial grain and extent of the
data (Wiens, 1989; Barton et al., 2013). When such measures are compared
between guilds, clades or functional
groups, the comparison carries an implicit assumption: that the two assemblages
are structurally comparable — that differences in their regional pool size,
dominance structure, taxonomic resolution, temporal span and sampling intensity
do not themselves alter measured turnover.

In practice, however, guilds and assemblages differ routinely in exactly these
properties. A predator guild and its prey guild typically differ in pool size;
a dominant species can occupy most of the sampled sites while its comparison
guild has none; one group may be identifiable to species while another is only
resolvable to genus; one dataset may integrate a decade of sampling while
another pools centuries; and the two sides may have been collected under
different effort regimes. Each of these structural properties is individually
known to affect diversity metrics. Measured beta diversity depends
on the size and composition of the regional species pool (Kraft et al., 2011;
Chase et al., 2011; Pärtel et al., 2011; Zobel, 2016), and comparisons across
assemblages of unequal richness are a known source of scale-dependent distortion
(Chase et al., 2018). Dominant species and the shape of the occupancy–frequency
distribution can drive dissimilarity values regardless of underlying spatial
processes (Lennon et al., 2004; McGeoch & Gaston, 2002; McGill et al., 2007;
Hillebrand et al., 2008). The taxonomic grain at which data are recorded alters
diversity patterns (Bertrand et al., 2006; Bevilacqua et al., 2012), temporal
aggregation reshapes apparent community change (Olszewski, 1999; Korhonen et al.,
2010; Blowes et al., 2019), and unequal sampling effort and incomplete detection
bias comparisons when they are not standardized (Gotelli & Colwell, 2001;
MacKenzie et al., 2002; Colwell et al., 2012; Chao et al., 2014). Because these
mechanisms co-occur in real data and interact, treating them as independent
additive corrections is itself an untested assumption. Each mechanism is
established; what is missing is a quantitative account of how large their
separate and joint effects on guild-level turnover contrasts can be.

This is not merely a fossil problem. Much of the biodiversity evidence now used
in macroecology is historically aggregated: museum and herbarium collections,
long-term monitoring compilations, archaeological faunas, pollen and sedimentary
records are all assembled over uneven taxonomic, temporal and sampling structure
(Shaffer et al., 1998; Graham et al., 2004; Pyke & Ehrlich, 2010; Lavoie, 2013).
Palaeoecological assemblages are the extreme end of the same spectrum — they push
every structural asymmetry further, with small and uneven taxon pools, strong
dominance, coarse taxonomic resolution and temporal averaging over thousands to
millions of years (Kidwell & Behrensmeyer, 1991; Olszewski, 1999; Behrensmeyer et
al., 2000; Badgley, 2010; Smith & McGowan, 2007; Vilhena & Smith, 2013). If
structural bias in guild-level turnover comparisons is consequential anywhere,
it should be consequential there. The fossil record therefore serves as an
informative stress test for a general inferential problem rather than a special
case with its own rules (Uhen et al., 2013; Peters & McClennen, 2015).

What is missing from the literature is not awareness that these biases exist but
their magnitudes under controlled conditions: how large can a structurally
generated guild contrast become when no true ecological difference exists?
Can structural asymmetry reverse the sign of a contrast? And does it alter only
the mean of dissimilarity, or also the shape of spatial turnover — the
distance-decay relationship that underlies biogeographic inference? Answering
these questions requires ground truth, which empirical assemblages cannot
provide; it requires simulation.

Here we combine (i) controlled simulations in which the true guild contrast is
zero by construction, on a one-dimensional spatial axis and, as a robustness
check, a two-dimensional lattice; (ii) a factorial map identifying joint
conditions that produce false differences and sign reversals; (iii) an analysis
of how structural asymmetry distorts distance-decay slopes, not just mean
dissimilarity; and (iv) an empirical fossil stress test — dinosaur assemblages of
the Late Jurassic Morrison Formation (Maidment et al., 2024) — in which an
initially strong guild-level turnover contrast is decomposed stepwise under
structural controls, with the Nemegt Formation as an external comparator. Our
central equation is Δβ_observed ≠ Δβ_ecological whenever the compared guilds
differ in assemblage structure. Our objectives are to quantify the magnitude of
structural bias under controlled conditions, to identify conditions causing
false differentiation, lost differentiation and sign reversal, to decompose the
Morrison signal empirically, and to derive a practical diagnostic workflow for
guild-level beta-diversity inference in structurally heterogeneous data.
