"""Fetch the Dryad dataset for the capelin-seabird positive control.

Dataset: Davoren et al. 2024, "Aggregative responses of marine predators to a
pulsed resource", Journal of Animal Ecology (doi:10.1111/1365-2656.14214).
Data DOI: https://doi.org/10.5061/dryad.jq2bvq8k8 (CC0 public domain).

NOTE: Dryad file downloads are protected by an Anubis proof-of-work check.
This script first tries plain HTTPS; if that fails (403/HTML response),
download manually through a browser:

  https://datadryad.org/dataset/doi:10.5061/dryad.jq2bvq8k8
  -> click "Davoren_et_al._2024_DRYAD.xlsx"

and place it at data/raw/dryad/Davoren_et_al._2024_DRYAD.xlsx.
The expected SHA-256 is checked by scripts/01_load.py regardless of how the
file arrived.
"""
import hashlib
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
DEST = os.path.join(ROOT, "data/raw/dryad/Davoren_et_al._2024_DRYAD.xlsx")
SHA = "0063605dc827a77c1ac2738941b6199fac811fb1d207a9d6505e8778b0f24236"
URL = "https://datadryad.org/downloads/file_stream/3594361"

os.makedirs(os.path.dirname(DEST), exist_ok=True)
if os.path.exists(DEST) and hashlib.sha256(open(DEST, "rb").read()).hexdigest() == SHA:
    print("already present and verified")
    sys.exit(0)
subprocess.run(["curl", "-sfL", "-A", "Mozilla/5.0", "-o", DEST, URL])
if os.path.exists(DEST) and \
        hashlib.sha256(open(DEST, "rb").read()).hexdigest() == SHA:
    print("downloaded and verified")
else:
    print(__doc__)
    sys.exit(1)
