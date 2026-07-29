#!/usr/bin/env python3
"""92_whitelist_tokenlist_manual.py — owner directive 2026-07-29.

Whitelist the owner's hand-curated selection from the full token list:
references/word_lists/tokenlist_manual_whitelist.md — 2,023 word forms picked
out of references/word_lists/token_list_full.md (the inflection-grouped token
list of the restored text, script 82). The selection covers 1,094 complete
inflection groups with no partially-covered group: every form of each chosen
group is listed, so protecting the listed forms protects the whole group.

This is the same mechanism as scripts/83_whitelist_common_and_numbers.py (the
>88-use groups and the number words, from the same token list): the words are
written to the owner-reviewed whitelist SOURCE
(references/word_lists/rare_word_review_no_safe_swap.md) as
`## word → NO-SAFE-SWAP — tokenlist-manual` blocks carrying an
`OWNER RULING ... DO NOT CHANGE` line, which is what
scripts/29_build_whitelist.py keys on. Idempotent: a word already carrying an
entry (from any round) is skipped, and re-running adds nothing. Nothing in
db/mandela.db is touched — no text changes, so no republish.

26 of the listed words are on references/word_blacklist.md, having been changed
in one or more verses by an earlier pass. Owner ruling for this pass:
whitelist them and drop them from the blacklist, so no word sits on both lists
(the applied verse changes themselves stand). scripts/49_build_blacklist.py
excludes words carrying this pass's `tokenlist-manual` tag; this script reports
them so the removal is visible.

After running:
    python3 scripts/29_build_whitelist.py
    python3 scripts/49_build_blacklist.py --allow-shrink
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "references" / "word_lists" / "tokenlist_manual_whitelist.md"
TOKENS = ROOT / "references" / "word_lists" / "token_list_full.md"
NSS = ROOT / "references" / "word_lists" / "rare_word_review_no_safe_swap.md"
BLACKLIST = ROOT / "references" / "word_blacklist.md"
DATE = "2026-07-29"
TAG = "tokenlist-manual"

ROW = re.compile(r"^\| (\d+) \| (\S+) \| (\d+) \| (.*?) \|")
FORM = re.compile(r"(\S+) \(×\d+\)")

REASON = ("Owner selection from the full token list review "
          "(references/word_lists/tokenlist_manual_whitelist.md): the owner "
          "read the restored text's token list group by group and marked this "
          "word to be left alone, so no replacement pass may touch it.")


def load_forms():
    """form -> (group label, group count) from token_list_full.md."""
    forms = {}
    for ln in TOKENS.read_text(encoding="utf-8").splitlines():
        m = ROW.match(ln)
        if not m:
            continue
        label, count = m.group(2).lower(), int(m.group(3))
        group = {f.lower() for f in FORM.findall(m.group(4))} | {label}
        for f in group:
            forms.setdefault(f, (label, count))
    return forms


def existing_words(text):
    return {m.group(1).strip().lower()
            for m in re.finditer(r"^## (.+?) → ", text, re.M)}


def blacklist_words():
    if not BLACKLIST.exists():
        return set()
    return {m.group(1).lower()
            for m in re.finditer(r'#### <a name="(.+?)"',
                                 BLACKLIST.read_text(encoding="utf-8"))}


def main():
    words = []
    seen = set()
    for ln in LIST.read_text(encoding="utf-8").splitlines():
        w = ln.strip().lower()
        if w and w not in seen:
            seen.add(w)
            words.append(w)
    if not words:
        sys.exit(f"no words read from {LIST.name} — aborting")

    forms = load_forms()
    if not forms:
        sys.exit(f"no table rows parsed from {TOKENS.name} — aborting")
    unknown = [w for w in words if w not in forms]
    if unknown:
        sys.exit(f"{len(unknown)} listed words are not token forms in "
                 f"{TOKENS.name} — aborting: {', '.join(sorted(unknown)[:20])}")

    text = NSS.read_text(encoding="utf-8")
    have = existing_words(text)

    blocks, added = [], []
    for word in words:
        if word in have:
            continue
        label, count = forms[word]
        added.append(word)
        blocks.append(
            f"## {word} → NO-SAFE-SWAP — {TAG}\n"
            f"- verdict: NO-SAFE-SWAP\n"
            f"- rationale: {REASON} (group \"{label}\", {count} uses "
            f"with inflections.)\n"
            f"- **OWNER RULING {DATE}: DO NOT CHANGE — owner selection from "
            f"the full token list review.**\n"
            f"- NEW: (no change — whitelisted word)\n")

    overlap = sorted(seen & blacklist_words())
    print(f"words in {LIST.name}: {len(words)}")
    print(f"new entries: {len(added)} | already present (skipped): "
          f"{len(words) - len(added)}")
    if overlap:
        print(f"also on the blacklist ({len(overlap)}) — dropped from it by "
              f"49_build_blacklist.py's {TAG} exclusion:")
        print("  " + ", ".join(overlap))
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
