#!/usr/bin/env python3
"""75_pronoun_and_word_swaps.py — owner directive 2026-07-26: a sequence of
bible-wide word/phrase swaps, applied IN ORDER (each rule operates on the
output of the previous, so no instance is double-counted):

  1. pavement(s)   -> road(s)
  2. "you terror"  -> "thine fear"      (phrase, before the general terror rule)
  3. terror(s)     -> fear(s)
  4. "an error"    -> "a sin"           (phrase, before the general error rule)
  5. error(s)      -> sin(s)
  6. your          -> thine
  7. you           -> thee

Owner-confirmed counts against the actual corpus (base KJV + approved
restorations), 2026-07-26: pavement 9, you-terror 1, terror 45 (of 46 total,
minus the 1 consumed by rule 2), an-error 2, error 14 (of 16 total, minus the
2 consumed by rule 4), your 1743, you 2558. The owner's initial rough counts
(11/1/45/2/17/~2000/~1600) were a manual estimate off by line-terminator
artifacts; the corpus-derived counts above are what this script enforces via
its own count assertions.

Mechanical, unambiguous, bible-wide directive (same footing as
scripts/50_strait_to_straight.py and scripts/59_corn_to_wheat.py) — applied
directly, not staged through a per-verse owner-ruling review file.

Idempotent: this migration's own flaw_type rows are rebuilt each run, and the
current-text loader EXCLUDES this script's own flaw_type so a re-run reads
the same pre-migration base text (the scripts/55 trap).
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
FLAW = "pronoun_and_word_swaps"

EXPECTED = {
    "pavement": 9,
    "you_terror": 1,
    "terror": 45,
    "an_error": 2,
    "error": 14,
    "your": 1743,
    "you": 2557,  # 2558 total "you" instances minus the 1 consumed by rule 2 (you terror)
}

EVIDENCE = (
    "Owner directive 2026-07-26: sequential bible-wide swaps (pavement->road, "
    "you terror->thine fear, terror->fear, an error->a sin, error->sin, "
    "your->thine, you->thee). If you have evidence for a different reading, "
    "create a GitHub issue: https://github.com/thomasmeadows/mandelabible/issues/new"
)


def cased_word(replacement, sample):
    """Match the case of `sample`'s first letter onto `replacement`."""
    if sample[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def word_sub(text, pattern, singular, plural=None):
    def repl(m):
        word = m.group(0)
        new = plural if plural and word.lower().endswith("s") else singular
        return cased_word(new, word)
    return re.sub(pattern, repl, text, flags=re.I)


def phrase_sub(text, pattern, replacement, count_holder):
    def repl(m):
        count_holder[0] += 1
        first = m.group(0).split()[0]
        words = replacement.split()
        words[0] = cased_word(words[0], first)
        return " ".join(words)
    return re.sub(pattern, repl, text, flags=re.I)


def main():
    con = sqlite3.connect(DB_PATH)
    text = {}
    for vid, t in con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV'"):
        text[vid] = t
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type != ? ORDER BY id", (FLAW,)):
        text[vid] = t

    counts = {k: 0 for k in EXPECTED}
    holder = [0]
    final = {}
    for vid, t in text.items():
        orig = t

        n = len(re.findall(r"\bpavements?\b", t, re.I))
        counts["pavement"] += n
        t = word_sub(t, r"\bpavements?\b", "road", "roads")

        holder[0] = 0
        t = phrase_sub(t, r"\byou terror\b", "thine fear", holder)
        counts["you_terror"] += holder[0]

        n = len(re.findall(r"\bterrors?\b", t, re.I))
        counts["terror"] += n
        t = word_sub(t, r"\bterrors?\b", "fear", "fears")

        holder[0] = 0
        t = phrase_sub(t, r"\ban error\b", "a sin", holder)
        counts["an_error"] += holder[0]

        n = len(re.findall(r"\berrors?\b", t, re.I))
        counts["error"] += n
        t = word_sub(t, r"\berrors?\b", "sin", "sins")

        n = len(re.findall(r"\byour\b", t, re.I))
        counts["your"] += n
        t = word_sub(t, r"\byour\b", "thine")

        n = len(re.findall(r"\byou\b", t, re.I))
        counts["you"] += n
        t = word_sub(t, r"\byou\b", "thee")

        if t != orig:
            final[vid] = (orig, t)

    mismatches = {k: (counts[k], EXPECTED[k]) for k in EXPECTED
                  if counts[k] != EXPECTED[k]}
    if mismatches:
        raise SystemExit(f"REFUSING: count mismatch vs expected: {mismatches}")

    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for vid, (orig, new) in final.items():
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, FLAW, orig, new,
             "Sequential bible-wide swaps (owner directive 2026-07-26): "
             "pavement->road, you terror->thine fear, terror->fear, "
             "an error->a sin, error->sin, your->thine, you->thee.",
             EVIDENCE, 0.95, "approved"))
    con.commit()
    con.close()

    print(f"{len(final)} verses updated.")
    for k in EXPECTED:
        print(f"  {k}: {counts[k]} (expected {EXPECTED[k]})")


if __name__ == "__main__":
    main()
