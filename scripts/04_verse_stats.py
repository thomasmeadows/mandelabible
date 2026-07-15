#!/usr/bin/env python3
"""04_verse_stats.py — Phase 2: per-verse character/word stats and outliers.

Per roadmap Phase 2 decisions:
- char_count includes whitespace (the corruption engine's fixed-length
  constraint — instructions.md Phase 8); char_count_no_ws excludes it.
- word_count uses the same tokenizer as 03_tokenize.py (v2).
- Outliers: per-book mean/stddev of char_count; verses beyond ±2σ within
  their book are flagged (is_outlier=1), and the global longest/shortest
  are reported.

Idempotent: rebuilds verse_stats for the translation each run.
"""

import re
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
TRANSLATION = "KJV"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")  # tokenizer v2

SCHEMA = """
CREATE TABLE IF NOT EXISTS verse_stats (
    verse_id            INTEGER PRIMARY KEY REFERENCES verses(id),
    char_count          INTEGER,    -- including whitespace (the corruption engine's constraint)
    char_count_no_ws    INTEGER,
    word_count          INTEGER,
    book_zscore_chars   REAL,       -- how unusual this verse is within its book
    is_outlier          INTEGER DEFAULT 0
);
"""


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)

        rows = con.execute(
            "SELECT id, book_id, text FROM verses WHERE translation=?", (TRANSLATION,)
        ).fetchall()

        stats = {}  # verse_id -> (book_id, chars, chars_no_ws, words)
        by_book = defaultdict(list)
        for vid, book_id, text in rows:
            chars = len(text)
            no_ws = len("".join(text.split()))
            words = len(TOKEN_RE.findall(text))
            stats[vid] = (book_id, chars, no_ws, words)
            by_book[book_id].append(chars)

        book_mu_sigma = {
            b: (statistics.mean(v), statistics.pstdev(v)) for b, v in by_book.items()
        }

        out = []
        for vid, (book_id, chars, no_ws, words) in stats.items():
            mu, sigma = book_mu_sigma[book_id]
            z = (chars - mu) / sigma if sigma else 0.0
            out.append((vid, chars, no_ws, words, z, 1 if abs(z) > 2 else 0))

        con.execute("BEGIN")
        con.execute(
            "DELETE FROM verse_stats WHERE verse_id IN "
            "(SELECT id FROM verses WHERE translation=?)",
            (TRANSLATION,),
        )
        con.executemany("INSERT INTO verse_stats VALUES (?,?,?,?,?,?)", out)
        con.commit()

        n_out = sum(o[5] for o in out)
        print(f"verse_stats: {len(out)} rows, {n_out} outliers (|z| > 2 within book)")

        for label, order in (("Longest", "DESC"), ("Shortest", "ASC")):
            top = con.execute(
                f"""SELECT b.name, v.chapter, v.verse, s.char_count
                    FROM verse_stats s
                    JOIN verses v ON v.id = s.verse_id
                    JOIN books b ON b.translation = v.translation AND b.id = v.book_id
                    WHERE v.translation = ?
                    ORDER BY s.char_count {order} LIMIT 5""",
                (TRANSLATION,),
            ).fetchall()
            print(f"{label} verses:")
            for name, ch, vs, c in top:
                print(f"  {name} {ch}:{vs} — {c} chars")
    finally:
        con.close()


if __name__ == "__main__":
    main()
