#!/usr/bin/env python3
"""60_apply_wheat_edits.py — apply the owner's hand-edited final wording for the
wheat verses (references/verses_wheat_apply.md, owner directive 2026-07-21).

These are owner full-verse corrections refining the global corn->wheat output:
ears->heads, a few wheat->grain (to remove the "wheat...wheat" duplications
flagged at II Samuel 17:28 / Amos 8:5), shocks->sheaves, and dropped trailing
clauses (Amos 8:5 "set forth wheat"->"set forth"; Luke 6:1 drops "turning them
in their hands"). Treated like the other manual verse corrections — each becomes
a superseding, owner-approved restoration (flaw_type='wheat_verse_edit'); no
blacklist/whitelist churn (the corn->wheat swap is already recorded by
scripts/59 / global_word_swaps.md, which is left intact).

Source of truth: references/verses_wheat_apply.md (the file on disk is the
verdict; applied verbatim). Idempotent: rows are deleted and re-inserted each
run, and the loader EXCLUDES this flaw_type (scripts/55 & 58 idempotency trap).

After running:  python3 scripts/17_export_full.py
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
SRC = ROOT / "references" / "verses_wheat_apply.md"
FLAW = "wheat_verse_edit"

REF_LINE = re.compile(r"^(.+? \d+:\d+)\s+-\s+(.*)$")
REF = re.compile(r"^(.+) (\d+):(\d+)$")
TAG = re.compile(r"^_.+_$")


def parse():
    """-> {(book,ch,vs): final_text}. Handles the two-line Matthew 12:1 case
    where the text after ' - ' is a lone _flaw_type_ tag and the verse text is
    on the following line."""
    lines = [ln.rstrip() for ln in SRC.read_text(encoding="utf-8").splitlines()]
    out = {}
    i = 0
    while i < len(lines):
        m = REF_LINE.match(lines[i])
        if not m:
            i += 1
            continue
        refstr, text = m.group(1), m.group(2).strip()
        if TAG.match(text):                      # tag only -> text is next line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            text = lines[j].strip() if j < len(lines) else ""
            i = j + 1
        else:
            i += 1
        rm = REF.match(refstr.strip())
        out[(rm.group(1).strip(), int(rm.group(2)), int(rm.group(3)))] = text
    return out


def main():
    con = sqlite3.connect(DB)
    edits = parse()

    # current text per verse, excluding this migration's own rows (idempotency)
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL AND flaw_type != ? ORDER BY id", (FLAW,)):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    curmap, vidmap = {}, {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        key = (names[bid], ch, vs)
        curmap[key] = resto.get(vid, text)
        vidmap[key] = vid

    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    applied, noop, missing = [], [], []
    for ref, final in edits.items():
        if ref not in vidmap:
            missing.append(ref)
            continue
        if final.strip() == curmap[ref].strip():
            noop.append(ref)
            continue
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vidmap[ref], FLAW, curmap[ref], final,
             "Owner full-verse wheat edit 2026-07-21 "
             "(references/verses_wheat_apply.md): ears->heads / wheat->grain / "
             "shocks->sheaves / trimmed clauses. Applied verbatim, merged onto "
             "current text.",
             "Owner-supplied verse wording.", 0.95, "approved"))
        applied.append(ref)
    con.commit()
    con.close()

    print(f"wheat_verse_edit restorations: {len(applied)} applied, "
          f"{len(noop)} already-current (no-op), {len(missing)} missing.")
    for r in applied:
        print("  applied:", r)
    if noop:
        print("  no-op:", ", ".join(f"{b} {c}:{v}" for b, c, v in noop))
    if missing:
        print("  MISSING:", missing)
    print("Now run: python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
