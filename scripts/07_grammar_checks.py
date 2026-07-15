#!/usr/bin/env python3
"""07_grammar_checks.py — Phase 3: Early Modern English grammar rule checks.

Rules implemented (each anomaly's detail names the rule that fired):

R1 `its` — essentially absent from the 1611 KJV (period English used "his"/
   "thereof"); every occurrence is flagged. Score 0.6.
R2 Second-person mixing — a verse using both the thou-series (thou/thee/thy/
   thine) and the you-series (ye/you/your/yours) is flagged as a WEAK signal
   (score 0.2): period grammar allows genuine singular/plural mixing, but
   "your where thy belongs" is the exact Lord's Prayer signature, so mixed
   verses go on the review queue rather than being ignored.
R3 Modern bare verb forms — third-person singular forms that period English
   wrote with -eth (hath/doth/saith/goeth...): has, does, says, goes, makes,
   gives, loves, knows, comes, takes, sees, lives. Score 0.6.

Not implemented yet (documented gap): full -eth/-est conjugation checking and
n-gram idiom comparison against Geneva/Tyndale need POS tagging / n-gram
models — deferred until the simpler rules' output is reviewed.

Idempotent: rebuilds type='grammar' anomalies each run.
"""

import re
import sqlite3
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")  # tokenizer v2

THOU_SERIES = {"thou", "thee", "thy", "thine"}
YOU_SERIES = {"ye", "you", "your", "yours"}
MODERN_VERBS = {
    "has": "hath", "does": "doth", "says": "saith", "goes": "goeth",
    "makes": "maketh", "gives": "giveth", "loves": "loveth",
    "knows": "knoweth", "comes": "cometh", "takes": "taketh",
    "sees": "seeth", "lives": "liveth",
}


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("BEGIN")
        con.execute("DELETE FROM anomalies WHERE type='grammar'")
        counts = Counter()

        def add(vid, token, detail, score):
            con.execute(
                "INSERT INTO anomalies (verse_id, type, token, detail, score) "
                "VALUES (?,'grammar',?,?,?)",
                (vid, token, detail, score))

        for vid, text in con.execute("SELECT id, text FROM verses WHERE translation='KJV'"):
            tokens = [t.lower() for t in TOKEN_RE.findall(text)]
            tokset = set(tokens)

            for _ in range(tokens.count("its")):
                add(vid, "its",
                    "R1: 'its' is essentially absent from 1611 English "
                    "(period usage: 'his'/'thereof')", 0.6)
                counts["R1 its"] += 1

            thou = tokset & THOU_SERIES
            you = tokset & YOU_SERIES
            if thou and you:
                add(vid, ",".join(sorted(thou | you)),
                    f"R2: second-person mixing — thou-series {sorted(thou)} and "
                    f"you-series {sorted(you)} in one verse (weak signal; the "
                    "Lord's Prayer 'your-for-thy' signature)", 0.2)
                counts["R2 mixed 2nd person"] += 1

            for tok in tokset & set(MODERN_VERBS):
                add(vid, tok,
                    f"R3: modern bare verb form '{tok}' — period English wrote "
                    f"'{MODERN_VERBS[tok]}'", 0.6)
                counts["R3 modern verb"] += 1

        con.commit()
        total = con.execute(
            "SELECT COUNT(*) FROM anomalies WHERE type='grammar'").fetchone()[0]
        print(f"grammar anomalies: {total}")
        for rule, c in counts.items():
            print(f"  {rule}: {c}")

        print("\nMatthew 6:9-13 grammar flags:")
        for row in con.execute(
            """SELECT v.verse, a.token, a.detail FROM anomalies a
               JOIN verses v ON v.id = a.verse_id
               JOIN books b ON b.translation = v.translation AND b.id = v.book_id
               WHERE a.type='grammar' AND b.name='Matthew' AND v.chapter=6
                 AND v.verse BETWEEN 9 AND 13"""):
            print(f"  v{row[0]} [{row[1]}]: {row[2]}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
