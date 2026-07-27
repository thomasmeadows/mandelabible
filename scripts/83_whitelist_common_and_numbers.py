#!/usr/bin/env python3
"""83_whitelist_common_and_numbers.py — owner directive 2026-07-26.

Two whitelist additions, both driven by references/token_list_full.md (the
full inflection-grouped token list of the restored text, script 82):

  A. **Every group occurring more than 88 times counting inflections** —
     items 2439 and greater in that file (line 2449 onward). Owner citation:
     *these were extremely common words and unlikely to be wrong.* Rarity is
     the project's corruption signal; a word used 89+ times across the corpus
     carries no rarity suspicion at all, so it is protected from any further
     replacement pass.

  B. **Every number word, archaic or modern**, at any frequency — cardinals,
     ordinals, multiplicatives and the archaic score-forms (threescore,
     fourscore, twain, thrice, sevenfold...). Numbers are quantities carried
     over from the source-language text, not English vocabulary choices, so
     a replacement pass has nothing legitimate to say about them.

Every form of a whitelisted group is protected, not just the group label.

Mechanics follow the Reverting/whitelist pattern in CLAUDE.md: this script
writes to the owner-reviewed whitelist SOURCE
(references/rare_word_review_no_safe_swap.md) as
`## word → NO-SAFE-SWAP — <tag>` blocks carrying an `OWNER RULING ... DO NOT
CHANGE` line, which is what scripts/29_build_whitelist.py keys on. It is
idempotent: a word already carrying an entry (from any round) is skipped, and
re-running adds nothing. Nothing in db/mandela.db is touched.

After running:
    python3 scripts/29_build_whitelist.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "references" / "token_list_full.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
DATE = "2026-07-26"
THRESHOLD = 88

ROW = re.compile(r"^\| (\d+) \| (\S+) \| (\d+) \| (.*?) \|")
FORM = re.compile(r"(\S+) \(×\d+\)")

# Number words, archaic and modern. Cardinals, ordinals, the score-family,
# multiplicatives, and the fraction/multiplier words the KJV uses numerically.
NUMBER_WORDS = set("""
one two three four five six seven eight nine ten eleven twelve thirteen
fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty
fifty sixty seventy eighty ninety hundred thousand million billion
first second third fourth fifth sixth seventh eighth ninth tenth eleventh
twelfth thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth
nineteenth twentieth thirtieth fortieth fiftieth sixtieth seventieth
eightieth ninetieth hundredth thousandth
score twain threescore fourscore fivescore sixscore sevenscore eightscore
ninescore
once twice thrice single double treble
half halves quarter
twofold threefold fourfold fivefold sevenfold tenfold hundredfold
thirtyfold sixtyfold
""".split())

COMMON_TAG = "common-88"
NUMBER_TAG = "numbers"
COMMON_REASON = ("Owner ruling — extremely common words and unlikely to be "
                 "wrong: this word occurs more than 88 times in the restored "
                 "text counting all inflections, so it carries no rarity "
                 "suspicion and no replacement pass may touch it.")
NUMBER_REASON = ("Owner ruling — all numbers, archaic or modern, are "
                 "whitelisted: number words are quantities carried over from "
                 "the source-language text, not English vocabulary choices.")


def load_groups():
    groups = []
    for ln in TOKENS.read_text(encoding="utf-8").splitlines():
        m = ROW.match(ln)
        if not m:
            continue
        idx, label, count = int(m.group(1)), m.group(2), int(m.group(3))
        forms = FORM.findall(m.group(4)) or [label]
        groups.append((idx, label.lower(), count,
                       sorted({f.lower() for f in forms} | {label.lower()})))
    return groups


def existing_words(text):
    return {m.group(1).strip().lower()
            for m in re.finditer(r"^## (.+?) → ", text, re.M)}


def main():
    groups = load_groups()
    if not groups:
        sys.exit(f"no table rows parsed from {TOKENS.name} — aborting")

    common, numbers = {}, {}
    for idx, label, count, forms in groups:
        if count > THRESHOLD:
            for f in forms:
                common.setdefault(f, (label, count))
        if label in NUMBER_WORDS or any(f in NUMBER_WORDS for f in forms):
            for f in forms:
                numbers.setdefault(f, (label, count))
    # a number word that is also common belongs to the number citation
    for w in numbers:
        common.pop(w, None)

    text = NSS.read_text(encoding="utf-8")
    have = existing_words(text)

    blocks, added_common, added_numbers = [], [], []
    for word, (label, count) in sorted(numbers.items()):
        if word in have:
            continue
        added_numbers.append(word)
        blocks.append(
            f"## {word} → NO-SAFE-SWAP — {NUMBER_TAG}\n"
            f"- verdict: NO-SAFE-SWAP\n"
            f"- rationale: {NUMBER_REASON} (group \"{label}\", {count} uses.)\n"
            f"- **OWNER RULING {DATE}: DO NOT CHANGE — all numbers, archaic or "
            f"modern, are whitelisted.**\n"
            f"- NEW: (no change — whitelisted number)\n")
    for word, (label, count) in sorted(common.items()):
        if word in have:
            continue
        added_common.append(word)
        blocks.append(
            f"## {word} → NO-SAFE-SWAP — {COMMON_TAG}\n"
            f"- verdict: NO-SAFE-SWAP\n"
            f"- rationale: {COMMON_REASON} (group \"{label}\", {count} uses "
            f"with inflections.)\n"
            f"- **OWNER RULING {DATE}: DO NOT CHANGE — extremely common word "
            f"({count} uses with inflections), unlikely to be wrong.**\n"
            f"- NEW: (no change — whitelisted common word)\n")

    print(f"groups parsed: {len(groups)}")
    print(f"forms in >{THRESHOLD}-use groups: {len(common) + len(numbers)}"
          f" | number forms: {len(numbers)}")
    print(f"new entries: {len(added_common)} common + {len(added_numbers)} numbers"
          f" | already present (skipped): "
          f"{len(common) + len(numbers) - len(added_common) - len(added_numbers)}")
    if not blocks:
        print("nothing to add — already up to date.")
        return
    if not text.endswith("\n"):
        text += "\n"
    text += ("\n" + "\n".join(blocks))
    NSS.write_text(text, encoding="utf-8")
    print("appended to", NSS.relative_to(ROOT))


if __name__ == "__main__":
    main()
