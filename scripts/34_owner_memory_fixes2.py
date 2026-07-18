#!/usr/bin/env python3
"""34_owner_memory_fixes2.py — owner-ruled memory restorations (2026-07-18).

Four Genesis verses supplied verbatim by the owner as memory testimony:

1. Genesis 2:20 — "an help meet for him" -> "a helper fit for him"
2. Genesis 2:24 — "they shall be one flesh" -> "they shall be as one flesh"
3. Genesis 3:24 — "to keep the way of the tree of life" ->
   "to guard the way to the tree of life"
4. Genesis 4:15 — "should kill him" -> "should smite him"

Same mechanics as script 32: each fix is a phrase replacement applied to the
verse's LATEST approved restoration text (rows compose; script 17 takes the
highest id). Idempotent: prior owner_memory_fix2 rows are rebuilt each run.
Errors out if an anchor phrase is not found in the verse's final text.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

# (ref, old phrase, new phrase, memory note)
FIXES = [
    ("Genesis 2:20", "an help meet for him", "a helper fit for him",
     "Owner memory 2026-07-18: 'but for Adam there was not found a helper "
     "fit for him'"),
    ("Genesis 2:24", "they shall be one flesh",
     "they shall be as one flesh",
     "Owner memory 2026-07-18: 'and they shall be as one flesh'"),
    ("Genesis 3:24", "to keep the way of the tree of life",
     "to guard the way to the tree of life",
     "Owner memory 2026-07-18: 'a flaming sword which turned every way, to "
     "guard the way to the tree of life'"),
    ("Genesis 4:15", "should kill him", "should smite him",
     "Owner memory 2026-07-18: 'lest any finding him should smite him'"),
]

EVIDENCE = (
    "Owner-ruled memory restoration (2026-07-18), remembered_verses.md. "
    "If you have evidence for a different reading, create a GitHub issue "
    "with your sources: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute("SELECT DISTINCT name, id FROM books"))
    con.execute("DELETE FROM restorations WHERE flaw_type='owner_memory_fix2'")
    base = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL ORDER BY id"):
        base[vid] = t
    for ref, old, new, note in FIXES:
        book, cv = ref.rsplit(" ", 1)
        ch, vs = map(int, cv.split(":"))
        vid, orig = con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV' AND "
            "book_id=? AND chapter=? AND verse=?",
            (books[book], ch, vs)).fetchone()
        text = base.get(vid, orig)
        if old not in text:
            raise SystemExit(f"ANCHOR NOT FOUND in {ref}: {old!r}")
        merged = text.replace(old, new)
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "owner_memory_fix2", text, merged, note, EVIDENCE, 0.95,
             "approved"))
        print(f"{ref}: applied")
    con.commit()


if __name__ == "__main__":
    main()
