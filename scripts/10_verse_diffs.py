#!/usr/bin/env python3
"""10_verse_diffs.py — Phase 4: diff every KJV verse against each English witness.

Alignment is by (book_id, chapter, verse) — book ids were remapped to KJV ids
at import (script 08). Original-language witnesses (TR, WLC) are excluded:
cross-language string similarity is meaningless; they serve word-level lookup.

similarity = Jaccard overlap of lowercase token sets (tokenizer v2 regex) —
fast and robust to the witnesses' period spelling. `notable` records the
top content-word substitutions (words unique to each side). Verses missing
in a witness get a row with witness_text NULL (logged, not force-aligned).

Idempotent: rebuilds verse_diffs each run.
"""

import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")  # tokenizer v2
ENGLISH_WITNESSES = ["Geneva1599", "Tyndale", "Wycliffe", "KJVPCE", "AKJV",
                     "Webster", "RNKJV", "UKJV", "YLT", "DRC"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS verse_diffs (
    verse_id     INTEGER,       -- KJV verse
    witness      TEXT,
    witness_text TEXT,          -- NULL = verse missing in witness
    similarity   REAL,
    notable      TEXT
);
CREATE INDEX IF NOT EXISTS idx_diffs_verse ON verse_diffs (verse_id);
CREATE INDEX IF NOT EXISTS idx_diffs_sim ON verse_diffs (witness, similarity);
"""


def toks(text: str) -> set:
    return {t.lower().replace("’", "'").replace("–", "-")
            for t in TOKEN_RE.findall(text)}


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)
        con.execute("DELETE FROM verse_diffs")

        kjv = {(b, c, v): (vid, text) for vid, b, c, v, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'")}

        for w in ENGLISH_WITNESSES:
            wit = {(b, c, v): text for b, c, v, text in con.execute(
                "SELECT book_id, chapter, verse, text FROM verses WHERE translation=?", (w,))}
            wit_books = {b for b, _, _ in wit}
            rows, missing = [], 0
            for ref, (vid, ktext) in kjv.items():
                if ref[0] not in wit_books:
                    continue  # witness never had this book — not an alteration signal
                wtext = wit.get(ref)
                if wtext is None:
                    rows.append((vid, w, None, None, "missing in witness"))
                    missing += 1
                    continue
                kt, wt = toks(ktext), toks(wtext)
                union = kt | wt
                sim = len(kt & wt) / len(union) if union else 1.0
                only_k = sorted(kt - wt)[:6]
                only_w = sorted(wt - kt)[:6]
                notable = ""
                if only_k or only_w:
                    notable = f"KJV-only: {', '.join(only_k)} | {w}-only: {', '.join(only_w)}"
                rows.append((vid, w, wtext, round(sim, 4), notable))
            con.executemany("INSERT INTO verse_diffs VALUES (?,?,?,?,?)", rows)
            con.commit()
            n = len(rows) - missing
            print(f"{w}: {n} verses diffed, {missing} missing in witness")

        # validation against a known case (roadmap acceptance criterion)
        print("\nMatthew 9:17 (bottles/wineskins validation):")
        for w, sim, notable in con.execute(
            """SELECT d.witness, d.similarity, d.notable FROM verse_diffs d
               JOIN verses v ON v.id = d.verse_id
               JOIN books b ON b.translation='KJV' AND b.id = v.book_id
               WHERE b.name='Matthew' AND v.chapter=9 AND v.verse=17
                 AND d.witness IN ('Geneva1599','Tyndale','Wycliffe')"""):
            print(f"  {w} (sim {sim}): {notable}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
