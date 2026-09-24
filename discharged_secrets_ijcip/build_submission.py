#!/usr/bin/env python3
"""Assemble the Transport Economics and Management (Elsevier, open access)
submission package (manuscript, title page, cover letter, highlights, checklist)
for the shared-micromobility lifecycle data-exposure study.

This is the manuscript-body / cover-letter generator. It is intentionally kept
out of the public repository because it contains the article prose and does not
contribute to result reproducibility. All quantitative claims are imported from
``reproduce`` (the public reproducibility engine), so the numbers, figures, and
tables it embeds are exactly those regenerated from the committed public data.
Citations use the journal's numbered style ([n], order of first appearance).
"""

from __future__ import annotations

import json
import os
import re
import textwrap
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from reproduce import (
    ROOT, OUTPUT, FIGDIR,
    REFS, CITEMETA, intext, CITE_RX, _parse_label,
    resolve_citations, CITATION_ORDER_FILE,
    fmt, pct, ci, domain_count,
    DOMAINS, N_OPERATORS, N_CODED,
    SCR, N_REGISTRY, N_REACHABLE, N_MOTOR_FEEDS, N_OP_DOMAINS,
    FIG_CAPTIONS, TABLES,
    build_figures, build_tables_docx, build_figures_pptx,
    configure_document, add_table, reset_dirs,
)

TITLE = (
    "Lifecycle Data Exposure in Shared Micromobility: A Scoping Review and "
    "Audit of Public Vehicle Feeds and Operator Disclosures"
)
SHORT_TITLE = "Lifecycle data exposure in shared micromobility"
AUTHOR = "Onishi Tatsuki"
AFFILIATION = ("Data Science and AI Innovation Research Promotion Center, "
               "Shiga University, Hikone, Japan")
EMAIL = "bougtoir@gmail.com"
ORCID = "0000-0001-7261-9062"
POSTAL_ADDRESS = "1-1-1 Banba, Hikone, Shiga 522-8522, Japan"
JOURNAL = "Transport Economics and Management"
JOURNAL_ABBR = "TEM"
PUBLISHER = "Elsevier"
ARTICLE_TYPE = "Research article"
PUBLIC_REPO_URL = "https://github.com/bougtoir/discharged-secrets-scoping-review"
BUILD_DATE = "9 September 2026"

# The TEM guide for authors asks for each illustration as a separate file with
# captions supplied in the manuscript, so figures are not embedded in the
# source manuscript; captions are placed at first mention. Set to True for a
# self-contained review draft.
EMBED_FIGURES = False

# --- Review-model toggle -------------------------------------------------
# The same pipeline serves single-blind (default) and double-masked review.
# Transport Economics and Management uses double-anonymized peer review, so
# the main manuscript is built blinded by default. BLINDED=1 removes author-identifying content from the
# *main manuscript* (byline, acknowledgements, and any identity-revealing
# repository URL). The title page and cover letter are always non-anonymized
# because journals collect them separately and do not forward them to reviewers.
BLINDED = os.environ.get("BLINDED", "1") == "1"

# Persistent DOI for the archived deposit (e.g. Zenodo concept DOI covering all
# versions). Set ZENODO_DOI once the archive is minted; the availability
# statement then cites the DOI instead of the bare repository URL.
ZENODO_DOI = os.environ.get("ZENODO_DOI", "").strip()

# Identity-free link used *only* during double-masked review, and only after
# an anonymous mirror has actually been created. Do not insert a default
# anonymous URL before the mirror exists; leave this empty and the blinded
# data availability statement will omit a repository URL.
ANON_REPO_URL = os.environ.get("ANON_REPO_URL", "").strip()

# Transport Economics and Management allows a maximum of six keywords; avoid
# general and plural terms and multiword concepts containing 'and' or 'of'.
KEYWORDS = [
    "shared micromobility",
    "data governance",
    "location privacy",
    "procurement",
    "concession design",
    "GBFS",
]

# Nonstandard abbreviations used in the abstract; defined there and again in a
# first-page footnote as required by the journal.
ABBREVIATIONS = [
    ("GBFS", "General Bikeshare Feed Specification"),
    ("PRISMA-ScR", "Preferred Reporting Items for Systematic Reviews and "
                   "Meta-Analyses extension for Scoping Reviews"),
    ("CI", "confidence interval"),
]

# Elsevier-style highlights: 3-5 bullets, each no more than 85 characters
# including spaces.
HIGHLIGHTS = [
    f"Scoping review of {fmt(SCR['identified'])} records yields "
    f"{SCR['included']} direct micromobility studies.",
    "Public vehicle feeds disclose persistent identifiers and GPS almost everywhere.",
    "No audited privacy notice addressed vulnerability reporting or device disposal.",
    "A reproducible lifecycle model links evidence strength to management controls.",
    "Disclosure gaps are observable indicators for concession design and procurement.",
]

# Contents of the archive, reused across every availability-statement variant.
_ARCHIVE_CONTENTS = (
    "the frozen GBFS registry snapshot and its checksum, the title/abstract "
    "and full-text screening decisions, the disclosure-audit coding sheets "
    "with verbatim locator quotations, the analysis scripts, the analysis "
    "results, and the figure- and table-generation code. Raw vehicle "
    "identifiers, exact coordinates, and vehicle-specific deep links were not "
    "retained; only field presence or absence was recorded.")
_REPRO_SENTENCE = (
    " Every count, proportion, and confidence interval reported in the article "
    "can be regenerated from these materials with a single build command.")


def data_availability_statement() -> str:
    """Return the availability statement matching the current review model.

    - double-masked (BLINDED) with an anonymous mirror URL: cite the mirror;
    - double-masked (BLINDED) without a mirror: omit the URL and state that
      the archive is available on request during peer review; DOI/URL added
      on acceptance;
    - single-blind + Zenodo DOI: cite the persistent DOI plus the repository;
    - single-blind, no DOI yet: cite the public repository URL.
    """
    if BLINDED and ANON_REPO_URL:
        return (
            "The data and code that support the findings of this study are "
            f"available to reviewers via an anonymized repository at "
            f"{ANON_REPO_URL}. The archive contains " + _ARCHIVE_CONTENTS +
            " Upon acceptance, these materials will be deposited in a public "
            "repository with a permanent DOI." + _REPRO_SENTENCE)
    if BLINDED:
        return (
            "The data and code that support the findings of this study will be "
            "deposited in a public repository on acceptance and are available "
            "from the corresponding author on reasonable request during peer "
            "review. The archive contains " + _ARCHIVE_CONTENTS +
            " Upon acceptance, these materials will be assigned a permanent DOI."
            + _REPRO_SENTENCE)
    if ZENODO_DOI:
        return (
            "The data and code that support the findings of this study are "
            f"openly archived on Zenodo at https://doi.org/{ZENODO_DOI} "
            "(concept DOI, covering all versions), with ongoing development at "
            f"{PUBLIC_REPO_URL}. The archive contains " + _ARCHIVE_CONTENTS +
            _REPRO_SENTENCE)
    return (
        "The data and code that support the findings of this study are openly "
        f"available in the project repository at {PUBLIC_REPO_URL}. This "
        "includes " + _ARCHIVE_CONTENTS + _REPRO_SENTENCE)


# Disclosure statements required by Transport Economics and Management, placed
# after the main text and before the references: CRediT author contributions,
# generative-AI declaration, funding, declaration of competing interest, and
# data availability. Acknowledgements and the ethics statement are included as
# good practice.
def build_declarations() -> list[tuple[str, str]]:
    acknowledgements = (
        "Acknowledgements are withheld to preserve author anonymity for "
        "double-masked peer review; they will be restored on acceptance."
        if BLINDED else
        "The author thanks the maintainers of the public GBFS ecosystem and "
        "the open bibliographic sources that made this audit possible.")
    contributions = (
        "Author contributions are withheld to preserve author anonymity for "
        "double-masked peer review; they will be restored on acceptance."
        if BLINDED else
        f"{AUTHOR}: Conceptualization, Methodology, Software, Formal "
        "analysis, Data curation, Writing - original draft, Writing - review "
        "& editing.")
    who = "the author" if not BLINDED else "the author(s)"
    ai_use = (
        f"During the preparation of this work {who} used generative AI "
        "language tools only to improve the readability and language of the "
        "manuscript. No generative AI tool was used to produce scientific "
        f"content, analysis, or interpretation. After using these tools, {who} "
        "reviewed and edited the content as needed and take(s) full "
        "responsibility for the content of the published article.")
    return [
        ("CRediT authorship contribution statement", contributions),
        ("Declaration of generative AI and AI-assisted technologies in the "
         "writing process", ai_use),
        ("Funding",
         "This research did not receive any specific grant from funding "
         "agencies in the public, commercial, or not-for-profit sectors."),
        ("Declaration of competing interest",
         "The author(s) declare that they have no known competing financial "
         "interests or personal relationships that could have appeared to "
         "influence the work reported in this paper."
         if BLINDED else
         "The author declares that he has no known competing financial "
         "interests or personal relationships that could have appeared to "
         "influence the work reported in this paper."),
        ("Acknowledgements", acknowledgements),
        ("Ethical standards",
         "The research meets all ethical guidelines, including adherence to "
         "the legal requirements of the study jurisdiction. No human "
         "participants were recruited. The study analyzed only publicly "
         "accessible feeds and documents and did not attempt authentication, "
         "access-control circumvention, or interaction with individual users."),
        ("Data availability", data_availability_statement()),
    ]


DECLARATIONS = build_declarations()


def body_blocks() -> list[tuple]:
    n_id = fmt(SCR["identified"])
    doi_pct = 100 * SCR["with_doi"] / SCR["identified"]
    reach = pct("all_registry_entries", "auto_discovery_reachable")
    reach_ci = ci("all_registry_entries", "auto_discovery_reachable")
    blocks: list[tuple] = []

    blocks.append(("h1", "1. Introduction"))
    blocks += [("p", t) for t in [
        "Shared micromobility - dockless electric scooters and bicycles rented "
        "through a smartphone application - has become a visible class of "
        "connected devices that organizations and the public use but do not "
        "own, maintain, or decommission. Each vehicle continuously produces "
        "location, motion, and battery telemetry that is transmitted to an "
        "operator backend and, in many cities, republished through open data "
        "feeds. Prior work has shown that such telemetry can support "
        "re-identification and tracking well beyond the individual rental that "
        "generated it [[demontjoye;elzer]].",
        "Transport economics and management scholarship has examined how "
        "cities regulate, permit, and integrate e-scooter and bikeshare "
        "operators [[gossling;button]] and how the governance of smart "
        "mobility shifts control over service data toward private platforms "
        "[[docherty;pangbourne]], but it has devoted less attention to the "
        "data-governance implications of procuring connected vehicles whose "
        "telemetry is collected by a third-party operator and, in many cities, "
        "republished in open data feeds. Economically, the relationship between "
        "a city or procuring organization and a micromobility operator is a "
        "principal-agent contract under information asymmetry: the operator "
        "observes what its vehicles collect, retain, and transmit across the "
        "lifecycle, whereas the principal observes only what is published in "
        "feeds and privacy notices. Data handling is, in the terms of the "
        "incomplete-contracting literature on contracting out public services, "
        "a quality dimension that is costly to specify and verify [[hart]]. "
        "Concession and procurement clauses are the instruments through which "
        "that asymmetry is managed, because they shape who owns, retains, and "
        "must protect data, and public disclosure is the information about "
        "operator practice that a principal can obtain without cooperation "
        "from the operator, which it can use to benchmark operators, specify "
        "data-related obligations, and allocate liability. Privacy "
        "considerations have been raised for mobility-as-a-service platforms "
        "[[cottrill]]; here we extend that concern from platform data to the "
        "vehicle lifecycle. Measuring what is actually disclosed is therefore a "
        "management question, not merely a technical one.",
        "Security research on shared micromobility has grown quickly but "
        "unevenly. Studies span privacy measurement of rental applications, "
        "firmware and protocol attacks on scooters, location-spoofing threats, "
        "and forensic recovery from returned devices [[vinayaga2022;espoofer;"
        "yilmaz2023;hilgert]]. These contributions are scattered across "
        "security, transportation, and forensics venues, use different threat "
        "models and units of analysis, and have not been assembled into a "
        "single map of what is actually demonstrated as opposed to argued. As "
        "a result, it is difficult to state precisely which data-exposure "
        "pathways rest on direct empirical evidence and which rest on analogy.",
        "A second gap concerns exposure that persists across the device "
        "lifecycle. Attention typically concentrates on real-time position "
        "during a rental, yet information created at deployment, maintenance, "
        "recall, and disposal can remain accessible after custody changes hands "
        "[[iotreuse;remanence]]. Battery and diagnostic channels, in "
        "particular, can leak activity patterns even when positioning is "
        "restricted [[leaky;bms]]. Whether operators disclose these lifecycle "
        "practices to the public is largely unexamined. For transport managers, "
        "the consequence is that oversight built around real-time location "
        "alone says little about data at rest or about what happens to a "
        "vehicle's data when it leaves service.",
        "This article addresses both gaps with an empirical, reproducible "
        "package rather than a conceptual argument. We bridge transport "
        "management and connected-device data governance by (i) conducting a "
        "scoping review, following the Preferred Reporting Items for Systematic "
        "Reviews and Meta-Analyses extension for Scoping Reviews (PRISMA-ScR) "
        "[[prisma_scr]], of evidence on micromobility data exposure; (ii) "
        "auditing the fields that operators actually publish worldwide through "
        "the General Bikeshare Feed Specification (GBFS) [[gbfs_spec]]; and "
        "(iii) auditing what a matched set of operator privacy notices "
        "discloses about collection, retention, transfer, and device "
        "end-of-life. Our research questions are: RQ1, what data-exposure "
        "pathways in shared micromobility are supported by direct evidence; "
        "RQ2, which vehicle-level fields are publicly disclosed, and at what "
        "prevalence; and RQ3, how completely do public operator documents "
        "describe lifecycle data handling.",
        "We are deliberately conservative about interpretation. Publishing a "
        "field, or remaining silent about a practice, is a disclosure signal; "
        "it is not by itself evidence of a privacy harm, a compromise, or a "
        "regulatory violation. The contribution is a transparent evidence base "
        "and a lifecycle model that ties each stage to the strength of its "
        "supporting evidence and to controls whose effectiveness remains to be "
        "tested.",
    ]]

    blocks.append(("h1", "2. Methods"))
    blocks.append(("h2", "2.1. Design and reporting"))
    blocks += [("p", t) for t in [
        "The study combines three prespecified components: a scoping review "
        "(work package WP1), a cross-sectional field audit of public GBFS feeds "
        "(WP2), and a structured disclosure audit of public operator documents "
        "(WP3). The review component is reported in line with PRISMA-ScR "
        "[[prisma_scr]] and follows the scoping-review framework of Arksey and "
        "O'Malley [[year:arksey]]. Eligibility criteria and data sources for all "
        "three components are summarized in Table 1. The protocol, screening "
        "rules, coding sheets, and analysis code are openly available so that "
        "the counts reported here can be regenerated.",
    ]]
    blocks.append(("table", 1))
    blocks.append(("h2", "2.2. Scoping review (WP1)"))
    blocks += [("p", t) for t in [
        f"We compiled {n_id} records from programmatic searches of open "
        "bibliographic metadata. A digital object identifier (DOI) was "
        f"available for {fmt(SCR['with_doi'])} of {n_id} records ({doi_pct:.1f}%), "
        "for which abstracts were retrieved automatically where possible; the "
        "remaining records were screened on title and available metadata only. "
        "Title/abstract screening applied a deterministic rule set that combined "
        "target-domain relevance with the presence of a described data path, and "
        "recorded a decision and reason for every record. Because the rules are "
        "deterministic, we re-applied them to a delayed "
        f"{round(100 * SCR['resample_n'] / SCR['identified'])}% sample "
        f"(n = {fmt(SCR['resample_n'])}) and reproduced every original decision "
        f"({SCR['resample_agreement_pct']}% agreement); this demonstrates "
        "computational reproducibility rather than inter-rater reliability, as a "
        "single reviewer conducted the screening.",
        "Records marked include or uncertain were sought for full-text "
        "assessment. Each retrieved study was classified by evidence distance: "
        "D4, direct target-domain empirical evidence; D3, direct target-domain "
        "documentary evidence; D2, near-domain empirical evidence; D1, "
        "mechanism analogy; and N, normative evidence. This ordering is an "
        "operational classification defined for the present study; it is "
        "conceptually related to the GRADE notion of indirectness "
        "[[grade_indirectness]] but is not a GRADE certainty rating. We did not "
        "treat a "
        "title/abstract decision as equivalent to a confirmed full-text "
        "finding, and we did not claim to have read full text that could not be "
        "retrieved. From the included studies we built a study-level extraction "
        "table capturing device or service, design, data fields, access path, "
        "reported outcome, and limitations.",
    ]]
    blocks.append(("h2", "2.3. Public GBFS field audit (WP2)"))
    blocks += [("p", t) for t in [
        "We froze a snapshot of the public GBFS systems catalogue [[gbfs_registry]] "
        "and recorded its checksum. For each system we attempted to reach the "
        "auto-discovery endpoint, to locate a declared vehicle-status feed, to "
        "retrieve that feed, and to record which specification fields it "
        "contained. The unit of analysis is the system/feed. To respect the "
        "study's safety constraints, we recorded only the presence or absence "
        "of each field; raw vehicle identifiers, exact coordinates, and "
        "vehicle-specific deep links were not retained. Unavailable or empty "
        "feeds were separated from feeds that were retrieved but omitted a "
        "field, and all proportions are reported against explicit denominators "
        "with 95% Wilson confidence intervals (CIs). For k feeds with a field "
        "out of n retrieved, the interval is",
    ]]
    blocks.append(("eq", "wilson"))
    blocks += [("p", t) for t in [
        "where z is the 97.5th percentile of the standard normal distribution. "
        "Because several large operators run many city systems, we also "
        "computed an operator-domain sensitivity analysis to check whether "
        "prevalence was driven by a few operators.",
    ]]
    blocks.append(("h2", "2.4. Public-document disclosure audit (WP3)"))
    blocks += [("p", t) for t in [
        "Operators were selected from the audited GBFS population by a "
        "prespecified rule: eligible motorized systems were grouped by "
        f"normalized operator website domain, and the {N_OPERATORS} domains "
        "with the largest number of eligible systems formed the document "
        "sample (ties resolved alphabetically). The selection table is "
        "published with the code. We then retrieved each operator's public "
        "privacy notice. For each operator document we coded "
        f"{len(DOMAINS)} "
        "disclosure domains - location; trip and time data; vehicle "
        "identifiers; battery or diagnostic data; maintenance or repair "
        "records; account, payment, and device data; analytics or profiling; "
        "retention; processors or contractors; international transfers; "
        "data-subject rights; incident contact; vulnerability disclosure; and "
        "device return, recycling, or disposal - using the values explicit, "
        "partial, not found, not applicable, and unavailable. A not-found "
        "coding means the document did not address the domain; it is not "
        "evidence that the practice does not occur. Each coding is accompanied "
        "by a short verbatim locator quotation in the coding sheet so that a "
        "third party can check it. Coding was computer-assisted and reviewed by "
        "a single reviewer; governance and standards documents "
        "[[mds_privacy;edpb_cv;nist88;nist161;eu_battery]] were used as "
        "reference points and were not coded as operator practices.",
    ]]

    blocks.append(("h1", "3. Results"))
    blocks.append(("h2", "3.1. Scoping review (RQ1)"))
    blocks += [("p", t) for t in [
        f"Of {n_id} records screened, {fmt(SCR['ta_excluded'])} were excluded at "
        f"title/abstract and {fmt(SCR['sought'])} were sought for full text "
        f"(Fig. 1). Of these, {fmt(SCR['not_retrieved'])} could not be retrieved "
        f"and were recorded as such rather than assessed; "
        f"{fmt(SCR['excluded_fulltext'])} retrieved records were excluded "
        f"because they contained no relevant data path ({SCR['no_data_path']}) "
        f"or described a mechanism that did not transfer to the target domain "
        f"({SCR['not_transferable']}). In total, {SCR['included']} direct "
        f"studies were included: {SCR['d4']} at evidence distance D4, "
        f"{SCR['d3']} at D3, and {SCR['d2']} at D2 (Fig. 2; Table 2).",
        "The included D4 studies provide the strongest evidence. A long-term "
        "real-world analysis reconstructed rider-relevant patterns from "
        "operator data [[elzer]]; investigative studies of rental applications "
        "and scooter ecosystems demonstrated collection and protocol weaknesses "
        "[[vinayaga2022;espoofer;etrojans]]; and a forensic analysis recovered "
        "data from micromobility devices [[hilgert]]. D3 studies document "
        "platform architectures, location-spoofing threats, data-acquisition "
        "frameworks, and user-facing traceability concerns "
        "[[isik;vinayaga2020;yilmaz2022;yilmaz2023;sato;li2020;petersen;zhou;"
        "hannemann]]. D2 studies transfer from adjacent domains: battery "
        "side channels and battery-management data [[leaky;bms]], residual data "
        "in reused IoT devices [[iotreuse]], and cloud data remanence "
        "[[remanence]]. No included study, on its own, demonstrated an "
        "end-to-end lifecycle compromise; the evidence is strongest for "
        "operation and weakest for recall and disposal.",
    ]]
    blocks.append(("fig", 1))
    blocks.append(("fig", 2))
    blocks.append(("table", 2))
    blocks.append(("h2", "3.2. Public GBFS field audit (RQ2)"))
    blocks += [("p", t) for t in [
        f"Of {fmt(N_REGISTRY)} registry systems, {reach} (95% CI {reach_ci}; "
        f"n = {fmt(N_REACHABLE)}) exposed a reachable auto-discovery endpoint, "
        f"{pct('reachable_registry_entries', 'vehicle_feed_declared')} of "
        "reachable systems declared a vehicle-status feed, and "
        f"{pct('successful_vehicle_feeds', 'vehicle_feed_nonempty')} of "
        "successfully retrieved feeds contained at least one vehicle (Table 3). "
        f"Restricting to the {fmt(N_MOTOR_FEEDS)} non-empty feeds that declared "
        "motorized micromobility, a vehicle identifier was present in "
        f"{pct('declared_motorized_micromobility_feeds', 'has_vehicle_id')} of "
        "feeds and latitude/longitude in "
        f"{pct('declared_motorized_micromobility_feeds', 'has_location_fields')} "
        "(Fig. 3). The remaining fields were published less consistently: "
        "current range in "
        f"{pct('declared_motorized_micromobility_feeds', 'has_range')}, "
        "vehicle-specific rental links in "
        f"{pct('declared_motorized_micromobility_feeds', 'has_deep_link')}, "
        "last-reported timestamps in "
        f"{pct('declared_motorized_micromobility_feeds', 'has_last_reported')}, "
        "and battery or fuel percentage in "
        f"{pct('declared_motorized_micromobility_feeds', 'has_battery_percent')}.",
        "The operator-domain sensitivity analysis indicates that these are not "
        f"artefacts of a few large operators. Across {fmt(N_OP_DOMAINS)} "
        "eligible operator domains, a vehicle identifier appeared in every "
        "eligible feed for "
        f"{pct('declared_motorized_micromobility_operator_domains_all', 'has_vehicle_id')} "
        "of domains and latitude/longitude for "
        f"{pct('declared_motorized_micromobility_operator_domains_all', 'has_location_fields')}, "
        "whereas battery percentage was present in at least one eligible feed "
        "for only "
        f"{pct('declared_motorized_micromobility_operator_domains_any', 'has_battery_percent')} "
        "of domains. These figures describe what is disclosed publicly; they do "
        "not describe what operators collect or store on their backends, which "
        "the public feed cannot reveal.",
    ]]
    blocks.append(("fig", 3))
    blocks.append(("table", 3))
    blocks.append(("h2", "3.3. Public-document disclosure audit (RQ3)"))
    exp_loc = domain_count("location_data", "explicit")
    nf_batt = domain_count("battery_or_diagnostic_data", "not_found")
    nf_vuln = domain_count("vulnerability_disclosure", "not_found")
    nf_disp = domain_count("return_recycling_disposal", "not_found")
    ret_min = min(domain_count(d, "explicit") for d in (
        "retention", "processors_or_contractors", "account_payment_device_data"))
    ret_all = (f"all {N_CODED}" if ret_min == N_CODED
               else f"at least {ret_min} of {N_CODED}")
    blocks += [("p", t) for t in [
        f"We coded {N_CODED} operator privacy notices across {len(DOMAINS)} "
        f"domains; {N_OPERATORS - N_CODED} "
        "further operators could not be retrieved as reproducible text and were "
        "recorded as unavailable (Fig. 4; Table 4). Operational and "
        "account-level processing was disclosed almost universally: location "
        f"data were explicit for {exp_loc} of {N_CODED} operators, and "
        "retention, processors or contractors, and account/payment/device data "
        f"were explicit for {ret_all}. Data-subject rights and international "
        "transfers were explicit or partial for the large majority, consistent "
        "with a predominantly European operator sample governed by the General "
        "Data Protection Regulation [[gdpr]].",
        "Disclosure was markedly thinner for device-centred and lifecycle "
        f"domains. Battery or diagnostic data collection was not found in "
        f"{nf_batt} of {N_CODED} notices, even though such data are technically "
        "central to these vehicles [[leaky;bms]]. No operator notice in the "
        f"sample described a vulnerability-disclosure channel ({nf_vuln} of "
        f"{N_CODED} not found), and none addressed device return, recycling, or "
        f"disposal handling ({nf_disp} of {N_CODED} not found). We stress that "
        "these are gaps in public documents, not proof that the corresponding "
        "practices are absent; they nonetheless mark the parts of the lifecycle "
        "that are least visible to the public and to procuring organizations.",
    ]]
    blocks.append(("fig", 4))
    blocks.append(("table", 4))

    blocks.append(("h1", "4. Discussion"))
    blocks += [("p", t) for t in [
        "Read together, the three components describe a consistent pattern. "
        "Direct evidence for data exposure is concentrated in the operation "
        "stage, where audits and attack studies demonstrate collection, "
        "tracking, and re-identification potential [[elzer;espoofer;"
        "vinayaga2022]]. The public feed audit shows that the raw materials for "
        "such analyses - persistent identifiers and precise positions - are "
        "disclosed at high prevalence worldwide, while more operationally "
        "sensitive fields are published less uniformly. The disclosure audit "
        "shows that operators describe operational data handling in detail but "
        "are silent on device end-of-life and on security-reporting channels, "
        "the same stages for which the review found only near-domain (D2) "
        "evidence [[iotreuse;remanence]].",
        "We integrate these observations in a six-stage lifecycle model that "
        "links each stage to the evidence distance of its supporting sources "
        "and to a proposed control (Fig. 5; Table 5). The model makes the "
        "strength of the underlying evidence explicit: procurement, deployment, "
        "operation, and maintenance are anchored by direct (D3-D4) evidence, "
        "whereas recall/return and second-life/disposal rest on near-domain "
        "(D2) analogy and on governance and standards guidance "
        "[[nist88;nist161;eu_battery]]. The controls - field minimization, "
        "local processing, access and retention limits, controlled contractor "
        "access, chain-of-custody for returned units, and verified media "
        "sanitization - are proposals whose effectiveness this study did not "
        "test; Table 5 records their effectiveness evidence conservatively.",
        "For procuring organizations, the practical implication is that a "
        "narrow focus on real-time position understates exposure. A telemetry "
        "inventory that spans identifiers, timestamps, range, and battery "
        "state, and that follows devices through maintenance and disposal, is a "
        "more faithful basis for assessment than the intuition that "
        "coordinates alone are the only sensitive field.",
        "From a transport-economics perspective, the results also locate where "
        "the information asymmetry between principal and operator is largest. "
        "Operation-stage practices are both well evidenced and well disclosed, "
        "so a procuring body can verify them from public sources without "
        "operator cooperation. End-of-life practices are neither: the review "
        "found only near-domain evidence and the document audit found "
        "near-complete silence, so any contractual obligation on returned or "
        "retired vehicles cannot currently be monitored from public "
        "information and would have to be enforced through reporting, audit "
        "rights, or certification clauses. Such clauses shift verification "
        "effort onto operators and regulators, in line with the general "
        "observation that contracted-out public services under-deliver on "
        "quality dimensions that are hard to specify and verify [[hart]]; the "
        "lifecycle model helps managers direct that effort to the stages where "
        "public verification is weakest rather than duplicating disclosure that "
        "already exists. We did not measure the costs or welfare effects of "
        "such clauses, and the principal-agent framing is an interpretive "
        "lens rather than a tested model.",
    ]]
    blocks.append(("fig", 5))
    blocks.append(("table", 5))
    blocks.append(("h2", "4.1. Implications for transport management and "
                          "concession design"))
    blocks += [("p", t) for t in [
        "For procuring organizations, concession authorities, and transport "
        "managers, the findings point to three priorities for "
        "shared-micromobility data governance.",
        "First, procurement clauses and concession agreements should require "
        "disclosure of the vehicle fields that are published in open feeds, not "
        "only real-time location. Prior work indicates that identifiers and "
        "timestamps, combined with position, are what make re-identification "
        "and tracking feasible [[demontjoye;elzer]], and range and battery "
        "state add further activity information [[leaky]]; their prevalence "
        "in public feeds means that procurement templates or service-level "
        "agreements that consider only GPS coordinates understate what is "
        "disclosed. Requiring an auditable field inventory "
        "in procurement documents would let managers compare operators on a "
        "common checklist rather than on self-reported privacy claims.",
        "Second, operator accountability frameworks should close the lifecycle "
        "gaps visible in the document audit. Battery and diagnostic data were "
        "addressed by a minority of notices, and vulnerability disclosure "
        "channels and device return or disposal handling by none. These "
        "omissions matter because near-domain evidence places data-remanence "
        "and secondary-market risks at custody changes near the end of a "
        "device's life [[iotreuse;remanence]]. Requiring operators to "
        "publish plain statements on these domains - or to explain why they are "
        "not applicable - would make the market easier to compare and govern "
        "without mandating specific technical architectures.",
        "Third, standards and guidance can be targeted where evidence is "
        "strongest. GBFS already exposes which fields are published, so feed-level "
        "transparency can be improved by standardizing the optional fields that "
        "affect privacy and by documenting the rationale for their inclusion. "
        "For end-of-life handling, where only near-domain evidence exists, "
        "governance bodies should treat disposal requirements as precautionary "
        "rather than evidence-based until device-level empirical studies become "
        "available. The lifecycle framework supplied in this article is "
        "designed to make these gradations explicit so that management can track "
        "evidence rather than assume it.",
        "Together, these priorities turn feed-level disclosures and privacy "
        "notices into observable governance indicators that managers can use "
        "to compare operators, score tenders, and write more complete "
        "concession contracts without prescribing technical implementation. "
        "Because the indicators are derived from public artefacts with a "
        "reproducible procedure, they can be recomputed at each tender or "
        "permit renewal without additional data collection from operators, "
        "which makes them candidates for monitoring metrics in multi-year "
        "concession arrangements; whether they predict operator behaviour "
        "or improve contract outcomes remains to be tested.",
    ]]
    blocks.append(("h2", "4.2. Limitations"))
    blocks += [("p", t) for t in [
        "Several limitations bound these findings. Screening and coding were "
        "performed by a single reviewer with computer assistance; although the "
        "process is deterministic and reproducible, it does not provide "
        "inter-rater reliability, and some included studies were characterized "
        "from abstracts and curated metadata rather than from independently "
        "reproduced experiments. The GBFS audit observes only what is published "
        "in public feeds at a single point in time; it cannot show what "
        "operators collect or retain internally, and field presence is not a "
        "measure of harm. The disclosure audit reflects the public documents we "
        f"could retrieve for {N_OPERATORS} operators selected by number of "
        "GBFS systems; not-found codings denote silence, two operators were "
        "unavailable, the sample is small relative to the population of "
        "operator domains and is weighted toward European and North American "
        "providers, and smaller operators may disclose differently. The "
        "principal-agent interpretation is a framing, not an estimated model: "
        "we did not observe contracts, tender scores, compliance costs, or "
        "prices, so the study cannot quantify the economic value of disclosure "
        "or the cost of the proposed clauses. Finally, the lifecycle controls "
        "are proposals; validating them would require intervention studies or "
        "operator cooperation that were outside this study's scope.",
    ]]

    blocks.append(("h1", "5. Conclusion"))
    blocks += [("p", t) for t in [
        "Shared micromobility offers a tractable, fully public setting in which "
        "to study lifecycle data exposure in connected devices that "
        f"organizations use but do not control. A scoping review of {n_id} "
        f"records identified {SCR['included']} direct studies whose strongest "
        f"evidence concerns the operation stage; a global audit of "
        f"{fmt(N_REACHABLE)} public GBFS "
        "systems showed that persistent identifiers and precise positions are "
        "disclosed at high prevalence; and a disclosure audit showed that "
        f"operators document operational processing thoroughly but are silent "
        f"on device disposal and vulnerability reporting. These are disclosure "
        "and evidence signals, not demonstrations of harm. The lifecycle model "
        "and its traceability table turn them into an auditable agenda for "
        "procurement and risk governance: extend assessment beyond real-time "
        "location, close the documentation gaps at end-of-life, and empirically "
        "validate the proposed controls with operators and procuring bodies.",
    ]]
    return blocks


# ---------------------------------------------------------------------------
# Citation resolution
def _m(tag: str, text: str | None = None, **attrs) -> OxmlElement:
    el = OxmlElement(f"m:{tag}")
    for k, v in attrs.items():
        el.set(qn(f"m:{k}"), v)
    if text is not None:
        el.text = text
    return el


def _mr(text: str, italic: bool = True) -> OxmlElement:
    """A math run; Word italicizes variables by default, so plain style is
    requested explicitly for operators and digits."""
    r = _m("r")
    if not italic:
        rpr = _m("rPr")
        rpr.append(_m("sty", val="p"))
        r.append(rpr)
    r.append(_m("t", text))
    return r


def _frac(num: list, den: list) -> OxmlElement:
    f = _m("f")
    n = _m("num")
    d = _m("den")
    for e in num:
        n.append(e)
    for e in den:
        d.append(e)
    f.append(n)
    f.append(d)
    return f


def _sup(base: list, sup: list) -> OxmlElement:
    e = _m("sSup")
    b = _m("e")
    s = _m("sup")
    for x in base:
        b.append(x)
    for x in sup:
        s.append(x)
    e.append(b)
    e.append(s)
    return e


def _hat(inner: list) -> OxmlElement:
    acc = _m("acc")
    pr = _m("accPr")
    pr.append(_m("chr", val="\u0302"))
    acc.append(pr)
    e = _m("e")
    for x in inner:
        e.append(x)
    acc.append(e)
    return acc


def _sqrt(inner: list) -> OxmlElement:
    rad = _m("rad")
    pr = _m("radPr")
    pr.append(_m("degHide", val="1"))
    rad.append(pr)
    rad.append(_m("deg"))
    e = _m("e")
    for x in inner:
        e.append(x)
    rad.append(e)
    return rad


def wilson_omml() -> OxmlElement:
    """Wilson score interval as native Word (OMML) display math."""
    z2 = lambda: _sup([_mr("z")], [_mr("2", italic=False)])  # noqa: E731
    p_hat = lambda: _hat([_mr("p")])  # noqa: E731
    para = _m("oMathPara")
    om = _m("oMath")
    om.append(p_hat())
    om.append(_mr(" = ", italic=False))
    om.append(_mr("k"))
    om.append(_mr("/", italic=False))
    om.append(_mr("n"))
    om.append(_mr(",  CI = ", italic=False))
    inner = [
        _frac([p_hat(), _mr("(1 - ", italic=False), p_hat(), _mr(")", italic=False)],
              [_mr("n")]),
        _mr(" + ", italic=False),
        _frac([z2()], [_mr("4", italic=False), _sup([_mr("n")], [_mr("2", italic=False)])]),
    ]
    num = [
        p_hat(), _mr(" + ", italic=False),
        _frac([z2()], [_mr("2", italic=False), _mr("n")]),
        _mr(" \u00b1 ", italic=False), _mr("z"), _sqrt(inner),
    ]
    den = [_mr("1 + ", italic=False), _frac([z2()], [_mr("n")])]
    om.append(_frac(num, den))
    para.append(om)
    return para


def add_equation(doc: Document) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph._p.append(wilson_omml())


def add_body_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Inches(0.3)
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def add_figure(doc: Document, num: int, png: Path, repl) -> None:
    if EMBED_FIGURES:
        image_p = doc.add_paragraph()
        image_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        image_p.paragraph_format.space_before = Pt(14)
        width = 6.3 if num in (1, 2, 3) else 6.5
        image_p.add_run().add_picture(str(png), width=Inches(width))
    caption = doc.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_before = Pt(6)
    caption.paragraph_format.space_after = Pt(14)
    run = caption.add_run(repl(FIG_CAPTIONS[num]))
    run.italic = True
    run.font.size = Pt(10)


def add_page_number(section) -> None:
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, end])


def count_word(n: int) -> str:
    return "none" if n == 0 else str(n)


ABSTRACT_STRUCT = [
    ("Abstract", "Shared micromobility - dockless electric scooters and "
     "bicycles rented via smartphone - is a globally deployed transport "
     "service that cities procure through permits and concessions but do not "
     "operate. Because the operator alone observes what its vehicles collect "
     "and retain, public disclosure is the information about operator "
     "practice that a procuring organization can obtain without operator "
     "cooperation and use to benchmark operators and allocate liability. This "
     "study maps the direct evidence for data exposure across the vehicle "
     "lifecycle, measures which vehicle fields operators publish worldwide, "
     "and assesses how completely operators disclose lifecycle data handling. "
     "A scoping review following the Preferred Reporting Items for Systematic "
     "Reviews and Meta-Analyses extension for Scoping Reviews (PRISMA-ScR) of "
     f"{fmt(SCR['identified'])} records yielded {SCR['included']} direct studies, "
     "with the strongest evidence at the operation stage. A cross-sectional "
     f"audit of {fmt(N_REACHABLE)} reachable public General Bikeshare Feed Specification "
     "(GBFS) feeds, reported with 95% Wilson confidence intervals (CIs), found "
     "vehicle identifiers in "
     f"{pct('declared_motorized_micromobility_feeds', 'has_vehicle_id')} and "
     "positions in "
     f"{pct('declared_motorized_micromobility_feeds', 'has_location_fields')} "
     "of motorized feeds, but battery percentage in only "
     f"{pct('declared_motorized_micromobility_feeds', 'has_battery_percent')}. "
     f"A disclosure audit of {N_CODED} operator privacy notices showed that "
     "operational data handling is documented thoroughly, but "
     f"{count_word(N_CODED - domain_count('return_recycling_disposal', 'not_found'))} "
     "addressed device disposal and "
     f"{count_word(N_CODED - domain_count('vulnerability_disclosure', 'not_found'))} "
     "described a vulnerability-reporting channel. "
     "These findings are disclosure and evidence signals, not "
     "demonstrations of harm. A reproducible lifecycle model ties each stage "
     "to the strength of its evidence and to governance controls, and shows "
     "that assessment for procurement and concession design should move beyond "
     "real-time location and concentrate contractual monitoring on the "
     "end-of-life stages where public verification is weakest."),
]


def build_abstract_text() -> str:
    return " ".join(text for _, text in ABSTRACT_STRUCT)



def build_manuscript(blocks, tables, figpaths, repl, references) -> Path:
    doc = Document()
    configure_document(doc)
    add_page_number(doc.sections[0])
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run(TITLE).bold = True
    byline = doc.add_paragraph()
    byline.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if BLINDED:
        # Double-masked: the main manuscript carries no identifying byline; the
        # author details travel on the separate, non-anonymized title page.
        anon = byline.add_run(
            "Author and affiliation details removed for double-masked peer "
            "review")
        anon.italic = True
        anon.font.size = Pt(10)
    else:
        byline.add_run(AUTHOR).bold = True
        aff = doc.add_paragraph()
        aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ar = aff.add_run(
            f"{AFFILIATION}\nCorresponding author: {EMAIL}; ORCID {ORCID}")
        ar.italic = True
        ar.font.size = Pt(10)

    doc.add_heading("Abstract", level=1)
    _, abstract_text = ABSTRACT_STRUCT[0]
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(abstract_text)

    doc.add_heading("Highlights", level=1)
    for bullet in HIGHLIGHTS:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(bullet)

    kw = doc.add_paragraph()
    kw.add_run("Keywords: ").bold = True
    kw.add_run("; ".join(KEYWORDS))

    # First-page abbreviation footnote required by the journal for nonstandard
    # abbreviations used in the abstract.
    ab = doc.add_paragraph()
    ab.paragraph_format.space_before = Pt(6)
    r = ab.add_run("Abbreviations: ")
    r.bold = True
    r.font.size = Pt(10)
    r2 = ab.add_run("; ".join(f"{a}, {d}" for a, d in ABBREVIATIONS) + ".")
    r2.font.size = Pt(10)

    for kind, payload in blocks:
        if kind == "h1":
            doc.add_heading(payload, level=1)
        elif kind == "h2":
            doc.add_heading(payload, level=2)
        elif kind == "p":
            add_body_paragraph(doc, repl(payload))
        elif kind == "eq":
            add_equation(doc)
        elif kind == "fig":
            add_figure(doc, payload, figpaths[payload]["png"], repl)
        elif kind == "table":
            add_table(doc, tables[payload], repl)

    for label, value in DECLARATIONS:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)
        p.add_run(f"{label}. ").bold = True
        p.add_run(value)

    doc.add_heading("References", level=1)
    for num, label in enumerate(references, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(4)
        p.add_run(format_reference(num, label))

    path = OUTPUT / f"Manuscript_{JOURNAL_ABBR}.docx"
    doc.save(path)
    return path


def format_reference(num: int, label: str) -> str:
    """``[n] text`` with the journal's ``[dataset]`` prefix preceding the number."""
    text = REFS[label]
    if text.startswith("[dataset] "):
        return f"[dataset] [{num}] {text[len('[dataset] '):]}"
    return f"[{num}] {text}"


def build_title_page(word_count: int, n_refs: int) -> Path:
    doc = Document()
    configure_document(doc)
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run(TITLE).bold = True
    doc.add_paragraph()
    for text, bold in [(AUTHOR, True), (AFFILIATION, False),
                       (POSTAL_ADDRESS, False),
                       (f"Corresponding author: {AUTHOR}; {EMAIL}", False),
                       (f"ORCID: {ORCID}", False)]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(text).bold = bold
    doc.add_paragraph()
    highlights_count = len(HIGHLIGHTS)
    abstract_words = len(re.findall(r"\b[\w'-]+\b", build_abstract_text()))
    fields = [
        ("Full title", TITLE),
        ("Short title", SHORT_TITLE),
        ("Article type", ARTICLE_TYPE),
        ("Journal", f"{JOURNAL} ({PUBLISHER})"),
        ("Peer review", "Double-anonymized; the manuscript file is anonymized"),
        ("Abstract word count", str(abstract_words)),
        ("Keywords", "; ".join(KEYWORDS)),
        ("Highlights", f"{highlights_count} bullets"),
        ("Main-text word count (excludes title, abstract, references)", str(word_count)),
        ("Figures", "5"),
        ("Tables", "5"),
        ("References", str(n_refs)),
        ("Funding", "This research did not receive any specific grant from "
                    "funding agencies in the public, commercial, or "
                    "not-for-profit sectors."),
        ("Declaration of competing interest", "None declared"),
        ("Present/permanent address", "Same as the affiliation above"),
    ]
    for label, value in fields:
        p = doc.add_paragraph()
        p.add_run(f"{label}: ").bold = True
        p.add_run(value)
    path = OUTPUT / f"Title_Page_{JOURNAL_ABBR}.docx"
    doc.save(path)
    return path


def build_cover_letter() -> Path:
    doc = Document()
    configure_document(doc)
    for line in [AUTHOR, AFFILIATION, EMAIL, f"ORCID: {ORCID}", BUILD_DATE]:
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(2)
    doc.add_paragraph()
    doc.add_paragraph("The Editors-in-Chief")
    doc.add_paragraph(JOURNAL)
    doc.add_paragraph(PUBLISHER)
    doc.add_paragraph()
    doc.add_paragraph("Dear Editors,")
    paras = [
        f"I submit the manuscript \"{TITLE}\" for consideration as a "
        f"research article in {JOURNAL}.",
        "Shared micromobility is a globally deployed transport service that "
        "cities procure through permits and concessions but do not operate "
        "themselves. The manuscript treats the city-operator relationship as a "
        "contract under information asymmetry and asks what a procuring "
        "organization can actually observe about lifecycle data handling from "
        "public sources. It reports an empirical, reproducible package: a "
        "PRISMA-ScR scoping review that maps the direct evidence for data "
        "exposure; a global audit of public GBFS feeds that measures which "
        "vehicle fields operators publish; and a structured audit of public "
        f"operator privacy notices across {len(DOMAINS)} disclosure domains.",
        f"The work fits the scope of {JOURNAL} - transportation business, "
        "management, and economic policy across all modes - because it turns "
        "worldwide disclosure practice into observable governance indicators "
        "for procurement, concession design, and operator benchmarking, and "
        "because it shows where contractual monitoring must rely on audit or "
        "reporting clauses rather than on public verification. The framing "
        "builds on the transport literature on e-scooter regulation and smart-"
        "mobility governance and on the incomplete-contracting view of "
        "contracted-out public services. Each finding is tied to the actors "
        "bearing the risk, the management controls that could address it, the "
        "strength of the supporting evidence, and the stage at which "
        "verification effort would fall on operators. Throughout, we treat "
        "field presence and document silence as disclosure and evidence "
        "signals rather than as proof of harm, compromise, or regulatory "
        "violation, and we state the effectiveness of proposed controls "
        "conservatively as not yet validated.",
        "The study analyzed only publicly accessible feeds and documents; it "
        "did not attempt authentication or access-control circumvention, did "
        "not interact with users, and retained no raw identifiers, exact "
        "coordinates, or vehicle deep links. Consistent with the journal's "
        "double-anonymized peer review, the manuscript file contains no "
        "identifying information; the anonymised repository link and the "
        "public repository URL will be disclosed on acceptance. All data, "
        "coding sheets, and code are available so that every reported count "
        "can be regenerated with a single command. The manuscript is original "
        "and is not under consideration elsewhere. There is no funding or "
        "competing interest to declare; generative AI tools were used only for "
        "language editing, as declared in the manuscript. I understand that "
        f"{JOURNAL} is an open access journal and accept the article "
        "publishing charge terms should the manuscript be accepted.",
        "Thank you for considering this submission.",
    ]
    for text in paras:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.add_run(text)
    doc.add_paragraph("Sincerely,")
    doc.add_paragraph(AUTHOR)
    path = OUTPUT / f"Cover_Letter_{JOURNAL_ABBR}.docx"
    doc.save(path)
    return path


def build_highlights() -> tuple[Path, Path]:
    doc = Document()
    configure_document(doc)
    h = doc.add_paragraph(style="Title")
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h.add_run("Highlights").bold = True
    for bullet in HIGHLIGHTS:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(bullet)
    docx_path = OUTPUT / f"Highlights_{JOURNAL_ABBR}.docx"
    doc.save(docx_path)
    txt_path = OUTPUT / f"Highlights_{JOURNAL_ABBR}.txt"
    txt_path.write_text("\n".join(f"- {b}" for b in HIGHLIGHTS) + "\n", encoding="utf-8")
    return docx_path, txt_path


def build_reporting_guideline() -> Path:
    doc = Document()
    configure_document(doc)
    h = doc.add_paragraph(style="Title")
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h.add_run("PRISMA-ScR reporting checklist").bold = True
    p = doc.add_paragraph()
    p.add_run(
        "The scoping-review component (WP1) follows the PRISMA-ScR checklist "
        "(Tricco et al., 2018). The field audit (WP2) and disclosure audit "
        "(WP3) are cross-sectional observational studies of public artefacts "
        "and are reported with explicit denominators, confidence intervals, and "
        "open code. The table below maps each PRISMA-ScR item to its location.")
    items = [
        ("Title", "Identifies the report as a scoping review", "Title page"),
        ("Abstract", "Summary", "Abstract"),
        ("Rationale", "Rationale in the context of what is known", "Section 1"),
        ("Objectives", "Research questions RQ1-RQ3", "Section 1"),
        ("Protocol", "Protocol availability", "Data availability statement"),
        ("Eligibility criteria", "Characteristics used as criteria", "Section 2.2; Table 1"),
        ("Information sources", "Sources searched", "Section 2.2; Table 1"),
        ("Selection of sources", "Screening process", "Section 2.2; Fig. 1"),
        ("Data charting", "Extraction process and items", "Section 2.2; Table 2"),
        ("Synthesis of results", "Methods of summarizing", "Sections 3-4"),
        ("Results of sources", "Numbers screened and included", "Section 3.1; Fig. 1"),
        ("Results of syntheses", "Charted results", "Sections 3.1-3.3"),
        ("Limitations", "Limitations of the review", "Section 4.1"),
        ("Conclusions", "Interpretation and implications", "Section 5"),
        ("Funding", "Sources of funding", "Declarations"),
    ]
    add_table(doc, {"title": "PRISMA-ScR item mapping",
                    "headers": ["Item", "Checklist description", "Location"],
                    "rows": items}, lambda x: x)
    path = OUTPUT / "Reporting_Guideline_PRISMA-ScR.docx"
    doc.save(path)
    return path


def _json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 ref-check (mailto:" + EMAIL + ")"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.load(resp)


def resolve_identifier(ident: str) -> tuple[str, str]:
    """Live existence check. DOIs are looked up in Crossref (fallback
    DataCite, which indexes arXiv DOIs) and the registered title is returned
    so it can be compared with the reference. Plain URLs (standards,
    regulations, registries) are fetched with GET. Falls back gracefully
    when offline so the build stays reproducible."""
    if ident.startswith("https://doi.org/"):
        doi = ident[len("https://doi.org/"):]
        try:
            msg = _json(f"https://api.crossref.org/works/{doi}")["message"]
            return "verified_crossref", (msg.get("title") or [""])[0]
        except urllib.error.HTTPError:
            pass
        except Exception:
            return "not_checked_offline", ""
        try:
            attrs = _json(f"https://api.datacite.org/dois/{doi}")["data"]["attributes"]
            return "verified_datacite", (attrs.get("titles") or [{}])[0].get("title", "")
        except urllib.error.HTTPError as exc:
            return f"doi_not_found_http_{exc.code}", ""
        except Exception:
            return "not_checked_offline", ""
    if ident.startswith("http"):
        req = urllib.request.Request(
            ident, headers={"User-Agent": "Mozilla/5.0 ref-check", "Accept": "text/html"})
        try:
            code = urllib.request.urlopen(req, timeout=25).status
            return f"url_resolves_http_{code}", ""
        except urllib.error.HTTPError as exc:
            # 403/429 are anti-bot responses from a live page.
            return f"url_exists_http_{exc.code}", ""
        except Exception:
            return "not_checked_offline", ""
    return "no_identifier", ""


def build_reference_verification(refs) -> Path:
    path = OUTPUT / "Reference_Verification.csv"
    lines = ["Number,Label,Reference,Identifier,VerificationDate,Status,RegisteredTitle"]
    for i, label in enumerate(refs, 1):
        text = format_reference(i, label)
        m = re.search(r"(https?://\S+)", text)
        ident = m.group(1).rstrip(".") if m else "(no identifier)"
        status, title = resolve_identifier(ident)
        row = [str(i), label, text, ident, BUILD_DATE, status, title]
        lines.append(",".join(f'"{v.replace(chr(34), chr(34)*2)}"' for v in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def build_citation_audit(blocks, tables, order, repl) -> Path:
    first: dict[str, tuple[str, str]] = {}
    location = "Body"
    for kind, payload in blocks:
        if kind in ("h1", "h2"):
            location = payload
            continue
        frags = []
        if kind == "p":
            frags = [payload]
        elif kind == "table":
            frags = [c for r in tables[payload]["rows"] for c in r]
            location = f"Table {payload}"
        for frag in frags:
            for m in CITE_RX.finditer(frag):
                for raw in m.group(1).split(";"):
                    label, _ = _parse_label(raw)
                    if label not in first:
                        first[label] = (location, textwrap.shorten(repl(frag), 200, placeholder="..."))
    path = OUTPUT / "Citation_Audit.csv"
    lines = ["Number,Label,Authors,Year,First appearance,Context"]
    for num, label in enumerate(order, 1):
        loc, ctx = first[label]
        lines.append(",".join(f'"{v.replace(chr(34), chr(34)*2)}"'
                              for v in [str(num), label, intext(label),
                                        CITEMETA[label][1], loc, ctx]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def word_count(blocks, repl) -> int:
    """Main-text word count excluding title, abstract, and references."""
    text = ""
    for kind, payload in blocks:
        if kind == "p":
            text += " " + repl(payload)
    return len(re.findall(r"\b[\w'-]+\b", text))


def validate(blocks, tables, order, ref_list, repl) -> dict:
    # every cited label resolves (resolve_citations already raises on unknown)
    all_resolve = all(l in REFS for l in order)
    # all refs used, none orphan or phantom
    orphan = set(order) ^ set(REFS.keys())
    # reference list follows first-appearance order (numbered style)
    refs_in_order = ref_list == order
    # every rendered [n] stays within 1..len(ref_list)
    rendered = " ".join(repl(p) for k, p in blocks if k == "p")
    nums = [int(n) for grp in re.findall(r"\[([\d,\-]+)\]", rendered)
            for part in grp.split(",") for n in part.split("-")]
    numbers_in_range = all(1 <= n <= len(ref_list) for n in nums)
    body = word_count(blocks, repl)
    abstract_words = len(re.findall(r"\b[\w'-]+\b", build_abstract_text()))
    highlights_ok = 3 <= len(HIGHLIGHTS) <= 5
    highlights_max_len = all(len(h) <= 85 for h in HIGHLIGHTS)
    # figures/tables cited in text
    body_text = " ".join(repl(p) for k, p in blocks if k == "p")
    figs_cited = all(f"Fig. {i}" in body_text for i in range(1, 6))
    tabs_cited = all(f"Table {i}" in body_text for i in range(1, 6))
    # figure/table blocks present and sequential
    fig_seq = [p for k, p in blocks if k == "fig"]
    tab_seq = [p for k, p in blocks if k == "table"]
    # in-text markers must not leak into the rendered text
    no_raw_markers = not any(CITE_RX.search(repl(p)) for k, p in blocks if k == "p")
    # required Transport Economics and Management disclosure statements
    decl_labels = {lbl for lbl, _ in DECLARATIONS}
    required_disclosures = {
        "Data availability", "Funding", "Declaration of competing interest",
        "CRediT authorship contribution statement",
        "Declaration of generative AI and AI-assisted technologies in the "
        "writing process",
    }.issubset(decl_labels)
    # abstract must define every nonstandard abbreviation it uses and carry no
    # citation markers
    abstract = build_abstract_text()
    abstract_abbrs_defined = all(
        f"({abbr})" in abstract or f"({abbr}s)" in abstract
        for abbr, _ in ABBREVIATIONS if abbr in abstract)
    abstract_no_refs = not CITE_RX.search(abstract) and "[" not in abstract
    keywords_ok = 1 <= len(KEYWORDS) <= 6 and not any(
        re.search(r"\b(and|of)\b", k) for k in KEYWORDS)
    # double-masked guard: no author-identifying token may reach the disclosures
    identity_tokens = [PUBLIC_REPO_URL, "bougtoir"]
    for value in (AUTHOR, EMAIL, ORCID):
        if value and "[" not in value:
            identity_tokens.append(value)
    decl_text = " ".join(v for _, v in DECLARATIONS)
    no_identity_leak = (not BLINDED) or not any(
        tok in decl_text for tok in identity_tokens)
    checks = {
        "all_citations_resolve": all_resolve,
        "no_orphan_or_phantom_refs": not orphan,
        "references_in_first_appearance_order": refs_in_order,
        "citation_numbers_within_range": numbers_in_range,
        "no_unresolved_markers": no_raw_markers,
        "figures_cited_in_text": figs_cited,
        "tables_cited_in_text": tabs_cited,
        "five_figures_present": sorted(set(fig_seq)) == [1, 2, 3, 4, 5],
        "five_tables_present": sorted(set(tab_seq)) == [1, 2, 3, 4, 5],
        "abstract_within_250w": abstract_words <= 250,
        "abstract_abbreviations_defined": abstract_abbrs_defined,
        "abstract_has_no_references": abstract_no_refs,
        "highlights_3_to_5": highlights_ok,
        "highlights_max_85_chars": highlights_max_len,
        "keywords_at_most_six_no_and_of": keywords_ok,
        "required_disclosures_present": required_disclosures,
        "no_identity_leak_when_blinded": no_identity_leak,
    }
    failures = [k for k, v in checks.items() if not v]
    if failures:
        raise RuntimeError(f"Validation failed: {failures}; orphan={orphan}")
    # abbreviation-at-first-use spot check
    joined = body_text
    for abbr, definition in {
        "GBFS": "General Bikeshare Feed Specification (GBFS)",
        "PRISMA-ScR": "Scoping Reviews (PRISMA-ScR)",
        "DOI": "digital object identifier (DOI)",
        "GDPR": "General Data Protection Regulation",
    }.items():
        if abbr in joined and definition not in joined:
            raise RuntimeError(f"Undefined abbreviation at first use: {abbr}")
    return {"word_count": body, "abstract_words": abstract_words,
            "highlights": len(HIGHLIGHTS), "keywords": len(KEYWORDS),
            "references": len(ref_list), **checks}


def build_validation_report(validation: dict, figpaths) -> Path:
    path = OUTPUT / "VALIDATION.txt"
    lines = ["Submission validation report", "=" * 30, ""]
    for k, v in validation.items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("Figure files:")
    for num, kinds in figpaths.items():
        for kind, p in kinds.items():
            lines.append(f"  Figure {num} {kind}: {p.name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def build_checklist(validation) -> Path:
    doc = Document()
    configure_document(doc)
    h = doc.add_paragraph(style="Title")
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h.add_run("Submission checklist").bold = True
    rows = [
        ["Cover letter", "Included", f"Cover_Letter_{JOURNAL_ABBR}.docx"],
        ["Title page with author details, postal address, corresponding author", "Included", f"Title_Page_{JOURNAL_ABBR}.docx"],
        ["Article file (anonymized for double-anonymized review; figure files supplied separately)", "Included", f"Manuscript_{JOURNAL_ABBR}.docx"],
        ["Highlights (3-5 bullets, <=85 chars, separate file)", f"{validation['highlights']} bullets", f"Highlights_{JOURNAL_ABBR}.docx/.txt"],
        ["Abstract (concise, factual, no references)", f"{validation['abstract_words']} words", "Manuscript"],
        ["Keywords (max 6; no 'and'/'of')", f"{validation['keywords']}", "Manuscript"],
        ["Abbreviations footnote on first page", "Included", "Manuscript"],
        ["Figures as separate files (PNG + TIFF + PDF, 600 dpi)", "Included", "figures/Figure1-5.*"],
        ["Figure captions at first mention in manuscript", "Included", "Manuscript"],
        ["Editable figures (native Office format, one per slide)", "Included", f"Figures_{JOURNAL_ABBR}_editable.pptx"],
        ["Editable tables (text; no vertical rules or shading)", "Included", f"Tables_{JOURNAL_ABBR}_editable.docx"],
        ["Reporting guideline (PRISMA-ScR)", "Included", "Reporting_Guideline_PRISMA-ScR.docx"],
        ["Citation audit (numbered, order of first appearance)", "Included", "Citation_Audit.csv"],
        ["Reference verification", "Included", "Reference_Verification.csv"],
        [f"Main-text word count (excl. title, abstract, references): {validation['word_count']}",
         "Reported", f"Title_Page_{JOURNAL_ABBR}.docx"],
        ["CRediT authorship contribution statement", "Included (withheld while blinded)", "Manuscript"],
        ["Declaration of generative AI in the writing process", "Included", "Manuscript"],
        ["Funding statement", "Included", "Manuscript"],
        ["Declaration of competing interest", "Included", "Manuscript"],
        ["Data availability statement", "Included", "Manuscript"],
    ]
    add_table(doc, {"title": "Items included in the submission package",
                    "headers": ["Item", "Status", "File"], "rows": rows},
              lambda x: x)
    path = OUTPUT / f"Submission_Checklist_{JOURNAL_ABBR}.docx"
    doc.save(path)
    return path


def build_zip(figpaths) -> Path:
    path = OUTPUT / f"{JOURNAL_ABBR}_submission_package.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(OUTPUT.rglob("*")):
            if item.is_file() and item != path:
                zf.write(item, item.relative_to(OUTPUT))
    return path


def main() -> None:
    reset_dirs()
    FIGDIR.mkdir(parents=True, exist_ok=True)
    figpaths = build_figures()
    blocks = body_blocks()
    order, ref_list, repl = resolve_citations(blocks, TABLES)
    # Persist the manuscript numbering so the public reproduce.py renders the
    # same reference numbers in the standalone editable tables.
    CITATION_ORDER_FILE.write_text(json.dumps(order, indent=2) + "\n",
                                   encoding="utf-8")
    validation = validate(blocks, TABLES, order, ref_list, repl)

    build_manuscript(blocks, TABLES, figpaths, repl, ref_list)
    wc = validation["word_count"]
    build_title_page(wc, len(ref_list))
    build_cover_letter()
    build_highlights()
    build_tables_docx(TABLES, repl)
    build_figures_pptx(figpaths, repl)
    build_reporting_guideline()
    build_reference_verification(ref_list)
    build_citation_audit(blocks, TABLES, order, repl)
    build_checklist(validation)
    build_validation_report(validation, figpaths)
    zip_path = build_zip(figpaths)

    print("Build complete.")
    print(f"  references: {len(ref_list)} (numbered, order of first appearance)")
    print(f"  main-text words: {wc}; abstract words: {validation['abstract_words']}; "
          f"highlights: {validation['highlights']}")
    print(f"  package: {zip_path.relative_to(ROOT)}")
    for k, v in validation.items():
        if isinstance(v, bool):
            print(f"  {k}: {'OK' if v else 'FAIL'}")


if __name__ == "__main__":
    main()
