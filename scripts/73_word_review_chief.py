#!/usr/bin/env python3
"""73_word_review_chief.py — build the data skeleton for a targeted single-
word review of "chief"/"chiefest" -> "head" (owner request 2026-07-26),
following the Rare-Word Review List Protocol (CLAUDE.md, owner directive
2026-07-22): every occurrence gets its current text, Geneva 1599, and
Standard Oxford Edition (1769 base KJV) readings, plus blank slots for the
King James agent's proposal/alternates/WHITELIST-advice and the owner's
ruling.

Unlike the round-N rarest-lemma reviews, this is not a rarity-ranked batch —
it is every occurrence of one word the owner named directly. Output:
references/word_reviews/word_review_chief_head.md (skeleton; KJ proposals filled in by a
follow-up pass, same as scripts/68/71's merge step).
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
GENEVA = ROOT / "bible_databases" / "formats" / "sqlite" / "Geneva1599.db"
OXFORD = ROOT / "bible_databases" / "formats" / "sqlite" / "KJV.db"
OUT = ROOT / "references" / "word_reviews" / "word_review_chief_head.md"

WORD_RE = re.compile(r"\bchief\w*", re.I)


def load_current(con):
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL ORDER BY id"):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    cur = {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        key = (names[bid], ch, vs)
        cur[key] = resto.get(vid, text)
    return cur


def load_geneva():
    con = sqlite3.connect(GENEVA)
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM Geneva1599_books")}
    out = {}
    for bid, ch, vs, text in con.execute(
            "SELECT book_id, chapter, verse, text FROM Geneva1599_verses"):
        key = (names[bid], ch, vs)
        if key not in out:
            out[key] = text
    con.close()
    return out


def load_oxford():
    con = sqlite3.connect(OXFORD)
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM KJV_books")}
    out = {}
    for bid, ch, vs, text in con.execute(
            "SELECT book_id, chapter, verse, text FROM KJV_verses"):
        out[(names[bid], ch, vs)] = text
    con.close()
    return out


def main():
    con = sqlite3.connect(DB)
    cur = load_current(con)
    con.close()
    geneva = load_geneva()
    oxford = load_oxford()

    hits = [(ref, text) for ref, text in cur.items() if WORD_RE.search(text)]
    hits.sort(key=lambda r: (r[0][0], r[0][1], r[0][2]))

    forms = sorted({m.group(0).lower() for _, t in hits for m in WORD_RE.finditer(t)})

    out = [
        "# Word Review — chief / chiefest -> head",
        "",
        f"*Every occurrence of \"chief\" (forms: {', '.join(forms)}) over the "
        "current output (base KJV + all approved restorations), owner request "
        "2026-07-26. Not a rarity-ranked round — a targeted single-word sweep "
        "proposing \"head\" in place of \"chief\". For each verse: current text, "
        "Geneva 1599, and Standard Oxford Edition (1769 base KJV); the King "
        "James agent's proposed replacement verse and alternate word/phrase "
        "suggestions (advice **WHITELIST** where \"chief\" is part of a fixed "
        "title/proper name that should not change); then a blank owner ruling.*",
        "",
        f"**{len(hits)} occurrences.**",
        "",
    ]

    for ref, text in hits:
        b, c, v = ref
        gen = geneva.get(ref, "(not in Geneva)")
        oxf = oxford.get(ref, "(not found in Oxford base)")
        out.append(f"## {b} {c}:{v}")
        out.append(f"- text: {text}")
        out.append(f"- Geneva 1599: {gen}")
        out.append(f"- Oxford (KJV 1769): {oxf}")
        out.append("- KJ proposal: (pending — King James agent)")
        out.append("- alternates: (pending — King James agent)")
        out.append("- advice: (pending — King James agent)")
        out.append("- owner ruling: ")
        out.append("")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(hits)} occurrences, forms={forms}")


if __name__ == "__main__":
    main()
