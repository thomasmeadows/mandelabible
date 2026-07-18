#!/usr/bin/env python3
"""39_rare_word_witnesses_round2.py — witness batches for the RESTORED-text rare words.

Round 2 of the rare-word review (owner directive 2026-07-18): the 336 rare
groups found by re-tokenizing the restored text (scripts/36, listed in
references/rare_words_restored.md) are exported as witness batches for the
king-james agent, one entry per group, each occurrence showing the CURRENT
restored verse text plus every local witness rendering.

Batches are written to references/rare_word_witness_batches_2/ (the round-2
folder — round-1 files in rare_word_witness_batches/ are never touched).
Refuses to overwrite an existing batch file with a smaller one
(generated-artifact guard).

Usage:
  python3 scripts/39_rare_word_witnesses_round2.py            # all batches
  python3 scripts/39_rare_word_witnesses_round2.py --batch-size 40
"""
import argparse
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "references" / "rare_words_restored.md"
DB_PATH = ROOT / "db" / "mandela.db"
SQLITE_DIR = ROOT / "bible_databases" / "formats" / "sqlite"
BATCH_DIR = ROOT / "references" / "rare_word_witness_batches_2"

WITNESSES = [
    "Wycliffe", "Tyndale", "Geneva1599", "DRC",
    "Webster", "RWebster", "YLT", "Darby", "ASV",
    "UKJV", "ACV", "BBE", "BSB",
]

ENTRY_RE = re.compile(r"^- \*\*(.+?)\*\* — (.+?) — (.+?)\s*$")
REF_RE = re.compile(r"^(.+?) (\d+):(\d+)$")


def parse_groups():
    groups = []
    for line in MD_PATH.read_text(encoding="utf-8").splitlines():
        m = ENTRY_RE.match(line)
        if not m:
            continue
        word, forms, refs_raw = m.groups()
        refs = []
        for r in refs_raw.split("; "):
            rm = REF_RE.match(r.strip())
            if rm:
                refs.append((rm.group(1), int(rm.group(2)), int(rm.group(3))))
        groups.append({"word": word, "forms": forms, "refs": refs})
    return groups


def load_restored():
    """(book, chapter, verse) -> current restored text."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))
    final = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        final[vid] = t
    out = {}
    for vid, book_id, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        out[(books[book_id], ch, vs)] = final.get(vid, orig)
    con.close()
    return out


def load_witness(name):
    path = SQLITE_DIR / f"{name}.db"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    rows = con.execute(
        f"SELECT b.name, v.chapter, v.verse, v.text "
        f"FROM {name}_verses v JOIN {name}_books b ON v.book_id = b.id"
    ).fetchall()
    con.close()
    return {(b, c, v): t for b, c, v, t in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=40)
    args = ap.parse_args()

    groups = parse_groups()
    print(f"{len(groups)} rare groups parsed from {MD_PATH.name}")
    restored = load_restored()
    witnesses = {w: load_witness(w) for w in WITNESSES}

    BATCH_DIR.mkdir(exist_ok=True)
    bs = args.batch_size
    n_batches = (len(groups) + bs - 1) // bs
    for n in range(1, n_batches + 1):
        lo, hi = (n - 1) * bs, min(n * bs, len(groups))
        lines = [f"# Restored-text rare word batch {n:04d} — groups "
                 f"{lo + 1}–{hi} (of {len(groups)})", ""]
        for g in groups[lo:hi]:
            lines.append(f"## {g['word']} — {g['forms']}")
            for book, ch, vs in g["refs"]:
                lines.append(f"### {book} {ch}:{vs}")
                cur = restored.get((book, ch, vs))
                lines.append(f"- CUR: {cur.strip() if cur else '(verse not found)'}")
                for w in WITNESSES:
                    t = witnesses[w].get((book, ch, vs))
                    if t:
                        lines.append(f"- {w}: {t.strip()}")
                lines.append("")
        out = BATCH_DIR / f"batch_{n:04d}.md"
        text = "\n".join(lines) + "\n"
        if out.exists() and len(text) < len(out.read_text(encoding="utf-8")):
            raise SystemExit(f"REFUSING to overwrite {out} with smaller content")
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({hi - lo} groups)")


if __name__ == "__main__":
    main()
