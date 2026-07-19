#!/usr/bin/env python3
"""41_fold_back_proposals.py — fold the approved witness-pass proposals back
into references/rare_word_replacements.md (roadmap Phase item, Decision Log
#12; owner directive 2026-07-17: MERGE multi-entry verses, never overwrite).

Source of truth: references/rare_word_ai_suggestions.md (the owner-reviewed
split of the batch proposals — the same file script 30 applied to the db).
For each verse, every suggestion's changed span (diff of the verse's original
KJV text vs the suggestion's NEW) is merged onto ONE evolving verse text —
identical logic to script 30 — so multi-entry verses (up to 6 proposals)
compose instead of clobbering each other. Overlapping spans with differing
text are NOT applied; they are listed in
references/rare_word_fold_back_conflicts.md for owner resolution.

The md is edited conservatively: ONLY the content of `- NEW:` lines changes
(one line stays one line), so header lines, line numbers (referenced by the
witness batches' `md line:` fields), and every other byte are preserved.
A dated backup of the md is written to
references/removed_words/pre_triage_backups/ before any change (and never
overwritten if it already exists — generated-artifact guard).

Idempotent: re-running recomputes the same merged NEW values.
"""
import difflib
import re
import shutil
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "references" / "rare_word_replacements.md"
SRC = ROOT / "references" / "rare_word_ai_suggestions.md"
DB_PATH = ROOT / "db" / "mandela.db"
CONFLICTS = ROOT / "references" / "rare_word_fold_back_conflicts.md"
BACKUP = (ROOT / "references" / "removed_words" / "pre_triage_backups" /
          "rare_word_replacements_pre_foldback_2026-07-18.md")

HEADER_SRC_RE = re.compile(r"^## (.+?) → (.*?) — (.+?) (\d+):(\d+)\s*$")
HEADER_MD_RE = re.compile(r"^## .+? — (.+?) (\d+):(\d+)\s*$")
BOOK_ALIASES = {"Revelation": "Revelation of John"}


def spans(old, new):
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    return [(i1, i2, new[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes()
            if tag != "equal"]


def merged_texts():
    """(book, ch, vs) -> merged NEW text; plus conflict list."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    verse_text = {}
    for book, ch, vs, text in con.execute(
            "SELECT b.name, v.chapter, v.verse, v.text FROM verses v "
            "JOIN books b ON v.book_id=b.id WHERE v.translation='KJV'"):
        verse_text[(book, ch, vs)] = text
    con.close()

    by_verse = defaultdict(list)
    cur = None
    for line in SRC.read_text(encoding="utf-8").splitlines():
        m = HEADER_SRC_RE.match(line)
        if m:
            book = BOOK_ALIASES.get(m.group(3).strip(), m.group(3).strip())
            cur = [m.group(1).strip(), "",
                   (book, int(m.group(4)), int(m.group(5)))]
        elif cur is not None and line.startswith("- NEW:"):
            cur[1] = line[len("- NEW:"):].strip()
            by_verse[cur[2]].append((cur[0], cur[1]))
            cur = None

    merged, conflicts = {}, []
    for key, sugg in sorted(by_verse.items()):
        if key not in verse_text:
            continue
        original = verse_text[key]
        all_ops = []
        for word, new in sugg:
            for op in spans(original, new):
                all_ops.append(op + (word,))
        all_ops.sort()
        ops, bad = [], False
        for op in all_ops:
            if ops and op[0] < ops[-1][1]:
                if (op[0], op[1], op[2]) != ops[-1][:3]:
                    bad = True
                    break
                continue
            if ops and op[:3] == ops[-1][:3]:
                continue
            ops.append(op)
        if bad:
            conflicts.append((key, sugg))
            continue
        text = original
        for i1, i2, repl, _ in sorted(ops, reverse=True):
            text = text[:i1] + repl + text[i2:]
        merged[key] = text
    return merged, conflicts


def main():
    merged, conflicts = merged_texts()
    print(f"{len(merged)} verses with merged fold-back text; "
          f"{len(conflicts)} span conflicts")

    if not BACKUP.exists():
        BACKUP.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(MD_PATH, BACKUP)
        print(f"backup -> {BACKUP.relative_to(ROOT)}")

    lines = MD_PATH.read_text(encoding="utf-8").splitlines()
    cur_key, updated = None, 0
    for i, line in enumerate(lines):
        m = HEADER_MD_RE.match(line)
        if m:
            cur_key = (m.group(1).strip(), int(m.group(2)), int(m.group(3)))
            continue
        if (cur_key in merged and line.startswith("- NEW:")
                and line[len("- NEW:"):].strip() != merged[cur_key]):
            lines[i] = f"- NEW: {merged[cur_key]}"
            updated += 1
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"updated {updated} NEW lines in {MD_PATH.name}")

    if conflicts:
        out = ["# Fold-back span conflicts (owner resolution needed)", "",
               "*Generated by `scripts/41_fold_back_proposals.py`.* These "
               "verses have suggestions whose changed spans overlap with "
               "different text — their md entries were left unchanged.", ""]
        for key, sugg in conflicts:
            out.append(f"## {key[0]} {key[1]}:{key[2]}")
            for word, new in sugg:
                out += [f"- {word}", f"  - NEW: {new}"]
            out.append("")
        CONFLICTS.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"conflicts -> {CONFLICTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
