#!/usr/bin/env python3
"""50_strait_to_straight.py — owner directive 2026-07-19: "Change all
instances of strait to straight".

Applies strait -> straight and straits -> straights (case-preserving)
across the composed restored text as approved restorations (flaw_type
`strait_straight`, highest-id wins — superseded, never deleted).

Derived forms straitly/straitened/straitness/straitest are NOT touched:
they carry the sense "strictly/constrained", where "straightened" would
change the meaning — flagged for a separate owner ruling.

Idempotent: strait_straight rows are rebuilt each run.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

PATTERN = re.compile(r"\b([Ss])trait(s?)\b")
EVIDENCE = (
    "Owner directive 2026-07-19: strait -> straight bible-wide. If you "
    "have evidence for a different reading, create a GitHub issue: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)


def main():
    con = sqlite3.connect(DB_PATH)
    text = {}
    for vid, t in con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV'"):
        text[vid] = t
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type!='strait_straight' ORDER BY id"):
        text[vid] = t

    con.execute("DELETE FROM restorations WHERE flaw_type='strait_straight'")
    applied = 0
    for vid, t in sorted(text.items()):
        fixed = PATTERN.sub(r"\1traight\2", t)
        if fixed == t:
            continue
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "strait_straight", t, fixed,
             "strait -> straight (owner directive 2026-07-19; "
             "case-preserving, plural included).",
             EVIDENCE, 0.95, "approved"))
        applied += 1
    con.commit()
    con.close()
    print(f"strait -> straight: {applied} verses updated")


if __name__ == "__main__":
    main()
