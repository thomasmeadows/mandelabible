#!/usr/bin/env python3
"""45_manual_verse_corrections.py — apply the owner's manual verse
corrections (owner directive 2026-07-18).

1. references/manual_verse_corrections.md — owner-supplied full-verse
   readings (`Book C:V - "text"`), applied as approved restorations,
   flaw_type `manual_verse_correction`. These are owner memory rulings and
   supersede ALL earlier rows for the verse (highest-id wins in script 17)
   — including the Genesis 1:2 owner_override from script 38, which this
   file's newer "face of the earth" reading replaces.

2. Alleluia -> Hallelujah bible-wide (owner ruling 2026-07-18), applied to
   the composed restored text (Revelation 19:1,3,4,6), same flaw_type with
   its own rationale. Case preserved.

Idempotent: manual_verse_correction rows are rebuilt each run; superseded
rows are kept, never deleted.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "references" / "manual_verse_corrections.md"
DB_PATH = ROOT / "db" / "mandela.db"

LINE_RE = re.compile(r'^(.+?) (\d+):(\d+)\s*-\s*"(.*)"\s*$')
BOOK_ALIASES = {"Revelation": "Revelation of John"}

EVIDENCE = (
    "Owner-ruled memory correction (2026-07-18), "
    "references/manual_verse_corrections.md. If you have evidence for a "
    "different reading, create a GitHub issue with your sources: "
    "https://github.com/thomasmeadows/mandelabible/issues/new"
)


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute(
        "SELECT name, id FROM books WHERE translation='KJV'"))
    vids = {}
    for vid, book_id, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        vids[(book_id, ch, vs)] = (vid, text)

    base = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type!='manual_verse_correction' ORDER BY id"):
        base[vid] = t

    con.execute(
        "DELETE FROM restorations WHERE flaw_type='manual_verse_correction'")

    # 1. full-verse corrections from the md
    applied, unparsed = 0, []
    for raw in MD_PATH.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        m = LINE_RE.match(raw.strip())
        if not m:
            unparsed.append(raw.strip()[:60])
            continue
        book = BOOK_ALIASES.get(m.group(1).strip(), m.group(1).strip())
        ch, vs, reading = int(m.group(2)), int(m.group(3)), m.group(4)
        key = (books.get(book), ch, vs)
        if key not in vids:
            unparsed.append(f"ref not found: {raw.strip()[:60]}")
            continue
        vid, orig = vids[key]
        cur = base.get(vid, orig)
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "manual_verse_correction", cur, reading,
             "Owner-supplied full-verse correction "
             "(manual_verse_corrections.md, 2026-07-18)",
             EVIDENCE, 0.95, "approved"))
        base[vid] = reading
        applied += 1
    print(f"{applied} manual verse corrections applied; "
          f"{len(unparsed)} unparsed lines: {unparsed}")

    # 2. Alleluia -> Hallelujah bible-wide
    word_re = re.compile(r"\b[Aa]lleluia\b")
    fixed = 0
    for (bid, ch, vs), (vid, orig) in vids.items():
        cur = base.get(vid, orig)
        if not word_re.search(cur):
            continue
        new = word_re.sub(
            lambda m: "Hallelujah" if m.group(0)[0] == "A" else "hallelujah",
            cur)
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "manual_verse_correction", cur, new,
             "Alleluia -> Hallelujah (owner ruling 2026-07-18)",
             EVIDENCE, 0.95, "approved"))
        fixed += 1
    con.commit()
    con.close()
    print(f"Alleluia -> Hallelujah in {fixed} verses")


if __name__ == "__main__":
    main()
