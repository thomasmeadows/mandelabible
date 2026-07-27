#!/usr/bin/env python3
"""83_thine_to_thy_before_consonants.py — owner directive 2026-07-26: correct
the attributive possessive to "thy" wherever it stands before a consonant.

In Early Modern English the singular possessive splits on the sound that
follows, exactly as a/an does:

    thine  before a vowel or h   — thine eyes, thine heart, thine own, thine hand
    thy    before a consonant    — thy God, thy father, thy land, thy feet

`scripts/75_pronoun_and_word_swaps.py` mapped every plural "your" to "thine"
without that split, producing 1,357 forms that no 1611 printing would set:
"thine God" (182), "thine fathers" (88), "thine father" (40), "thine brethren"
(38), "thine children" (33). A few more of the same shape were introduced by
earlier passes (chief->head, the memory fixes) and are corrected here too, so
the rule holds everywhere rather than only over script 75's output.

This is a phonological/agreement fix only. It does NOT touch the separate
number question (whether "your"->"thine" and "you"->"thee" should have been
applied at all, given that you/ye/your are the KJV's plural set) — that stands
as ruled, and the finding is recorded in the roadmap Decision Log.

The ABSOLUTE possessive is left alone. When "thine" is a pronoun in its own
right rather than a modifier, it stays "thine" whatever follows:

    Genesis 31:32    discern thou what is thine with me
    Deuteronomy 15:3 that which is thine with thy brother
    Deuteronomy 30:4 If any of thine be driven out
    I Chronicles 21:24  I will not take that which is thine for the Lord
    Jeremiah 32:7    the right of redemption is thine to buy it
    John 17:6        thine they were, and thou gavest them me

These are identified by the function word that follows (see ABSOLUTE_FOLLOWERS);
every other consonant-initial follower in the corpus is a noun or adjective,
i.e. attributive. Vowel- and h-initial followers are never touched.

Idempotent: this migration's own flaw_type rows are rebuilt each run, and the
current-text loader EXCLUDES its own flaw_type, so a re-run reads the same
pre-migration text and produces the same result (the scripts/55 trap).

Downstream (run separately — the text of the Bible changes, so the site must be
republished):
    python3 scripts/17_export_full.py
    python3 scripts/81_publish_site_editions.py
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
FLAW = "thine_thy_agreement"

EXPECTED_CONVERSIONS = 1357
EXPECTED_ABSOLUTE_KEPT = 6

# Words that mark the preceding "thine" as an absolute possessive (a pronoun,
# not a modifier). Every other consonant-initial follower in the corpus is a
# noun or an adjective heading a noun phrase.
ABSOLUTE_FOLLOWERS = {"with", "be", "for", "to", "they"}

# "thine" + space + a consonant-initial word. h is deliberately excluded: EModE
# takes "thine" before h (thine heart, thine hand, thine house).
PATTERN = re.compile(r"\bthine (?=([bcdfgjklmnpqrstvwxyz]\w*))", re.I)

EVIDENCE = (
    "Early Modern English possessive agreement: thine before a vowel or h, thy "
    "before a consonant (the same split as a/an). Owner directive 2026-07-26, "
    "correcting the undifferentiated your->thine mapping in "
    "scripts/75_pronoun_and_word_swaps.py. If you have evidence for a "
    "different reading, create a GitHub issue: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)

RATIONALE = (
    "thine -> thy before a consonant (EModE possessive agreement; owner "
    "directive 2026-07-26). Absolute possessives and vowel/h-initial "
    "followers are unchanged."
)


def fix(text, stats):
    """Return text with attributive 'thine' before a consonant set to 'thy'."""
    def repl(m):
        follower = m.group(1).lower()
        if follower in ABSOLUTE_FOLLOWERS:
            stats["kept_absolute"] += 1
            return m.group(0)
        stats["converted"] += 1
        word = m.group(0)[:5]                      # 'thine' as it was cased
        return ("Thy " if word[0].isupper() else "thy ")
    return PATTERN.sub(repl, text)


def load_current(con):
    """The text the exporter would emit, minus this migration's own rows."""
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


def main():
    con = sqlite3.connect(DB_PATH)
    text = load_current(con)

    stats = {"converted": 0, "kept_absolute": 0}
    final = {}
    for vid, t in text.items():
        new = fix(t, stats)
        if new != t:
            final[vid] = (t, new)

    print(f"{stats['converted']} 'thine' -> 'thy' across {len(final)} verses")
    print(f"{stats['kept_absolute']} absolute possessives kept as 'thine'")

    if stats["converted"] != EXPECTED_CONVERSIONS or \
            stats["kept_absolute"] != EXPECTED_ABSOLUTE_KEPT:
        raise SystemExit(
            f"REFUSING: count mismatch — converted {stats['converted']} "
            f"(expected {EXPECTED_CONVERSIONS}), kept "
            f"{stats['kept_absolute']} (expected {EXPECTED_ABSOLUTE_KEPT}). "
            "The text moved under this migration; re-review before applying.")

    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for vid, (old, new) in final.items():
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, FLAW, old, new, RATIONALE, EVIDENCE, 0.95, "approved"))
    con.commit()

    # ---- verify against the freshly written text -------------------------
    after = {}
    for vid, t in con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV'"):
        after[vid] = t
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL ORDER BY id"):
        after[vid] = t
    leftover = 0
    for t in after.values():
        for m in PATTERN.finditer(t):
            if m.group(1).lower() not in ABSOLUTE_FOLLOWERS:
                leftover += 1
    con.close()
    print(f"remaining attributive 'thine' before a consonant: {leftover}")
    print("\nDone. Now republish:\n"
          "  python3 scripts/17_export_full.py\n"
          "  python3 scripts/81_publish_site_editions.py")


if __name__ == "__main__":
    main()
