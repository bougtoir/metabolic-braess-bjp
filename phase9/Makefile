# Phase-9 pipeline (BBS hysteresis)
PY=python3
all:
	cd src && $(PY) env_fetch.py
	cd src && $(PY) species_hg.py
	cd src && $(PY) matched.py
	cd src && $(PY) anomaly.py
	cd src && $(PY) sim9.py
	cd src && $(PY) observers_mod.py
	cd src && $(PY) loyo_compare.py
	cd src && $(PY) figures9.py
	cd src && $(PY) report9.py
