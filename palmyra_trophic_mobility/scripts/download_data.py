"""Download the Palmyra Bluewater telemetry dataset from DataONE (member node:
Research Workspace) and verify MD5 checksums.

Dataset: Palmyra Bluewater Research Marine Animal Telemetry Dataset, 2022-2023
DOI: https://doi.org/10.24431/rw1k8ez  (license: US public domain)

Usage: python3 scripts/download_data.py
Files land in data/raw/palmyra_bluewater/ alongside metadata/dataone_manifest.json.
"""
import hashlib
import json
import os
import subprocess
import sys
import zipfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "data/raw/palmyra_bluewater")
EXT = os.path.join(ROOT, "data/raw/extracted")
BASE = "https://dataone.researchworkspace.com/mn/v2/object"

os.makedirs(OUT, exist_ok=True)
os.makedirs(EXT, exist_ok=True)
manifest = json.load(open(os.path.join(ROOT, "metadata/dataone_manifest.json")))
fail = []
for m in manifest:
    pid, fn = m["pid"], m.get("fileName", pid)
    dest = os.path.join(OUT, fn)
    if not (os.path.exists(dest) and
            hashlib.md5(open(dest, "rb").read()).hexdigest() == m["checksum"]):
        print("downloading", fn, flush=True)
        subprocess.run(["curl", "-sfL", "--retry", "5", "--retry-delay", "10",
                        "-o", dest, f"{BASE}/{pid}"], check=True)
    ok = hashlib.md5(open(dest, "rb").read()).hexdigest() == m["checksum"]
    if not ok:
        fail.append(fn)
        continue
    # extract zip archives to data/raw/extracted/<archive-stem>/ so that
    # 01_ingest_tracks.py finds one directory per deployment
    if zipfile.is_zipfile(dest):
        target = os.path.join(EXT, os.path.splitext(fn)[0])
        if not os.path.isdir(target):
            with zipfile.ZipFile(dest) as z:
                z.extractall(target)
print("done.", len(manifest) - len(fail), "ok;", len(fail), "failed:", fail)
sys.exit(1 if fail else 0)
