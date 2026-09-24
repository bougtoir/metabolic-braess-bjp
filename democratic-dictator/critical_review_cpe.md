# Pre-Submission Critical Review: Constitutional Political Economy

Target: *Constitutional Political Economy* (CPE)
Manuscript: "Democracy as Control over Delegated Authority: Periodic Constitutional Dictatorship as a Limiting-Case Thought Experiment"

## Final assessment

The manuscript has been retargeted from *Perspectives on Politics* to *Constitutional Political Economy* and now meets the formal CPE submission requirements:

- Language: English.
- Citation style: author-date (name and year in parentheses).
- Reference list: alphabetical, CPE/APA-like, with journal and book titles italicized and DOIs included where available; 34 references, all cited in the body.
- Main-body prose: ~9,050 words (excluding references, equations, figure captions, and dividers). CPE has no hard main-body ceiling for an original article.
- Abstract: 173 words (within the CPE 150–250 word range).
- Keywords: 6 (within the CPE 4–6 keyword range).
- JEL Classification: D71, D72, H11, K10, P16.
- Title page included: title, author placeholders, corresponding author placeholder, Acknowledgments, Statements and Declarations (competing interests, funding, ethics approval, consent to participate, consent for publication, author contributions), Data Availability, and AI/LLM statement.
- Decimal headings are used and do not exceed three levels.
- Figures: two in-text citations each, with working DOCX containing inline figures and submission DOCX containing figure legends at the end; separate PNG files and an editable PPTX are provided.
- Normative framing: PCD is consistently presented as a thought experiment / stress test, not a policy proposal.
- Data/Code Availability statement included; simulation protocol is in `simulation_en.py` and supplementary notes are in `supplementary_materials_en.md`.

---

## Reviewer-perspective findings and implemented fixes

### 1. Journal retargeting: PoP → CPE

**Issue:** The previous package was formatted for *Perspectives on Politics* (Vancouver numbered citations, no JEL codes, PoP-style word framing).

**Fix:** Converted the entire manuscript to CPE style: author-date citations, alphabetical reference list, italicized journal/book titles, 4–6 keywords, JEL codes, and the CPE-required title-page sections.

### 2. Control-rights theory as the first contribution

**Issue:** PCD was introduced before the theoretical architecture was established.

**Fix:** The first contribution is now a control-rights conception of democracy (Θ = (θs, θc, θd, θe, θr)). Sections 1–2 review minimalist, polyarchy, liberal/constitutional, participatory/deliberative, principal-agent/representation, and democratic-backsliding literatures and show how the Θ vector unifies them.

### 3. Object-level vs. meta-level distinction

**Issue:** The distinction was implicit rather than receiving independent theoretical treatment.

**Fix:** Elevated the distinction to its own Section 3, with examples from corporate law, administrative law, federalism, and emergency powers. Clarified that object-level authority can be concentrated without ceasing to be democratically controlled, provided meta-level rights are retained.

### 4. PCD as a limiting-case thought experiment

**Issue:** PCD risked being read as a policy proposal.

**Fix:** Section 4 introduces PCD only as a stress test for the control-rights framework. The abstract, introduction, and conclusion all state that PCD is offered as a thought experiment, not a policy recommendation.

### 5. Social-choice motivation (Arrow/Gibbard-Satterthwaite)

**Issue:** The prior claim that "formal dictator is unavoidable" overstates the social-choice results and invites attacks.

**Fix:** Rewrote Section 5 so Arrow and Gibbard-Satterthwaite motivate the delegation/aggregation dilemma rather than prove political dictatorship. The claim is now: perfect aggregation is impossible, delegation is unavoidable, and PCD asks how delegation can be controlled.

### 6. WWII as heuristic, not causal claim

**Issue:** The WWII synchronization was presented as a strong historical interpretation, risking the paper's theoretical credibility.

**Fix:** Retained the case as a heuristic analogy and added explicit language that "synchronization provides a lens for understanding how democratic breakdowns can cascade, not a full account of why the Second World War occurred."

### 7. Figure 2 as intertemporal accountability mechanism

**Issue:** The simulation was framed as a PCD simulation rather than a general mechanism.

**Fix:** Relabeled the model as an "intertemporal accountability game" and the y-axis as "public-will alignment." Section 7 now sells the result as evidence that a rare, high-value selection event can lengthen the shadow of the future, of which PCD is one implementation.

### 8. Reference formatting

**Issue:** CPE requires author-date citations and an alphabetized reference list with italicized journal/book titles.

**Fix:** Rebuilt the reference list in alphabetical order with CPE-style entries and replaced all bracketed Vancouver citations with sorted author-date citations.

### 9. Reproducibility and hard-coded numbers

**Issue:** Simulation numbers must be derived from code, not hand-typed.

**Fix:** Reran `simulation_en.py` (seed 42) and verified that the manuscript's illustrative statistics—final public-will alignment mean 0.014 (λ=0) and 0.917 (λ=3); P(final>0.8)=0.82 for λ=3—match `simulation_summary_en.txt`. The PPTX generator now reads these values directly from the summary.

### 10. Submission package

**Issue:** CPE and many journals prefer figures as separate files and figure legends at the end of the manuscript.

**Fix:** Produced a working DOCX with inline figures, a submission DOCX and `.txt` with a "Figure Legends" section and no inline images, an editable `figures_en.pptx`, and separate PNG/TIFF files under `figures_en_submission/`.

---

## 1. 原稿（マクロ）

### Strengths
- The paper leads with control rights and object/meta theory, fitting CPE's focus on institutional design, constitutional political economy, and the rules of the political game.
- The Θ vector gives a portable vocabulary for comparing minimalist, polyarchy, liberal, participatory, principal-agent, and backsliding accounts.
- The intertemporal-accountability simulation is presented as a general mechanism, making Figure 2 independently evaluable even by skeptics of PCD.
- Historical and comparative cases (Rome, Polish-Lithuanian Commonwealth, Weimar, post-war Germany, Britain, Japan) provide concrete anchors without overclaiming.

### Priority issues for CPE

#### 1.1 Theoretical fit
- CPE readers will appreciate the formalization of control rights and the constitutional-cycle model. The connection between delegation, social-choice impossibility, and institutional design is well aligned with the journal.
- **Status:** addressed.

#### 1.2 Formal density
- Equations and the agent-based model remain, but each is introduced with plain-language intuition. Full parameter discussion is in `supplementary_materials_en.md`.
- **Status:** addressed.

#### 1.3 Normative clarity
- The thought-experiment framing is explicit in the abstract, introduction, Section 4, and conclusion.
- **Status:** addressed.

#### 1.4 Empirical illustration
- Cases are integrated throughout and tied to the control-rights framework.
- **Status:** addressed.

---

## 2. 統計設計 / モデル

- The simulation uses illustrative parameters, not empirical estimates, and the manuscript is explicit about this.
- The Moran/Fermi process and parameter values are summarized in the main text; the full protocol and robustness checks are in `supplementary_materials_en.md`.
- **Status:** addressed.

---

## 3. 図表

- Figure 1 shows the unimodality of L(T) and the asymmetric slope around T*.
- Figure 2 uses English labels, a log axis, individual trajectories, a percentile band, and final-distribution insets, and is framed as an intertemporal accountability mechanism rather than a PCD simulation.
- **Status:** addressed; separate `figures_en_submission/` files provided, plus `figures_en.pptx`.

---

## 4. 再現性

- `simulation_en.py`, `make_docx_en.py`, `make_docx_en_submission.py`, `gen_submission_txt.py`, and `make_figures_pptx_en.py` can reproduce all figures and the final docx from the plain-text source.
- `README.md` and `supplementary_materials_en.md` contain reproduction instructions.
- **Status:** addressed; source files are in `/home/ubuntu/repos/wip/democratic-dictator/` and the `bougtoir/wip` sync workflow is configured.

---

## 5. 主張の強さ

- Central claim is framed as a thought experiment / analytical device, not as an empirical finding or policy recommendation.
- The WWII counterfactual is explicitly treated as an analogy, not a test.
- Arrow/Gibbard-Satterthwaite are presented as motivation for the delegation problem, not as proof of dictatorship.

---

## 6. 優先度まとめ

### 最優先（投稿前に必須）— all addressed
1. Convert citations and references to CPE author-date style.
2. Add CPE title page, JEL codes, and 4–6 keywords.
3. Reorder contributions: control-rights theory → object/meta distinction → PCD as stress test.
4. Clarify normative framing (thought experiment, not proposal).

### 高優先— addressed
5. Weaken Arrow/WWII claims to heuristic/motivational roles.
6. Present Figure 2 as an intertemporal accountability mechanism.
7. Produce separate submission figures and figure legends.

### 中優先— addressed
8. Expand theoretical sections to strengthen journal fit.
9. Add a supplementary-materials file with parameters and robustness notes.

### 残作業（ユーザー対応が必要）
10. Fill in author names, affiliations, and corresponding author email on the title page.
11. Verify that `bougtoir/democratic-dictator` has been created and populated by the `sync-to-repos` workflow; if it has not appeared after the next scheduled run, manually trigger the workflow from the Actions tab of `bougtoir/wip`.

## CPE-fit revisions applied (final pass)

- Subtitle changed to "Constitutional Design under Periodic Delegation"; central claim restated as "constitutional design determines how citizens allocate and retain control rights over delegated political authority".
- Constitutional-choice literature added and tied to the object/meta distinction: Buchanan and Tullock (1962), Buchanan (1975), Brennan and Buchanan (1985), V. Ostrom (1987), E. Ostrom (1990), Voigt (2011), Lewis and Meadowcroft (2024), Grajzl et al. (2025), Kantorowicz and Voigt (2025). All DOIs verified via Crossref.
- Section 6 reframed as a rule-selection problem, min_T L(T), over two institutional failure risks; Section 7 retitled "Intertemporal Constitutional Incentives".
- Abstract 173 words; body ~8,500 words; 34 references, all cited, alphabetical; no non-ASCII characters in any text file; equations are Word OMML.
