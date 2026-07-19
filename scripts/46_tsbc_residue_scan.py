#!/usr/bin/env python3
"""46_tsbc_residue_scan.py — place the owner's OCR'd TSBC residue images
(references/tsbc_residue.md, owner directive 2026-07-18) against the
restored text and check for collisions with existing memories/restorations.

For each `## <image>.png` block:
- candidate verse refs come from the image filename (NNN_book_ch_vs...) and
  any "Book C:V" citations inside the OCR text;
- the block's text is fuzzy-matched (normalized token alignment) against the
  CURRENT composed restored verse for each candidate ref; the best segment
  is extracted as the residue's reading;
- classification:
    MATCH    — residue agrees with the current restored text (corroboration)
    VARIANT  — residue clearly quotes the verse but reads differently
               (candidate pre-change residue; word-level diff shown)
    UNPLACED — no verse quote found / similarity too low
- collision check for every placed ref: existing approved restorations
  (per flaw_type), rows in `memories` (verse_ref/scope_refs), and TSBC
  change/memory rows for the same verse.

Residue evidence rank (owner ruling 2026-07-19, Decision Log #14):
residuals cannot be assumed pre-Mandela-effect. Every VARIANT therefore
gets (a) a VERSION-ATTRIBUTION check — the residue reading is compared to
all 13 witness translations; a close witness match means the scan is
probably quoting that version, not pre-change KJV residue; (b) a
DRASTIC-CHANGE measure — the fraction of the verse's words changed
(single-word swaps rank low; large-section restructurings rank high); and
(c) the memory-alignment count. VARIANTs are sorted candidates-first:
unattributed + drastic on top.

Output: references/tsbc_residue_placements.md (report only — nothing is
applied; VARIANT entries are owner-review candidates). Overwrite guard:
refuses to write a report with fewer placed blocks than an existing one
unless --allow-shrink is passed.
"""
import difflib
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "references" / "tsbc_residue.md"
DB_PATH = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "tsbc_residue_placements.md"

BOOK_TOKENS = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
    "judges": "Judges", "ruth": "Ruth", "samuel": "Samuel",
    "kings": "Kings", "chronicles": "Chronicles", "ezra": "Ezra",
    "nehemiah": "Nehemiah", "esther": "Esther", "job": "Job",
    "psalm": "Psalms", "psalms": "Psalms", "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "song": "Song of Solomon",
    "isaiah": "Isaiah", "jeremiah": "Jeremiah",
    "lamentations": "Lamentations", "ezekiel": "Ezekiel",
    "daniel": "Daniel", "hosea": "Hosea", "joel": "Joel", "amos": "Amos",
    "obadiah": "Obadiah", "jonah": "Jonah", "micah": "Micah",
    "nahum": "Nahum", "habakkuk": "Habakkuk", "zephaniah": "Zephaniah",
    "haggai": "Haggai", "zechariah": "Zechariah", "malachi": "Malachi",
    "matthew": "Matthew", "matrhew": "Matthew", "mathew": "Matthew",
    "mark": "Mark", "luke": "Luke", "john": "John", "acts": "Acts",
    "romans": "Romans", "corinthians": "Corinthians",
    "galatians": "Galatians", "ephesians": "Ephesians",
    "philippians": "Philippians", "colossians": "Colossians",
    "thessalonians": "Thessalonians", "timothy": "Timothy",
    "titus": "Titus", "philemon": "Philemon", "hebrews": "Hebrews",
    "james": "James", "peter": "Peter", "jude": "Jude",
    "revelation": "Revelation of John", "revelations": "Revelation of John",
}
NUMBERED = {"Samuel", "Kings", "Chronicles", "Corinthians",
            "Thessalonians", "Timothy", "Peter"}

SQLITE_DIR = ROOT / "bible_databases" / "formats" / "sqlite"
WITNESSES = [
    "Wycliffe", "Tyndale", "Geneva1599", "DRC",
    "Webster", "RWebster", "YLT", "Darby", "ASV",
    "UKJV", "ACV", "BBE", "BSB",
]

FNAME_RE = re.compile(r"^\d+_(?:(\d|i{1,3})_)?([a-z]+)_(\d+)_(\d+)")
TEXT_REF_RE = re.compile(
    r"\b((?:[1-3]|I{1,3})?\s*[A-Z][a-z]+)\s+(\d+)[:.](\d+)")


def norm_tokens(text):
    text = text.lower().replace("’", "'").replace("“", '"')
    return re.findall(r"[a-z]+(?:'[a-z]+)*", text)


def to_db_book(raw, num=None):
    base = BOOK_TOKENS.get(raw.lower())
    if not base:
        return None
    if base in NUMBERED:
        r = {"1": "I", "2": "II", "3": "III",
             "i": "I", "ii": "II", "iii": "III"}.get(str(num).lower(), "I")
        return f"{r} {base}"
    return base


def best_window(verse_toks, block_toks):
    """Best-matching contiguous window of block_toks vs verse_toks:
    (ratio, start, end)."""
    n = len(verse_toks)
    if not n or len(block_toks) < 4:
        return 0.0, 0, 0
    best = (0.0, 0, 0)
    step = max(1, n // 4)
    for start in range(0, max(1, len(block_toks) - 4), step):
        for width in (n, int(n * 1.3) + 2):
            w = block_toks[start:start + width]
            r = difflib.SequenceMatcher(None, verse_toks, w).ratio()
            if r > best[0]:
                best = (r, start, start + width)
    # refine around the best start
    r0, s0, e0 = best
    for start in range(max(0, s0 - step), min(len(block_toks), s0 + step)):
        for width in (n, int(n * 1.15) + 1, int(n * 1.3) + 2):
            w = block_toks[start:start + width]
            r = difflib.SequenceMatcher(None, verse_toks, w).ratio()
            if r > best[0]:
                best = (r, start, start + width)
    return best


def word_diff(verse_toks, resid_toks):
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, verse_toks, resid_toks).get_opcodes():
        if tag == "equal":
            continue
        out.append(f"'{' '.join(verse_toks[i1:i2])}' -> "
                   f"'{' '.join(resid_toks[j1:j2])}'")
    return out


def load_witness(name):
    path = SQLITE_DIR / f"{name}.db"
    wcon = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    rows = wcon.execute(
        f"SELECT b.name, v.chapter, v.verse, v.text "
        f"FROM {name}_verses v JOIN {name}_books b ON v.book_id = b.id"
    ).fetchall()
    wcon.close()
    return {(b, c, v): t for b, c, v, t in rows}


def main():
    witness_texts = {w: load_witness(w) for w in WITNESSES}
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    books = dict(con.execute(
        "SELECT name, id FROM books WHERE translation='KJV'"))
    verse_of, restored = {}, {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        restored[vid] = t
    texts = {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        texts[(bid, ch, vs)] = (vid, restored.get(vid, text))

    def collisions(bid, ch, vs, book_name):
        vid = texts[(bid, ch, vs)][0]
        rows = con.execute(
            "SELECT flaw_type, status, COUNT(*) FROM restorations "
            "WHERE verse_id=? GROUP BY flaw_type, status", (vid,)).fetchall()
        ref = f"{book_name} {ch}:{vs}"
        mem = con.execute(
            "SELECT COUNT(*) FROM memories WHERE verse_ref=? OR "
            "scope_refs LIKE ?", (ref, f"%{ref}%")).fetchone()[0]
        short = book_name.replace("Revelation of John", "Revelation")
        tsbc = con.execute(
            "SELECT COUNT(*) FROM tsbc_changes WHERE book_name IN (?,?) "
            "AND chapter=? AND verse=?", (book_name, short, ch, vs)
        ).fetchone()[0]
        return rows, mem, tsbc

    blocks = re.split(r"^## ", SRC.read_text(encoding="utf-8"),
                      flags=re.M)[1:]
    match, variant, unplaced = [], [], []
    for block in blocks:
        name, _, body = block.partition("\n")
        name = name.strip()
        body = body.replace("---", " ")
        cands = []
        m = FNAME_RE.match(name)
        if m:
            b = to_db_book(m.group(2), m.group(1))
            if b and b in books:
                cands.append((b, int(m.group(3)), int(m.group(4))))
        for bm in TEXT_REF_RE.finditer(body):
            raw = bm.group(1).strip()
            parts = raw.split()
            num = parts[0] if len(parts) > 1 else None
            b = to_db_book(parts[-1], num)
            if b and b in books:
                c = (b, int(bm.group(2)), int(bm.group(3)))
                if c not in cands:
                    cands.append(c)
        block_toks = norm_tokens(body)
        best = None  # (ratio, ref tuple, window)
        for (b, ch, vs) in cands:
            key = (books[b], ch, vs)
            if key not in texts:
                continue
            vtoks = norm_tokens(texts[key][1])
            r, s, e = best_window(vtoks, block_toks)
            if best is None or r > best[0]:
                best = (r, (b, ch, vs), block_toks[s:e], vtoks)
        if best is None or best[0] < 0.45:
            unplaced.append((name, [f"{b} {c}:{v}" for b, c, v in cands]))
            continue
        r, (b, ch, vs), wtoks, vtoks = best
        ref = f"{b} {ch}:{vs}"
        rows, mem, tsbc = collisions(books[b], ch, vs, b)
        coll = []
        for ft, st, n in rows:
            coll.append(f"{n}× {ft} ({st})")
        info = (name, ref, r, coll, mem, tsbc)
        if r >= 0.985:
            match.append(info)
        else:
            diffs = word_diff(vtoks, wtoks)
            # version attribution: does a witness read like the residue?
            best_w, best_wr = None, 0.0
            for w in WITNESSES:
                wt = witness_texts[w].get((b, ch, vs))
                if not wt:
                    continue
                wr = difflib.SequenceMatcher(
                    None, norm_tokens(wt), wtoks).ratio()
                if wr > best_wr:
                    best_w, best_wr = w, wr
            attributed = best_wr > r and best_wr >= 0.9
            # drastic-change measure: fraction of verse tokens changed
            sm = difflib.SequenceMatcher(None, vtoks, wtoks)
            changed = sum(max(i2 - i1, j2 - j1)
                          for tag, i1, i2, j1, j2 in sm.get_opcodes()
                          if tag != "equal")
            drastic = changed / max(1, len(vtoks))
            variant.append(info + (diffs, texts[(books[b], ch, vs)][1],
                                   " ".join(wtoks), best_w, best_wr,
                                   attributed, drastic))
    con.close()

    lines = [
        "# TSBC Residue Placements",
        "",
        "*Generated by `scripts/46_tsbc_residue_scan.py` from the owner's "
        "OCR scans in `tsbc_residue.md` (report only — nothing applied).* "
        "Each block is matched against the CURRENT restored text. VARIANT "
        "entries are candidate pre-change residue readings for owner "
        "review; collision columns show what already exists for the verse.",
        "",
        f"Blocks: {len(blocks)} — {len(match)} MATCH, {len(variant)} "
        f"VARIANT, {len(unplaced)} UNPLACED",
        "",
        "## VARIANT — residue differs from current restored text",
        "",
        "*Per Decision Log #14: a variant matters only if it is a DRASTIC "
        "change AND is NOT attributable to another bible version (and/or "
        "leans toward memories). Sorted candidates-first: unattributed + "
        "most-drastic on top; version-attributed entries sink to the "
        "bottom.*",
        "",
    ]
    for (name, ref, r, coll, mem, tsbc, diffs, cur, resid,
         best_w, best_wr, attributed, drastic) in sorted(
            variant, key=lambda x: (x[11], -x[12])):
        verdict = (f"ATTRIBUTED to {best_w} ({best_wr:.2f}) — likely a "
                   f"quotation of that version, not KJV residue"
                   if attributed else
                   "NO version match — candidate true residue")
        lines += [f"### {ref} — `{name}` (similarity {r:.2f}, "
                  f"{drastic:.0%} of verse changed)",
                  f"- **{verdict}**"
                  + (f" (closest version: {best_w} {best_wr:.2f})"
                     if not attributed and best_w else ""),
                  f"- collisions: restorations [{', '.join(coll) or 'none'}]"
                  f"; memories: {mem}; tsbc_changes: {tsbc}",
                  f"- CURRENT: {cur}",
                  f"- RESIDUE (normalized): {resid}"]
        for d in diffs[:12]:
            lines.append(f"  - {d}")
        lines.append("")
    lines += ["## MATCH — residue corroborates the current text", ""]
    for (name, ref, r, coll, mem, tsbc) in sorted(match, key=lambda x: x[1]):
        lines.append(f"- {ref} — `{name}` (similarity {r:.2f}; "
                     f"restorations [{', '.join(coll) or 'none'}], "
                     f"memories {mem}, tsbc {tsbc})")
    lines += ["", "## UNPLACED — no verse quote located", ""]
    for name, cands in unplaced:
        lines.append(f"- `{name}` (candidates tried: "
                     f"{', '.join(cands) or 'none'})")
    out = "\n".join(lines) + "\n"

    if OUT.exists() and "--allow-shrink" not in sys.argv:
        old = OUT.read_text(encoding="utf-8")
        if out.count("### ") + out.count("\n- ") < \
           old.count("### ") + old.count("\n- "):
            raise SystemExit("REFUSING to overwrite with smaller report")
    OUT.write_text(out, encoding="utf-8")
    print(f"{len(blocks)} blocks: {len(match)} MATCH, {len(variant)} "
          f"VARIANT, {len(unplaced)} UNPLACED -> {OUT.name}")


if __name__ == "__main__":
    main()
