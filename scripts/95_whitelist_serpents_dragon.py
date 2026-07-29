#!/usr/bin/env python3
"""95_whitelist_serpents_dragon.py — owner ruling 2026-07-29.

Two whitelist corrections around the dragon/serpent pass
(`scripts/90_dragons_outside_revelation.py`, owner directive 2026-07-27:
only the book of Revelation has dragons):

  A. **serpents → whitelisted.** `serpent` (49 uses) was whitelisted by the
     King James whitelist review; the plural `serpents` (30 uses) never was —
     and the dragon→serpent pass created many of those occurrences. Protecting
     the singular but not the plural leaves a later replacement pass free to
     move them, so the owner ruled the plural in.

  B. **dragon stays OFF the whitelist.** The word carries two dated owner
     rulings in the whitelist source: the 2026-07-27 "DO NOT CHANGE — animal,
     not a verb", then the same day's superseding ruling that changes it to
     serpent everywhere except Revelation. `29_build_whitelist.py` keeps the
     LAST ruling, so dragon already lands in the "Excluded from the whitelist
     (owner ruled a change)" section — this script only appends a third, dated
     ruling line making the exclusion explicit rather than a side effect of
     parse order. Nothing is erased: all prior ruling lines stay (the same
     append-beneath pattern used for `gladness` and `dragon` before).

Mechanics follow CLAUDE.md's whitelist pattern: writes only to the
owner-reviewed source `references/word_lists/rare_word_review_no_safe_swap.md`.
Idempotent — each step checks the current state first. Nothing in
`db/mandela.db` is touched, so no text changes and no republish.

After running:
    python3 scripts/29_build_whitelist.py
    python3 scripts/49_build_blacklist.py --allow-shrink
    python3 scripts/82_full_token_list.py --allow-shrink
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NSS = ROOT / "references" / "word_lists" / "rare_word_review_no_safe_swap.md"
DATE = "2026-07-29"

SERPENTS_BLOCK = f"""## serpents → NO-SAFE-SWAP — owner ruling (animal, plural of a whitelisted word)
- verdict: NO-SAFE-SWAP
- rationale: plural of the whitelisted `serpent` — a named creature, and the
  form the dragon→serpent pass (scripts/90_dragons_outside_revelation.py)
  wrote into the text. Protecting the singular alone would leave 30 occurrences
  of the plural open to a later replacement pass.
- **OWNER RULING {DATE}: DO NOT CHANGE — whitelist the plural with the
  singular.**
- NEW: (no change — whitelisted animal)
"""

DRAGON_RULINGS = [
    ("NOT WHITELISTED",
     f"- **OWNER RULING {DATE} (confirms the supersession): NOT "
     "WHITELISTED — dragon is excluded from the whitelist; only the book of "
     "Revelation keeps its dragons, and serpent stands everywhere else.**"),
    ("RE-WHITELISTED",
     f"- **OWNER RULING {DATE} (latest, supersedes the above): "
     "RE-WHITELISTED — DO NOT CHANGE. The dragon→serpent swap is complete "
     "(25 replaced, Revelation's 13 stand), so a whitelist entry no longer "
     "blocks anything; it protects the surviving Revelation uses and keeps "
     "the word off the token list, which is what put it in front of the "
     "King James agent for re-review.**"),
]


def main():
    text = NSS.read_text(encoding="utf-8")
    changed = []

    # A. serpents
    if re.search(r"^## serpents → ", text, re.M):
        print("serpents: already has a whitelist entry — skipped")
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + SERPENTS_BLOCK
        changed.append("serpents whitelisted")

    # B. dragon — append the confirming ruling beneath the existing ones
    m = re.search(r"^## dragon → .*?(?=^## )", text, re.M | re.S)
    if not m:
        sys.exit("no `## dragon → ` entry found in the whitelist source — "
                 "aborting rather than guessing")
    block = m.group(0)
    lines = block.rstrip("\n").splitlines()
    added = []
    for marker, ruling in DRAGON_RULINGS:
        if any(marker in l for l in lines):
            continue
        # insert after the last OWNER RULING line, before any trailing NEW:
        last = max(i for i, l in enumerate(lines) if "OWNER RULING" in l)
        # a ruling may wrap over several lines; extend to the end of it
        while last + 1 < len(lines) and not lines[last + 1].startswith("- "):
            last += 1
        lines.insert(last + 1, ruling)
        added.append(marker)
    if added:
        text = text[:m.start()] + "\n".join(lines) + "\n\n" + text[m.end():]
        changed.append("dragon rulings recorded: " + ", ".join(added))
    else:
        print("dragon: rulings already recorded — skipped")

    if not changed:
        print("nothing to do — already up to date.")
        return
    NSS.write_text(text, encoding="utf-8")
    print("updated", NSS.relative_to(ROOT), "—", "; ".join(changed))


if __name__ == "__main__":
    main()
