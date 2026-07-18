#!/usr/bin/env python3
"""30_apply_rare_word_suggestions.py — apply the owner-approved AI suggestions
(references/rare_word_ai_suggestions.md) as restorations (owner directive
2026-07-17).

Per verse: every suggestion's changed span (diff of the verse's original KJV
text vs the suggestion's NEW text) is MERGED onto one evolving verse text —
multi-entry verses (e.g. Deuteronomy 18:11) never overwrite each other's
changes. Overlapping/conflicting spans are NOT applied; they are written to
references/rare_word_merge_conflicts.md for owner resolution.

Each restoration row stores:
- rationale: the per-word AI footnotes ("word -> proposed: rationale")
- evidence: the owner's standard replacement note + GitHub issue link
Conflict guard (Content Modification Protocol): verses already carrying an
approved restoration from another workstream get status 'proposed' instead of
'approved'.

Idempotent: rows are keyed by flaw_type='rare_word_swap' per verse — re-runs
replace this script's own prior rows and never touch other workstreams' rows.
"""
import difflib
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "references" / "rare_word_ai_suggestions.md"
DB_PATH = ROOT / "db" / "mandela.db"
CONFLICTS = ROOT / "references" / "rare_word_merge_conflicts.md"

STANDARD_NOTE = (
    "The word was replaced because it was unlikely to be both accurate for "
    "use during the period and because it was rarely used in the Bible, "
    "appearing only 1-2 times. The human who made this decision believes the "
    "word being replaced is accurate, but the replacement word has been "
    "selected by human, AI, or taste and is believed to be more likely "
    "correct for the period. Other translations have been considered, along "
    "with memories from before the Mandela effect. If you have a better "
    "replacement recommendation, create a GitHub issue with your sources: "
    "https://github.com/thomasmeadows/mandelabible/issues/new — be sure to "
    "search first to confirm your replacement appears in the KJV more than "
    "1-2 times."
)

HEADER_RE = re.compile(r"^## (.+?) → (.*?) — (.+?) (\d+):(\d+)\s*$")
BOOK_ALIASES = {"Revelation": "Revelation of John"}


def spans(old, new):
    """Replacement operations (i1, i2, replacement) from old -> new."""
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    return [(i1, i2, new[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes()
            if tag != "equal"]


def main():
    con = sqlite3.connect(DB_PATH)
    verse_rows = {}
    for vid, book, ch, vs, text in con.execute(
            "SELECT v.id, b.name, v.chapter, v.verse, v.text FROM verses v "
            "JOIN books b ON v.book_id=b.id WHERE v.translation='KJV'"):
        verse_rows[(book, ch, vs)] = (vid, text)

    # parse suggestions grouped by verse
    by_verse = defaultdict(list)  # key -> [(word, proposed, rationale, new)]
    cur = None
    for line in SRC.read_text(encoding="utf-8").splitlines():
        m = HEADER_RE.match(line)
        if m:
            book = BOOK_ALIASES.get(m.group(3).strip(), m.group(3).strip())
            cur = [m.group(1).strip(), m.group(2).strip(), "", "",
                   (book, int(m.group(4)), int(m.group(5)))]
        elif cur is not None and line.startswith("- rationale:"):
            cur[2] = line[len("- rationale:"):].strip()
        elif cur is not None and line.startswith("- NEW:"):
            cur[3] = line[len("- NEW:"):].strip()
            by_verse[cur[4]].append(tuple(cur[:4]))
            cur = None

    applied, conflicts, missing = 0, [], []
    con.execute("DELETE FROM restorations WHERE flaw_type='rare_word_swap'")
    for key, sugg in sorted(by_verse.items()):
        if key not in verse_rows:
            missing.append(key)
            continue
        vid, original = verse_rows[key]
        # collect all spans from all suggestions for this verse
        all_ops, bad = [], False
        for word, proposed, rationale, new in sugg:
            for op in spans(original, new):
                all_ops.append(op + (word,))
        # detect overlaps with differing replacements
        all_ops.sort()
        merged_ops = []
        for op in all_ops:
            if merged_ops and op[0] < merged_ops[-1][1]:
                if (op[0], op[1], op[2]) != merged_ops[-1][:3]:
                    bad = True
                    break
                continue  # identical span from a paired entry — dedupe
            if merged_ops and op[:3] == merged_ops[-1][:3]:
                continue
            merged_ops.append(op)
        ref = f"{key[0]} {key[1]}:{key[2]}"
        if bad:
            conflicts.append((ref, sugg))
            continue
        merged = original
        for i1, i2, repl, _ in sorted(merged_ops, reverse=True):
            merged = merged[:i1] + repl + merged[i2:]
        footnotes = "; ".join(
            f"{w} -> {p}: {r}" for w, p, r, _ in sugg)
        (prior,) = con.execute(
            "SELECT COUNT(*) FROM restorations WHERE verse_id=? AND "
            "status='approved' AND flaw_type!='rare_word_swap'",
            (vid,)).fetchone()
        status = "proposed" if prior else "approved"
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "rare_word_swap", original, merged, footnotes,
             STANDARD_NOTE, 0.7, status))
        applied += 1
    con.commit()

    if conflicts:
        lines = ["# Rare-word merge conflicts (owner resolution needed)", "",
                 "*Generated by `scripts/30_apply_rare_word_suggestions.py`.* "
                 "These verses have suggestions whose changed spans overlap "
                 "with different text — no change was applied.", ""]
        for ref, sugg in conflicts:
            lines.append(f"## {ref}")
            for w, p, r, new in sugg:
                lines += [f"- {w} → {p}", f"  - NEW: {new}"]
            lines.append("")
        CONFLICTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    n_prop = con.execute("SELECT COUNT(*) FROM restorations WHERE "
                         "flaw_type='rare_word_swap' AND status='proposed'"
                         ).fetchone()[0]
    print(f"applied {applied} verse restorations ({n_prop} held as proposed "
          f"due to prior approved restorations); {len(conflicts)} merge "
          f"conflicts -> {CONFLICTS.name if conflicts else 'none'}; "
          f"{len(missing)} refs not found: {missing[:5]}")


if __name__ == "__main__":
    main()
