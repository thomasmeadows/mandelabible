#!/usr/bin/env python3
"""06_punctuation_audit.py — Phase 3: punctuation, emoticon & capitalization audit.

Per roadmap Phase 3 decisions and Decision Log #6:
- Full character inventory of the KJV text into `punctuation_inventory`
  (every non-letter character and its count).
- `anomalies` rows for:
  - 'punctuation': every ( and ) occurrence (parenthesis inventory), plus any
    character outside the expected 1611 set [A-Za-z space , . ; : ? ! ' ( ) -].
  - 'emoticon': punctuation adjacencies that read as emoticons, e.g. ";)"
    produced by "...God;)" — pattern [;:]-?[)(].
  - 'capitalization': (a) ALL-CAPS tokens of length >= 2 — LORD/GOD/JEHOVAH
    are logged as seam candidates even though LORD is the approved exception
    (Decision Log #6 sub-decision); (b) doctrinal title-casing: "Holy Ghost",
    "Holy Spirit", and mid-verse capitalized "Spirit"/"Ghost".

Idempotent: rebuilds its anomaly types and the inventory each run.
"""

import re
import sqlite3
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"

EXPECTED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ,.;:?!'()-")
EMOTICON_RE = re.compile(r"[;:]-?[)(]")
ALLCAPS_RE = re.compile(r"\b[A-Z]{2,}\b")
TITLECASE_RE = re.compile(r"\b(Holy Ghost|Holy Spirit)\b")
MIDVERSE_SPIRIT_RE = re.compile(r"(?<!^)(?<![.?!] )\b(Spirit|Ghost)\b")
LORD_EXCEPTION = {"LORD", "GOD", "JEHOVAH"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS punctuation_inventory (
    character TEXT PRIMARY KEY,
    count     INTEGER
);
"""


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)
        con.execute("BEGIN")
        con.execute("DELETE FROM punctuation_inventory")
        con.execute(
            "DELETE FROM anomalies WHERE type IN ('punctuation','emoticon','capitalization')")

        char_inv: Counter = Counter()
        counts = Counter()

        def add(vid, typ, token, detail, score):
            con.execute(
                "INSERT INTO anomalies (verse_id, type, token, detail, score) "
                "VALUES (?,?,?,?,?)", (vid, typ, token, detail, score))
            counts[typ] += 1

        for vid, text in con.execute("SELECT id, text FROM verses WHERE translation='KJV'"):
            for ch in text:
                if not ch.isalpha():
                    char_inv[ch] += 1

            for m in re.finditer(r"[()]", text):
                add(vid, "punctuation", m.group(),
                    f"parenthesis '{m.group()}' at position {m.start()}", 0.1)
            for ch in set(text) - EXPECTED_CHARS:
                add(vid, "punctuation", ch,
                    f"character U+{ord(ch):04X} {ch!r} outside expected 1611 set", 0.5)
            for m in EMOTICON_RE.finditer(text):
                ctx = text[max(0, m.start() - 12):m.end() + 2]
                add(vid, "emoticon", m.group(),
                    f"emoticon pattern '{m.group()}' in context '...{ctx}'", 0.9)

            for m in ALLCAPS_RE.finditer(text):
                tok = m.group()
                note = (" — approved LORD/GOD/JEHOVAH exception, logged as seam candidate"
                        if tok in LORD_EXCEPTION else "")
                add(vid, "capitalization", tok,
                    f"ALL-CAPS token '{tok}' (original languages are caseless){note}",
                    0.2 if tok in LORD_EXCEPTION else 0.5)
            for m in TITLECASE_RE.finditer(text):
                add(vid, "capitalization", m.group(),
                    f"doctrinal title-casing '{m.group()}' — target reading is "
                    "'spirit of god' (Decision Log #6)", 0.4)
            for m in MIDVERSE_SPIRIT_RE.finditer(text):
                if TITLECASE_RE.search(text[max(0, m.start() - 5):m.end()]):
                    continue  # already flagged as Holy Ghost/Spirit
                add(vid, "capitalization", m.group(),
                    f"mid-verse capitalized '{m.group()}' — doctrinal casing, "
                    "original languages are caseless", 0.3)

        con.executemany(
            "INSERT INTO punctuation_inventory VALUES (?,?)", sorted(char_inv.items()))
        con.commit()

        print("Anomalies inserted:", dict(counts))
        print("Character inventory (non-letter):")
        for ch, c in char_inv.most_common():
            label = ch if ch != " " else "<space>"
            print(f"  {label!r}: {c}")
        emo = con.execute(
            "SELECT COUNT(*) FROM anomalies WHERE type='emoticon'").fetchone()[0]
        print(f"Emoticon patterns found: {emo}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
