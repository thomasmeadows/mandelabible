#!/usr/bin/env python3
"""56_round3_blacklist_whitelist.py — record the round-3 replacements in the
blacklist (words replaced) and whitelist (words replacing them). Owner directive
2026-07-21: "all replaced words -> blacklist; all words replacing them -> whitelist."

- Blacklist: writes the round-3 replacements to a builder source,
  references/rare_word_round3_replacements.md (per-verse `## old → new — ref`
  format), which scripts/49_build_blacklist.py now reads (round3()) and folds
  into references/word_blacklist.md — integrated alphabetically and durably,
  exactly like the whitelist path.
- Whitelist: appends the round-3 replacement words to the owner-reviewed source
  references/rare_word_review_no_safe_swap.md so scripts/29_build_whitelist.py
  folds them into references/word_whitelist.md durably.

Idempotent. After running:
    python3 scripts/49_build_blacklist.py    (integrate blacklist)
    python3 scripts/29_build_whitelist.py    (integrate whitelist)
"""
import re, difflib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "references" / "rare_word_round3_review.md"
RECORD = ROOT / "references" / "rare_word_round3_applied.md"
BL_SRC = ROOT / "references" / "rare_word_round3_replacements.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
NSS_MARK = "# Round-3 replacement words (2026-07-21)"
STOP = set("a an and the that this those these i thou he she it we ye you they me him "
           "her us them my thy his its our your their of to in on for with by at from "
           "unto into upon as is are was were be been am art shall will not no nor but "
           "or so if then than there here when why how which who whom whose what do "
           "doth did done have hath had haue also out up down over all any some more "
           "most let may can could would should o oh yea verily said".split())


def replace_lemmas():
    lemmas, forms_of = [], {}
    cur = None
    for ln in REVIEW.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^#### <a name="[^"]+"></a>(.+?) — \d+ uses$', ln)
        if m:
            cur = {"l": m.group(1), "f": "", "r": ""}
        elif cur is not None:
            if ln.startswith("- forms:"):
                cur["f"] = ln[8:].strip()
            elif ln.startswith("- owner ruling:"):
                cur["r"] = ln[15:].strip()
                rl = cur["r"].lower()
                if "replace" in rl and "white" not in rl and "???" not in cur["r"]:
                    lemmas.append(cur["l"])
                    forms_of[cur["l"]] = re.findall(r"([A-Za-z'\-]+)\s*\(\d+\)", cur["f"])
                cur = None
    return lemmas, forms_of


def parse_record():
    """-> list of (ref, words, was, now)."""
    out, ref, words, was = [], None, None, None
    for ln in RECORD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (.+?)\s+\[(.+?)\]\s*$", ln)
        if m:
            ref = m.group(1).strip()
            words = [w.strip() for w in m.group(2).split(",")]
        elif ln.startswith("- was:"):
            was = ln[6:].strip()
        elif ln.startswith("- now:"):
            out.append((ref, words, was, ln[6:].strip()))
    return out


def main():
    lemmas, forms_of = replace_lemmas()
    old_forms = sorted({f.lower() for fs in forms_of.values() for f in fs})
    records = parse_record()

    # per-verse (old_form -> new phrase) pairs for the blacklist source, and the
    # new-word set for the whitelist.
    src_entries = []   # (old, new, ref)
    new_words = set()
    seen = set()
    for ref, words, was, now in records:
        sm = difflib.SequenceMatcher(a=was.split(), b=now.split(), autojunk=False)
        bj, nj = was.split(), now.split()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("replace", "insert"):
                for x in nj[j1:j2]:
                    n = re.sub(r"[^A-Za-z']", "", x).lower()
                    if n and n not in STOP and n not in old_forms:
                        new_words.add(n)
            if tag == "replace":
                olds = bj[i1:i2]
                # clean the replacement: strip punctuation off each token, drop
                # leading articles, so "an alien:" -> "a stranger:" yields "stranger"
                cleaned = [re.sub(r"^[^A-Za-z']+|[^A-Za-z']+$", "", x) for x in nj[j1:j2]]
                cleaned = [c for c in cleaned if c]
                while cleaned and cleaned[0].lower() in ("a", "an", "the"):
                    cleaned = cleaned[1:]
                new_phrase = " ".join(cleaned) or "(deleted)"
                for ox in olds:
                    o = re.sub(r"[^A-Za-z']", "", ox).lower()
                    if o in old_forms and (o, new_phrase, ref) not in seen:
                        seen.add((o, new_phrase, ref))
                        src_entries.append((o, new_phrase, ref))
    new_words = sorted(new_words)

    # ---- blacklist source (builder 49 reads this; integrated on rebuild) ----
    src_entries.sort(key=lambda e: (e[0], e[2]))
    src = ["# Rare Word Replacements — Round 3 (owner-ruled)", "",
           "*Round-3 owner rulings (2026-07-21) from the reviewed "
           "`rare_word_round3_replace_preview.md`; per-verse detail in "
           "`rare_word_round3_applied.md`. Read by `scripts/49_build_blacklist.py` "
           "(round3()) and folded into `word_blacklist.md`.*", ""]
    for old, new, ref in src_entries:
        src += [f"## {old} → {new} — {ref}",
                "- source: round-3 owner ruling 2026-07-21", ""]
    BL_SRC.write_text("\n".join(src) + "\n", encoding="utf-8")
    print(f"rare_word_round3_replacements.md: {len(src_entries)} entries "
          f"({len(set(e[0] for e in src_entries))} distinct old words)")

    # ---- whitelist source: append round-3 replacement words ----
    nsstext = NSS.read_text(encoding="utf-8")
    if NSS_MARK in nsstext:
        print("rare_word_review_no_safe_swap.md: round-3 replacement words already present")
    else:
        blk = ["", NSS_MARK, "",
               "*Words introduced as round-3 replacements (owner ruled 2026-07-21). "
               "Protected so later passes do not re-flag them.*", ""]
        for w in new_words:
            blk += [f"## {w} → NO-SAFE-SWAP — round-3",
                    "- verdict: NO-SAFE-SWAP",
                    "- rationale: Round-3 replacement word; owner ruled keep + whitelist.",
                    "- **OWNER RULING 2026-07-21: DO NOT CHANGE — round-3 replacement.**",
                    "- NEW: (no change — round-3 replacement word)", ""]
        NSS.write_text(nsstext.rstrip("\n") + "\n\n" + "\n".join(blk) + "\n", encoding="utf-8")
        print(f"rare_word_review_no_safe_swap.md: added {len(new_words)} round-3 "
              "replacement words")
    print("Now run: python3 scripts/49_build_blacklist.py "
          "&& python3 scripts/29_build_whitelist.py")


if __name__ == "__main__":
    main()
