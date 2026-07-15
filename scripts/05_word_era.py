#!/usr/bin/env python3
"""05_word_era.py — Phase 3: era-clear the KJV vocabulary; flag rare words.

Builds the cleared-word list from the local pre-1611 corpora (all ADVISORY
under Decision Log #5 — attestation lowers suspicion, never vetoes memory):
  - Wycliffe (1382), Tyndale (1526), Geneva1599 witness databases
  - King James's own Essayes (1585)
  - the Middle English reference texts

Outputs:
  - `word_era` rows: cleared_by + verdict ('period' if attested locally,
    'suspect' if attested nowhere — pending manual first-use dating; the
    manual step fills first_use_year and may upgrade to 'anachronism').
    Proper nouns (every surface form capitalized) get verdict 'proper_noun'
    instead: names are transliterations, not English vocabulary, so era
    dating does not apply — they await the Hebrew/Greek retranslation pass
    (owner request 2026-07-14; needs Phase 4 Strong's data), e.g. Noah,
    Jesus, Mary should derive from the original-language forms rather than
    modernized spellings.
  - `anomalies` rows of type 'rare_word' for words appearing <=5 times
    bible-wide (validated signal: "matrix" appears exactly 5x). Words whose
    every surface form is capitalized are treated as proper nouns and
    skipped (names are legitimately rare).
  - `references/uncleared_words.md` — the generated list for manual dating.

Idempotent: rebuilds word_era and its anomaly rows each run.
"""

import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
SQLITE_DIR = REPO_ROOT / "bible_databases" / "formats" / "sqlite"
REFS = REPO_ROOT / "references"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")  # tokenizer v2
TOKENIZER_VERSION = 2


def fold(form: str) -> str:
    return form.lower().replace("’", "'").replace("–", "-")

WITNESS_DBS = ["Wycliffe", "Tyndale", "Geneva1599"]  # oldest first
TEXT_CORPORA = {
    "KJ-Essayes": [
        "King James Writing Sample - The Essayes of a Prentise in the Divine Art of Poesie.txt"
    ],
    "MiddleEnglish": [
        "Middle English - The Canterbury Tales.txt",
        "Middle English - The Book of Quinte Essence or the Fifth Being.txt",
        "Middle English - The Wright's Chaste Wife.txt",
        "Understand Middle English - A middle English Reader.txt",
    ],
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS word_era (
    word              TEXT PRIMARY KEY,
    cleared_by        TEXT,     -- 'Wycliffe', 'Tyndale', 'Geneva1599', 'KJ-Essayes', 'MiddleEnglish', NULL
    first_use_year    INTEGER,  -- from manual/external dating when not cleared
    first_use_source  TEXT,
    verdict           TEXT,     -- 'period', 'suspect', 'anachronism' (Axis 1: 1611 English)
    source_verdict    TEXT      -- Axis 2: biblical-era referent (Decision Log #4)
);
CREATE TABLE IF NOT EXISTS anomalies (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id  INTEGER REFERENCES verses(id),
    type      TEXT,
    token     TEXT,
    detail    TEXT,
    score     REAL
);
CREATE INDEX IF NOT EXISTS idx_anomalies_verse ON anomalies (verse_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies (type);
"""


def corpus_vocab_from_db(name: str) -> set:
    con = sqlite3.connect(SQLITE_DIR / f"{name}.db")
    try:
        vocab = set()
        for (text,) in con.execute(f"SELECT text FROM {name}_verses"):
            vocab.update(fold(t) for t in TOKEN_RE.findall(text))
        return vocab
    finally:
        con.close()


def corpus_vocab_from_texts(files: list) -> set:
    vocab = set()
    for fname in files:
        text = (REFS / fname).read_text(encoding="utf-8", errors="replace")
        vocab.update(fold(t) for t in TOKEN_RE.findall(text))
    return vocab


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)

        corpora = []  # (label, vocab), oldest attestation first
        for name in WITNESS_DBS:
            corpora.append((name, corpus_vocab_from_db(name)))
        corpora.insert(0, ("MiddleEnglish", corpus_vocab_from_texts(TEXT_CORPORA["MiddleEnglish"])))
        corpora.append(("KJ-Essayes", corpus_vocab_from_texts(TEXT_CORPORA["KJ-Essayes"])))
        for label, vocab in corpora:
            print(f"Corpus {label}: {len(vocab)} distinct words")

        kjv = dict(con.execute(
            "SELECT word, count FROM word_counts "
            "WHERE translation='KJV' AND book_id IS NULL AND tokenizer_version=?",
            (TOKENIZER_VERSION,)))

        # proper-noun heuristic: every surface form is capitalized
        proper = {
            w for (w,) in con.execute(
                """SELECT word FROM word_forms
                   WHERE translation='KJV' AND tokenizer_version=?
                   GROUP BY word
                   HAVING SUM(CASE WHEN form = lower(form) THEN 1 ELSE 0 END) = 0""",
                (TOKENIZER_VERSION,))
        }

        con.execute("BEGIN")
        con.execute("DELETE FROM word_era")
        con.execute("DELETE FROM anomalies WHERE type='rare_word'")

        uncleared = []
        n_proper = 0
        for word, count in sorted(kjv.items()):
            cleared_by = next((label for label, v in corpora if word in v), None)
            if word in proper:
                verdict = "proper_noun"
                n_proper += 1
            elif cleared_by:
                verdict = "period"
            else:
                verdict = "suspect"
            con.execute(
                "INSERT INTO word_era (word, cleared_by, verdict) VALUES (?,?,?)",
                (word, cleared_by, verdict))
            if verdict == "suspect":
                uncleared.append((word, count))

        # rare-word anomalies: <=5 bible-wide, not proper-noun-only
        rare = {w: c for w, c in kjv.items() if c <= 5 and w not in proper}
        n_rare_rows = 0
        for vid, text in con.execute("SELECT id, text FROM verses WHERE translation='KJV'"):
            seen = set()
            for form in TOKEN_RE.findall(text):
                w = fold(form)
                if w in rare and w not in seen:
                    seen.add(w)
                    c = rare[w]
                    con.execute(
                        "INSERT INTO anomalies (verse_id, type, token, detail, score) "
                        "VALUES (?,?,?,?,?)",
                        (vid, "rare_word", w,
                         f"'{w}' appears only {c}x bible-wide"
                         + (" (hapax legomenon)" if c == 1 else ""),
                         0.4 if c == 1 else 0.2))
                    n_rare_rows += 1
        con.commit()

        lines = [
            "# Uncleared Words — generated by scripts/05_word_era.py",
            "",
            "KJV words attested in NONE of the local pre-1611 corpora "
            "(Wycliffe, Tyndale, Geneva1599, KJ Essayes, Middle English texts).",
            "Manual dating task (roadmap Phase 3): record first-use year + source "
            "in `word_era`. Attestation is advisory only (Decision Log #5).",
            "",
            "Proper nouns (names of people/places) are excluded — era dating does "
            "not apply to transliterations; they carry verdict `proper_noun` in "
            "`word_era` and await the Hebrew/Greek name-retranslation pass "
            "(owner request 2026-07-14).",
            "",
            "| word | KJV count |",
            "|------|-----------|",
        ]
        lines += [f"| {w} | {c} |" for w, c in sorted(uncleared, key=lambda x: -x[1])]
        (REFS / "uncleared_words.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"word_era: {len(kjv)} words; proper nouns {n_proper}, "
              f"cleared {len(kjv)-len(uncleared)-n_proper}, "
              f"uncleared {len(uncleared)} -> references/uncleared_words.md")
        print(f"rare_word anomalies: {n_rare_rows} rows "
              f"({len(rare)} distinct rare non-proper-noun words)")
        row = con.execute(
            "SELECT verdict, cleared_by FROM word_era WHERE word='matrix'").fetchone()
        print(f"Spot check 'matrix': verdict={row[0]}, cleared_by={row[1]}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
