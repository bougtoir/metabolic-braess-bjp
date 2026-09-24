.PHONY: all validate build generic cctc clinical_trials jbs clean

all: validate build

validate:
	python validation/run_validation.py

build:
	python build_paper.py

generic: build
	cp 04_paper_rsm.md 04_paper_generic.md
	cp KOTHA_Framework_RSM.docx KOTHA_Framework_generic.docx

cctc:
	python build_paper_cct.py
	python build_figures_pptx.py --md 05_paper_cctc.md --out KOTHA_Framework_CCTC_figures.pptx
	python build_tables_docx.py --src KOTHA_Framework_CCTC.docx --out KOTHA_Framework_CCTC_tables.docx
	python build_supplementary_tables_docx.py --out KOTHA_Framework_CCTC_supplementary_tables.docx
	python3 sanitize_office_outputs.py KOTHA_Framework_CCTC.docx KOTHA_Framework_CCTC_tables.docx KOTHA_Framework_CCTC_supplementary_tables.docx KOTHA_Framework_CCTC_figures.pptx KOTHA_Framework_CCTC_highlights.docx

clinical_trials:
	python build_paper_clinical_trials.py

jbs:
	python build_paper_jbs.py

clean:
	rm -f 04_paper_rsm.md KOTHA_Framework_RSM.docx
	rm -f 04_paper_generic.md KOTHA_Framework_generic.docx
	rm -f 05_paper_cctc.md KOTHA_Framework_CCTC.docx KOTHA_Framework_CCTC_tables.docx KOTHA_Framework_CCTC_figures.pptx KOTHA_Framework_CCTC_supplementary_tables.docx
	rm -f 05_paper_clinical_trials.md KOTHA_Framework_ClinicalTrials*.docx KOTHA_Framework_ClinicalTrials*.pptx cover_letter_ClinicalTrials.docx submission_package_ClinicalTrials.zip
	rm -f 05_paper_jbs.md KOTHA_Framework_JBS*.docx KOTHA_Framework_JBS*.pptx cover_letter_JBS.docx submission_package_JBS.zip
	rm -rf JBS_figures ClinicalTrials_figures validation/figures/*.png validation/results_summary.txt
	rm -f *_highlights.docx
