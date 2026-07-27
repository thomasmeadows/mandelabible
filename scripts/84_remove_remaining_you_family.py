#!/usr/bin/env python3
"""84_remove_remaining_you_family.py — owner directive 2026-07-26: no form of
"you" remains in the text; second person is carried by ye / thou / thee / thy /
thine alone.

`scripts/75_pronoun_and_word_swaps.py` mapped `you -> thee` and `your -> thy|
thine` (the thy/thine split corrected by `scripts/83`). It matched whole words,
so two members of the family survived it:

    yours       12   absolute possessive
    yourselves 188   reflexive

This migration removes both.

  yours -> thine
      "thine" is the attested Early Modern English absolute possessive, so
      this is a plain, unambiguous case match:
          Luke 6:20   for yours is the kingdom of God
                   -> for thine is the kingdom of God
          I Cor 3:21  For all things are yours  ->  are thine

  yourselves -> thyself   (owner ruling 2026-07-26)
      "thyself" is the attested EModE reflexive; there is no "thyselves" in
      1611 English, so the alternative would have been a coinage. Taking
      "thyself" follows the same principle already governing "thee": number is
      carried by context, and by the nominative "ye" where it stands in the
      same sentence.
          Gen 49:2    Gather yourselves together, and hear, ye sons of Jacob
                   -> Gather thyself together, and hear, ye sons of Jacob

WHY NO CASE FIXES ARE NEEDED HERE — verified 2026-07-26 across the whole
corpus: every one of the 2,549 pre-pass "you" instances was OBLIQUE (object of
a verb or preposition — preceded by of/among/with/unto/upon/in or a transitive
verb). Zero stood in subject position. "thee" is the correct oblique form, so
the `you -> thee` map was already case-accurate and nothing needs to become
"thou" or "ye". The resulting system marks number in the nominative
(thou/ye, both untouched) and collapses it in the oblique and possessive.

Idempotent: this migration's own flaw_type rows are rebuilt each run, and the
current-text loader EXCLUDES its own flaw_type, so a re-run reads the same
pre-migration text (the scripts/55 trap).

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
FLAW = "you_family_removal"

# word -> replacement, applied in one pass so nothing cascades
RULES = [
    (re.compile(r"\byourselves\b", re.I), "thyself"),
    (re.compile(r"\byours\b", re.I), "thine"),
]
EXPECTED = {"yourselves": 188, "yours": 12}

# every remaining member of the family, checked for after the rewrite
FAMILY = ["you", "your", "yours", "yourself", "yourselves"]

EVIDENCE = (
    "Owner directive 2026-07-26: no form of \"you\" remains; second person is "
    "carried by ye/thou/thee/thy/thine. \"thine\" is the attested EModE "
    "absolute possessive; \"thyself\" is the attested EModE reflexive (there "
    "is no \"thyselves\" in 1611 English), with number carried by context and "
    "by the nominative \"ye\". Completes scripts/75 and scripts/83. If you "
    "have evidence for a different reading, create a GitHub issue: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)

RATIONALE = ("yourselves -> thyself, yours -> thine (owner directive "
             "2026-07-26): the last members of the \"you\" family removed.")


def cased(replacement, sample):
    if sample[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


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

    counts = {k: 0 for k in EXPECTED}
    final = {}
    for vid, t in text.items():
        new = t
        for pattern, replacement in RULES:
            key = pattern.pattern.strip("\\b")
            counts[key] += len(pattern.findall(new))
            new = pattern.sub(lambda m: cased(replacement, m.group(0)), new)
        if new != t:
            final[vid] = (t, new)

    for pattern, replacement in RULES:
        k = pattern.pattern.strip("\\b")
        print(f"  {k} -> {replacement}: {counts[k]} (expected {EXPECTED[k]})")
    print(f"{len(final)} verses updated")

    mismatch = {k: (counts[k], EXPECTED[k]) for k in EXPECTED
                if counts[k] != EXPECTED[k]}
    if mismatch:
        raise SystemExit(f"REFUSING: count mismatch vs expected: {mismatch}. "
                         "The text moved under this migration; re-review "
                         "before applying.")

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
    print("\nRemaining \"you\"-family words in the published text:")
    for w in FAMILY:
        n = sum(len(re.findall(rf"\b{w}\b", t, re.I)) for t in after.values())
        print(f"   {w:12} {n}")
    print("\nSecond-person inventory:")
    for w in ["thou", "thee", "thy", "thine", "ye", "thyself"]:
        n = sum(len(re.findall(rf"\b{w}\b", t, re.I)) for t in after.values())
        print(f"   {w:12} {n:,}")
    con.close()
    print("\nDone. Now republish:\n"
          "  python3 scripts/17_export_full.py\n"
          "  python3 scripts/81_publish_site_editions.py")


if __name__ == "__main__":
    main()
