"""Verify references in manuscript_en.md by DOI or Crossref title search."""
from __future__ import annotations
import re, json, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ref_section = Path(ROOT / "manuscript" / "manuscript_en.md").read_text().split("## References")[-1]

citations = [m.group(0).strip() for m in re.finditer(r"(?m)^[A-Z][A-Za-z\-]+, .*?(?=\n(?=[A-Z][A-Za-z\-]+, )|\Z)", ref_section, re.DOTALL)]
print(f"Found {len(citations)} references")

HEADERS = {"User-Agent": "Devin/1.0 (mailto:devin@cognition.ai)"}

def check(citation: str):
    doi_match = re.search(r"https?://doi\.org/([^\s]+)", citation)
    if doi_match:
        doi = doi_match.group(1)
        # Crossref work endpoint
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto=devin@cognition.ai"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
                title = data.get("message", {}).get("title", [""])[0]
                return ("doi", doi, "ok", title[:80])
        except Exception as e:
            return ("doi", doi, str(e), None)
    # No DOI: try title search
    title_match = re.search(r"\(\d{4}\)\.?\s+(.*?)(?:\.\s*\*|\. In |\.$)", citation, re.DOTALL)
    if not title_match:
        return ("title", None, "could not parse title", None)
    title = title_match.group(1).replace("\n", " ").strip().strip("*")
    q = urllib.parse.quote(title)
    url = f"https://api.crossref.org/works?query.title={q}&rows=3&mailto=devin@cognition.ai"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            items = data.get("message", {}).get("items", [])
            if items:
                first = items[0]
                score = first.get("score", 0)
                found_title = first.get("title", [""])[0]
                return ("title", title, found_title, score)
            return ("title", title, "no items", None)
    except Exception as e:
        return ("title", title, str(e), None)

failures = []
for c in citations:
    first_author = c.split(",")[0]
    kind, key, detail, extra = check(c)
    status = "ok" if (kind == "doi" and detail == "ok") or (kind == "title" and isinstance(extra, float) and extra > 25) else "verify"
    if status != "ok":
        failures.append((first_author, kind, key, detail, extra))
    print(f"{first_author}: {kind} {key[:60] if key else ''} -> {status} ({detail}) {extra}")
    time.sleep(0.25)

print(f"\nFailures / needs verification: {len(failures)}")
for f in failures:
    print(f)
