#!/usr/bin/env python3
"""03_tokenize.py — Phase 2: tokenize the KJV and fill word_counts.

Tokenizer rules (TOKENIZER_VERSION 2, per roadmap Phase 2 decisions):
- A token is a maximal run of letters plus internal apostrophes and hyphens:
  regex [A-Za-z]+(?:['’–-][A-Za-z]+)*  — so "serpent's" and "Baal-zebub" stay
  single tokens, but surrounding punctuation ( , . ; : ! ? ( ) ) is stripped.
- v2: the base text uses curly apostrophes (’, e.g. "wife’s") and en-dashes
  (–, e.g. "Beth–el") — these join tokens like their ASCII cousins and are
  normalized (’ -> ', – -> -) in the stored word so counts unify; the raw
  characters themselves stay flagged by 06_punctuation_audit.py as
  out-of-1611 print evidence. (v1 wrongly split "wife’s" into wife + s.)
- Counting is case-folded to lowercase in `word_counts.word`; the original-case
  surface forms are preserved in `word_forms` (capitalization is itself
  evidence — Decision Log #6).
- Per-book rows carry the book_id; whole-bible totals use book_id NULL.
- The tokenizer version is stored with every row so counts can be regenerated
  if rules change.

Idempotent: replaces all rows for (translation, tokenizer version) each run.
"""

import re
import sqlite3
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
TRANSLATION = "KJV"
TOKENIZER_VERSION = 2
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")


def fold(form: str) -> str:
    """Case-fold and normalize curly apostrophe / en-dash to ASCII."""
    return form.lower().replace("’", "'").replace("–", "-")

SCHEMA = """
CREATE TABLE IF NOT EXISTS word_counts (   -- one row per (word, book); book_id NULL = whole-bible total
    translation TEXT,
    word        TEXT,               -- case-folded token
    book_id     INTEGER,            -- NULL for bible-wide totals
    count       INTEGER,
    tokenizer_version INTEGER
);
CREATE TABLE IF NOT EXISTS word_forms (    -- original-case surface forms (Decision Log #6 evidence)
    translation TEXT,
    word        TEXT,               -- case-folded token
    form        TEXT,               -- surface form as printed
    count       INTEGER,
    tokenizer_version INTEGER
);
CREATE INDEX IF NOT EXISTS idx_word_counts_word ON word_counts (word);
CREATE INDEX IF NOT EXISTS idx_word_forms_word ON word_forms (word);
"""


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)
        con.execute("BEGIN")
        con.execute(
            "DELETE FROM word_counts WHERE translation=? AND tokenizer_version=?",
            (TRANSLATION, TOKENIZER_VERSION),
        )
        con.execute(
            "DELETE FROM word_forms WHERE translation=? AND tokenizer_version=?",
            (TRANSLATION, TOKENIZER_VERSION),
        )

        by_book: Counter = Counter()   # (book_id, word) -> count
        totals: Counter = Counter()    # word -> count
        forms: Counter = Counter()     # (word, form) -> count

        for book_id, text in con.execute(
            "SELECT book_id, text FROM verses WHERE translation=?", (TRANSLATION,)
        ):
            for form in TOKEN_RE.findall(text):
                word = fold(form)
                by_book[(book_id, word)] += 1
                totals[word] += 1
                forms[(word, form)] += 1

        con.executemany(
            "INSERT INTO word_counts VALUES (?,?,?,?,?)",
            [(TRANSLATION, w, b, c, TOKENIZER_VERSION) for (b, w), c in by_book.items()]
            + [(TRANSLATION, w, None, c, TOKENIZER_VERSION) for w, c in totals.items()],
        )
        con.executemany(
            "INSERT INTO word_forms VALUES (?,?,?,?,?)",
            [(TRANSLATION, w, f, c, TOKENIZER_VERSION) for (w, f), c in forms.items()],
        )
        con.commit()

        total_words = sum(totals.values())
        print(f"Tokenized {TRANSLATION} (tokenizer v{TOKENIZER_VERSION})")
        print(f"Total word count: {total_words}")
        print(f"Distinct words: {len(totals)}")
        print("Top 10 tokens:", ", ".join(f"{w}={c}" for w, c in totals.most_common(10)))
    finally:
        con.close()


if __name__ == "__main__":
    main()
