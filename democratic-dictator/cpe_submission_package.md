# Constitutional Political Economy Submission Package

Target journal: **Constitutional Political Economy** (Springer)  
Article type: **Original Paper**

---

## 1. Title

**Democracy as Control over Delegated Authority: Constitutional Design under Periodic Delegation**

---

## 2. Abstract (173 words)

This article treats constitutional design as the choice of how citizens allocate and retain control rights over delegated political authority. It develops a control-rights conception of democracy in which popular sovereignty consists of control over the source, scope, duration, termination, and residual allocation of authority, and it distinguishes object-level choices within rules from meta-level choices over rules, in the tradition of constitutional political economy. Periodic Constitutional Dictatorship (PCD), a scheduled and bounded concentration of object-level authority, is then used as a limiting-case thought experiment to ask how far delegation can be pushed before meta-level democratic control fails. Drawing on social-choice theory, a competing-hazards model, and an agent-based model of intertemporal accountability, the argument shows why delegation is unavoidable, how the choice of a constitutional cycle minimizes the expected loss from institutional sclerosis and abuse of power, and how a rare high-value trust election can lengthen the shadow of the future. The framework offers a common vocabulary for analyzing executive aggrandizement, constitutional compliance, and democratic backsliding as changes in the allocation of control rights.

---

## 3. Keywords

constitutional political economy, control rights, delegation, constitutional choice, accountability, periodic constitutional dictatorship

---

## 4. JEL Classification

D71, D72, H11, K10, P16

---

## 5. Manuscript details

- Main-body prose: ~9,050 words (excluding abstract, references, equations, figure captions, and appendices)
- Total word count: ~9,900 words (including references and captions)
- Abstract: 173 words
- Figures: 2 (separate PNG/TIFF files provided; captions placed at end of submission manuscript)
- Tables: 0
- Citations: author-date (name and year in parentheses)
- References: 34 (alphabetical, CPE/APA-like, italicized journal/book titles, DOIs where available)
- Article type: Original Paper
- Supplementary materials: `supplementary_materials_en.md` (simulation protocol and robustness notes)

---

## 6. Author Biography (placeholder; <=100 words)

Tatsuki Onishi is [affiliation/position]. His research examines the institutional foundations of democratic control, the political economy of constitutional design, and the relationship between elections and popular sovereignty.

*(Please replace bracketed information before submission.)*

---

## 7. Fit Statement for Constitutional Political Economy

*Constitutional Political Economy* publishes research at the intersection of economics, political science, and law that examines the design, evolution, and consequences of political constitutions and institutional rules. This manuscript fits that mission by reframing democracy as a problem of control rights over delegated authority. It draws on social-choice theory, principal-agent theory, and a competing-hazards model to ask how concentrated object-level power can be made compatible with meta-level democratic control. The analysis is neither a pure formal exercise nor a policy proposal; it is a constitutional thought experiment designed to clarify the institutional conditions under which temporary delegation strengthens rather than erodes popular sovereignty. By connecting abstract control-rights theory to concrete institutional mechanisms--federalism, judicial review, sunset clauses, and trust elections--the article speaks directly to CPE's interest in the design of rules that constrain and channel political authority.

---

## 8. Cover Letter (template)

Dear Editors,

We are pleased to submit our manuscript, **"Democracy as Control over Delegated Authority: Constitutional Design under Periodic Delegation,"** for consideration as an Original Paper in *Constitutional Political Economy*.

The article addresses a question central to constitutional political economy: how can a democratic polity retain popular sovereignty while delegating concentrated, object-level authority to agents who must act decisively in complex societies? We argue that democracy is better understood as popular control over the *source, scope, duration, termination, and residual authority* of political power than as the mere presence of competitive elections. We introduce a distinction between object-level policy decisions and meta-level rules about who may decide, and we use Periodic Constitutional Dictatorship as a limiting-case thought experiment to test whether temporary concentration of object-level authority can coexist with long-run democratic control. The article builds on the constitutional-choice tradition of Buchanan, Tullock, Brennan, and Vincent Ostrom, treating the object-level/meta-level distinction as the democratic counterpart of choices within rules versus choices over rules, and it engages recent work in this journal on constitutional compliance and federalism. The argument draws on Arrow's impossibility theorem and the Gibbard-Satterthwaite theorem only as motivation for the delegation problem, not as proof of political dictatorship, and it presents a competing-hazards model and an agent-based model of intertemporal accountability as illustrative formalizations rather than empirical calibrations.

We believe the manuscript fits *Constitutional Political Economy*'s scope because it connects formal institutional analysis to the normative design of democratic rules. The article is original, not under review elsewhere, and all authors have approved the submission.

Sincerely,  
Tatsuki Onishi  
[Affiliation]  
[Email]

---

## 9. Files included in this package

- `paper_draft_en.txt` -- plain-text CPE manuscript with inline figure markers
- `paper_draft_en.docx` -- formatted working draft with inline figures
- `paper_draft_en_submission.txt` -- plain-text submission version with figure legends at the end
- `paper_draft_en_submission.docx` -- formatted submission manuscript (legends at end, no embedded figures)
- `simulation_en.py` -- English-labeled agent-based simulation and L(T) illustration
- `simulation_summary_en.txt` -- reproducible summary statistics
- `docx_math.py` -- shared helpers for Word OMML equations and italic formatting
- `make_docx_en.py` / `make_docx_en_submission.py` -- build the working and submission DOCX files
- `make_figures_pptx_en.py` -- build editable PowerPoint figures
- `gen_submission_txt.py` -- derive the submission text from the working text
- `supplementary_materials_en.md` -- full simulation protocol and robustness notes
- `figures_en.pptx` -- editable PowerPoint, one figure per slide
- `figures_en_submission/figure1_constitutional_cycle_loss.png/.tiff`
- `figures_en_submission/figure2_trust_election_game.png/.tiff`
- `simulation_p1_en.png` / `simulation_p2_en.png` -- generated figure images
- `cover_letter_en.docx` -- standalone cover letter for submission
- `make_cover_letter_en.py` -- cover letter DOCX generator
- `README.md` -- reproduction instructions

---

## 10. Notes on APC / Open Access

- *Constitutional Political Economy* is a hybrid journal published by Springer.
- APC (Open Choice, Gold OA): approximately **EUR 2,590** as of the 2024 Springer APC list; please confirm the current value on the journal's author instructions page.
- Institutional read-and-publish / transformative agreements may reduce or eliminate the APC.

---

## 11. Remaining pre-submission tasks

1. **Public repository:** `https://github.com/bougtoir/democratic-dictator` is live and reproduces all figures and numbers from a clean clone (`python3 simulation_en.py`).
2. Fill in author names, affiliations, and corresponding-author email on the title page.
3. Confirm the current APC and any Springer author-instructions details before submission.
4. Ensure the submission DOCX contains no author-identifying metadata beyond the title page.
