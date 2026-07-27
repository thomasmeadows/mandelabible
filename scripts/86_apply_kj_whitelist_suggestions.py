#!/usr/bin/env python3
"""86_apply_kj_whitelist_suggestions.py — owner ruling 2026-07-27: "I agree
with all the suggestions made."

Folds the 141 King James agent whitelist recommendations
(references/word_lists/kj_whitelist_suggestions.md, consolidated by scripts/85 from the
five batch files) into the owner-reviewed whitelist SOURCE,
references/word_lists/rare_word_review_no_safe_swap.md, so scripts/29_build_whitelist.py
picks them up.

Each recommendation covers a token GROUP, whose `word` cell may list several
forms ("bank, banks"); every form becomes its own whitelist entry, since the
whitelist matches on individual words.

**The agent's reason is carried into the entry's `- rationale:` line** (owner
directive 2026-07-27: "use the reason for white list in the link to the word
on the whitelist") — scripts/29 renders that rationale as the description the
alphabetical link points to.

Idempotent: a word already carrying an entry in the source file is skipped, so
re-running adds nothing. Nothing in db/mandela.db is touched.

After running:
    python3 scripts/29_build_whitelist.py
    python3 scripts/82_full_token_list.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUGG = ROOT / "references" / "word_lists" / "kj_whitelist_suggestions.md"
NSS = ROOT / "references" / "word_lists" / "rare_word_review_no_safe_swap.md"
DATE = "2026-07-27"
CATEGORIES = {"proper-noun", "genealogy", "animal", "plant", "location"}

ROW = re.compile(r"^\|\s*([a-z-]+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|")


def main():
    recs = []
    for ln in SUGG.read_text(encoding="utf-8").splitlines():
        m = ROW.match(ln)
        if m and m.group(1) in CATEGORIES:
            cat, words, idx, reason = (m.group(1), m.group(2), m.group(3),
                                       m.group(5).rsplit("|", 1)[0].strip())
            for w in words.split(","):
                w = w.strip().lower()
                if w:
                    recs.append((w, cat, idx, reason))
    if not recs:
        sys.exit(f"no recommendation rows parsed from {SUGG.name} — aborting")

    text = NSS.read_text(encoding="utf-8")
    have = {m.group(1).strip().lower()
            for m in re.finditer(r"^## (.+?) → ", text, re.M)}

    blocks, added, skipped = [], [], []
    seen = set()
    for word, cat, idx, reason in recs:
        if word in have or word in seen:
            skipped.append(word)
            continue
        seen.add(word)
        added.append((word, cat))
        blocks.append(
            f"## {word} → NO-SAFE-SWAP — King James whitelist review ({cat})\n"
            f"- verdict: NO-SAFE-SWAP\n"
            f"- rationale: {reason}\n"
            f"- **OWNER RULING {DATE}: DO NOT CHANGE — {cat}, not a verb; "
            f"King James agent whitelist review (token group #{idx}), owner "
            f"approved all suggestions.**\n"
            f"- NEW: (no change — whitelisted {cat})\n")

    from collections import Counter
    print(f"recommendation forms: {len(recs)} | new: {len(added)} | "
          f"already present (skipped): {len(skipped)}")
    print(" by category:", dict(Counter(c for _, c in added)))
    if not blocks:
        print("nothing to add — already up to date.")
        return
    if not text.endswith("\n"):
        text += "\n"
    text += "\n" + "\n".join(blocks)
    NSS.write_text(text, encoding="utf-8")
    print("appended to", NSS.relative_to(ROOT))


if __name__ == "__main__":
    main()
