#!/usr/bin/env python3
"""88_word_swaps_talk_glad_tarry.py — owner directive 2026-07-27: a further
sequence of bible-wide word/phrase swaps, applied IN ORDER (each rule operates
on the output of the previous, so no instance is double-counted):

   1. talk (noun, 6 verses)      -> speech       (Job 11:2, Job 15:3,
                                                  Prov 14:23, Eccl 10:13,
                                                  Matt 22:15, Titus 1:10)
   2. talkest/talketh/talking/talked/talk
                                 -> speakest/speaketh/speaking/spake/speak
   3. alway                      -> always
   4. "glad tidings"             -> "good tidings"   (phrase, before glad)
   5. gladness                   -> thankfulness
   6. glad                       -> thankful
   7. tarry/tarried/tarrying     -> stay/stayed/staying
   8. think/thinkest/thinketh/thinking
                                 -> ponder/ponderest/pondereth/pondering
   9. "a habitation"             -> "an abode"       (article fix, before
                                                      the general rule)
  10. habitation / habitations   -> abode / dwelling places
  11. sojourn/sojourned/sojourner/sojourners/sojourneth/sojourning
                                 -> dwell/dwelt/dweller/dwellers/dwelleth/
                                    dwelling
  12. "a prey"                   -> "prey"           (article removal)
  13. sepulchre / sepulchres     -> grave / graves

and then one verse-scoped repair (VERSE_FIXES), applied after the general rules:

  14. II Samuel 18:27 "Me pondereth" -> "I ponder"

Owner rulings taken during review, 2026-07-27 (the directive as first written
carried four items that could not be applied mechanically):

  * talkest -> speakest and talketh -> speaketh, not the past-tense "spake"/
    "spoke" of the original list — every occurrence is present tense
    ("thou talkest with me", "his tongue talketh of judgment").
  * the 6 NOUN uses of "talk" -> "speech", not "speak" ("a man full of
    speech", "unprofitable speech"); the other 20 are verbs -> "speak".
  * sojourneth -> dwelleth, not "dwell" — all 15 are third-person singular
    ("the stranger that sojourneth among thee").
  * "glad tidings" -> "good tidings" (owner's wording: good tidings for all
    verses with tidings), so the gospel set phrase is not turned into
    "thankful tidings" by the general glad -> thankful rule.
  * II Samuel 18:27 reads "I ponder the running" — the base "Me thinketh" is
    the EModE impersonal ("it seems to me"), and the word-for-word swap had
    made it "Me pondereth".

Article corrections requested by the directive ("if necessary correct articles
before the word"): "a habitation" -> "an abode" (Ezek 25:5) is the only
article that changes; the 6 "an habitation" already agree with "abode".
"a prey" -> "prey" is itself one of the requested swaps.

Mechanical, unambiguous, bible-wide directive (same footing as
scripts/75_pronoun_and_word_swaps.py) — applied directly, not staged through a
per-verse owner-ruling review file.

Idempotent: this migration's own flaw_type rows are rebuilt each run, and the
current-text loader EXCLUDES this script's own flaw_type so a re-run reads the
same pre-migration base text (the scripts/55 trap).

Usage:
    python3 scripts/88_word_swaps_talk_glad_tarry.py            # apply
    python3 scripts/88_word_swaps_talk_glad_tarry.py --dry-run  # counts only
"""
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
FLAW = "word_swaps_talk_glad_tarry"

# The six verses where "talk" is a noun (owner ruling 2026-07-27).
NOUN_TALK_REFS = [
    ("Job", 11, 2),
    ("Job", 15, 3),
    ("Proverbs", 14, 23),
    ("Ecclesiastes", 10, 13),
    ("Matthew", 22, 15),
    ("Titus", 1, 10),
]

# Verse-scoped repairs applied AFTER the general rules, where the swap left a
# construction the word-for-word map cannot fix (owner ruling 2026-07-27).
#   (book, chapter, verse, pattern, replacement, key)
VERSE_FIXES = [
    # "Me thinketh" is the EModE impersonal ("it seems to me"), which the
    # think -> ponder swap turned into "Me pondereth". Owner ruling: it reads
    # "I ponder the running".
    ("II Samuel", 18, 27, r"\bMe pondereth\b", "I ponder", "me_pondereth"),
]

# (key, pattern, replacement) applied in this order to every verse.
# "noun_talk" is handled separately because it is restricted to six verses.
RULES = [
    ("talkest", r"\btalkest\b", "speakest"),
    ("talketh", r"\btalketh\b", "speaketh"),
    ("talking", r"\btalking\b", "speaking"),
    ("talked", r"\btalked\b", "spake"),
    ("talk", r"\btalk\b", "speak"),
    ("alway", r"\balway\b", "always"),
    ("glad_tidings", r"\bglad tidings\b", "good tidings"),
    ("gladness", r"\bgladness\b", "thankfulness"),
    ("glad", r"\bglad\b", "thankful"),
    ("tarrying", r"\btarrying\b", "staying"),
    ("tarried", r"\btarried\b", "stayed"),
    ("tarry", r"\btarry\b", "stay"),
    ("thinkest", r"\bthinkest\b", "ponderest"),
    ("thinketh", r"\bthinketh\b", "pondereth"),
    ("thinking", r"\bthinking\b", "pondering"),
    ("think", r"\bthink\b", "ponder"),
    ("a_habitation", r"\ba habitation\b", "an abode"),
    ("habitations", r"\bhabitations\b", "dwelling places"),
    ("habitation", r"\bhabitation\b", "abode"),
    ("sojourneth", r"\bsojourneth\b", "dwelleth"),
    ("sojourning", r"\bsojourning\b", "dwelling"),
    ("sojourners", r"\bsojourners\b", "dwellers"),
    ("sojourner", r"\bsojourner\b", "dweller"),
    ("sojourned", r"\bsojourned\b", "dwelt"),
    ("sojourn", r"\bsojourn\b", "dwell"),
    ("a_prey", r"\ba prey\b", "prey"),
    ("sepulchres", r"\bsepulchres\b", "graves"),
    ("sepulchre", r"\bsepulchre\b", "grave"),
]

# Counts derived from the corpus (base KJV + approved restorations) on
# 2026-07-27, in rule order — each is what remains after the earlier rules
# have consumed their share (e.g. "talk" is 26 total minus the 6 noun uses;
# "glad" is 88 total minus the 4 consumed by "glad tidings").
EXPECTED = {
    "noun_talk": 6,
    "talkest": 3,
    "talketh": 2,
    "talking": 10,
    "talked": 42,
    "talk": 20,
    "alway": 22,
    "glad_tidings": 4,
    "gladness": 48,
    "glad": 84,
    "tarrying": 2,
    "tarried": 34,
    "tarry": 51,
    "thinkest": 9,
    "thinketh": 8,
    "thinking": 3,
    "think": 65,
    "a_habitation": 1,
    "habitations": 20,
    "habitation": 60,
    "sojourneth": 15,
    "sojourning": 3,
    "sojourners": 5,
    "sojourner": 11,
    "sojourned": 12,
    "sojourn": 33,
    "a_prey": 34,
    "sepulchres": 16,
    "sepulchre": 54,
    "me_pondereth": 1,
}

RATIONALE = (
    "Bible-wide word swaps (owner directive 2026-07-27): talk->speak "
    "(noun talk->speech), talked->spake, talkest->speakest, talketh->"
    "speaketh, talking->speaking, alway->always, glad tidings->good tidings, "
    "gladness->thankfulness, glad->thankful, tarry->stay, tarried->stayed, "
    "tarrying->staying, think->ponder, thinkest->ponderest, thinketh->"
    "pondereth, thinking->pondering, habitation->abode, habitations->"
    "dwelling places, sojourn->dwell, sojourned->dwelt, sojourner->dweller, "
    "sojourners->dwellers, sojourneth->dwelleth, sojourning->dwelling, "
    "a prey->prey, sepulchre->grave, sepulchres->graves; and, in II Samuel "
    "18:27 only, the impersonal 'Me thinketh' -> 'I ponder'."
)

EVIDENCE = (
    "Owner directive 2026-07-27: bible-wide plain-speech swaps, with the "
    "articles before the swapped word corrected (a habitation->an abode, "
    "a prey->prey). If you have evidence for a different reading, create a "
    "GitHub issue: https://github.com/thomasmeadows/mandelabible/issues/new"
)


def cased(replacement, sample):
    """Match the case of `sample`'s first letter onto `replacement`."""
    if sample[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def apply_rule(text, pattern, replacement):
    """Case-preserving whole-word (or whole-phrase) substitution.

    Returns (new_text, n). The case of the match's first letter is carried
    onto the replacement, which is what keeps sentence-initial "Talk"/"A prey"
    correct.
    """
    n = 0

    def repl(m):
        nonlocal n
        n += 1
        return cased(replacement, m.group(0))

    return re.sub(pattern, repl, text, flags=re.I), n


def load_text(con):
    """Current text = base KJV overlaid with approved restorations, EXCLUDING
    this migration's own rows so a re-run reads the same pre-migration base."""
    text = {}
    for vid, t in con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV'"):
        text[vid] = t
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type != ? ORDER BY id", (FLAW,)):
        text[vid] = t
    return text


def verse_id(con, book, chapter, verse):
    row = con.execute(
        "SELECT v.id FROM verses v JOIN books b "
        "ON b.id = v.book_id AND b.translation = v.translation "
        "WHERE v.translation='KJV' AND b.name=? AND v.chapter=? "
        "AND v.verse=?", (book, chapter, verse)).fetchone()
    if row is None:
        raise SystemExit(f"REFUSING: verse not found: {book} {chapter}:{verse}")
    return row[0]


def noun_talk_ids(con):
    return {verse_id(con, *ref) for ref in NOUN_TALK_REFS}


def verse_fixes_by_id(con):
    """verse id -> [(pattern, replacement, key)]"""
    fixes = {}
    for book, chapter, verse, pattern, replacement, key in VERSE_FIXES:
        fixes.setdefault(verse_id(con, book, chapter, verse), []).append(
            (pattern, replacement, key))
    return fixes


def main():
    dry_run = "--dry-run" in sys.argv
    con = sqlite3.connect(DB_PATH)
    text = load_text(con)
    nouns = noun_talk_ids(con)
    fixes = verse_fixes_by_id(con)

    counts = {k: 0 for k in EXPECTED}
    final = {}
    for vid, t in text.items():
        orig = t
        if vid in nouns:
            t, n = apply_rule(t, r"\btalk\b", "speech")
            counts["noun_talk"] += n
        for key, pattern, replacement in RULES:
            t, n = apply_rule(t, pattern, replacement)
            counts[key] += n
        for pattern, replacement, key in fixes.get(vid, ()):
            t, n = apply_rule(t, pattern, replacement)
            counts[key] += n
        if t != orig:
            final[vid] = (orig, t)

    for key in EXPECTED:
        flag = "" if counts[key] == EXPECTED[key] else \
            f"  <-- MISMATCH (expected {EXPECTED[key]})"
        print(f"  {key}: {counts[key]}{flag}")
    print(f"{len(final)} verses affected.")

    mismatches = {k: (counts[k], EXPECTED[k]) for k in EXPECTED
                  if counts[k] != EXPECTED[k]}
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
