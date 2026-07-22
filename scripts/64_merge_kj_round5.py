#!/usr/bin/env python3
"""64_merge_kj_round5.py — merge the King James agent's suggestion files into
references/rare_word_round5_review.md (Rare-Word Review List Protocol,
CLAUDE.md, owner directive 2026-07-22).

Usage:
    python3 scripts/64_merge_kj_round5.py <suggestions1.md> [<suggestions2.md> ...]

Each suggestions file holds strict blocks:

    ## <word>
    - KJ proposal: <Book C:V> — <full verse or (no change — reason)>
    - KJ proposal: ...            (one per occurrence verse)
    - alternates: <w1, w2, w3>
    - advice: <WHITELIST — proper noun | keep | swap>

For every matching `#### <a name=...>word — ...` entry in the review, the three
"(pending — King James agent)" lines are replaced by the agent's lines (KJ
proposal lines may be several). Idempotent + safe: an entry whose fields are
already filled is only re-replaced if the new content differs AND --force is
given; otherwise it is left alone (Generated Artifacts are permanent).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "references" / "rare_word_round5_review.md"
PENDING = "(pending — King James agent)"


def parse_suggestions(paths):
    sugg = {}
    for p in paths:
        word = None
        for ln in Path(p).read_text(encoding="utf-8").splitlines():
            m = re.match(r"^## (\S+)\s*$", ln)
            if m:
                word = m.group(1).lower()
                sugg[word] = []
            elif word and ln.startswith(("- KJ proposal:", "- alternates:",
                                         "- advice:")):
                sugg[word].append(ln)
    return sugg


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    if not args:
        sys.exit(__doc__)
    sugg = parse_suggestions(args)

    lines = REVIEW.read_text(encoding="utf-8").splitlines()
    out, i = [], 0
    merged, skipped_filled, missing = [], [], []
    while i < len(lines):
        ln = lines[i]
        m = re.match(r'^#### <a name="[^"]+"></a>(.+?) — ', ln)
        if not m:
            out.append(ln); i += 1
            continue
        word = m.group(1).lower()
        # collect the entry: up to (not incl.) the owner-ruling line
        j = i
        entry = []
        while j < len(lines) and not lines[j].startswith("- owner ruling:"):
            entry.append(lines[j]); j += 1
        field_idx = [k for k, e in enumerate(entry)
                     if e.startswith(("- KJ proposal:", "- alternates:", "- advice:"))]
        filled = [k for k in field_idx if PENDING not in entry[k]]
        if word not in sugg:
            if field_idx and not filled:
                missing.append(word)
            out.extend(entry); i = j
            continue
        if filled and not force:
            skipped_filled.append(word)
            out.extend(entry); i = j
            continue
        # replace the field lines (contiguous block ending before owner ruling)
        first = min(field_idx) if field_idx else len(entry)
        out.extend(entry[:first])
        out.extend(sugg[word])
        merged.append(word)
        i = j
    REVIEW.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"merged: {len(merged)} | already filled (skipped): {len(skipped_filled)}"
          f" | still pending (no suggestion): {len(missing)}")
    if missing:
        print("  pending:", ", ".join(missing))
    if skipped_filled:
        print("  skipped:", ", ".join(skipped_filled))


if __name__ == "__main__":
    main()
