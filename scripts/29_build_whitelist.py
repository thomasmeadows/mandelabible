#!/usr/bin/env python3
"""29_build_whitelist.py — build the do-not-change word whitelist
(roadmap task + owner directive 2026-07-17; extended 2026-07-20 per owner
directive to sweep the blacklist for "no safe swap"/duplicate noise).

Sources:
1. references/rare_word_review_no_safe_swap.md (owner-reviewed): every
   NO-SAFE-SWAP word stays as-is — no attested alternative exists, or the
   flag itself is spurious. Entries carrying an inline OWNER RULING that
   prescribes a replacement (grandmother, horseleach) are EXCLUDED from the
   whitelist; "DO NOT CHANGE" rulings (Jacob's ladder) are included.
2. word_era proper nouns (3,602): names of people and places —
   transliterations, not English vocabulary; never altered except by the
   separate name-retranslation workstream (Decision Log #8).
3. Orphaned round-1 no-safe-swap flags (2026-07-20): references/
   rare_word_replacements.md carries 249 rows tagged "King James agent: no
   safe one-word swap found — edit or delete this entry" — an internal note
   the round-1 pass never acted on. These were never an accepted change (the
   word was never actually replaced) and were wrongly aggregating into
   word_blacklist.md as if they were. Words already covered by source 1 are
   skipped here (pure duplicates, dropped from the blacklist by
   scripts/49_build_blacklist.py); the remainder are added to the whitelist
   under a distinct heading since they were never owner-reviewed the way
   source 1 was.

Output: references/word_whitelist.md — alphabetical word list at top, each
word linking to a description below explaining why it must not be altered
(unless modernizing), per the roadmap's format requirement.
"""
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
R1 = ROOT / "references" / "rare_word_replacements.md"
DB_PATH = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "word_whitelist.md"

HEADER_RE = re.compile(r"^## (.+?) → .*? — (.+?)\s*$")
R1_HEADER_RE = re.compile(r"^## (.+?) → (.+?) — (.+?) (\d+):(\d+)\s*$")
NO_SAFE_SWAP = "no safe one-word swap found"


def anchor(word):
    return re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-")


def main():
    # 1. parse the owner-reviewed NO-SAFE-SWAP file
    entries = defaultdict(list)  # word -> [(ref, reason, owner_change)]
    word, ref, rationale, ruling = None, None, "", None

    def commit():
        nonlocal word
        if word:
            entries[word].append((ref, rationale.strip(), ruling))
        word = None

    for line in NSS.read_text(encoding="utf-8").splitlines():
        m = HEADER_RE.match(line)
        if m:
            commit()
            word, ref, rationale, ruling = (m.group(1).strip().lower(),
                                            m.group(2).strip(), "", None)
        elif word and line.startswith("- rationale:"):
            rationale = line[len("- rationale:"):].strip()
        elif word and "OWNER RULING" in line:
            ruling = line.strip("- *").strip()
    commit()

    # exclude words where the owner ruled an actual change
    whitelist, excluded = {}, []
    for w, es in sorted(entries.items()):
        rulings = [r for (_, _, r) in es if r]
        if rulings and not any("DO NOT CHANGE" in r.upper() for r in rulings):
            excluded.append((w, rulings[0]))
        else:
            whitelist[w] = es

    # 3. orphaned round-1 no-safe-swap flags not already covered by source 1
    r1_entries, cur, orphaned = [], None, {}
    for line in R1.read_text(encoding="utf-8").splitlines():
        m = R1_HEADER_RE.match(line)
        if m:
            cur = {"word": m.group(1).strip().lower(),
                   "ref": f"{m.group(3)} {m.group(4)}:{m.group(5)}",
                   "source": "", "old": ""}
            r1_entries.append(cur)
        elif cur is not None and line.startswith("- source:"):
            cur["source"] = line[len("- source:"):].strip()
        elif cur is not None and line.startswith("- OLD:"):
            cur["old"] = line[len("- OLD:"):].strip()
    for e in r1_entries:
        if NO_SAFE_SWAP not in e["source"].lower():
            continue
        if e["word"] in whitelist:
            continue  # duplicate of the owner-reviewed source-1 entry
        reason = (f'round-1 pipeline flagged "no safe one-word swap found" '
                   f'here (word never actually replaced): {e["old"]}')
        orphaned.setdefault(e["word"], []).append((e["ref"], reason, None))
    for w, es in orphaned.items():
        whitelist[w] = es

    # 2. proper nouns
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    proper = [w for (w,) in con.execute(
        "SELECT word FROM word_era WHERE verdict='proper_noun' ORDER BY word")]
    con.close()

    reviewed_words = sorted(w for w in whitelist if w not in orphaned)
    orphaned_words = sorted(orphaned)

    out = ["# Word Whitelist — do not alter (unless modernizing)", "",
           "*Generated by `scripts/29_build_whitelist.py` from the "
           "owner-reviewed `rare_word_review_no_safe_swap.md` (2026-07-17), "
           "orphaned round-1 no-safe-swap flags from "
           "`rare_word_replacements.md` (2026-07-20), and the corpus "
           "proper-noun scan.* Words listed here must not be changed by any "
           "replacement pass; at most their inflection may be modernized. "
           "Each word links to the reason below.", "",
           "## Alphabetical list", "",
           "### Reviewed no-safe-swap words "
           f"({len(reviewed_words)})", ""]
    # one link per line: line-based git diffs, but renders as one line
    # (Markdown collapses single newlines into spaces)
    out.append(",\n".join(f"[{w}](#{anchor(w)})" for w in reviewed_words))
    out += ["", "### Orphaned round-1 no-safe-swap flags "
            f"({len(orphaned_words)})", "",
            "Never routed through the dedicated owner-review file, but "
            "carrying the same round-1 \"no safe one-word swap found\" "
            "flag — the word was never actually replaced in the text.", ""]
    out.append(",\n".join(f"[{w}](#{anchor(w)})" for w in orphaned_words))
    out += ["", f"### Proper names and places ({len(proper)})", "",
            "All entries below share one rationale — see "
            "[Proper names and places](#proper-names-and-places-rationale).",
            ""]
    out.append(",\n".join(proper))
    out += ["", "## Why each word is protected", ""]
    for w in sorted(whitelist):
        out.append(f"### {w}")
        for ref, reason, ruling in whitelist[w]:
            line = f"- {ref}: {reason}" if reason else f"- {ref}"
            out.append(line)
            if ruling:
                out.append(f"  - **{ruling}**")
        out.append("")
    out += ["### Proper names and places rationale", "",
            "Names of people and places are transliterations of Hebrew/Greek "
            "names, not English vocabulary — rarity and era-attestation "
            "checks do not apply, so they are never altered by word "
            "replacement. Spelling changes belong exclusively to the "
            "original-language name-retranslation workstream (roadmap "
            "Decision Log #8).", ""]
    if excluded:
        out += ["## Excluded from the whitelist (owner ruled a change)", ""]
        for w, r in excluded:
            out.append(f"- {w} — {r}")
        out.append("")
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"whitelist: {len(reviewed_words)} reviewed + "
          f"{len(orphaned_words)} orphaned round-1 no-safe-swap words + "
          f"{len(proper)} proper nouns; {len(excluded)} excluded by owner "
          "ruling")


if __name__ == "__main__":
    main()
