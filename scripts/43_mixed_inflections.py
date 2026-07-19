#!/usr/bin/env python3
"""43_mixed_inflections.py — list words using MIXED inflection in the
restored corpus (roadmap task: "IE built and builded, cursed and cursedst —
most of the bible uses built, so builded should be scrapped in place of the
modern built").

A mixed-inflection group is a base word that appears in the composed restored
text (same composition as script 36) under BOTH an archaic inflection and a
parallel form of the same word, e.g.:

  1. Irregular past-tense doublets (curated list): builded vs built,
     digged vs dug, spake vs spoke, bare vs bore, ...
  2. Archaic 2nd-person -edst past forms alongside the plain past:
     cursedst vs cursed, plantedst vs planted, ...
  3. Contracted vs full 2nd-person auxiliary/verb forms: shouldst vs
     shouldest, wouldst vs wouldest, ...
  4. shew-family vs show-family spellings.

For each group the report gives every form with its corpus count, the
majority form, a recommendation (minority -> majority), and the verse refs
of the minority form(s). Whitelisted words are still listed but marked
"whitelisted — do not change" (the whitelist protects them).

Output: references/mixed_inflections.md (report only — no text is changed).
Refuses to overwrite an existing report with fewer groups unless
--allow-shrink is passed (generated-artifact guard).

Deliberately EXCLUDED: -eth vs -s third-person pairs (walketh/walks) — in
this corpus the -s form is usually a plural noun (works, sleeps), so the
detector would be mostly noise; revisit only with part-of-speech data.
"""
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
WHITELIST = ROOT / "references" / "word_whitelist.md"
OUT_PATH = ROOT / "references" / "mixed_inflections.md"

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")

# Curated archaic/modern doublets (archaic first). Both members must occur
# in the corpus for the group to be reported.
DOUBLETS = [
    ("builded", "built"), ("buildedst", "builtest"),
    ("digged", "dug"), ("spake", "spoke"), ("brake", "broke"),
    ("bare", "bore"), ("sware", "swore"), ("tare", "tore"),
    ("drave", "drove"), ("clave", "clove"), ("gat", "got"),
    ("begat", "begot"), ("holpen", "helped"), ("holden", "held"),
    ("gotten", "got"), ("stricken", "struck"), ("shapen", "shaped"),
    ("graven", "engraved"), ("catched", "caught"), ("kneeled", "knelt"),
    ("leaped", "leapt"), ("learned", "learnt"), ("shined", "shone"),
    ("sung", "sang"), ("sprung", "sprang"), ("swum", "swam"),
    ("drunk", "drank"), ("begun", "began"), ("wringed", "wrung"),
    ("hanged", "hung"), ("lien", "lain"), ("spitted", "spat"),
    ("shew", "show"), ("shewed", "showed"), ("sheweth", "showeth"),
    ("shewing", "showing"), ("shewest", "showest"), ("shewn", "shown"),
]


def fold(form):
    return form.lower().replace("’", "'").replace("–", "-")


def main():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))
    final = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        final[vid] = t

    totals = defaultdict(int)
    refs = defaultdict(list)
    for vid, book_id, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        text = final.get(vid, orig)
        ref = f"{books[book_id]} {ch}:{vs}"
        for tok in TOKEN_RE.findall(text):
            w = fold(tok)
            totals[w] += 1
            if len(refs[w]) < 25:
                refs[w].append(ref)
    con.close()

    whitelist = set(re.findall(r"\[([a-z0-9'’–-]+)\]\(#",
                               WHITELIST.read_text(encoding="utf-8")))

    groups = []  # (base label, [(form, count)], kind)

    # 1. curated doublets
    for arch, mod in DOUBLETS:
        if totals.get(arch) and totals.get(mod):
            groups.append((mod, [(arch, totals[arch]), (mod, totals[mod])],
                           "irregular doublet"))

    # 2. -edst past 2nd-person alongside plain past (cursedst vs cursed)
    for w in sorted(totals):
        if w.endswith("edst") and totals.get(w[:-2]):
            groups.append((w[:-2], [(w, totals[w]), (w[:-2], totals[w[:-2]])],
                           "2nd-person -edst vs plain past"))

    # 3. contracted vs full 2nd person: B+"st" vs B+"est"
    for w in sorted(totals):
        if w.endswith("est") and not w.endswith("edst"):
            contracted = w[:-3] + "st"
            if totals.get(contracted):
                groups.append((w[:-3],
                               [(contracted, totals[contracted]),
                                (w, totals[w])],
                               "contracted -st vs full -est"))

    # dedupe (a pair may be found by two detectors)
    seen, uniq = set(), []
    for base, forms, kind in groups:
        key = tuple(sorted(f for f, _ in forms))
        if key in seen:
            continue
        seen.add(key)
        uniq.append((base, forms, kind))
    uniq.sort()

    lines = [
        "# Mixed-Inflection Words in the Restored Text",
        "",
        "Generated by `scripts/43_mixed_inflections.py` from the composed "
        "restored corpus (report only — nothing changed). A group is a word "
        "appearing under both an archaic inflection and a parallel form; "
        "the recommendation follows the roadmap rule: the minority form is "
        "scrapped in favour of the majority form (e.g. builded -> built "
        "only if built is the majority). Whitelisted words are marked and "
        "must not be changed.",
        "",
        f"**Groups found: {len(uniq)}**",
        "",
    ]
    for base, forms, kind in uniq:
        forms = sorted(forms, key=lambda fc: -fc[1])
        major, minor = forms[0], forms[1:]
        surface = ", ".join(f"{f} (×{n})" for f, n in forms)
        lines.append(f"## {base} — {surface} — *{kind}*")
        for f, n in minor:
            wl = " — **whitelisted, do not change**" if f in whitelist else ""
            if n == major[1]:
                lines.append(f"- **TIE (×{n} each) — owner ruling needed**: "
                             f"{f} vs {major[0]}{wl}")
            else:
                lines.append(f"- recommend: **{f} → {major[0]}** "
                             f"(majority ×{major[1]} vs ×{n}){wl}")
            shown = refs[f][:20]
            more = f" … (+{n - len(shown)} more)" if n > len(shown) else ""
            lines.append(f"  - {f} at: " + "; ".join(shown) + more)
        lines.append("")

    out = "\n".join(lines) + "\n"
    if OUT_PATH.exists() and "--allow-shrink" not in sys.argv:
        old = OUT_PATH.read_text(encoding="utf-8").count("\n## ")
        if out.count("\n## ") < old:
            raise SystemExit(f"REFUSING to overwrite {OUT_PATH.name}: "
                             f"fewer groups than existing report")
    OUT_PATH.write_text(out, encoding="utf-8")
    print(f"{len(uniq)} mixed-inflection groups -> {OUT_PATH.name}")


if __name__ == "__main__":
    main()
