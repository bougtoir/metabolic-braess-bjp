"""Heredity manuscript content populated from current analysis outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
STATISTICS = json.loads(
    (PROJECT_DIR / "data" / "correction_stats.json").read_text(encoding="utf-8")
)
NEANDERTHAL = STATISTICS["nean"]
DENISOVAN = STATISTICS["deni"]
PROVENANCE = json.loads(
    (PROJECT_DIR / "data" / "analysis_provenance.json").read_text(encoding="utf-8")
)


def value(statistics: dict[str, object], key: str, digits: int = 3) -> str:
    return f"{float(statistics[key]):.{digits}f}"


def _abo_counts() -> dict[str, int]:
    segments = pd.read_csv(PROJECT_DIR / "data" / "abo_neanderthal_segments.csv")
    populations = pd.read_csv(PROJECT_DIR / "data" / "abo_population_summary.csv")
    indigenous = populations["analysis_group"] == "Indigenous Americas"
    return {
        "interval_segments": int(len(segments)),
        "strict_overlap": int(segments["strict_overlap"].sum()),
        "ties": int((segments["closest_reference"] == "Tie").sum()),
        "indigenous_individuals": int(populations.loc[indigenous, "n_total"].sum()),
    }


ABO = _abo_counts()
INDIVIDUALS = int(PROVENANCE["individuals"])
POPULATIONS = int(PROVENANCE["included_populations"])
PAIRS = int(PROVENANCE["population_pairs"])
PRIMARY_PERMUTATIONS = int(STATISTICS["permutations"])
SENSITIVITY_PERMUTATIONS = int(STATISTICS["sensitivity_permutations"])


TITLE = (
    "Population structure, not special connections: a dependence-aware baseline "
    f"for archaic-segment sharing across {POPULATIONS} human populations"
)
RUNNING_TITLE = "A dependence-aware baseline for archaic-segment sharing"
AUTHOR = "Onishi Tatsuki"
AFFILIATION = "Data Science and AI Innovation Research Promotion Center"
CORRESPONDENCE = (
    "Onishi Tatsuki, Data Science and AI Innovation Research Promotion Center; "
    "Email: bougtoir@gmail.com"
)

ABSTRACT = (
    "Archaic-like segments near focal loci such as the ABO blood-group gene are "
    "often read as evidence of a special population connection or migration "
    "route, yet such readings are rarely tested against a genome-wide baseline "
    "that respects the dependence structure of pairwise data. Here we frame "
    "that reading as an explicit, falsifiable claim and use a reproducible "
    "baseline as a well-powered negative test. High-confidence Neanderthal and "
    f"Denisovan introgression calls from {INDIVIDUALS:,} individuals in "
    f"{POPULATIONS} populations were summarised in 500-kilobase windows, and "
    f"profile similarity was computed for {PAIRS:,} population pairs. "
    "Distance associations and pair-level outliers were assessed with "
    "population-label quadratic assignment procedure (QAP) permutations and "
    "false-discovery-rate (FDR) control. Profile similarity declined with "
    f"geographic distance for Neanderthal (r={value(NEANDERTHAL, 'raw_r')}) and "
    f"Denisovan (r={value(DENISOVAN, 'raw_r')}), with partial distance "
    f"correlations of {value(NEANDERTHAL, 'partial_r')} and "
    f"{value(DENISOVAN, 'partial_r')} and permutation P values of "
    f"{value(NEANDERTHAL, 'distance_qap_p', 4)} and "
    f"{value(DENISOVAN, 'distance_qap_p', 4)}. No non-admixed pair reached "
    "both a residual above two standard deviations and an FDR below 0.10, "
    "and a prespecified ABO-window scan showed no route-level signal. "
    "Population-level archaic-segment sharing reflects broad geographic "
    "structure but supports neither exceptional population pairs nor an "
    "ABO-mediated migration history. By providing a reusable dependence-aware "
    "baseline, the framework turns the negative ABO finding into a set of "
    "testable alternative explanations for focal-locus archaic claims."
)

KEYWORDS = (
    "ABO Blood-Group System; gene flow; Neanderthals; Denisovans; population genetics; "
    "statistical models"
)


# Helper for author formatting

def _format_authors(*authors: str, et_al: bool = False) -> str:
    """Format author names as 'Surname1 Initial1, Surname2 Initial2 et al.'"""
    parts = []
    for author in authors:
        bits = author.split()
        if len(bits) == 1:
            parts.append(bits[0])
        else:
            surname = bits[-1]
            initials = "".join(n[0].upper() for n in bits[:-1] if n)
            parts.append(f"{surname} {initials}")
    if et_al:
        return ", ".join(parts) + " et al."
    return ", ".join(parts)


REFERENCE_RECORDS = [
    (
        "1000 Genomes Project Consortium 2015",
        "1000 Genomes Project Consortium. 2015. A global reference for human genetic variation. Nature 526:68-74. https://doi.org/10.1038/nature15393.",
    ),
    (
        "Benjamini and Hochberg 1995",
        "Benjamini Y, Hochberg Y. 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. J R Stat Soc B 57:289-300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x.",
    ),
    (
        "Bergström et al. 2020",
        "Bergström A, McCarthy SA, Hui R, et al. 2020. Insights into human genetic variation and population history from 929 diverse genomes. Science 367:eaay5012. https://doi.org/10.1126/science.aay5012.",
    ),
    (
        "Calafell et al. 2008",
        "Calafell F, Roubinet F, Ramirez-Soriano A, et al. 2008. Evolutionary dynamics of the human ABO gene. Hum Genet 124:123-135. https://doi.org/10.1007/s00439-008-0530-8.",
    ),
    (
        "Carroll et al. 2020",
        "Carroll SR, Garba I, Figueroa-Rodríguez OL, et al. 2020. The CARE principles for indigenous data governance. Data Sci J 19:43. https://doi.org/10.5334/dsj-2020-043.",
    ),
    (
        "Claw et al. 2018",
        "Claw KG, Lippert D, Bardill J, et al. 2018. A framework for enhancing ethical genomic research with Indigenous communities. Nat Commun 9:2957. https://doi.org/10.1038/s41467-018-05188-3.",
    ),
    (
        "Condemi et al. 2021",
        "Condemi S, Mazières A, Faux P, et al. 2021. Blood groups of Neandertals and Denisova decrypted. PLoS ONE 16:e0254175. https://doi.org/10.1371/journal.pone.0254175.",
    ),
    (
        "Dekker, Krackhardt, and Snijders 2007",
        "Dekker D, Krackhardt D, Snijders TAB. 2007. Sensitivity of MRQAP tests to collinearity and autocorrelation conditions. Psychometrika 72:563-581. https://doi.org/10.1007/s11336-007-9016-1.",
    ),
    (
        "Green et al. 2010",
        "Green RE, Krause J, Briggs AW, et al. 2010. A draft sequence of the Neandertal genome. Science 328:710-722. https://doi.org/10.1126/science.1188021.",
    ),
    (
        "Halverson and Bolnick 2008",
        "Halverson MS, Bolnick DA. 2008. An ancient DNA test of a founder effect in Native American ABO blood group frequencies. Am J Phys Anthropol 137:342-347. https://doi.org/10.1002/ajpa.20887.",
    ),
    (
        "Iasi et al. 2024",
        "Iasi LNM, Chintalapati M, Skov L, et al. 2024. Neanderthal ancestry through time: insights from genomes of ancient and present-day humans. Science 386:eadq3010. https://doi.org/10.1126/science.adq3010.",
    ),
    (
        "Jacobs et al. 2019",
        "Jacobs GS, Hudjashov G, Saag L, et al. 2019. Multiple deeply divergent Denisovan ancestries in Papuans. Cell 177:1010-1021.e32. https://doi.org/10.1016/j.cell.2019.02.035.",
    ),
    (
        "Krackhardt 1988",
        "Krackhardt D. 1988. Predicting with networks: nonparametric multiple regression analysis of dyadic data. Soc Networks 10:359-381. https://doi.org/10.1016/0378-8733(88)90004-4.",
    ),
    (
        "Mantel 1967",
        "Mantel N. 1967. The detection of disease clustering and a generalized regression approach. Cancer Res 27:209-220.",
    ),
    (
        "Ohashi et al. 2006",
        "Ohashi J, Naka I, Kimura R, et al. 2006. Polymorphisms in the ABO blood group gene in three populations in the New Georgia Group of the Solomon Islands. J Hum Genet 51:407-411. https://doi.org/10.1007/s10038-006-0375-8.",
    ),
    (
        "Petr et al. 2019",
        "Petr M, Pääbo S, Kelso J, Vernot B. 2019. Limits of long-term selection against Neandertal introgression. Proc Natl Acad Sci USA 116:1639-1644. https://doi.org/10.1073/pnas.1814338116.",
    ),
    (
        "Prüfer et al. 2017",
        "Prüfer K, de Filippo C, Grote S, et al. 2017. A high-coverage Neandertal genome from Vindija Cave in Croatia. Science 358:655-658. https://doi.org/10.1126/science.aao1887.",
    ),
    (
        "Quilodran et al. 2023",
        "Quilodran CS, Rio J, Tsoupas A, Currat M. 2023. Past human expansions shaped the spatial pattern of Neanderthal ancestry. Sci Adv 9:eadg9817. https://doi.org/10.1126/sciadv.adg9817.",
    ),
    (
        "Raghavan et al. 2014",
        "Raghavan M, Skoglund P, Graf KE, et al. 2014. Upper Palaeolithic Siberian genome reveals dual ancestry of Native Americans. Nature 505:87-91. https://doi.org/10.1038/nature12736.",
    ),
    (
        "Reich et al. 2010",
        "Reich D, Green RE, Kircher M, et al. 2010. Genetic history of an archaic hominin group from Denisova Cave in Siberia. Nature 468:1053-1060. https://doi.org/10.1038/nature09710.",
    ),
    (
        "Sankararaman et al. 2014",
        "Sankararaman S, Mallick S, Dannemann M, et al. 2014. The genomic landscape of Neanderthal ancestry in present-day humans. Nature 507:354-357. https://doi.org/10.1038/nature12961.",
    ),
    (
        "Sankararaman et al. 2016",
        "Sankararaman S, Mallick S, Patterson N, Reich D. 2016. The combined landscape of Denisovan and Neanderthal ancestry in present-day humans. Curr Biol 26:1241-1247. https://doi.org/10.1016/j.cub.2016.03.037.",
    ),
    (
        "Segurel et al. 2012",
        "Segurel L, Thompson EE, Flutre T, et al. 2012. The ABO blood group is a trans-species polymorphism in primates. Proc Natl Acad Sci USA 109:18493-18498. https://doi.org/10.1073/pnas.1210603109.",
    ),
    (
        "Skoglund et al. 2015",
        "Skoglund P, Mallick S, Bortolini MC, et al. 2015. Genetic evidence for two founding populations of the Americas. Nature 525:104-108. https://doi.org/10.1038/nature14895.",
    ),
    (
        "Skov et al. 2018",
        "Skov L, Hui R, Shchur V, et al. 2018. Detecting archaic introgression using an unadmixed outgroup. PLoS Genet 14:e1007641. https://doi.org/10.1371/journal.pgen.1007641.",
    ),
]

REFERENCE_KEYS = [record[0] for record in REFERENCE_RECORDS]
REFERENCES = [record[1] for record in REFERENCE_RECORDS]


INTRODUCTION = [
    (
        "Genomic comparisons established gene flow from Neanderthals "
        "and Denisovans into ancestors of "
        "present-day populations outside Africa (Green et al. 2010; Reich et al. 2010). "
        "The amount and genomic distribution of introgressed sequence vary among "
        "populations because of demographic history, drift, selection, and multiple "
        "introgression histories (Sankararaman et al. 2014; Sankararaman et al. 2016; "
        "Jacobs et al. 2019). These differences invite a recurring style of inference "
        "in which shared archaic segments, often at a focal locus such as the ABO "
        "blood-group gene, are read as evidence of a special connection between two "
        "populations or of a particular migration route (Calafell et al. 2008; "
        "Halverson and Bolnick 2008; Condemi et al. 2021). We call this the "
        "special-connection claim."
    ),
    (
        "This claim has been especially prominent around the ABO blood-group locus. "
        "ABO polymorphism is ancient, medically visible, and has been interpreted as "
        "a trans-species polymorphism maintained by balancing selection (Segurel et al. "
        "2012); compatible long-shared haplotypes have been read as signs of archaic "
        "introgression (Calafell et al. 2008), and inferred blood-group states in "
        "Neanderthals and Denisovans have fuelled popular narratives of ABO-mediated "
        "migration (Condemi et al. 2021). Yet earlier work also cautioned that ABO "
        "frequencies in Indigenous Americans are compatible with founder effects and "
        "drift rather than a special connection (Halverson and Bolnick 2008), and that "
        "the mere presence of an archaic segment near ABO does not specify a route. "
        "What these perspectives share is the absence of a reproducible, dependence-aware "
        "genome-wide baseline against which focal-locus claims can be judged."
    ),
    (
        "The special-connection claim is difficult to evaluate because pairwise "
        "profile similarity is dyadic: each of the "
        f"{POPULATIONS} populations appears in many pair rows, so the "
        f"{PAIRS:,} pairs are not independent observations. Standard row-wise "
        "regressions, bootstraps, or response shuffles do not preserve this "
        "population-level dependence, and an apparently exceptional pair can arise "
        "from broad structure alone. What is generally missing is a genome-wide "
        "baseline that constructs population profiles reproducibly, tests distance "
        "and pair-level effects under a permutation scheme that respects the "
        "dependence structure, and applies explicit multiple-testing control."
    ),
    (
        "Mantel tests address dyadic dependence by permuting matrix labels to test "
        "a single matrix correlation (Mantel 1967), but they do not provide "
        "regression coefficients for multiple predictors, pair-level residuals, or a "
        "multiple-testing framework across pairs. Quadratic assignment procedures "
        "(QAP) extend this permutation logic to multiple regression and, in our "
        "implementation, to pair-level residual null distributions and "
        "false-discovery-rate (FDR) control (Krackhardt 1988; Dekker, Krackhardt, "
        "and Snijders 2007)."
    ),
    (
        "We build such a baseline and use it as a well-powered negative test of two "
        "recurring claims: that particular population pairs share an exceptional "
        "excess of archaic segments, and that a focal locus such as ABO marks a "
        "specific migration route. A clearly framed negative result under "
        "dependence-aware inference is itself informative, because it sets the "
        "genome-wide expectation that any positive focal-locus or special-connection "
        "claim must exceed. Using great-circle distance across "
        f"{POPULATIONS} populations from the 1000 Genomes Project and Human "
        "Genome Diversity Project (HGDP), we test whether Neanderthal- and "
        "Denisovan-segment profile similarity declines with distance, whether any "
        "population pair is an FDR-supported residual outlier, and whether a "
        "prespecified interval centred on the ABO blood-group locus shows anything "
        "beyond the genome-wide expectation. Robustness to alternative windows, "
        "similarity metrics, sample-size thresholds, datasets, co-located pairs, "
        "and regional omission is assessed throughout. Although we use ABO as the "
        "illustrative focal locus, the same negative-control procedure can be "
        "applied to any locus or population pair that is read as evidence of a "
        "special connection, so the contribution is a reusable baseline rather "
        "than a single-locus finding."
    ),
]


METHODS = [
    (
        "Data sources and population inclusion",
        [
            (
                "We analysed publicly archived segment calls generated with hmmix, "
                "a hidden Markov model-based method that detects candidate archaic "
                "sequence without requiring an unadmixed modern outgroup (Skov et al. "
                "2018). Segment files for the 1000 Genomes Project and HGDP samples were "
                "obtained from Zenodo record 14136628. Source population definitions "
                "followed those resources (1000 Genomes Project Consortium 2015; "
                "Bergström et al. 2020). Secure Hash Algorithm 256 (SHA-256) checksums "
                "of both raw files are written to the analysis provenance record."
            ),
            (
                "Segments with mean posterior probability below 0.8 were excluded. "
                "Populations with fewer than seven represented individuals were "
                f"excluded, leaving {INDIVIDUALS:,} individuals in {POPULATIONS} "
                "populations. Source calls annotated as Neanderthal or Both entered the "
                "Neanderthal profile; calls annotated as Denisova or Both entered the "
                "Denisovan profile."
            ),
        ],
    ),
    (
        "Population profiles and pairwise similarity",
        [
            (
                "Autosomes were partitioned into 500-kilobase (kb) windows. Within "
                "each ancestry category, overlapping or fragmented source segments were "
                "collapsed so that each individual-haplotype-window contributed at most "
                "one presence. For each population and window, unique haplotype "
                "presences were divided by twice the number of represented individuals. "
                "A runtime validity check required every frequency to lie between 0 and 1."
            ),
            (
                "For each population pair, Pearson correlation was calculated across the "
                "union of windows with a non-zero frequency in either population. Pairs "
                "required more than 100 union windows for Neanderthal and more than 50 "
                "for Denisovan profiles. The "
                f"{POPULATIONS}-population matrices contained {PAIRS:,} unique "
                "off-diagonal pairs. Correlations describe profile similarity and do not "
                "establish identity by descent. Spearman correlation and cosine similarity "
                "were calculated as metric sensitivities."
            ),
            (
                "Population coordinates were consolidated in a versioned metadata table "
                "from source sampling locations or population centroids. Great-circle "
                "distance was calculated with the Haversine formula. Coordinate "
                "uncertainty and co-located population labels were assessed by excluding "
                "zero-distance pairs."
            ),
        ],
    ),
    (
        "Dyadic regression and permutation inference",
        [
            (
                "The primary expanded descriptive model regressed pairwise similarity "
                "on great-circle distance per 1,000 km, an indicator for involvement of one "
                "of four designated recently admixed American populations (Puerto Ricans "
                "from Puerto Rico, PUR; Colombians from Medellín, Colombia, CLM; people "
                "with Mexican ancestry from Los Angeles, United States, MXL; and "
                "Peruvians from Lima, Peru, PEL), same-continent status, and same-dataset "
                "status. These indicators are coarse sensitivity covariates, not individual "
                "ancestry estimates or causal controls. Distance-only models were also fit."
            ),
            (
                f"Coefficient P values used {PRIMARY_PERMUTATIONS:,} QAP permutations. "
                "At each iteration, the response matrix was permuted by the same random "
                "population-label order on rows and columns, after which the model was "
                "refit. Two-sided P values were the proportion of permuted coefficient "
                "magnitudes at least as large as the observed magnitude, including a "
                "plus-one correction. Descriptive R-squared values quantify fit to the "
                "observed pair matrix and are not interpreted as independent "
                "observations or causal variance explained."
            ),
            (
                "Mantel tests and QAP both use matrix permutation to respect dyadic "
                "dependence, but they answer different questions. A Mantel test "
                "evaluates one correlation between two distance matrices (Mantel 1967); "
                "it does not estimate regression coefficients for several predictors, "
                "does not generate a residual for each pair, and does not support FDR "
                "control across pairs. Our QAP implementation permutes the response "
                "matrix, refits the multiple regression, and records the coefficient and "
                "each pair's residual at every iteration. The same population-label "
                "permutation therefore provides a dependence-aware null for the distance "
                "coefficient, a pair-level residual null distribution, and a joint basis "
                "for Benjamini-Hochberg FDR control."
            ),
            (
                "Population-deletion stability intervals were calculated by refitting "
                "the expanded model after removing every pair containing one population "
                "in turn and reporting the 2.5th and 97.5th percentiles of the resulting "
                "coefficients. These are sensitivity intervals rather than "
                "independent-sample confidence intervals."
            ),
        ],
    ),
    (
        "Residual outliers and multiple testing",
        [
            (
                "Outlier analysis was restricted to the complete matrix after removing "
                "PUR, CLM, MXL, and PEL. Similarity was modelled using distance, "
                "same-continent status, and same-dataset status. Positive residuals were "
                "standardised by the residual standard deviation. For every pair, a "
                "one-sided nominal P value was calculated from its own residual null "
                f"distribution across {PRIMARY_PERMUTATIONS:,} population-label "
                "permutations. Because pair residuals are dyadically dependent, this null "
                "was generated by the same joint row-and-column population-label "
                "permutation used for the coefficient tests rather than by row-wise "
                "resampling, following the rationale for multiple-regression QAP with "
                "dependent dyads (Dekker, Krackhardt, and Snijders 2007). The "
                "Benjamini-Hochberg procedure was applied jointly to all non-admixed "
                "pairs within each ancestry analysis to control the FDR (Benjamini and "
                "Hochberg 1995). A supported positive outlier required z>2 and q<0.10. "
                "Because no pair met this threshold, the qualitative absence of FDR-supported "
                "outliers is robust to the exact dependence structure among pair-level "
                "P values; stricter dependence-aware procedures would only strengthen the "
                "absence of findings."
            ),
        ],
    ),
    (
        "Robustness analyses",
        [
            (
                "We repeated distance-only population-label tests for 250-kb, 500-kb, "
                "and 1-megabase (Mb) windows. At 500 kb, robustness summaries compared "
                "Pearson, Spearman, and cosine similarity; minimum population sizes of "
                "7, 10, 15, and 20; the complete dataset, non-admixed populations, 1000 "
                "Genomes-only and HGDP-only subsets; exclusion of zero-distance pairs; "
                "and leave-one-continent-out subsets. Full-window Pearson correlation "
                "and presence-absence Jaccard similarity assessed sensitivity to the "
                "non-zero-window union. Sensitivity tests used "
                f"{SENSITIVITY_PERMUTATIONS:,} population-label permutations. No "
                "genome-wide callable mask was available in the source release, so "
                "mask-adjusted profiles could not be evaluated."
            ),
        ],
    ),
    (
        "Secondary ABO-centered analysis",
        [
            (
                "The ABO gene was defined on Genome Reference Consortium Human Build 38 "
                "(GRCh38) as chromosome 9 (chr9):133,233,278-133,276,024. We "
                "distinguished strict gene overlap from any overlap with a 500-kb "
                "interval spanning chr9:133.0-133.5 Mb. Population carrier frequencies "
                "used unique individuals in the numerator and all represented source "
                "individuals in the denominator."
            ),
            (
                "For Neanderthal or Both segments in the interval, similarity counts to "
                "Altai, Vindija, and Chagyrskaya were compared; tied maxima remained "
                "ties. The Vindija reference is a high-coverage Neanderthal genome "
                "(Prüfer et al. 2017). The O2 blood-group subtype-defining rs41302905 T "
                "allele was summarised from Ensembl/1000 Genomes frequencies and "
                "published Solomon Islands frequencies (Ohashi et al. 2006). Ancient-window "
                "observations were extracted by a documented, reproducible script from the "
                "public Neanderthal-segment catalogue of Iasi et al. (2024), using the "
                "GRCh37 ABO interval that corresponds to the GRCh38 window analysed here; "
                "ancient and modern calls used different pipelines and were not directly "
                "compared statistically."
            ),
        ],
    ),
    (
        "Ethical review, community engagement, and interpretation",
        [
            (
                "This computational secondary analysis used de-identified public data "
                "and involved no recruitment, contact, biospecimen collection, or new "
                "individual-level phenotype inference. The author did not obtain a "
                "separate institutional review determination for this secondary "
                "analysis; approvals, consent, and data-access procedures were those "
                "reported by the source studies. This limitation is disclosed rather "
                "than treating public availability as equivalent to unrestricted "
                "ethical reuse."
            ),
            (
                "No source community or stakeholder representatives participated in the "
                "design, analysis, interpretation, or dissemination of the present "
                "secondary study, and no direct community return-of-results process was "
                "conducted. Because the dataset includes Indigenous participants and the "
                "topic can affect narratives of ancestry and migration, analyses were "
                "interpreted in light of Indigenous data-governance guidance and the "
                "Collective Benefit, Authority to Control, Responsibility, and Ethics "
                "(CARE) Principles (Claw et al. 2018; Carroll et al. 2020). Population "
                "labels were retained only when needed for transparent source-data "
                "description; locus-level observations were not generalised to "
                "communities, and migration routes were not assigned from these data. "
                "The public article, code, and derived aggregate results are the current "
                "means of results availability. These disclosures are made in the "
                "interest of transparent ethical reporting for secondary genomic analyses."
            ),
        ],
    ),
]


RESULTS = [
    (
        "Data-validity correction",
        (
            "Collapsing fragmented segments at the individual-haplotype-window level "
            "removed duplicate contributions that could otherwise make a nominal "
            "frequency exceed 1. In the rebuilt profiles, the maximum frequency was "
            "1.0 for both ancestry categories and no population-window frequency "
            f"exceeded 1. The analysis retained {POPULATIONS} populations, "
            f"{INDIVIDUALS:,} individuals, and {PAIRS:,} unique population pairs."
        ),
        [],
    ),
    (
        "Geographic distance decay",
        (
            "Neanderthal profile similarity declined with distance "
            f"(raw r={value(NEANDERTHAL, 'raw_r')}); the corresponding Denisovan "
            f"correlation was {value(DENISOVAN, 'raw_r')}. Partial distance "
            "correlations from the expanded descriptive models were "
            f"{value(NEANDERTHAL, 'partial_r')} and "
            f"{value(DENISOVAN, 'partial_r')}. Distance-only R-squared values were "
            f"{value(NEANDERTHAL, 'distance_only_r_squared')} and "
            f"{value(DENISOVAN, 'distance_only_r_squared')}; expanded-model values "
            f"were {value(NEANDERTHAL, 'expanded_r_squared')} and "
            f"{value(DENISOVAN, 'expanded_r_squared')}. The QAP distance coefficients "
            f"per 1,000 km were {value(NEANDERTHAL, 'distance_qap_beta', 5)} "
            f"(P={value(NEANDERTHAL, 'distance_qap_p', 4)}) and "
            f"{value(DENISOVAN, 'distance_qap_beta', 5)} "
            f"(P={value(DENISOVAN, 'distance_qap_p', 4)}) (Figure 1)."
        ),
        ["Figure 1"],
    ),
    (
        "Population structure",
        (
            "The representative heat maps showed broad regional blocks and a stronger "
            "Oceanian contrast in the Denisovan profile (Figure 2). The complete "
            "66-population heat map is provided as Figure S1."
        ),
        ["Figure 2"],
    ),
    (
        "Robustness analyses",
        (
            "Negative distance correlations were examined across admixture exclusions, "
            "within-dataset subsets, minimum sample sizes, and regional omissions. "
            "Figure 3 shows the effect of excluding designated recently admixed "
            "populations, and Figure 4 shows window-size results at 250 kb, 500 kb, "
            "and 1 Mb. These analyses were treated as robustness checks rather than "
            "independent confirmatory tests."
        ),
        ["Figure 3", "Figure 4"],
    ),
    (
        "Residual outlier testing",
        (
            "No non-admixed pair met both the positive-residual z>2 criterion and "
            "Benjamini-Hochberg q<0.10 for either ancestry category. Nominal residual "
            "ranks are retained in the full pairwise data table for auditability but "
            "are not interpreted as statistically supported population connections "
            "(Table 1)."
        ),
        ["Table 1"],
    ),
    (
        "Prespecified ABO-window check",
        (
            "As a prespecified focal-locus check, the 500-kb ABO-centred scan "
            f"identified {ABO['interval_segments']:,} Neanderthal or Both source "
            f"segments, of which {ABO['strict_overlap']} overlapped the ABO gene and "
            f"{ABO['ties']} were tied for maximum reference similarity. In the "
            "Indigenous American HGDP subset only two segments among "
            f"{ABO['indigenous_individuals']} represented individuals fell in the "
            "interval. Both observations fall within the genome-wide expectation, and "
            "this focal scan produced no route-level signal. Exploratory segment-level "
            "compositions and counts are provided as Supplementary material (Figure S2; "
            "Table S1) and are not interpreted as regional proportions or migration routes."
        ),
        [],
    ),
    (
        "Contextual displays",
        (
            "Several descriptive context panels are provided as supplementary "
            "figures because they do not derive from the pairwise analysis. The "
            "O2-defining allele and ABO-window carrier summaries use different "
            "sources and are displayed descriptively rather than as an association "
            "analysis (Figure S3). Ancient and modern ABO-window observations were "
            "produced by different pipelines and permit no formal temporal comparison "
            "(Figure S4). A bivariate global map summarising each population's mean "
            "Neanderthal and Denisovan segment coverage from the present profiles "
            "provides broad geographic context and was not used in the statistical "
            "models (Figure S5)."
        ),
        [],
    ),
]


DISCUSSION = [
    (
        "The principal contribution of this study is not a new archaic signal but a "
        "reproducible, dependence-aware negative control. After correcting the "
        "population-frequency construction, both Neanderthal and Denisovan profile "
        "similarities retained negative geographic associations, so this pattern is not "
        "an artifact of allowing fragmented segments to contribute repeatedly to the same "
        "haplotype-window."
    ),
    (
        "The population-label permutation is central to interpretation. A dataset of "
        f"{PAIRS:,} pairs does not contain {PAIRS:,} independent geographic "
        f"comparisons because each of {POPULATIONS} populations appears repeatedly. "
        "QAP preserves the complete matrix while testing whether the observed "
        "distance coefficient is unusual under population relabeling (Krackhardt "
        "1988; Dekker, Krackhardt, and Snijders 2007). The expanded-model R-squared "
        "values remain descriptive; coarse same-continent, recent-admixture, and "
        "dataset indicators should not be read as causal adjustment."
    ),
    (
        "The distance-decay signal is compatible with broad serial demographic "
        "structure and the spatial patterning of introgressed sequence described in "
        "earlier work (Sankararaman et al. 2014; Sankararaman et al. 2016; Quilodran "
        "et al. 2023). It does not identify the timing, direction, or number of "
        "migration or introgression events. Population coordinates are "
        "approximations, and archaic-call similarity can also reflect callability, "
        "allele-frequency differences, linkage, selection, and reference-panel "
        "composition."
    ),
    (
        "The absence of FDR-supported residual outliers constrains the strongest "
        "historical claims. A highly ranked pair cannot be promoted as evidence for a "
        "special connection when its pair-specific permutation result does not "
        "survive the declared testing family. This is especially important for "
        "admixed American populations, for which recent mixture can alter both "
        "inferred archaic profiles and geographic interpretations."
    ),
    (
        "The ABO analysis illustrates the limits of a focal-locus narrative. ABO has "
        "deep allelic history, and selection can affect the persistence of introgressed "
        "sequence (Segurel et al. 2012; Petr et al. 2019). Calafell et al. (2008) and "
        "Condemi et al. (2021) reported patterns compatible with archaic contribution to "
        "or sharing near ABO, which encouraged strong interpretations of a special "
        "population connection. Halverson and Bolnick (2008), by contrast, argued that "
        "Indigenous American ABO frequencies fit a founder-effect model without invoking "
        "an archaic-specific route, and Segurel et al. (2012) showed that a trans-species "
        "polymorphism under balancing selection offers an alternative explanation that "
        "does not require a unique migration path. Our result adds to this more cautious "
        "side of the literature: after accounting for pairwise dependence and the "
        "genome-wide geographic baseline, the ABO window is not an outlier. "
        "Nevertheless, an inferred segment in a 500-kb interval is not an ABO allele, "
        "closest-reference similarity is not a transmission path, and the O2-defining "
        "variant cannot be labelled Neanderthal-derived from proximity alone. The focal "
        "ABO scan was prespecified as a negative test of the special-connection claim: it "
        "asks whether ABO-window sharing exceeds the genome-wide expectation, not whether "
        "it traces a migration route. The absence of a route-level signal shows that "
        "ABO-window sharing is consistent with the broad geographic structure seen "
        "genome-wide."
    ),
    (
        "A negative result on the route claim is best read not as an absence of "
        "signal but as a constraint that removes one class of explanations. Long "
        "shared haplotypes around ABO may reflect balancing selection acting on an "
        "ancient trans-species polymorphism (Segurel et al. 2012), recurrent low-level "
        "gene flow from multiple archaic sources (Sankararaman et al. 2016; Jacobs "
        "et al. 2019), or drift during population bottlenecks (Halverson and Bolnick "
        "2008) rather than a single ABO-marked migration. Technical factors such as "
        "reference-panel composition, callable-mask variation, and linkage to nearby "
        "selected sites can also modulate where archaic ancestry is detected "
        "(Sankararaman et al. 2014; Jacobs et al. 2019). Treating the ABO window as a "
        "special-connection marker is therefore only one of several possibilities, and "
        "our analysis removes it as a sufficient explanation. Future work can now "
        "test the remaining hypotheses with method-matched ancient genomes, phased "
        "local genealogies, and explicit community governance."
    ),
    (
        "Published Ancient North Eurasian and multiple-founder models provide broader "
        "contexts for First American ancestry (Raghavan et al. 2014; Skoglund et al. "
        "2015), but they do not validate a route for either ABO-window segment. Such "
        "a claim would require independently sampled ancient genomes, a phased local "
        "genealogy, method-matched calling, and explicit community-engaged governance "
        "for any new Indigenous genomic analysis."
    ),
    (
        "Limitations include modest sizes for several populations, sparse Denisovan "
        "calls outside Oceania, centroid-based distances, lack of a common callable "
        "mask, and correlation measures that do not distinguish identity by descent "
        "from identity by state. The dataset combines two projects, and same-dataset "
        "status only partially represents technical heterogeneity. Population-deletion "
        "and sensitivity analyses assess stability but cannot replace validation in "
        "independent modern and ancient data."
    ),
    (
        "The procedure used here is not tied to ABO. Any focal locus or population "
        "pair that is read as evidence of a special connection can, in principle, be "
        "compared against the same dependence-aware, genome-wide baseline. Applying "
        "this protocol to other visible loci, to haplotype-level data that distinguish "
        "identity by descent from identity by state, and to ancient genomes with "
        "method-matched calling would produce a sequence of testable predictions: "
        "balancing-selection targets, multiple introgression pulses, and reference-bias "
        "effects can be separated from migration-route claims by the same baseline. "
        "ABO is therefore a worked example of a reusable negative-control design "
        "rather than the unique subject of the study."
    ),
    (
        f"In conclusion, across {POPULATIONS} geographically diverse populations, "
        "archaic-segment profiles show a broad geographic distance-decay pattern under "
        "dependence-aware permutation tests, but the same analysis provides no support "
        "for an exceptional population pair, an ABO-mediated migration history, or a "
        "specific route through Beringia or island Southeast Asia. The contribution is "
        "therefore less a new signal than a reproducible, dependence-aware baseline "
        "that narrows the hypothesis space: by combining frequency-constrained profile "
        "construction, population-label QAP inference, and explicit FDR control, it "
        "offers a reusable negative control against which focal-locus and "
        "special-connection archaic claims can be judged."
    ),
]


FIGURES = {
    1: (
        "fig1_sharing_vs_distance.png",
        "Archaic-segment profile similarity and geographic distance. Each point is a "
        "dependent population pair. Lines are descriptive distance-only fits; reported "
        "P values use population-label QAP permutations.",
    ),
    2: (
        "fig2_sharing_heatmap.png",
        "Pairwise archaic-segment profile similarity for 31 populations selected for "
        "visual legibility and ordered by geographic region; all 66 populations were "
        "analyzed (see Figure S1).",
    ),
    3: (
        "fig4_sensitivity_admixed.png",
        "Sensitivity of the descriptive Neanderthal distance correlation to exclusion "
        "of designated recently admixed populations.",
    ),
    4: (
        "fig5_window_sensitivity.png",
        "Descriptive geographic distance correlations at 250-kb, 500-kb, and 1-Mb "
        "window sizes. QAP results are tabulated in Supplementary Data.",
    ),
}


SUPPORTING_FIGURES = {
    1: (
        "figS1_full_heatmap.png",
        "Complete 66-population Neanderthal and Denisovan profile-similarity matrices.",
    ),
    2: (
        "fig5_abo_sublineage.png",
        "Exploratory ABO-centered analysis preserving the historical grouped-bar and "
        "segment-map layout. Equal maximum-similarity ties are excluded from the "
        "displayed three-reference proportions and retained in Supplementary Data. The "
        "Pima segment overlaps ABO; the Maya segment is within the wider interval but "
        "does not overlap the gene. Counts are segments, not regional frequencies, and "
        "are not interpreted as a migration route.",
    ),
    3: (
        "fig6_o2_introgression.png",
        "O2 blood-group subtype-defining allele frequencies and ABO-window "
        "segment-carrier frequencies. The panels use different sources and are not an "
        "association analysis; proximity does not establish that the O2 allele is "
        "Neanderthal-derived.",
    ),
    4: (
        "fig8_temporal_dynamics.png",
        "Descriptive ancient and modern ABO-window summaries generated by different "
        "pipelines; no formal temporal comparison is made.",
    ),
    5: (
        "fig9_bivariate_world_map.png",
        "Bivariate global context computed in this study. Circle area encodes the mean "
        "per-bin Neanderthal-segment coverage and colour encodes the mean per-bin "
        "Denisovan-segment coverage for each population, both from "
        "data/population_profiles_500kb.npz; coordinates are approximate sampling "
        "locations from data/population_metadata.csv. These descriptive summaries were "
        "not used in the pairwise statistical models.",
    ),
}
