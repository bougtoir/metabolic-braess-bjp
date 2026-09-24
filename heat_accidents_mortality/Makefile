PY = python3
S  = scripts

.PHONY: all us japan figures clean data_us data_jp manuscript test aap ehp ehp_bw

all: us japan figures

## --- data building (downloads public sources into data/raw) ---
data_us:
	$(PY) $(S)/build_fars.py
	$(PY) $(S)/build_fars_strata.py
	$(PY) $(S)/build_temperature.py
	$(PY) $(S)/build_humidity.py
	$(PY) $(S)/build_controls.py
	$(PY) $(S)/build_state_controls.py
	$(PY) $(S)/build_cdc_heat.py

data_jp:
	$(PY) $(S)/build_japan.py

## --- analysis ---
us: data_us
	$(PY) $(S)/analyze_us.py
	$(PY) $(S)/analyze_us_strata.py

japan: data_jp
	$(PY) $(S)/analyze_japan.py

## --- figures + manuscript ---
figures:
	$(PY) $(S)/figures_us.py
	$(PY) $(S)/figures_japan.py

manuscript:
	$(PY) $(S)/make_manuscript.py

aap: manuscript
	$(PY) $(S)/make_aap_submission.py

ehp: manuscript
	$(PY) $(S)/make_ehp_submission.py

figures_bw:
	FIGURES_BW=1 $(PY) $(S)/figures_us.py
	FIGURES_BW=1 $(PY) $(S)/figures_japan.py

manuscript_bw: figures_bw
	FIGURES_BW=1 FIGURES_DIR=output/figures_bw MANUSCRIPT_DIR=output/manuscript_bw $(PY) $(S)/make_manuscript.py

ehp_bw: manuscript_bw
	FIGURES_BW=1 $(PY) $(S)/make_ehp_submission.py

test:
	$(PY) -m pytest -q tests

clean:
	rm -f data/processed/*.csv output/*.txt output/figures/*
