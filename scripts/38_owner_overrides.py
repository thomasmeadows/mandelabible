#!/usr/bin/env python3
"""38_owner_overrides.py — owner full-verse overrides of prior restorations.

Verses where the owner has supplied an exact remembered reading that
OVERRIDES an earlier approved restoration (including TSBC rows, which
otherwise stand per the "lean towards the TSBC, until told otherwise"
ruling — these are the explicit "told otherwise" cases, exercising
Decision Log #11's revisit-later clause).

Current overrides:
1. Genesis 1:2 (2026-07-18) — reverts TSBC row 3598 ("...darkness was upon
   the surface of the waters: and the Spirit of God moved upon the surface
   of the waters.") to the owner's remembered reading: "void and without
   form" word order, "face of the deep", "moved upon the waters".

Mechanics as scripts 32/34/37: flaw_type `owner_override`, approved,
highest-id row wins in script 17, so superseded rows are kept, never
deleted. Idempotent (rows rebuilt each run).
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

# (book, chapter, verse) -> (owner reading, note)
OVERRIDES = {
    ("Genesis", 1, 2): (
        "And the earth was void and without form; and darkness was upon "
        "the face of the deep: and the Spirit of God moved upon the "
        "waters.",
        "Owner memory 2026-07-18; explicit override of TSBC row 3598 "
        "(revisit-later clause, Decision Log #11)"),
}

EVIDENCE = (
    "Owner-ruled memory restoration (2026-07-18), remembered_verses.md; "
    "explicit owner override of a TSBC reading. If you have evidence for "
    "a different reading, create a GitHub issue with your sources: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute("SELECT DISTINCT name, id FROM books"))
    con.execute("DELETE FROM restorations WHERE flaw_type='owner_override'")
    base = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        base[vid] = t
    for (book, ch, vs), (reading, note) in OVERRIDES.items():
        vid, orig = con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV' AND "
            "book_id=? AND chapter=? AND verse=?",
            (books[book], ch, vs)).fetchone()
        text = base.get(vid, orig)
        if text == reading:
            print(f"{book} {ch}:{vs}: already reads the owner text")
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "owner_override", text, reading, note, EVIDENCE,
             0.95, "approved"))
        print(f"{book} {ch}:{vs}: applied")
    con.commit()


if __name__ == "__main__":
    main()
