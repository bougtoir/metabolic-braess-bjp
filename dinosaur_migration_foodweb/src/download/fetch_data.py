"""Download Morrison Formation datasets (Dryad + Zenodo) with provenance.

Dryad is behind an AWS WAF challenge, so plain HTTP requests are rejected
(401/403). Downloads therefore run through the session's Chrome via Playwright
CDP (http://localhost:29229). Zenodo files use plain HTTP.

Records dataset_name, source_url, doi, access_date, license,
original_filename, sha256, description into metadata/sources.csv.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
META = ROOT / "metadata"

DRYAD_DOI = "10.5061/dryad.6m905qg77"
DRYAD_PAGE = f"https://datadryad.org/dataset/doi:{DRYAD_DOI}"
DRYAD_VERSION_API = "https://datadryad.org/api/v2/versions/317696/files"
ZENODO_RECORD = "10727148"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_RECORD}"
CDP_URL = os.environ.get("CDP_URL", "http://localhost:29229")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "migration-foodweb/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def download_dryad(dest_dir: Path) -> list[str]:
    """Download all Dryad files via Chrome (WAF blocks plain HTTP)."""
    from playwright.sync_api import sync_playwright

    saved = []
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0]
        page = ctx.new_page()
        page.goto(DRYAD_PAGE, wait_until="domcontentloaded")
        time.sleep(3)
        links = page.eval_on_selector_all(
            "a[href*='file_stream']",
            "els => els.map(e => e.href)",
        )
        for href in links:
            with page.expect_download(timeout=60000) as dl_info:
                page.evaluate(f"window.location.href='{href}'")
            dl = dl_info.value
            dest = dest_dir / dl.suggested_filename
            dl.save_as(str(dest))
            saved.append(dl.suggested_filename)
            page.goto(DRYAD_PAGE, wait_until="domcontentloaded")
            time.sleep(2)
        page.close()
    return saved


def zenodo_files() -> list[tuple[str, str]]:
    with urllib.request.urlopen(ZENODO_API, timeout=60) as r:
        payload = json.load(r)
    return [(f["key"], f["links"]["self"]) for f in payload["files"]]


def main() -> None:
    (RAW / "maidment2024_dryad").mkdir(parents=True, exist_ok=True)
    (RAW / "maidment2024_zenodo_code").mkdir(parents=True, exist_ok=True)

    rows = []

    def record(dataset_name, source_url, doi, license_, filename, path, desc):
        rows.append(
            {
                "dataset_name": dataset_name,
                "source_url": source_url,
                "doi": doi,
                "access_date": date.today().isoformat(),
                "license": license_,
                "original_filename": filename,
                "local_path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "description": desc,
            }
        )
        print(f"saved {path.relative_to(ROOT)}")

    dryad_desc = (
        "Maidment et al. 2024 (J. Vertebr. Paleontol.): Morrison Formation "
        "tetrapod occurrences with systems tracts, collections, and "
        "diversity tables used for the published spatial/temporal analysis."
    )
    for name in download_dryad(RAW / "maidment2024_dryad"):
        record(
            "maidment2024_dryad",
            f"https://doi.org/{DRYAD_DOI}",
            DRYAD_DOI,
            "CC0-1.0",
            name,
            RAW / "maidment2024_dryad" / name,
            dryad_desc,
        )

    zen_desc = (
        "R scripts accompanying Maidment et al. 2024 (diversity analysis, "
        "collector curves, iNEXT rarefaction). Archived for provenance only."
    )
    for key, url in zenodo_files():
        dest = RAW / "maidment2024_zenodo_code" / key
        fetch(url, dest)
        record(
            "maidment2024_zenodo_code",
            f"https://doi.org/10.5281/zenodo.{ZENODO_RECORD}",
            f"10.5281/zenodo.{ZENODO_RECORD}",
            "MIT",
            key,
            dest,
            zen_desc,
        )

    META.mkdir(exist_ok=True)
    out_csv = META / "sources.csv"
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out_csv.relative_to(ROOT)} ({len(rows)} files)")


if __name__ == "__main__":
    sys.exit(main())
