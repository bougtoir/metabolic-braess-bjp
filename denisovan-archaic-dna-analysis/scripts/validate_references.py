#!/usr/bin/env python3
"""Validate Heredity manuscript references against Crossref/PubMed."""

import csv
import re
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys_path = ROOT / "scripts"
if sys_path not in __import__("sys").path:
    __import__("sys").path.insert(0, str(sys_path))

from heredity_content import REFERENCE_RECORDS


OUT_PATH = ROOT / "docs" / "heredity_submission" / "reference_validation.csv"


def extract_doi(ref: str) -> str | None:
    match = re.search(r"https?://doi\.org/([^\s,;:>]+)", ref)
    if match:
        doi = urllib.parse.unquote(match.group(1))
        return doi.rstrip(".,;:")
    return None


HEADERS = {
    "User-Agent": "mailto:bougtoir@gmail.com (Reference Validation; +https://github.com/bougtoir/denisovan-archaic-dna-analysis)",
}


def get_crossref_work(doi: str) -> dict | None:
    url = f"https://api.crossref.org/works/{doi}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.json().get("message")
    except Exception:
        return None


def search_crossref_title(title: str) -> dict | None:
    url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 1}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])
        return items[0] if items else None
    except Exception:
        return None


def get_pubmed_record(title: str, year: int, surname: str = "") -> dict | None:
    """Search PubMed by title, year, and first-author surname."""
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    # PubMed exact title search is brittle; combine author and a few content words.
    stop_words = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for"}
    content = [w for w in title.split() if len(w) > 3 and w.lower() not in stop_words][:4]
    keywords = " AND ".join(content) if content else ""
    if surname:
        if keywords:
            term = f"{surname}[Author] AND {year}[PDAT] AND ({keywords})"
        else:
            term = f"{surname}[Author] AND {year}[PDAT]"
    else:
        term = f'"{title}"[Title] AND {year}[PDAT]'
    try:
        search_resp = requests.get(
            search_url,
            params={"db": "pubmed", "term": term, "retmax": 5, "retmode": "json"},
            timeout=20,
        )
        search_resp.raise_for_status()
        ids = search_resp.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_resp = requests.get(
            summary_url,
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            timeout=20,
        )
        summary_resp.raise_for_status()
        records = summary_resp.json().get("result", {})
        for pmid in ids:
            rec = records.get(pmid, {})
            pubdate = rec.get("pubdate", "")
            rec_year = int(pubdate.split()[0]) if pubdate and pubdate[:4].isdigit() else 0
            if str(year) in str(rec_year):
                return rec
        return None
    except Exception:
        return None


def normalize_name(name: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").lower().strip(".,;:")


def parse_key_parts(key: str) -> tuple[str, int]:
    """Extract first-author string and year from citation key."""
    year_match = re.search(r"\b((?:19|20)\d{2})\b", key)
    if not year_match:
        return "", 0
    year = int(year_match.group(1))
    before_year = key[: year_match.start()].strip()
    before_year = re.sub(r"\s*et\s+al\.?\s*$", "", before_year, flags=re.I)
    first_author = before_year.strip()
    return normalize_name(first_author), year


def validate_record(key: str, ref: str) -> dict:
    doi = extract_doi(ref)
    surname, year = parse_key_parts(key)
    result = {
        "key": key,
        "doi": doi or "",
        "status": "unverified",
        "crossref_year": "",
        "crossref_first_author": "",
        "crossref_title": "",
        "note": "",
    }

    if doi:
        work = get_crossref_work(doi)
        if not work:
            result["status"] = "failed"
            result["note"] = "Crossref DOI lookup failed"
            return result
        pub_year = work.get("published-print", {}).get("date-parts", [[0]])[0][0]
        if not pub_year:
            pub_year = work.get("published-online", {}).get("date-parts", [[0]])[0][0]
        authors = work.get("author", [])
        first = authors[0].get("family", "").lower() if authors else ""
        result["crossref_year"] = str(pub_year)
        result["crossref_first_author"] = first
        result["crossref_title"] = work.get("title", [""])[0]

        if str(year) != str(pub_year):
            result["status"] = "failed"
            result["note"] = f"year mismatch: expected {year}, got {pub_year}"
            return result
        first_norm = normalize_name(first)
        if not (surname in first_norm or first_norm in surname or surname.split()[0] == first_norm):
            result["status"] = "failed"
            result["note"] = f"author mismatch: expected {surname}, got {first}"
            return result
        result["status"] = "ok"
        result["note"] = "verified by DOI"
    else:
        # Fallback for references without a DOI: extract title, check Crossref, then PubMed
        bits = ref.split(".")
        candidate = bits[2].strip() if len(bits) > 2 else ref
        work = search_crossref_title(candidate[:120])
        verified_by_crossref = False
        if work:
            pub_year = work.get("published-print", {}).get("date-parts", [[0]])[0][0]
            if not pub_year:
                pub_year = work.get("published-online", {}).get("date-parts", [[0]])[0][0]
            authors = work.get("author", [])
            first = authors[0].get("family", "").lower() if authors else ""
            result["crossref_year"] = str(pub_year)
            result["crossref_first_author"] = first
            result["crossref_title"] = work.get("title", [""])[0]
            first_norm = normalize_name(first)
            if str(year) == str(pub_year) and (surname in first_norm or first_norm in surname or surname.split()[0] == first_norm):
                result["status"] = "ok"
                result["note"] = "verified by title search"
                verified_by_crossref = True
        if not verified_by_crossref:
            # PubMed fallback (needed for older articles not indexed in Crossref)
            pm_rec = get_pubmed_record(candidate[:120], year, surname)
            if pm_rec:
                result["crossref_year"] = pm_rec.get("pubdate", "")
                result["crossref_first_author"] = pm_rec.get("sortfirstauthor", "")
                result["crossref_title"] = pm_rec.get("title", "")
                pm_author = normalize_name(pm_rec.get("sortfirstauthor", ""))
                if str(year) in result["crossref_year"] and (surname in pm_author or pm_author in surname or surname.split()[0] == pm_author):
                    result["status"] = "ok"
                    result["note"] = "verified by PubMed"
                else:
                    result["status"] = "failed"
                    result["note"] = "PubMed record found but author/year mismatch"
            else:
                result["status"] = "failed"
                result["note"] = "no DOI and no matching Crossref/PubMed record"
    return result


def main():
    rows = []
    for key, ref in REFERENCE_RECORDS:
        rows.append(validate_record(key, ref))
        time.sleep(0.25)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "key",
                "doi",
                "status",
                "crossref_year",
                "crossref_first_author",
                "crossref_title",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    ok = sum(1 for r in rows if r["status"] == "ok")
    print(f"Reference validation: {ok}/{len(rows)} verified")
    for r in rows:
        if r["status"] != "ok":
            print(f"  {r['key']}: {r['note']}")


if __name__ == "__main__":
    main()
