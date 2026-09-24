import sys; sys.path.insert(0, 'src')
from utils import load_config, load_model, sha256
from model_qc import run_qc
import os
cfg = load_config()
for key in ("human2", "recon3d"):
    model, spec = load_model(key, cfg)
    spec = dict(spec); spec["sha256"] = sha256(spec["file"])
    summ = run_qc(model, spec, f"results/qc/{key}")
    print(key, summ)
