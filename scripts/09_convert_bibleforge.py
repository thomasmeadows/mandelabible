#!/usr/bin/env python3
"""09_convert_bibleforge.py — Phase 4: parse BibleForge MySQL dumps into SQLite.

No MySQL server exists, so this reads the gzipped mysqldump files directly:
extracts each CREATE TABLE's column list, creates a matching SQLite table
(prefixed bf_ for the word tables, kept as-is for the lexicons), then parses
the INSERT ... VALUES tuple streams with a quote/escape-aware splitter.

Dumps converted (read-only source, never modified):
  bible_en_all.sql.gz     -> bf_words_en   (word-level KJV: divine/red/implied
                                            markers, orig word linkage)
  bible_original.sql.gz   -> bf_words_orig (word-level Hebrew/Greek + Strong's)
  lexicon_greek.sql.gz    -> lexicon_greek
  lexicon_hebrew.sql.gz   -> lexicon_hebrew

Idempotent: drops and rebuilds each bf_/lexicon table per run.
"""

import gzip
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
BF_DIR = REPO_ROOT / "bible_forge_db"

DUMPS = [  # (file, mysql table, sqlite table)
    ("bible_en_all.sql.gz", "bible_en", "bf_words_en"),
    ("bible_original.sql.gz", "bible_original", "bf_words_orig"),
    ("lexicon_greek.sql.gz", "lexicon_greek", "lexicon_greek"),
    ("lexicon_hebrew.sql.gz", "lexicon_hebrew", "lexicon_hebrew"),
]

COL_RE = re.compile(r"^\s*`(\w+)`")
UNESCAPE = {"\\'": "'", '\\"': '"', "\\\\": "\\", "\\n": "\n",
            "\\r": "\r", "\\t": "\t", "\\0": "\0", "\\Z": "\x1a"}
UNESCAPE_RE = re.compile(r"\\['\"\\nrt0Z]")


def parse_columns(text: str, table: str) -> list:
    m = re.search(rf"CREATE TABLE `{table}` \((.*?)\n\)", text, re.S)
    cols = []
    for line in m.group(1).splitlines():
        cm = COL_RE.match(line)
        if cm:
            cols.append(cm.group(1))
    return cols


def iter_tuples(line: str):
    """Yield value-tuples from one INSERT INTO ... VALUES (...),(...); line."""
    i = line.index("VALUES") + 6
    n = len(line)
    while i < n:
        while i < n and line[i] != "(":
            i += 1
        if i >= n:
            return
        i += 1
        fields, buf, in_str = [], [], False
        while i < n:
            c = line[i]
            if in_str:
                if c == "\\" and i + 1 < n:
                    buf.append(line[i:i + 2])
                    i += 2
                    continue
                if c == "'":
                    in_str = False
                else:
                    buf.append(c)
            elif c == "'":
                in_str = True
                buf.append("\x00str")  # mark as string even if empty
            elif c == ",":
                fields.append("".join(buf))
                buf = []
            elif c == ")":
                fields.append("".join(buf))
                yield fields
                break
            else:
                buf.append(c)
            i += 1
        i += 1


def convert_field(raw: str):
    if raw.startswith("\x00str"):
        s = raw[4:]
        return UNESCAPE_RE.sub(lambda m: UNESCAPE[m.group()], s)
    raw = raw.strip()
    if raw == "NULL":
        return None
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        for fname, mytable, sqtable in DUMPS:
            path = BF_DIR / fname
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            cols = parse_columns(text, mytable)
            con.execute(f"DROP TABLE IF EXISTS {sqtable}")
            con.execute(
                f"CREATE TABLE {sqtable} ({', '.join(cols)})")
            rows, total = [], 0
            for line in text.splitlines():
                if not line.startswith(f"INSERT INTO `{mytable}`"):
                    continue
                for fields in iter_tuples(line):
                    rows.append([convert_field(f) for f in fields])
                    if len(rows) >= 20000:
                        con.executemany(
                            f"INSERT INTO {sqtable} VALUES ({','.join('?'*len(cols))})", rows)
                        total += len(rows)
                        rows = []
            if rows:
                con.executemany(
                    f"INSERT INTO {sqtable} VALUES ({','.join('?'*len(cols))})", rows)
                total += len(rows)
            con.commit()
            print(f"{sqtable}: {total} rows, columns: {', '.join(cols)}")

        con.execute("CREATE INDEX IF NOT EXISTS idx_bf_en_ref ON bf_words_en (book, chapter, verse)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_bf_orig_ref ON bf_words_orig (book, chapter, verse)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_lex_g ON lexicon_greek (strongs)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_lex_h ON lexicon_hebrew (strongs)")
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    main()
