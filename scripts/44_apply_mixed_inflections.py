#!/usr/bin/env python3
"""44_apply_mixed_inflections.py — apply the mixed-inflection unification
(owner ruling 2026-07-18: "Update all occurrences to the suggestion"; tie
rulings sprang -> sprung and drave -> drove; girdedst removed from the
whitelist and changed to girded).

Every minority form from references/mixed_inflections.md is replaced by its
majority form bible-wide, on the composed restored text (same composition as
scripts 36/38). Rows are flaw_type `mixed_inflection`, approved —
highest-id wins in script 17, so prior rows are superseded, never deleted.
Initial capitals are preserved (Shew -> Show etc.).

Also edits references/word_whitelist.md: drops the girdedst link from the
round-1 list (count 165 -> 164) and annotates its reason section with the
owner ruling (the section itself is kept — nothing is lost).

Idempotent: mixed_inflection rows are rebuilt each run; the whitelist edit
is a no-op once applied.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
WHITELIST = ROOT / "references" / "word_whitelist.md"

# minority -> majority (report recommendations + owner tie rulings)
MAPPINGS = {
    "begun": "began",
    "calledst": "called",
    "commandedst": "commanded",
    "deliveredst": "delivered",
    "doest": "dost",
    "drunk": "drank",
    "drave": "drove",          # owner tie ruling
    "gat": "got",
    "gotten": "got",
    "holden": "held",
    "holpen": "helped",
    "lien": "lain",
    "promisedst": "promised",
    "shone": "shined",         # shined is the corpus majority (9 vs 8)
    "show": "shew",            # shew is the corpus majority (229 vs 2)
    "sprang": "sprung",        # owner tie ruling
    "sung": "sang",
    "stainedst": "stained",
    "stricken": "struck",
    "trustedst": "trusted",
    "wringed": "wrung",
    "girdedst": "girded",      # owner ruling; whitelist entry removed
}

EVIDENCE = (
    "Mixed-inflection unification (owner ruling 2026-07-18, "
    "references/mixed_inflections.md): the corpus used two inflections of "
    "the same word; the minority form is unified onto the majority form. "
    "If you have evidence for a different reading, create a GitHub issue: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)

WORD_RE = re.compile(
    r"\b(" + "|".join(sorted(MAPPINGS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE)


def replace(text):
    changed = []

    def sub(m):
        src = m.group(0)
        repl = MAPPINGS[src.lower()]
        if src[0].isupper():
            repl = repl[0].upper() + repl[1:]
        changed.append(f"{src.lower()} -> {repl.lower()}")
        return repl

    return WORD_RE.sub(sub, text), changed


def fix_whitelist():
    text = WHITELIST.read_text(encoding="utf-8")
    if "[girdedst](#girdedst), " in text:
        text = text.replace("[girdedst](#girdedst), ", "")
        text = text.replace("### Reviewed no-safe-swap words (165)",
                            "### Reviewed no-safe-swap words (164)")
        text = text.replace(
            "### girdedst",
            "### girdedst\n- **REMOVED from the whitelist by owner ruling "
            "2026-07-18** — girdedst -> girded (mixed-inflection "
            "unification, `mixed_inflections.md`); entry kept for history.")
        WHITELIST.write_text(text, encoding="utf-8")
        print("whitelist: girdedst link removed (165 -> 164), "
              "reason section annotated")
    else:
        print("whitelist: girdedst already removed")


def main():
    fix_whitelist()
    con = sqlite3.connect(DB_PATH)
    base = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type!='mixed_inflection' ORDER BY id"):
        base[vid] = t

    con.execute("DELETE FROM restorations WHERE flaw_type='mixed_inflection'")
    applied, words = 0, {}
    for vid, orig in con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV'"):
        cur = base.get(vid, orig)
        new, changed = replace(cur)
        if not changed:
            continue
        for c in changed:
            words[c] = words.get(c, 0) + 1
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "mixed_inflection", cur, new, "; ".join(changed),
             EVIDENCE, 0.9, "approved"))
        applied += 1
    con.commit()
    con.close()
    print(f"{applied} verses updated")
    for c, n in sorted(words.items()):
        print(f"  {c}: ×{n}")


if __name__ == "__main__":
    main()
