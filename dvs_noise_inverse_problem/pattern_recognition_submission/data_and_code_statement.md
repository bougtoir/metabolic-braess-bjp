# Data and code statement

## Data sources (all public; no data were created or modified)

* **EBSSA** (Afshar et al., 2020): labelled split, 43 recordings from a 180 x 240 and a 240 x 304-pixel sensor. Accessed through `tonic.datasets.EBSSA` (Tonic 1.6.0), which downloads `labelled_ebssa.h5` from the authors' Google Drive release. Ground truth: published object annotations (10 x 10-pixel box, 10 ms). The Drive file is subject to Google download quotas; the same file is served by the authors' institutional mirror as `https://rds.westernsydney.edu.au/Centres/ICNS/Afshar_EBSSA/Labelled%20Data/HDF5_Format/labelled_ebssa-008.h5` (12,106,528,328 bytes, SHA-256 `50a540354af30fdaf208970e9b50bc05b2b301d4491764bb7eeb20d685532cb0`, constants `EBSSA_H5_*` in `sp_evaluation.py`); save it as `data/EBSSA/labelled_ebssa.h5` and Tonic uses it without downloading.
* **DND21** (Guo and Delbruck, 2022): public AEDAT-2.0 recordings from the DND21 Drive folder (ids listed in `dnd21_evaluation.py:FILES`), DAVIS346 (346 x 260 px). Mixtures are constructed by `dnd21_evaluation.build_recordings()` from a signal recording and a *distinct* slice of a measured noise recording; labels are the exact origin of each event. These are synthetic combinations of two real recordings and are described as such in the manuscript.

## Result files (inputs of every number in the manuscript)

Status is read from `results/build_provenance.json`, written by `build_pr_submission.py`: *re-run in this build* = the producing analysis script was executed in the build that wrote this statement; *derived in this build* = recomputed from the tracked result files; *tracked output* = shipped as committed and checked by checksum only. Every file is produced by the released code; the clean-clone scope of each analysis is stated under "Data access".

* `results/sp_evaluation_summary.json` (tracked output (not re-derived in this build)) sha256 = `4f839ff6d1c2016c71069c1610360adabe5899257a5f6cd2f98b5cc97911859c`
* `results/sp_per_recording.json` (tracked output (not re-derived in this build)) sha256 = `5cbe231317af7b6058315706b8b999bc573a838fa65047eb4b54011ec51fdcbe`
* `results/sparsity_cost.json` (tracked output (not re-derived in this build)) sha256 = `cfded7c002ca6fd23877a385351a934c7a202beb120390525862ed6abb695484`
* `results/partial_auc.json` (tracked output (not re-derived in this build)) sha256 = `e8bf4f53ac1cc9ebb558d3a12d5552303246db9742f90e3f16a9a8caaf100222`
* `results/self_calibration.json` (tracked output (not re-derived in this build)) sha256 = `e0459477ed5dfa5fd1b2fb5b689ec8060b9b1fd4c3442fea8baadc96e225192b`
* `results/zero_knowledge.json` (tracked output (not re-derived in this build)) sha256 = `74003aa3b210a9a4c85e49f6948938c4242dc51b609c0ddb9c3534fc340c3a46`
* `results/hybrid_screening.json` (tracked output (not re-derived in this build)) sha256 = `e3125ef51a03cbebf033cb636f411646729ec342525462a5906f5d660a924545`
* `results/qualitative_example.json` (tracked output (not re-derived in this build)) sha256 = `d883ead11e317ca5b64890965443f49a580a134ce13d62c0713f1a98d0514b54`
* `results/dnd21_evaluation_summary.json` (tracked output (not re-derived in this build)) sha256 = `8048d536185a64ce4229a216fb65ce7208870f40ea01e15c7b86e6034649250f`
* `results/dnd21_per_recording.json` (tracked output (not re-derived in this build)) sha256 = `020dcc4b2e23759aef717f0a3d93365a2b86b6ab77dc7998b77bb5541bdcea15`
* `results/comparator_feasibility.json` (tracked output (not re-derived in this build)) sha256 = `f6a2c1fd5b2fc45d452b1cb9ecb56335f9ff95d690b33dfc8bc94a016ad1b620`
* `results/pr_effect_sizes.json` (derived in this build from the tracked result files) sha256 = `f9273986f6045861f9d8652a66d993db60e8509b887617486dff6653086949bb`
* `results/aednet_transfer.json` (tracked output (not re-derived in this build)) sha256 = `c3bff81addbd34cbbc308a29668d31beff8695e5a2cd7ceeb73c4d7337bcec60`

## Code

* `event_driven.py` proposed detector; `sp_evaluation.py` EBSSA framework and comparators; `dnd21_evaluation.py` DND21 protocol; `aedat2.py` AEDAT-2.0 reader; `comparator_feasibility.py` Supplementary Table S1 metadata; `pr_effect_sizes.py` effect sizes, bootstrap CIs and the DND21 segment/source-level sensitivity analysis (results/pr_effect_sizes.json); `aednet_transfer.py` zero-shot CPU transfer of the released AEDNet weights to EBSSA and DND21 (clones github.com/Fanghuachen/AEDNet at a pinned commit, downloads the release weights and checks their SHA-256, checks parity with the official loader/model on the released sample, then scores every EBSSA recording and DND21 mixture; results/aednet_transfer.json).
* `pattern_recognition_submission/` manuscript, figure and supporting-file generators (`make_pr_figures.py`, `create_pr_docx.py`, `create_pr_supporting.py`; driven by `../build_pr_submission.py`).

## Data access

* The EBSSA Google Drive file that Tonic downloads is subject to Google download quotas ("Too many users have viewed or downloaded this file recently" was returned during this revision); the institutional mirror above serves the same file and its SHA-256 is recorded in `sp_evaluation.py`. The EBSSA result files in `results/` (hybrid_screening.json, partial_auc.json, qualitative_example.json, self_calibration.json, sp_evaluation_summary.json, sp_per_recording.json, sparsity_cost.json, zero_knowledge.json) are shipped with their checksums; whether they were re-derived in the build that wrote this statement is given by their status above. The tracked `sp_evaluation_summary.json` and `sp_per_recording.json` were written by `sp_evaluation.py` run on the mirror file (SHA-256 above); every metric matched the earlier Drive-sourced run to floating-point precision, only wall-clock timings differed. The DND21 analysis downloads its public AEDAT files directly and re-runs end-to-end with `--full`.

## Public mirror

* The manuscript names `https://github.com/bougtoir/dvs-noise-inverse-pattern-recognition` as the release repository. It is populated by the `sync-to-repos` workflow of the development repository; the clean-clone check in REPRODUCIBILITY.md must be repeated on that mirror before submission (see reviewer_report.md, item R1).
