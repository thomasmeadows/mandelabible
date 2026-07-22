#!/usr/bin/env python3
"""63_round5_whitelist_gems.py — Round 5 owner ruling 2026-07-21: "materials and
gems should probably be whitelisted in most cases." Whitelists the material/gem
names surfaced by the round-5 rare-word review (references/rare_word_round5_review.md)
so later passes never flag them; the owner reviews the remaining round-5 items.

Words (all specific biblical substances with no better period/EModE equivalent):
  alabaster (stone), amber (resin/metal-glow), amethyst (gem),
  algum / almug (the transliterated Hebrew almug-wood, spelled both ways).

Adds them to the owner-reviewed whitelist source
references/rare_word_review_no_safe_swap.md as a self-contained "Round-5" section
spliced BEFORE the round-4 marker (so a re-run of scripts/58 — which rewrites the
file from its round-4 marker to EOF — leaves this section intact). Idempotent:
the section is removed and rewritten on each run.

After running:  python3 scripts/29_build_whitelist.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
MY_MARK = "# Round-5 reviewed words — materials & gems (2026-07-21)"
R4_MARK = "# Round-4 review words (2026-07-21)"

GEMS = ["alabaster", "algum", "almug", "amber", "amethyst"]


def main():
    block = [MY_MARK, "",
             "*Round-5 owner ruling 2026-07-21: material/gem names whitelisted "
             "(no better period term). Placed before the round-4 marker so "
             "scripts/58 re-runs leave it untouched.*", ""]
    for w in GEMS:
        block += [f"## {w} → NO-SAFE-SWAP — round-5",
                  "- verdict: NO-SAFE-SWAP",
                  "- rationale: Material/gem name; specific biblical substance "
                  "with no better period/EModE equivalent.",
                  "- **OWNER RULING 2026-07-21: DO NOT CHANGE — material/gem.**",
                  "- NEW: (no change — material/gem)", ""]
    blocktext = "\n".join(block)

    text = NSS.read_text(encoding="utf-8")
    head, sep, tail = text.partition(R4_MARK)
    if MY_MARK in head:                       # drop any prior copy (idempotent)
        head = head[:head.index(MY_MARK)]
    head = head.rstrip("\n") + "\n\n" + blocktext + "\n\n"
    NSS.write_text(head + sep + tail if sep else head, encoding="utf-8")

    print(f"whitelisted {len(GEMS)} material/gem words: {', '.join(GEMS)}")
    print("Now run: python3 scripts/29_build_whitelist.py")


if __name__ == "__main__":
    main()
