#!/usr/bin/env python3
"""85_merge_kj_whitelist_suggestions.py — owner directive 2026-07-26, step 3.

Consolidates the five King James agent batch files
(references/kj_whitelist_suggestions_batch{1..5}.md) into one owner-review
file, references/word_lists/kj_whitelist_suggestions.md:

  - all WHITELIST recommendations in one table, sorted by category then word,
    each carrying a blank owner-ruling cell;
  - every batch's "Borderline / not recommended" prose preserved verbatim
    below, so the owner can see what the verb rule and the category
    definitions excluded.

Report only. The batch files are generated artifacts and are never modified
or deleted (CLAUDE.md). Applying the owner's rulings is a separate migration.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "references" / "word_lists" / "kj_whitelist_suggestions.md"
ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([a-z-]+)\s*\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|?\s*$")


def main():
    recs, borderline = [], []
    for n in range(1, 6):
        p = ROOT / "references" / "word_lists" / f"kj_whitelist_suggestions_batch{n}.md"
        if not p.exists():
            print(f"missing {p.name} — skipping")
            continue
        in_rec, tail = False, []
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.startswith("## WHITELIST"):
                in_rec = True
                continue
            if ln.startswith("## ") and in_rec:
                in_rec = False
            if in_rec:
                m = ROW.match(ln)
                if m and m.group(3) in {"proper-noun", "genealogy", "animal",
                                        "plant", "location"}:
                    recs.append((m.group(3), m.group(2), int(m.group(1)),
                                 m.group(5), n))
            else:
                tail.append(ln)
        rest = "\n".join(tail).strip()
        if rest:
            borderline.append((n, rest))

    recs.sort(key=lambda r: (r[0], r[1].lower()))
    L = ["# King James agent — whitelist suggestions for the remaining words",
         "",
         "*Consolidated by `scripts/85_merge_kj_whitelist_suggestions.py` from "
         "the five batch files (owner directive 2026-07-26). The agent reviewed "
         "all 2,397 token groups used 88 times or fewer that survived the "
         "script-83 whitelist sweep, and recommends the words below — proper "
         "nouns, genealogical terms, animals, plants, and locations that are "
         "**not verbs**. Nothing has been applied; the owner-ruling column is "
         "blank for the owner.*",
         "",
         f"**{len(recs)} recommendations.**", "",
         "| category | word | item# | batch | reason | owner ruling |",
         "|---|---|---|---|---|---|"]
    for cat, word, idx, reason, batch in recs:
        L.append(f"| {cat} | {word} | {idx} | {batch} | {reason} | _____ |")
    L += ["", "## Borderline / not recommended (per batch)", ""]
    for n, text in borderline:
        L += [f"### Batch {n}", "", text, ""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    from collections import Counter
    print(Counter(r[0] for r in recs), "total", len(recs))
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
