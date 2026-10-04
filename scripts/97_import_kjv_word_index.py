#!/usr/bin/env python3
"""97_import_kjv_word_index.py — import the EYA Censored "KJV Bible Word
Index" (https://eyacensored-oss.github.io/KJV-Word-Index/; owner request
2026-10-04) into references/eya-new-words-list/.

The site is a single static page whose data is an inline JavaScript array
`const RAW = [[word, times_in_kjv, reference, scripture], ...];` ("parsed
from your Google Sheet"). Each row is one example verse for a word the site
presents as new or multiplied in the KJV.

Stages (all idempotent):
1. CACHE — fetch the page once into references/eya-new-words-list/source.html.
   The cache is a permanent generated artifact: never deleted, never
   re-fetched if present (pass --refresh to fetch again; the new copy is
   refused if it carries fewer rows than the cached one).
2. PARSE — extract RAW from the cached page.
3. WRITE — references/eya-new-words-list/kjv_word_index.tsv (one row per verse)
   and kjv_word_index.md (grouped by word). Overwrite guard: refuses to
   replace an existing output with one containing fewer rows.

Advisory corroboration only — never a veto (Premise Revision).
"""
import json
import re
import sys
import urllib.request
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "references" / "eya-new-words-list"
CACHE = OUT_DIR / "source.html"
TSV = OUT_DIR / "kjv_word_index.tsv"
MD = OUT_DIR / "kjv_word_index.md"
URL = "https://eyacensored-oss.github.io/KJV-Word-Index/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def parse(page):
    m = re.search(r"const RAW = (\[.*?\n\]);", page, re.S)
    if not m:
        sys.exit("ERROR: `const RAW = [...]` not found — the page layout changed.")
    rows = json.loads(re.sub(r",\s*\]$", "]", m.group(1)))
    bad = [r for r in rows if len(r) != 4]
    if bad:
        sys.exit(f"ERROR: {len(bad)} rows do not have 4 columns, e.g. {bad[0]!r}")
    return rows


def updated_date(page):
    m = re.search(r"Updated ([A-Z][a-z]+ \d{1,2}, \d{4})", page)
    return m.group(1) if m else "unknown"


def count_rows(path):
    if not path.exists():
        return 0
    if path.suffix == ".tsv":
        return max(0, len(path.read_text(encoding="utf-8").splitlines()) - 1)
    return len(re.findall(r"^- \*\*", path.read_text(encoding="utf-8"), re.M))


def guarded_write(path, text, new_rows):
    old_rows = count_rows(path)
    if new_rows < old_rows:
        print(f"REFUSED: {path.relative_to(ROOT)} has {old_rows} rows; "
              f"new version has only {new_rows}. Not overwritten.")
        return
    if path.exists() and path.read_text(encoding="utf-8") == text:
        print(f"{path.relative_to(ROOT)}: already current")
        return
    path.write_text(text, encoding="utf-8")
    print(f"{path.relative_to(ROOT)}: wrote {new_rows} rows")


def clean(s):
    return " ".join(str(s).split())


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refresh = "--refresh" in sys.argv

    if CACHE.exists() and not refresh:
        page = CACHE.read_text(encoding="utf-8")
        print(f"cache: {CACHE.relative_to(ROOT)} (not re-fetched)")
    else:
        page = fetch()
        if CACHE.exists():
            old = len(parse(CACHE.read_text(encoding="utf-8")))
            if len(parse(page)) < old:
                sys.exit(f"REFUSED: fetched page has fewer rows than the cache ({old}).")
        CACHE.write_text(page, encoding="utf-8")
        print(f"cache: fetched {URL} -> {CACHE.relative_to(ROOT)}")

    rows = parse(page)
    updated = updated_date(page)
    groups = OrderedDict()
    for word, times, ref, text in rows:
        groups.setdefault((clean(word), clean(times)), []).append((clean(ref), clean(text)))

    tsv = ["word\ttimes_in_kjv\treference\tscripture"]
    tsv += ["\t".join(clean(c) for c in r) for r in rows]
    guarded_write(TSV, "\n".join(tsv) + "\n", len(rows))

    md = [
        "# KJV Bible Word Index (EYA Censored)",
        "",
        f"Imported by `scripts/97_import_kjv_word_index.py` from <{URL}> "
        f"(site \"Updated {updated}\"). Source: the page's inline `RAW` array, "
        "which the site says is parsed from its Google Sheet. The site presents "
        "these as *a sampling* of words new or multiplied in the KJV, with "
        "example verses — not every occurrence.",
        "",
        "**Evidence status:** advisory corroboration only — never a veto "
        "(Premise Revision). The scripture text and the \"Times in KJV\" "
        "counts are the site's, reproduced as published.",
        "",
        f"**{len(groups)} word entries, {len(rows)} verse rows.** "
        "Machine-readable copy: `kjv_word_index.tsv`.",
        "",
    ]
    letter = None
    for (word, times), verses in groups.items():
        first = word[:1].upper()
        if first != letter:
            letter = first
            md += [f"## {letter}", ""]
        md += [f"### {word} — {times}", ""]
        md += [f"- **{ref}** — {text}" for ref, text in verses]
        md.append("")
    guarded_write(MD, "\n".join(md), len(rows))

    print(f"words: {len(groups)}  verse rows: {len(rows)}  site updated: {updated}")


if __name__ == "__main__":
    main()
