#!/usr/bin/env python3
"""61_apply_hail_greet.py — apply the owner-approved "hail -> greet" review
(references/hail_review.md, Group A; owner directive 2026-07-21: "apply all
suggestions").

Context: an earlier manual pass turned KJV *salute* into *hail* everywhere. The
owner's rule (hail_review.md) keeps *hail* only for the famous direct-address
acclamations (Group B: "Hail, King of the Jews", Gabriel's "Hail", risen
Christ's "All hail") and the weather/plague *hail* (Group C), and switches every
interpersonal greeting (Group A) to *greet* / *greeteth* — which implies
welcoming in. Per-verse rulings taken verbatim from the Group A table:
  - greet (30 verses), greeteth (Philemon 1:23, III John 1:14 — owner edit),
  - Mark 15:18 KEEP hail (mockery scene — skipped),
  - I Chronicles 18:10 revert to *congratulate* (a victory congratulation,
    not a plain greeting).

Each changed verse becomes a superseding, owner-approved restoration
(flaw_type='hail_greet'), case- and count-preserving over every *hail* token in
the verse. No blacklist/whitelist churn: greet/greets/greeteth are already
whitelisted, and *hail* remains valid (Groups B/C) so it is not blacklisted.

Source of truth: the Group A table in references/hail_review.md (file on disk is
the verdict). Idempotent: rows deleted + re-inserted each run; the loader
EXCLUDES this flaw_type (scripts/55 & 58 idempotency trap).

After running:  python3 scripts/17_export_full.py
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
REVIEW = ROOT / "references" / "hail_review.md"
FLAW = "hail_greet"

REF = re.compile(r"^(.+) (\d+):(\d+)$")
_Hail = re.compile(r"(?<![A-Za-z])Hail(?![A-Za-z])")
_hail = re.compile(r"(?<![A-Za-z])hail(?![A-Za-z])")


def parse_group_a():
    """-> {(book,ch,vs): target|None}. target None means keep hail (skip)."""
    out = {}
    in_a = False
    for ln in REVIEW.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## A."):
            in_a = True
            continue
        if ln.startswith("## B."):
            break
        if not (in_a and ln.startswith("| ")):
            continue
        if ln.startswith("| Verse") or set(ln) <= set("| -"):
            continue
        cols = [c.strip() for c in ln.strip("|").split("|")]
        if len(cols) < 5:
            continue
        refstr, sug = cols[0], cols[4].lower()
        if "keep hail" in sug:
            tgt = None
        elif "congratulate" in sug:
            tgt = "congratulate"
        elif "greeteth" in sug:
            tgt = "greeteth"
        elif "greet" in sug:
            tgt = "greet"
        else:
            continue
        m = REF.match(refstr)
        out[(m.group(1).strip(), int(m.group(2)), int(m.group(3)))] = tgt
    return out


def swap(text, target):
    text = _Hail.sub(target.capitalize(), text)
    text = _hail.sub(target, text)
    return text


def main():
    rulings = parse_group_a()
    con = sqlite3.connect(DB)

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
    applied, skipped, noop, missing = [], [], [], []
    for ref, tgt in rulings.items():
        if tgt is None:
            skipped.append(ref)
            continue
        if ref not in vidmap:
            missing.append(ref)
            continue
        was = curmap[ref]
        final = swap(was, tgt)
        if final == was:
            noop.append(ref)
            continue
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vidmap[ref], FLAW, was, final,
             f"Owner hail-review ruling 2026-07-21 (references/hail_review.md): "
             f"interpersonal greeting hail -> {tgt}. Merged onto current text.",
             "Owner per-verse hail/greet ruling.", 0.95, "approved"))
        applied.append((ref, tgt))
    con.commit()
    con.close()

    print(f"hail_greet restorations: {len(applied)} applied, "
          f"{len(skipped)} kept-as-hail (skipped: "
          f"{', '.join('%s %d:%d' % r for r in skipped)}), "
          f"{len(noop)} no-op, {len(missing)} missing.")
    for (ref, tgt) in applied:
        print(f"  {ref[0]} {ref[1]}:{ref[2]} -> {tgt}")
    if missing:
        print("  MISSING:", missing)
    print("Now run: python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
