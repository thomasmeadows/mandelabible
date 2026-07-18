#!/usr/bin/env python3
"""37_sampson_gen40_fixes.py — owner-ruled fixes (2026-07-18).

1. **Samson -> Sampson bible-wide** (owner memory, corroborated: TSBC change
   record at Judges 13:24 — "The name was originally spelled Sampson, with a
   letter 'p'" — and Wycliffe's 32 "Sampson" readings as advisory witness).
   Memory outranks the modern spelling per the evidence hierarchy.
2. **Judges 13:24 repaired**: the TSBC import (row flaw_type tsbc_memory)
   stored the change DESCRIPTION as the verse's restoration text; the verse
   is reset to the owner's reading with the Sampson spelling.
3. **Genesis 40:17 repaired**: a rare-word span merge left "of all manner of
   d goods"; reset to the owner's reading ("of all manner of goods").

Same composition mechanics as scripts 32/34 (flaw_type `owner_memory_fix3`,
approved, composes onto each verse's latest approved restoration; script 17
takes the highest id, so the broken rows are superseded, not deleted —
generated artifacts are never deleted). Idempotent.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

# Full-verse owner readings (override whatever the composed base says).
OVERRIDES = {
    ("Judges", 13, 24):
        "And the woman bare a son, and called his name Sampson: and the "
        "child grew, and the Lord blessed him.",
    ("Genesis", 40, 17):
        "And in the uppermost basket there was of all manner of goods for "
        "Pharaoh; and the birds did eat them out of the basket upon my head.",
}

EVIDENCE = (
    "Owner-ruled memory restoration (2026-07-18), remembered_verses.md; "
    "Sampson spelling corroborated by TSBC change (Judges 13:24) and "
    "Wycliffe's 32 'Sampson' readings (advisory). If you have evidence for "
    "a different reading, create a GitHub issue with your sources: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)

SAMSON = re.compile(r"\bSamson\b")


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))
    con.execute(
        "DELETE FROM restorations WHERE flaw_type='owner_memory_fix3'")
    base = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        base[vid] = t

    n = 0
    for vid, book_id, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        book = books[book_id]
        text = base.get(vid, orig)
        if (book, ch, vs) in OVERRIDES:
            merged = OVERRIDES[(book, ch, vs)]
            note = "Owner-supplied full-verse reading 2026-07-18 (repairs " \
                   "a defective prior restoration row)"
        elif SAMSON.search(text):
            merged = SAMSON.sub("Sampson", text)
            note = "Samson -> Sampson (owner memory 2026-07-18, TSBC + " \
                   "Wycliffe corroboration)"
        else:
            continue
        if merged == text:
            continue
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "owner_memory_fix3", text, merged, note, EVIDENCE,
             0.95, "approved"))
        n += 1
        print(f"{book} {ch}:{vs}: applied")
    con.commit()
    print(f"{n} verses fixed")


if __name__ == "__main__":
    main()
