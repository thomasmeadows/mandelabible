#!/usr/bin/env python3
"""51_apply_residue_proposals.py — owner directive 2026-07-20: "Add BLEND and
ADOPT-RESIDUE entries in the residue_verse_proposals_1.md and
residue_verse_proposals_2.md. Make sure to use the SUGGESTED verse precisely."

Applies every BLEND / ADOPT-RESIDUE entry from both files, using each
entry's SUGGESTED line verbatim as the restoration text. KEEP-CURRENT
entries are left untouched (no restoration row).

flaw_type `residue_verse_proposal` (highest-id wins in script 17's
composition — superseded, never deleted). Idempotent: rebuilt each run.

Two same-verse conflicts were found across the two files and are resolved
here rather than silently merged — see NOTES below and the run-time report:

  - Genesis 22:1: three entries (files 115, 116, 117) all propose the same
    SUGGESTED text ("tried" for "tempt") under an explicit owner decision
    dated 2026-07-19 — one restoration applied, duplicates collapsed.
  - Genesis 3:15: two DIFFERENT proposals for the same verse —
      * `222_genesis_3_15_gotquest.jpg` (batch 1... actually batch 2) is
        BLEND with an explicit "Owner Override 7/19/26" and keeps
        thee/thy/thou throughout: "he shall bruise thy head".
      * `221_genesis_3_15.jpg` is ADOPT-RESIDUE, an AI recommendation only
        (no owner ruling recorded), reading "it shall bruise thy head".
    The owner-overridden entry (222) is applied; 221 is recorded as
    NOT applied and flagged for owner ruling since it conflicts.
  - John 15:22: two ADOPT-RESIDUE entries, `86_john_15_22_res2.png`
    ("cloke") and `85_john_15_22_res1.png` ("cloak") — same word, two
    spellings, neither an owner override. `86`'s SUGGESTED text ("cloke")
    is applied because its own assessment cites an exact KJV.db match
    (the project's authoritative base text); `85` is recorded as NOT
    applied and flagged.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

EVIDENCE = (
    "references/residue_verse_proposals_1.md and _2.md (TSBC residue "
    "placements review, owner directive 2026-07-19/20): BLEND/ADOPT-RESIDUE "
    "entries applied using the SUGGESTED verse text verbatim."
)

# (book, chapter, verse, SUGGESTED text exactly as written, source filename,
#  recommendation, note)
ENTRIES = [
    ("Genesis", 22, 1,
     "And it came to pass after these things, that God tried Abraham, and "
     "said unto him, Abraham: and he said, Behold, here I am.",
     "117_genesis_22_1_res4.png / 116_genesis_22_1_res3.png / "
     "115_genesis_22_1_res1.png",
     "BLEND",
     "Owner decision 7/19/26: 'tempt' replaced with 'tried' "
     "(three independent residue scans agree; tempt implies desire, a "
     "trial does not)."),

    ("Matthew", 3, 12,
     "Whose fan is in his hand, and he will throughly purge his floor, and "
     "gather his wheat into the garner; but he will burn up the chaff with "
     "unquenchable fire.",
     "123_matthew_3_12_res1.png", "BLEND",
     "'garner'/'unquenchable fire' restored — verbatim match to KJV.db, "
     "Geneva1599, and Tyndale."),

    ("Matthew", 28, 20,
     "Teaching them to observe all things whatsoever I have commanded you: "
     "and, Lo, I am with you alway, even unto the end of the Age. Amen.",
     "130_matthew_28_20_res1.png", "BLEND",
     "'always' -> 'alway', matches KJV.db archaic spelling."),

    ("John", 14, 6,
     "I am the way, the truth and the life. No man comes to the Father "
     "except through me.",
     "233_john_14_6.jpg", "BLEND",
     "Owner Override 7/19/26: authentic memory."),

    ("John", 15, 22,
     "If I had not come and spoken unto them, they had not had sin: but "
     "now they have no cloke for their sin.",
     "86_john_15_22_res2.png", "ADOPT-RESIDUE",
     "'cloke' matches KJV.db and Geneva1599 exactly; applied over the "
     "competing 'cloak' spelling from 85_john_15_22_res1.png (see NOT "
     "APPLIED list)."),

    ("Jonah", 3, 10,
     "And God saw their works, that they turned from their evil way; and "
     "God relented of the plagues which He had said that He would inflict "
     "upon them; and He did it not.",
     "98_jonah_3_10_res3.png", "BLEND",
     "Owner Override 7/19/26: God does not commit evil and cannot "
     "'repent' of it."),

    ("Psalms", 119, 83,
     "For I am become like a vessel in the smoke; yet do I not forget thy "
     "statutes.",
     "109_psalms_119_83_res1.png", "BLEND",
     "Owner Override 7/19/26: wineskin overrides 'bottle' (a wealthy-only "
     "item); 'vessel'/clay jar is more accurate in context."),

    ("Genesis", 3, 15,
     "And I will put enmity between thee and the woman, and between thy "
     "seed and her seed; he shall bruise thy head, and thou shalt bruise "
     "his heel.",
     "222_genesis_3_15_gotquest.jpg", "BLEND",
     "Owner Override 7/19/26: 'bruise' (birth/life imagery, not violence); "
     "thee/thy/thou pronouns retained. Applied over the competing "
     "'it shall bruise... it/bruise both times' AI recommendation from "
     "221_genesis_3_15.jpg (see NOT APPLIED list; no owner ruling recorded "
     "on that entry)."),

    ("John", 12, 24,
     "Verily, verily, I say unto you, Except a grain of corn fall into the "
     "ground and die, it abideth alone: but if it die, it bringeth forth "
     "much fruit.",
     "84_john_12_24_25_res1.png", "ADOPT-RESIDUE",
     "Owner-override 7/16/26: word order 'grain of corn' (not 'corn of "
     "wheat' or 'grain of wheat')."),

    ("Mark", 1, 19,
     "And when He had gone a little farther thence, He saw James the son "
     "of Zebedee, and John his brother, who also were in the ship mending "
     "their nets.",
     "131_mark_1_19_wfg1.png", "ADOPT-RESIDUE",
     "'ship...mending their nets' is the authentic period AV wording; "
     "UKJV 1.00 match reflects shared original vocabulary, not paraphrase."),

    ("Isaiah", 13, 21,
     "But wild beasts of the desert shall lie there; and their houses "
     "shall be full of doleful creatures; and owls shall dwell there, and "
     "wild goats shall dance there.",
     "172_isaiah_13_21_1911bhb_p652.png", "ADOPT-RESIDUE",
     "'doleful creatures' is the genuine 1611 AV idiom; 'howlings' is a "
     "later plainer paraphrase."),

    ("John", 11, 16,
     "Then said Thomas, which is called Didymus, unto his fellowdisciples, "
     "Let us also go, that we may die with Him.",
     "79_john_11_16_res1.png", "ADOPT-RESIDUE",
     "Current text had an un-restored gap ('-disciples'); residue supplies "
     "the missing 'fellow' — restored as the genuine period compound "
     "'fellowdisciples'."),

    ("Romans", 8, 28,
     "And we know that all things work together for good to them that "
     "love God, to them who are called according to His purpose.",
     "33_Screenshot_2019-12-28-08-34-18.png", "ADOPT-RESIDUE",
     "Restores the AV's deliberate that/who variation between clauses "
     "(distinctive AV style)."),
]

# recorded but deliberately NOT applied — same-verse conflicts flagged for
# the owner rather than silently overwritten
NOT_APPLIED = [
    ("John", 15, 22, "85_john_15_22_res1.png",
     "If I had not come and spoken unto them, they had not had sin: but "
     "now they have no cloak for their sin.",
     "conflicts with 86_john_15_22_res2.png ('cloke'), which was applied "
     "instead — same word, competing spelling, neither is an owner "
     "override; flagged for owner ruling."),
    ("Genesis", 3, 15, "221_genesis_3_15.jpg",
     "And I will put enmity between thee and the woman, and between thy "
     "seed and her seed; it shall bruise thy head, and thou shalt bruise "
     "his heel.",
     "conflicts with 222_genesis_3_15_gotquest.jpg, which carries an "
     "explicit Owner Override (7/19/26) and was applied instead; this "
     "entry ('it'/bruise-bruise) is an AI recommendation only — flagged "
     "for owner ruling."),
]


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute(
        "SELECT name, id FROM books WHERE translation='KJV'"))
    vids, cur_text = {}, {}
    for vid, bid, ch, vs, t in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        vids[(bid, ch, vs)] = vid
        cur_text[vid] = t
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type!='residue_verse_proposal' ORDER BY id"):
        cur_text[vid] = t

    con.execute(
        "DELETE FROM restorations WHERE flaw_type='residue_verse_proposal'")

    seen, applied, unchanged, missing = set(), 0, 0, []
    for book, ch, vs, text, source, rec, note in ENTRIES:
        key = (book, ch, vs)
        if key in seen:
            continue  # duplicate SUGGESTED text for the same verse
        seen.add(key)
        vid = vids.get((books.get(book), ch, vs))
        if vid is None:
            missing.append(key)
            continue
        if text == cur_text[vid]:
            unchanged += 1
            continue
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "residue_verse_proposal", cur_text[vid], text,
             f"{rec} ({source}): {note}", EVIDENCE, 0.8, "approved"))
        applied += 1
    con.commit()
    con.close()

    print(f"applied {applied} verses (flaw_type residue_verse_proposal); "
          f"{unchanged} already identical; {len(missing)} refs not found: "
          f"{missing}")
    print(f"\n{len(NOT_APPLIED)} conflicting entries recorded but NOT "
          "applied (owner ruling needed):")
    for book, ch, vs, source, text, why in NOT_APPLIED:
        print(f"  - {book} {ch}:{vs} ({source}): {why}")
        print(f"    would-be text: {text}")


if __name__ == "__main__":
    main()
