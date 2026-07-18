#!/usr/bin/env python3
"""23_rare_word_witnesses.py — gather local witness renderings for rare-word verses.

For every entry in references/rare_word_replacements.md after the owner-audited
line (default 132), fetch the same verse from the local English witness
translations in bible_databases/formats/sqlite/ and store the renderings in
db/mandela.db (table rare_word_witnesses). Then export markdown batches for
review, each entry showing OLD, the current auto-selected NEW, and every
witness rendering — evidence for choosing a replacement, which may be one word
or a phrase.

Idempotent: the table is rebuilt from scratch on each run; batch export
overwrites the requested batch files.

Usage:
  python3 scripts/23_rare_word_witnesses.py                 # build table only
  python3 scripts/23_rare_word_witnesses.py --export 1 3    # also write batches 1..3
  python3 scripts/23_rare_word_witnesses.py --batch-size 40
"""
import argparse
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "references" / "rare_word_replacements.md"
DB_PATH = ROOT / "db" / "mandela.db"
SQLITE_DIR = ROOT / "bible_databases" / "formats" / "sqlite"
BATCH_DIR = ROOT / "references" / "rare_word_witness_batches"

# Order matters in the export: period witnesses first, then literal/revision
# lines, then modern public-domain renderings.
WITNESSES = [
    "Wycliffe", "Tyndale", "Geneva1599", "DRC",
    "Webster", "RWebster", "YLT", "Darby", "ASV",
    "UKJV", "ACV", "BBE", "BSB",
]

AUDITED_THROUGH_LINE = 132  # owner has reviewed entries up to this line

HEADER_RE = re.compile(r"^## (.+?) — (.+?) (\d+):(\d+)\s*$")


def parse_entries(start_line):
    entries = []
    cur = None
    for lineno, line in enumerate(MD_PATH.read_text(encoding="utf-8").splitlines(), 1):
        m = HEADER_RE.match(line)
        if m:
            cur = {"line": lineno, "title": m.group(1), "book": m.group(2),
                   "chapter": int(m.group(3)), "verse": int(m.group(4)),
                   "source": "", "old": "", "new": ""}
            if lineno > start_line:
                entries.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith("- source:"):
            cur["source"] = line[len("- source:"):].strip()
        elif line.startswith("- OLD:"):
            cur["old"] = line[len("- OLD:"):].strip()
        elif line.startswith("- NEW:"):
            cur["new"] = line[len("- NEW:"):].strip()
    return entries


def load_witness(name):
    """Return {(book, chapter, verse): text} for one translation."""
    path = SQLITE_DIR / f"{name}.db"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    rows = con.execute(
        f"SELECT b.name, v.chapter, v.verse, v.text "
        f"FROM {name}_verses v JOIN {name}_books b ON v.book_id = b.id"
    ).fetchall()
    con.close()
    return {(b, c, v): t for b, c, v, t in rows}


def build_table(entries):
    con = sqlite3.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS rare_word_witnesses")
    con.execute(
        """CREATE TABLE rare_word_witnesses (
               entry_idx INTEGER,          -- 1-based order within unaudited entries
               md_line INTEGER,            -- header line in rare_word_replacements.md
               title TEXT,                 -- 'oldword → newword' header text
               book TEXT, chapter INTEGER, verse INTEGER,
               source TEXT, old_text TEXT, new_text TEXT,
               witness TEXT, witness_text TEXT
           )"""
    )
    for w in WITNESSES:
        verses = load_witness(w)
        rows = []
        for i, e in enumerate(entries, 1):
            text = verses.get((e["book"], e["chapter"], e["verse"]))
            if text:
                rows.append((i, e["line"], e["title"], e["book"], e["chapter"],
                             e["verse"], e["source"], e["old"], e["new"], w, text))
        con.executemany(
            "INSERT INTO rare_word_witnesses VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
        print(f"{w}: {len(rows)}/{len(entries)} verses found")
    con.commit()
    con.close()


def export_batches(entries, first, last, batch_size):
    BATCH_DIR.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    for n in range(first, last + 1):
        lo = (n - 1) * batch_size + 1
        hi = min(n * batch_size, len(entries))
        if lo > len(entries):
            break
        lines = [f"# Rare word witness batch {n:04d} — entries {lo}–{hi} "
                 f"(of {len(entries)} unaudited)", ""]
        for i in range(lo, hi + 1):
            e = entries[i - 1]
            lines += [f"## {e['title']} — {e['book']} {e['chapter']}:{e['verse']}",
                      f"- md line: {e['line']}",
                      f"- current source: {e['source']}",
                      f"- OLD: {e['old']}",
                      f"- CUR: {e['new']}"]
            for w, t in con.execute(
                    "SELECT witness, witness_text FROM rare_word_witnesses "
                    "WHERE entry_idx = ? ORDER BY rowid", (i,)):
                lines.append(f"- {w}: {t.strip()}")
            lines.append("")
        out = BATCH_DIR / f"batch_{n:04d}.md"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({hi - lo + 1} entries)")
    con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-line", type=int, default=AUDITED_THROUGH_LINE)
    ap.add_argument("--batch-size", type=int, default=40)
    ap.add_argument("--export", nargs=2, type=int, metavar=("FIRST", "LAST"),
                    help="export batch files FIRST..LAST")
    args = ap.parse_args()

    entries = parse_entries(args.start_line)
    print(f"{len(entries)} unaudited entries (after line {args.start_line})")
    build_table(entries)
    if args.export:
        export_batches(entries, args.export[0], args.export[1], args.batch_size)


if __name__ == "__main__":
    main()
