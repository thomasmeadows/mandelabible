#!/usr/bin/env python3
"""32_owner_memory_fixes.py — owner-ruled memory restorations (2026-07-18).

1. I John 4:6: "spirit of error" -> "spirit that leads astray" (memory #77,
   owner override of unconfirmed status).
2. The eyes-to-see/ears-to-hear phrase family (memory #81): nine verses where
   the owner supplied exact replacement phrasing restoring the remembered
   "eyes to see and ears to hear" form.

Each fix is a phrase replacement applied to the verse's LATEST approved
restoration text (rows compose; script 17 takes the highest id). Idempotent:
prior owner_memory_fix rows are rebuilt each run. Errors out if an anchor
phrase is not found in the verse's current final text.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

# (ref, old phrase, new phrase, memory note)
FIXES = [
    ("I John 4:6", "the spirit of error",
     "the spirit that leads astray",
     "Memory #77 (spirit of error), owner override 2026-07-18"),
    ("John 8:11",
     "He who hath ears to hear, let him hear. He who has eyes to see, let him see.",
     "He who hath eyes to see and ears to hear.",
     "Memory #81 (eyes to see / ears to hear), owner ruling 3a"),
    ("Luke 14:35", "He that hath ears to hear, let him hear.",
     "He who hath eyes to see and ears to hear.",
     "Memory #81, owner ruling 3b"),
    ("Luke 8:8", "He that hath ears to hear, let him hear.",
     "He who hath eyes to see and ears to hear.",
     "Memory #81, owner ruling 3c"),
    ("Mark 7:16", "If any man have ears to hear, let him hear.",
     "If any man has eyes to see and ears to hear.",
     "Memory #81, owner ruling 3d"),
    ("Mark 4:23", "If any man have ears to hear, let him hear.",
     "If any man has eyes to see and ears to hear.",
     "Memory #81, owner ruling 3e"),
    ("Mark 4:9", "And he said unto them, He that hath ears to hear, let him hear.",
     "And he said unto them; If any man has eyes to see and ears to hear.",
     "Memory #81, owner ruling 3f"),
    ("Matthew 13:43", "Who hath ears to hear, let him hear.",
     "Who has eyes to see and ears to hear.",
     "Memory #81, owner ruling 3g"),
    ("Matthew 13:9", "Who hath ears to hear, let him hear.",
     "Who has eyes to see and ears to hear.",
     "Memory #81, owner ruling 3h"),
    ("Matthew 11:15", "He that hath ears to hear, let him hear.",
     "He who has eyes to see and ears to hear.",
     "Memory #81, owner ruling 3i"),
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
    con.execute("DELETE FROM restorations WHERE flaw_type='owner_memory_fix'")
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
            (vid, "owner_memory_fix", text, merged, note, EVIDENCE, 0.95,
             "approved"))
        print(f"{ref}: applied")
    con.execute("UPDATE memories SET status='owner-confirmed' WHERE id IN (77, 81)")
    con.commit()


if __name__ == "__main__":
    main()
