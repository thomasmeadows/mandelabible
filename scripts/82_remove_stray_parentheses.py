#!/usr/bin/env python3
"""82_remove_stray_parentheses.py — remove the last two bracketed passages from
the restored text (owner rulings 2026-07-26).

The global parenthesis/emoticon removal (owner ruling 2026-07-14, scripts
13/15) swept 221 verses. A full scan of the current restored text
(references/parenthesis_review.md) found exactly two survivors:

  Romans 1:13  "(but was let hitherto,)"
      Restoration #3338 (punctuation) already removed these parentheses, but
      restoration #9816 (kjvrestore_fold, the you->thee pass) composed after it
      and was rebuilt from the base Oxford text, carrying them back in. The
      exporter takes the highest-id approved row per verse, so 9816 wins.
      The owner keeps "thee" (the number-error flag on this verse was NOT
      ruled for change) and drops the parentheses only.

  I John 2:23  "[but]"
      Square brackets, so never in scope of the 2026-07-14 sweep, which matched
      "(" and ")" only. This is the only square bracket in the whole text.
      The owner keeps the supplied "but" and drops the brackets.

Both fixes are new approved restoration rows composing on top of every existing
row for the verse, per the migration pattern in CLAUDE.md — the builder scripts
are not edited. Fully idempotent: each step checks the current effective text
first, so a re-run inserts nothing.

Downstream (run separately — the text of the Bible changes, so the site must be
republished):
    python3 scripts/17_export_full.py
    python3 scripts/81_publish_site_editions.py
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"

FLAW = "punctuation"
RATIONALE = (
    "Stray-bracket sweep (owner ruling 2026-07-26; "
    "references/parenthesis_review.md). The 2026-07-14 global "
    "parenthesis-removal ruling left these two verses bracketed; wording per "
    "the King James agent's primary proposal as ruled by the owner. "
    "Merged onto current text."
)

# (book, chapter, verse, expected current text, ruled text, evidence)
RULINGS = [
    (
        "Romans", 1, 13,
        "Now I would not have thee ignorant, brethren, that oftentimes I "
        "purposed to come unto thee, (but was let hitherto,) that I might "
        "have some fruit among thee also, even as among other Gentiles.",
        "Now I would not have thee ignorant, brethren, that oftentimes I "
        "purposed to come unto thee, but was let hitherto, that I might have "
        "some fruit among thee also, even as among other Gentiles.",
        "Parentheses -> bare comma pair. The clause is genuine text "
        "(kai ekolythen), not an aside; comma-bounding is standard KJV "
        "practice. \"but\" kept over literal \"and\" on unanimous Geneva 1599 "
        "and Tyndale precedent; \"let\" (= hindered) kept, attested in both. "
        "Owner kept thee/thine; the plural-addressee flag was not ruled for "
        "change.",
    ),
    (
        "I John", 2, 23,
        "Whosoever denieth the Son, the same hath not the Father: [but] he "
        "that acknowledgeth the Son hath the Father also.",
        "Whosoever denieth the Son, the same hath not the Father: but he that "
        "acknowledgeth the Son hath the Father also.",
        "Square brackets removed, the supplied word kept. The bracket marked "
        "only the connective the 1611 translators supplied for the Greek "
        "asyndeton; the clause itself is plainly in the Textus Receptus, and "
        "Wycliffe 1382 independently supplies \"but\" two centuries before "
        "the AV. Geneva 1599's omission of the whole clause is a "
        "translation-base difference, not evidence of spuriousness.",
    ),
]


def verse_id(con, book, chapter, verse):
    row = con.execute(
        "SELECT v.id FROM verses v "
        "JOIN books b ON b.translation='KJV' AND b.id=v.book_id "
        "WHERE v.translation='KJV' AND b.name=? AND v.chapter=? AND v.verse=?",
        (book, chapter, verse)).fetchone()
    return row[0] if row else None


def current_text(con, vid):
    """The text the exporter would emit: highest-id approved row, else base."""
    row = con.execute(
        "SELECT proposed_text FROM restorations "
        "WHERE verse_id=? AND status='approved' AND proposed_text IS NOT NULL "
        "ORDER BY id DESC LIMIT 1", (vid,)).fetchone()
    if row:
        return row[0]
    return con.execute("SELECT text FROM verses WHERE id=?", (vid,)).fetchone()[0]


def apply_ruling(con, book, chapter, verse, expected, ruled, evidence):
    ref = f"{book} {chapter}:{verse}"
    vid = verse_id(con, book, chapter, verse)
    if vid is None:
        print(f"  {ref}: verse not found — skipped")
        return 0
    now = current_text(con, vid)
    if now == ruled:
        print(f"  {ref}: already ruled text — no change")
        return 0
    if now != expected:
        print(f"  {ref}: current text does not match the reviewed text "
              f"— skipped (nothing inserted)")
        print(f"    expected: {expected}")
        print(f"    found:    {now}")
        return 0
    con.execute(
        "INSERT INTO restorations (verse_id, flaw_type, current_text, "
        "proposed_text, rationale, evidence, confidence, status) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (vid, FLAW, now, ruled, RATIONALE, evidence, 0.95, "approved"))
    print(f"  {ref}: brackets removed (restoration inserted)")
    return 1


def scan_remaining(con):
    """Report any bracket left anywhere in the restored text."""
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        resto[vid] = new
    left = []
    for vid, bname, ch, vs, text in con.execute(
            "SELECT v.id, b.name, v.chapter, v.verse, v.text FROM verses v "
            "JOIN books b ON b.translation='KJV' AND b.id=v.book_id "
            "WHERE v.translation='KJV' ORDER BY v.book_id, v.chapter, v.verse"):
        t = resto.get(vid, text)
        if any(c in t for c in "()[]{}<>"):
            left.append(f"{bname} {ch}:{vs} — {t}")
    return left


def main():
    print("Removing the last bracketed passages (owner rulings 2026-07-26)")
    con = sqlite3.connect(DB)
    changed = sum(apply_ruling(con, *r) for r in RULINGS)
    con.commit()

    left = scan_remaining(con)
    print(f"\nVerses with brackets remaining in the restored text: {len(left)}")
    for line in left:
        print(f"  {line}")
    con.close()

    print(f"\nDone ({changed} restoration(s) inserted).")
    if changed:
        print("Now republish:\n"
              "  python3 scripts/17_export_full.py\n"
              "  python3 scripts/81_publish_site_editions.py")


if __name__ == "__main__":
    main()
