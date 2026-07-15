#!/usr/bin/env python3
"""02_import_kjv.py — Phase 1: import the scrollmapper KJV into db/mandela.db.

ATTACHes bible_databases/formats/sqlite/KJV.db (read-only source) and copies
translation metadata, books, and verses via INSERT ... SELECT — no text
parsing, no transcription risk. Idempotent: deletes and re-copies the KJV
rows on each run.
"""

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
SOURCE_PATH = REPO_ROOT / "bible_databases" / "formats" / "sqlite" / "KJV.db"
TRANSLATION = "KJV"


def main() -> None:
    if not DB_PATH.exists():
        sys.exit(f"{DB_PATH} not found — run scripts/01_create_db.py first.")
    if not SOURCE_PATH.exists():
        sys.exit(f"Source not found: {SOURCE_PATH}")

    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("ATTACH DATABASE ? AS src", (str(SOURCE_PATH),))

        con.execute("BEGIN")
        con.execute("DELETE FROM verses WHERE translation = ?", (TRANSLATION,))
        con.execute("DELETE FROM books WHERE translation = ?", (TRANSLATION,))
        con.execute("DELETE FROM translations WHERE translation = ?", (TRANSLATION,))

        con.execute(
            """INSERT INTO translations (translation, title, license)
               SELECT translation, title, license FROM src.translations
               WHERE translation = ?""",
            (TRANSLATION,),
        )
        con.execute(
            """INSERT INTO books (id, translation, name)
               SELECT id, ?, name FROM src.KJV_books""",
            (TRANSLATION,),
        )
        con.execute(
            """INSERT INTO verses (translation, book_id, chapter, verse, text)
               SELECT ?, book_id, chapter, verse, text FROM src.KJV_verses
               ORDER BY id""",
            (TRANSLATION,),
        )
        con.commit()

        books = con.execute(
            "SELECT COUNT(*) FROM books WHERE translation = ?", (TRANSLATION,)
        ).fetchone()[0]
        verses = con.execute(
            "SELECT COUNT(*) FROM verses WHERE translation = ?", (TRANSLATION,)
        ).fetchone()[0]
        print(f"Imported {TRANSLATION}: {books} books, {verses} verses")

        # Acceptance-criteria spot checks (roadmap Phase 1)
        gen11 = con.execute(
            """SELECT text FROM verses
               WHERE translation = ? AND book_id = 1 AND chapter = 1 AND verse = 1""",
            (TRANSLATION,),
        ).fetchone()[0]
        john316 = con.execute(
            """SELECT COUNT(*) FROM verses v JOIN books b
                 ON b.translation = v.translation AND b.id = v.book_id
               WHERE v.translation = ? AND b.name = 'John'
                 AND v.chapter = 3 AND v.verse = 16""",
            (TRANSLATION,),
        ).fetchone()[0]
        last = con.execute(
            """SELECT b.name, v.chapter, v.verse FROM verses v JOIN books b
                 ON b.translation = v.translation AND b.id = v.book_id
               WHERE v.translation = ?
               ORDER BY v.book_id DESC, v.chapter DESC, v.verse DESC LIMIT 1""",
            (TRANSLATION,),
        ).fetchone()

        print(f"Genesis 1:1 = {gen11!r}")
        print(f"John 3:16 present: {bool(john316)}")
        print(f"Final verse: {last[0]} {last[1]}:{last[2]}")

        ok = (
            books == 66
            and verses == 31102
            and gen11 == "In the beginning God created the heaven and the earth."
            and john316 == 1
            and last == ("Revelation of John", 22, 21)  # scrollmapper book name
        )
        print("Acceptance criteria:", "PASS" if ok else "FAIL")
        if not ok:
            sys.exit(1)
    finally:
        con.close()


if __name__ == "__main__":
    main()
