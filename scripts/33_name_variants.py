#!/usr/bin/env python3
"""33_name_variants.py — names/places variant-spelling list (roadmap Phase 5).

For every proper noun in the KJV (word_era verdict='proper_noun', the script
05 heuristic), scan the same verse in each English witness translation and
collect capitalized tokens whose spelling is close but not identical
(difflib ratio >= 0.72) — e.g. KJV "Hagar" vs Geneva "Agar". Output:
`references/name_variants.md`, alphabetical, one section per KJV name with
its per-witness variant spellings, counts, and an example reference.

Advisory data only (Premise Revision): witness spellings inform the Decision
Log #7/#8 name-retranslation research; they prove nothing by themselves.

Idempotent. Refuses to overwrite an existing output file with one that has
fewer name sections (owner directive 2026-07-17, generated-artifact guard).
"""
import re
import sqlite3
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
OUT_PATH = ROOT / "references" / "name_variants.md"

WITNESSES = ["Geneva1599", "Tyndale", "Wycliffe", "KJVPCE", "AKJV",
             "RNKJV", "UKJV", "Webster", "YLT", "DRC"]

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")
MIN_RATIO = 0.72

# Capitalized function/common words that are never name variants.
STOP = {w.lower() for w in (
    "And But For The Then When That Thus Also Now Lord God Which Who "
    "Blessed Behold He She They Thou Ye You His Her Him Them Their O "
    "After Before There This These Those Wherefore Therefore So If In "
    "On At To Of By Be It Is Was Were All My Thy Our Your I A An As "
    "From With Unto Upon Out Up Not No Yea Nay Amen Selah King Son "
    "Daughter Sons Children House City Land Mount River Sea Man Men "
    "Woman Israelite Israelites Jew Jews Gentiles Prophet Priest "
    "Spirit Ghost Word Most High Holy Almighty Father Mother Master "
    "Sir Rabbi Christ Jesus Saviour").split()}


def normalize(text):
    return text.replace("’", "'").replace("–", "-")


def main():
    con = sqlite3.connect(DB_PATH)
    proper = {w for (w,) in con.execute(
        "SELECT word FROM word_era WHERE verdict='proper_noun'")
        if "'" not in w}

    # Most common KJV surface form for each lowercase name.
    surface = {}
    for word, form, count in con.execute(
            "SELECT word, form, count FROM word_forms WHERE translation='KJV' "
            "ORDER BY count"):
        if word in proper:
            surface[word] = form  # ascending count: last (largest) wins

    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))

    kjv = con.execute(
        "SELECT book_id, chapter, verse, text FROM verses "
        "WHERE translation='KJV'").fetchall()
    wtexts = {}
    for w in WITNESSES:
        wtexts[w] = {(b, c, v): t for b, c, v, t in con.execute(
            "SELECT book_id, chapter, verse, text FROM verses "
            "WHERE translation=?", (w,))}

    # name -> witness -> variant surface -> [count, example ref]
    variants = defaultdict(lambda: defaultdict(dict))
    ratio_cache = {}

    def ratio(a, b):
        key = (a, b)
        if key not in ratio_cache:
            ratio_cache[key] = SequenceMatcher(None, a, b).ratio()
        return ratio_cache[key]

    for book_id, ch, vs, text in kjv:
        toks = TOKEN_RE.findall(normalize(text))
        lower = {t.lower() for t in toks}
        names = [t for t in toks
                 if t[0].isupper() and t.lower() in proper]
        if not names:
            continue
        ref = f"{books[book_id]} {ch}:{vs}"
        for w in WITNESSES:
            wt = wtexts[w].get((book_id, ch, vs))
            if not wt:
                continue
            cands = [t for t in TOKEN_RE.findall(normalize(wt))
                     if t[0].isupper() and len(t) >= 3
                     and t.lower() not in lower
                     and t.lower() not in STOP]
            if not cands:
                continue
            for name in set(names):
                nl = name.lower()
                best, best_r = None, 0.0
                for c in cands:
                    r = ratio(nl, c.lower())
                    if r > best_r:
                        best, best_r = c, r
                if best_r >= MIN_RATIO:
                    slot = variants[nl][w]
                    if best not in slot:
                        slot[best] = [0, ref]
                    slot[best][0] += 1

    # Build the report.
    sections = []
    for name in sorted(variants):
        disp = surface.get(name, name.capitalize())
        lines = [f"## {disp}", ""]
        for w in WITNESSES:
            if w not in variants[name]:
                continue
            for var, (cnt, ref) in sorted(
                    variants[name][w].items(),
                    key=lambda kv: -kv[1][0]):
                lines.append(f"- **{var}** — {w} (×{cnt}; e.g. {ref})")
        lines.append("")
        sections.append("\n".join(lines))

    if OUT_PATH.exists():
        old = OUT_PATH.read_text(encoding="utf-8").count("\n## ")
        if len(sections) < old:
            raise SystemExit(
                f"REFUSING to overwrite {OUT_PATH}: new report has "
                f"{len(sections)} name sections, existing has {old}")

    header = (
        "# Name & Place Variant Spellings Across Witness Translations\n\n"
        "Generated by `scripts/33_name_variants.py` (roadmap Phase 5: "
        "\"Create a list of all locations and names and any variances of "
        "those names in other translations\").\n\n"
        "For each KJV proper noun (script 05 heuristic, Decision Log #7), "
        "capitalized tokens in the same verse of each English witness with "
        "spelling similarity >= 0.72 but a different spelling are listed as "
        "variants. **Advisory only** (Premise Revision): these feed the "
        "Decision Log #7 name-retranslation research (e.g. Agar → Hagar); "
        "matching is heuristic, so entries may include near-name noise — "
        "owner review applies before any use in restorations.\n\n"
        f"Names with at least one variant: **{len(sections)}** "
        f"of {len(proper)} proper-noun forms.\n\n")
    OUT_PATH.write_text(header + "\n".join(sections), encoding="utf-8")
    print(f"wrote {OUT_PATH} ({len(sections)} names with variants)")


if __name__ == "__main__":
    main()
