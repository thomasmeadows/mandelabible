#!/usr/bin/env python3
"""01_create_db.py — Phase 1: create db/mandela.db with the base schema.

Creates the translations/books/verses tables per the roadmap Phase 1 schema.
Idempotent: uses CREATE TABLE IF NOT EXISTS; re-running never destroys data.
"""

import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS translations (
    translation TEXT PRIMARY KEY,   -- 'KJV', 'Geneva1599', ...
    title       TEXT,
    license     TEXT
);
CREATE TABLE IF NOT EXISTS books (
    id          INTEGER,            -- scrollmapper book id (1=Genesis ... 66=Revelation)
    translation TEXT REFERENCES translations(translation),
    name        TEXT,
    PRIMARY KEY (translation, id)
);
CREATE TABLE IF NOT EXISTS verses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    translation TEXT REFERENCES translations(translation),
    book_id     INTEGER,
    chapter     INTEGER,
    verse       INTEGER,
    text        TEXT,
    UNIQUE (translation, book_id, chapter, verse)
);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)
        con.commit()
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        print(f"Created {DB_PATH}")
        print(f"Tables: {', '.join(tables)}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
