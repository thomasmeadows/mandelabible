#!/usr/bin/env python3
"""48_fold_kjvrestore.py — fold the kjvrestore.org readings into the MVP
(owner directive 2026-07-19: "Fold in all kjvrestore_comparison.md items in
the file, make sure to remove the stars **").

Parses references/kjvrestore_comparison.md and applies each DIVERGES entry's
"their verse" reading as an approved restoration. DIVERGES only (repair
2026-07-19): the file the owner actually reviewed and curated contained only
the DIVERGES section — the first fold wrongly regenerated the report over
the owner's edits (misdiagnosed as a truncated write) and folded
THEY-KEPT-BASE too. Multi-verse contamination guard added the same day:
  - flaw_type `kjvrestore_fold` (highest-id wins in script 17's composition,
    so prior rows are superseded, never deleted);
  - the `**` bold markers around the highlighted phrase are stripped;
  - the site's literal `X` deletion markers are removed (with whitespace
    cleanup), since X marks a word they deleted at that spot.
Duplicate entries for the same verse (several highlights in one verse) carry
the same "their verse" text and collapse to a single row; if two entries for
one verse ever disagree the script refuses and lists them.

Idempotent: kjvrestore_fold rows are rebuilt each run.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "references" / "kjvrestore_comparison.md"
DB_PATH = ROOT / "db" / "mandela.db"

DB_BOOK_ALIASES = {"Revelation": "Revelation of John"}
for _n, _r in (("1", "I"), ("2", "II"), ("3", "III")):
    for _b in ("Samuel", "Kings", "Chronicles", "Corinthians",
               "Thessalonians", "Timothy", "Peter", "John"):
        DB_BOOK_ALIASES[f"{_n} {_b}"] = f"{_r} {_b}"

EVIDENCE = (
    "The KJV Restoration Project (https://kjvrestore.org/), a fellow "
    "restoration effort active since October 2020, marks this reading as "
    "restored pre-change text (yellow highlight on the source page). Folded "
    "in wholesale by owner directive 2026-07-19 from "
    "references/kjvrestore_comparison.md. Advisory corroboration per the "
    "Premise Revision; superseded, never deleted, if a later ruling differs."
)


def clean(text):
    text = text.replace("**", "")
    # site convention: a standalone X marks a deleted word
    text = re.sub(r"(^|\s)X(?=\s|$|[.,;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([.,;:!?)])", r"\1", text)
    return text


def parse_report():
    """{(book, ch, vs): their_verse_cleaned} from DIVERGES/THEY-KEPT-BASE."""
    section, ref, out, dupes = None, None, {}, []
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## ([A-Z-]+) \(\d+\)", line)
        if m:
            section = m.group(1)
            continue
        m = re.match(r"^### (.+?) (\d+):(\d+)", line)
        if m and section == "DIVERGES":
            ref = (m.group(1), int(m.group(2)), int(m.group(3)))
            continue
        if ref and line.startswith("- their verse:"):
            text = clean(line[len("- their verse:"):])
            if ref in out and out[ref] != text:
                dupes.append((ref, out[ref], text))
            out[ref] = text
            ref = None
    if dupes:
        for ref, a, b in dupes:
            print(f"CONFLICT {ref}:\n  {a}\n  {b}")
        raise SystemExit("REFUSING: same-verse entries disagree")
    return out


def main():
    entries = parse_report()
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
            "AND flaw_type!='kjvrestore_fold' ORDER BY id"):
        cur_text[vid] = t

    con.execute("DELETE FROM restorations WHERE flaw_type='kjvrestore_fold'")
    applied, unchanged, missing = 0, 0, []
    for (book, ch, vs), text in sorted(entries.items()):
        vid = vids.get((books.get(DB_BOOK_ALIASES.get(book, book)), ch, vs))
        if vid is None:
            missing.append((book, ch, vs))
            continue
        if text == cur_text[vid]:
            unchanged += 1
            continue
        # multi-verse contamination guard (repair 2026-07-19): script 47's
        # verse parser occasionally swallowed following verses into one
        # "their verse" line; a reading half again longer than our verse is
        # not a word-level restoration — skip and report for manual review.
        if len(text) > 1.5 * len(cur_text[vid]) + 30:
            print(f"SKIP multi-verse suspect {book} {ch}:{vs} "
                  f"({len(cur_text[vid])} -> {len(text)} chars)")
            continue
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "kjvrestore_fold", cur_text[vid], text,
             f"kjvrestore.org restored reading for {book} {ch}:{vs} folded "
             "in wholesale (owner directive 2026-07-19).",
             EVIDENCE, 0.7, "approved"))
        applied += 1
    con.commit()
    con.close()
    print(f"folded {applied} verses (flaw_type kjvrestore_fold); "
          f"{unchanged} already identical; {len(missing)} refs not found: "
          f"{missing}")


if __name__ == "__main__":
    main()
