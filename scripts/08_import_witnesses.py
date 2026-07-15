#!/usr/bin/env python3
"""08_import_witnesses.py — Phase 4: import witness translations into mandela.db.

Witness set per roadmap Phase 4: Geneva1599, Tyndale, Wycliffe, KJVPCE, AKJV,
Webster, RNKJV, UKJV, YLT, DRC (English) + TR, WLC (original languages).
All are ADVISORY under Decision Log #5.

Alignment: witness book ids are remapped to the KJV's book ids by book NAME
(verified necessary: Wycliffe's own file numbers books differently than
scrollmapper's KJV). Unmapped books and empty-text verses are logged, not
force-aligned (e.g. Tyndale ships whole books of empty rows for parts he
never translated).

Idempotent: deletes and re-copies each witness each run.
"""

import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
SQLITE_DIR = REPO_ROOT / "bible_databases" / "formats" / "sqlite"

WITNESSES = ["Geneva1599", "Tyndale", "Wycliffe", "KJVPCE", "AKJV",
             "Webster", "RNKJV", "UKJV", "YLT", "DRC", "TR", "WLC"]


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        kjv_ids = {name: bid for bid, name in con.execute(
            "SELECT id, name FROM books WHERE translation='KJV'")}

        for w in WITNESSES:
            src = sqlite3.connect(SQLITE_DIR / f"{w}.db")
            title, license_ = src.execute(
                "SELECT title, license FROM translations LIMIT 1").fetchone()

            con.execute("BEGIN")
            con.execute("DELETE FROM verses WHERE translation=?", (w,))
            con.execute("DELETE FROM books WHERE translation=?", (w,))
            con.execute("DELETE FROM translations WHERE translation=?", (w,))
            con.execute("INSERT INTO translations VALUES (?,?,?)", (w, title, license_))

            book_map, unmapped = {}, []
            for bid, name in src.execute(f"SELECT id, name FROM {w}_books"):
                if name in kjv_ids:
                    book_map[bid] = kjv_ids[name]
                else:
                    unmapped.append(name)
            for old, new in book_map.items():
                name = src.execute(
                    f"SELECT name FROM {w}_books WHERE id=?", (old,)).fetchone()[0]
                con.execute("INSERT INTO books (id, translation, name) VALUES (?,?,?)",
                            (new, w, name))

            copied = empty = skipped = 0
            for bid, ch, vs, text in src.execute(
                    f"SELECT book_id, chapter, verse, text FROM {w}_verses"):
                if bid not in book_map:
                    skipped += 1
                    continue
                if not text or not text.strip():
                    empty += 1
                    continue
                con.execute(
                    "INSERT OR IGNORE INTO verses (translation, book_id, chapter, verse, text) "
                    "VALUES (?,?,?,?,?)", (w, book_map[bid], ch, vs, text.strip()))
                copied += 1
            con.commit()
            src.close()

            msg = f"{w}: {copied} verses, {len(book_map)} books"
            if empty:
                msg += f"; {empty} empty verses skipped"
            if unmapped:
                msg += f"; unmapped books: {unmapped}"
            if skipped:
                msg += f"; {skipped} verses in unmapped books skipped"
            print(msg)

        print("\nRow counts per translation:")
        for t, c in con.execute(
                "SELECT translation, COUNT(*) FROM verses GROUP BY translation ORDER BY 1"):
            print(f"  {t}: {c}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
