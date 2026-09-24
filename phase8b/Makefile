.PHONY: all foss bbs elk wolf neon sim figs report
all: foss bbs elk wolf neon sim figs report
foss:    ; python3 src/download_foss.py && python3 src/foss_analysis.py
bbs:     ; python3 src/bbs_parse.py && python3 src/bbs_analysis.py
elk:     ; python3 src/elk_analysis.py
wolf:    ; python3 src/gps_analysis.py wolf
neon:    ; python3 src/download_neon.py && python3 src/neon_analysis.py
sim:     ; python3 src/sim_fp.py
figs:    ; python3 src/figures.py
report:  ; python3 src/report8b.py
