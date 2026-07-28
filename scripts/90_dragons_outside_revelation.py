#!/usr/bin/env python3
"""90_dragons_outside_revelation.py — owner directive 2026-07-27: *only the book
of Revelation should have dragons; all others are converted to serpents.*

    dragon  -> serpent     (outside Revelation of John)
    dragons -> serpents    (outside Revelation of John)

25 occurrences in 24 verses across Deuteronomy, Nehemiah, Job, Psalms, Isaiah,
Jeremiah, Lamentations, Ezekiel, Micah and Malachi are converted; the 13
occurrences in Revelation of John (12:3-17, 13:2-11, 16:13, 20:2) are left
exactly as they stand.

Owner rulings taken during review, 2026-07-27:

  * **Nehemiah 2:13** — "even before the dragon well" is a Jerusalem landmark
    (Hebrew *ʿEyn hat-Tannîn*, the Dragon Well), not a creature in the
    narrative. Owner ruling: **convert it too** ("the serpent well"), rather
    than protect it as a proper place name.
  * **Isaiah 27:1** — the verse already says "leviathan that crooked serpent",
    so converting gives "that crooked serpent; and he shall slay the serpent
    that is in the sea". Owner ruling: **convert it**; the repetition stands.

Note that Revelation itself glosses the two words as one creature — "the great
dragon… that old serpent" (12:9, 20:2) — so the directive reads as reserving
the *dragon* name for the apocalypse, not as splitting one creature into two.

Mechanical, unambiguous, book-scoped directive (same footing as
scripts/75_pronoun_and_word_swaps.py and scripts/88_word_swaps_talk_glad_tarry
.py) — applied directly, not staged through a per-verse owner-ruling review
file.

Idempotent: this migration's own flaw_type rows are rebuilt each run, and the
current-text loader EXCLUDES this script's own flaw_type so a re-run reads the
same pre-migration base text (the scripts/55 trap).

Usage:
    python3 scripts/90_dragons_outside_revelation.py            # apply
    python3 scripts/90_dragons_outside_revelation.py --dry-run  # counts only
"""
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
FLAW = "dragons_outside_revelation"
KEEP_BOOK = "Revelation of John"

RULES = [
    ("dragons", r"\bdragons\b", "serpents"),
    ("dragon", r"\bdragon\b", "serpent"),
]

# Counts over the corpus (base KJV + approved restorations) on 2026-07-27,
# outside Revelation of John. Revelation's own 13 are asserted untouched.
EXPECTED = {"dragons": 17, "dragon": 8}
EXPECTED_KEPT = 13

RATIONALE = (
    "Owner directive 2026-07-27: only the book of Revelation has dragons; "
    "everywhere else dragon->serpent and dragons->serpents. Includes the "
    "Dragon Well of Nehemiah 2:13 and Isaiah 27:1, both by explicit owner "
    "ruling."
)

EVIDENCE = (
    "Owner directive 2026-07-27. Revelation itself glosses the two words as "
    "one creature — 'the great dragon… that old serpent' (12:9, 20:2). If you "
    "have evidence for a different reading, create a GitHub issue: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)


def cased(replacement, sample):
    """Match the case of `sample`'s first letter onto `replacement`."""
    if sample[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def apply_rule(text, pattern, replacement):
    n = 0

    def repl(m):
        nonlocal n
        n += 1
        return cased(replacement, m.group(0))

    return re.sub(pattern, repl, text, flags=re.I), n


def main():
    dry_run = "--dry-run" in sys.argv
    con = sqlite3.connect(DB_PATH)

    text, book = {}, {}
    for vid, bname, t in con.execute(
            "SELECT v.id, b.name, v.text FROM verses v JOIN books b "
            "ON b.id = v.book_id AND b.translation = v.translation "
            "WHERE v.translation='KJV'"):
        text[vid] = t
        book[vid] = bname
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type != ? ORDER BY id", (FLAW,)):
        text[vid] = t

    counts = {k: 0 for k in EXPECTED}
    kept = 0
    final = {}
    for vid, t in text.items():
        if book[vid] == KEEP_BOOK:
            kept += len(re.findall(r"\bdragons?\b", t, re.I))
            continue
        orig = t
        for key, pattern, replacement in RULES:
            t, n = apply_rule(t, pattern, replacement)
            counts[key] += n
        if t != orig:
            final[vid] = (orig, t)

    for key in EXPECTED:
        flag = "" if counts[key] == EXPECTED[key] else \
            f"  <-- MISMATCH (expected {EXPECTED[key]})"
        print(f"  {key}: {counts[key]}{flag}")
    print(f"  kept in {KEEP_BOOK}: {kept} (expected {EXPECTED_KEPT})")
    print(f"{len(final)} verses affected.")

    mismatches = {k: (counts[k], EXPECTED[k]) for k in EXPECTED
                  if counts[k] != EXPECTED[k]}
    if kept != EXPECTED_KEPT:
        mismatches["kept_in_revelation"] = (kept, EXPECTED_KEPT)
    if mismatches:
        raise SystemExit(f"REFUSING: count mismatch vs expected: {mismatches}")

    if dry_run:
        print("dry run — no changes written.")
        con.close()
        return

    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for vid, (orig, new) in final.items():
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, FLAW, orig, new, RATIONALE, EVIDENCE, 0.95, "approved"))
    con.commit()
    con.close()
    print(f"{len(final)} verses updated.")


if __name__ == "__main__":
    main()
