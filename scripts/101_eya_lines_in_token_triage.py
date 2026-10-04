#!/usr/bin/env python3
"""101_eya_lines_in_token_triage.py — mark the token-triage groups whose words
are on the EYA KJV Bible Word Index (owner request 2026-10-04).

For every `### word — N uses` group in
references/word_lists/token_triage_summary_r2.md, the group's forms (its
headword plus the forms listed for it in references/word_lists/
token_list_full.md) are matched case-insensitively against the forms of the
imported index (references/eya-new-words-list/kjv_word_index.tsv, expanded
with script 98's `expand()`). On a match, one line is inserted directly above
the group's `- **OWNER RULING:**` line:

    - **EYA_SUGGESTION:** Kat does not remember this (EYA index: <entries>)

Insert-only: no existing line is changed. Idempotent: a group that already
carries an EYA_SUGGESTION line is skipped.
"""
import csv
import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIAGE = ROOT / "references" / "word_lists" / "token_triage_summary_r2.md"
TOKENS = ROOT / "references" / "word_lists" / "token_list_full.md"
INDEX = ROOT / "references" / "eya-new-words-list" / "kjv_word_index.tsv"

sys.path.insert(0, str(ROOT / "scripts"))
expand = importlib.import_module("98_kjv_word_index_not_blacklisted").expand

ROW = re.compile(r"^\| \d+ \| (\S+) \| (\d+) \| (.*?) \|")   # as script 93
FORM = re.compile(r"(\S+) \(×\d+\)")
GROUP = re.compile(r"^### (\S+) — \d+ uses")
LABEL = "- **EYA_SUGGESTION:**"
TEXT = "Kat does not remember this"


def main():
    groups = {}
    for line in TOKENS.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            groups[m.group(1).lower()] = (
                {f.lower() for f in FORM.findall(m.group(3))} | {m.group(1).lower()})

    eya = {}  # form -> index entries naming it
    with INDEX.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            for form in expand(row["word"]):
                entries = eya.setdefault(form.lower(), [])
                if row["word"] not in entries:
                    entries.append(row["word"])

    lines = TRIAGE.read_text(encoding="utf-8").splitlines(keepends=True)
    out, head, has_eya, added, skipped = [], None, False, 0, 0
    for line in lines:
        m = GROUP.match(line)
        if m:
            head, has_eya = m.group(1).lower(), False
        elif line.startswith(LABEL):
            has_eya = True
        elif line.startswith("- **OWNER RULING") and head:
            forms = groups.get(head, {head})
            entries = []
            for form in sorted(forms):
                for e in eya.get(form, []):
                    if e not in entries:
                        entries.append(e)
            if entries and has_eya:
                skipped += 1
            elif entries:
                out.append(f"{LABEL} {TEXT} (EYA index: {'; '.join(entries)})\n")
                added += 1
            head = None
        out.append(line)

    if added:
        TRIAGE.write_text("".join(out), encoding="utf-8")
    print(f"{TRIAGE.relative_to(ROOT)}: {added} EYA lines added, "
          f"{skipped} groups already marked")


if __name__ == "__main__":
    main()
