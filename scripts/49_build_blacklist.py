#!/usr/bin/env python3
"""49_build_blacklist.py — build references/word_blacklist.md (owner request
2026-07-19): every word that was deliberately changed across the word-level
passes, with the replacement, the reason, and whether the decision was made
by a human (the owner) or an AI agent (always owner-approved before apply).

Sources aggregated (never modified):
  1. references/rare_word_replacements.md          (round-1 rare words)
  2. references/rare_word_witness_batches_2/round2_ai_suggestions.md
                                                   (round-2 rare words)
  3. scripts/44_apply_mixed_inflections.py MAPPINGS (mixed inflections)
  4. scripts/31_manual_word_changes.py RULES        (owner word directives)
  5. Alleluia -> Hallelujah                         (owner ruling 2026-07-19)
  6. scripts/35_normalize_kjv_names.py MAPPING      (name normalization,
                                                    Decision Log #13)

The whitelist (word_whitelist.md) is the companion file: words protected
from change. This file is the opposite: words removed from the text and why.

Overwrite guard: refuses to replace an existing file with one listing fewer
words. Idempotent otherwise.
"""
import argparse
import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "references" / "word_blacklist.md"
R1 = ROOT / "references" / "rare_word_replacements.md"
R2 = (ROOT / "references" / "rare_word_witness_batches_2" /
      "round2_ai_suggestions.md")
R3 = ROOT / "references" / "rare_word_round3_replacements.md"

AI = "AI agent (king-james), owner-approved"
HUMAN = "Human (owner)"

HDR = re.compile(r"^## (.+?) → (.+?) — (.+?) (\d+):(\d+)")


def extract_dict(path, name):
    src = path.read_text(encoding="utf-8")
    m = re.search(rf"^{name} = \{{.*?^\}}", src, re.S | re.M)
    return ast.literal_eval(m.group(0).split("=", 1)[1].strip())


NO_SAFE_SWAP = "no safe one-word swap found"


def round1():
    """Blacklist rows from round 1 — excludes NO_SAFE_SWAP-flagged entries:
    those were never an actual accepted replacement (the word stayed as-is),
    they belong on the whitelist instead (see 29_build_whitelist.py)."""
    entries, cur = [], None
    for line in R1.read_text(encoding="utf-8").splitlines():
        m = HDR.match(line)
        if m:
            cur = [m.group(1).strip(), m.group(2).strip(),
                   f"{m.group(3)} {m.group(4)}:{m.group(5)}", ""]
            entries.append(cur)
        elif cur is not None and line.startswith("- source:"):
            cur[3] = line[len("- source:"):].strip()
    out = []
    for word, repl, ref, source in entries:
        if NO_SAFE_SWAP in source.lower():
            continue
        decider = HUMAN if re.match(
            r"(User|Owner)", source) else AI
        out.append((word, repl, ref, source or "rare word (1-2 KJV uses)",
                    decider, "rare word, round 1"))
    return out


def round2():
    entries, cur = [], None
    for line in R2.read_text(encoding="utf-8").splitlines():
        m = HDR.match(line)
        if m:
            cur = [m.group(1).strip(), m.group(2).strip(),
                   f"{m.group(3)} {m.group(4)}:{m.group(5)}", ""]
            entries.append(cur)
        elif cur is not None and line.startswith("- rationale:"):
            cur[3] = line[len("- rationale:"):].strip()
    return [(w, r, ref, why, AI, "rare word, round 2")
            for w, r, ref, why in entries]


def round3():
    """Round-3 owner-ruled replacements (references/rare_word_round3_replacements.md).
    Same per-verse `## old → new — Book C:V` format as round 1; owner-decided."""
    if not R3.exists():
        return []
    entries, cur = [], None
    for line in R3.read_text(encoding="utf-8").splitlines():
        m = HDR.match(line)
        if m:
            cur = [m.group(1).strip(), m.group(2).strip(),
                   f"{m.group(3)} {m.group(4)}:{m.group(5)}", ""]
            entries.append(cur)
        elif cur is not None and line.startswith("- source:"):
            cur[3] = line[len("- source:"):].strip()
    return [(w, r, ref, why or "round-3 owner ruling", HUMAN, "rare word, round 3")
            for w, r, ref, why in entries]


def mixed_inflections():
    mappings = extract_dict(
        ROOT / "scripts" / "44_apply_mixed_inflections.py", "MAPPINGS")
    owner_ruled = {"sprang", "drave", "girdedst"}
    out = []
    for w, r in mappings.items():
        if w in owner_ruled:
            why = ("mixed inflection; owner ruling (tie-break / "
                   "de-whitelisting) unified onto this form")
            decider = HUMAN
        else:
            why = ("mixed inflection: the corpus used two inflections of "
                   "the same word; the minority form is unified onto the "
                   "corpus-majority form (references/mixed_inflections.md)")
            decider = "AI detector recommendation, owner-approved"
        out.append((w, r, "bible-wide", why, decider, "mixed inflection"))
    return out


def manual_words():
    src = (ROOT / "scripts" / "31_manual_word_changes.py").read_text(
        encoding="utf-8")
    pairs = re.findall(r'\("([^"]+?) -> ([^"]+?)"', src)
    why = ("owner directive (references/manual_word_changes_flagged.md): "
           "the modern/remembered form replaces the altered one")
    out = [(a, b, "bible-wide", why, HUMAN, "manual word change")
           for a, b in pairs if "emoji" not in a]
    out.append(("Alleluia", "Hallelujah", "Revelation 19:1,3,4",
                "owner ruling 2026-07-19: Hallelujah is the remembered "
                "spelling", HUMAN, "manual word change"))
    out.append(("strait", "straight", "bible-wide",
                "owner directive 2026-07-19 (scripts/50_strait_to_straight"
                ".py); plural included; derived forms straitly/straitened/"
                "straitness/straitest left pending a separate ruling",
                HUMAN, "manual word change"))
    return out


def names():
    mapping = extract_dict(
        ROOT / "scripts" / "35_normalize_kjv_names.py", "MAPPING")
    why = ("name normalization (Decision Log #13): KJV-internal variant "
           "spellings unified onto the most common modern form "
           "(references/name_normalization.md)")
    return [(w, r, "bible-wide", why,
             "AI recommendation, owner-approved (Decision Log #13)",
             "name normalization") for w, r in mapping.items()]


ALLOW_SHRINK = "--allow-shrink" in sys.argv


def main():
    rows = round1() + round2() + round3() + mixed_inflections() + manual_words() \
        + names()
    by_word = defaultdict(list)
    for word, repl, ref, why, decider, source in rows:
        by_word[word.lower()].append((word, repl, ref, why, decider, source))
    words = sorted(by_word)

    if OUT.exists() and not ALLOW_SHRINK:
        old = len(re.findall(r"^#### ", OUT.read_text(encoding="utf-8"),
                             re.M))
        if old > len(words):
            raise SystemExit("REFUSING: existing blacklist has more words "
                              "(pass --allow-shrink for a deliberate "
                              "correction, e.g. removing no-safe-swap noise)")

    def slug(w):
        return re.sub(r"[^a-z0-9-]", "-", w.lower())

    n_ai = sum(1 for es in by_word.values()
               if not any(e[4] == HUMAN for e in es))
    out = [
        "# Word Blacklist — words changed and why", "",
        "*Generated by `scripts/49_build_blacklist.py` from the word-level "
        "change passes (rare words rounds 1–2, mixed inflections, owner "
        "manual word changes, name normalization). Companion to "
        "`word_whitelist.md` (words protected from change). Each entry "
        "names the replacement, the reason, and the decider — every "
        "AI-agent decision was owner-approved before it was applied.*", "",
        f"**{len(words)} blacklisted words** ({len(words) - n_ai} with a "
        f"human ruling, {n_ai} AI-decided with owner approval).", "",
        # one link per line: line-based git diffs, but renders as one line
        # (Markdown collapses single newlines into spaces)
        ",\n".join(f"[{w}](#{slug(w)})" for w in words), "",
        "## Entries", "",
    ]
    for w in words:
        es = by_word[w]
        display = es[0][0]
        repls = sorted(set(e[1] for e in es))
        out.append(f'#### <a name="{slug(w)}"></a>{display} → '
                   + " / ".join(repls))
        for word, repl, ref, why, decider, source in es:
            out.append(f"- **{repl}** ({ref}; {source}) — {why}")
            out.append(f"  - decided by: {decider}")
        out.append("")
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    counts = defaultdict(int)
    for es in by_word.values():
        for e in es:
            counts[e[5]] += 1
    print(f"{OUT.name}: {len(words)} words, {sum(counts.values())} entries "
          f"— " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
