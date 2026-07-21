#!/usr/bin/env python3
"""54_round3_whitelist_keeps.py — move the round-3 "KEEP WHITE LIST" words
(and every inflected form) into the whitelist (owner review 2026-07-20).

The owner reviewed references/rare_word_round3_review.md and ruled 66 lemmas
"KEEP WHITE LIST". This migration records each lemma and each of its inflected
forms as an owner-reviewed DO-NOT-CHANGE entry in the whitelist's owner-reviewed
source (references/rare_word_review_no_safe_swap.md), under a clearly-labelled
round-3 section, so scripts/29_build_whitelist.py folds them into
references/word_whitelist.md on the next build.

Does not edit the builder. Idempotent — the round-3 section is written once.

After running:  python3 scripts/29_build_whitelist.py   (regenerates the list)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "references" / "rare_word_round3_review.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
SECTION = "# Round-3 owner keeps (2026-07-20)"


def parse_review():
    lemma = forms = refs = ruling = None
    out = []
    for ln in REVIEW.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^#### <a name="[^"]+"></a>(.+?) — \d+ uses$', ln)
        if m:
            if lemma is not None:
                out.append((lemma, forms, refs, ruling))
            lemma, forms, refs, ruling = m.group(1), "", "", ""
        elif lemma is not None:
            if ln.startswith("- forms:"):
                forms = ln[len("- forms:"):].strip()
            elif ln.startswith("- refs:"):
                refs = ln[len("- refs:"):].strip()
            elif ln.startswith("- owner ruling:"):
                ruling = ln[len("- owner ruling:"):].strip()
    if lemma is not None:
        out.append((lemma, forms, refs, ruling))
    return out


def form_words(forms):
    # "adulteress (5), adulteresses (3)" -> ["adulteress", "adulteresses"]
    return [w for w in re.findall(r"([A-Za-z'\-]+)\s*\(\d+\)", forms)]


def main():
    text = NSS.read_text(encoding="utf-8")
    if SECTION in text:
        print("rare_word_review_no_safe_swap.md: round-3 keeps already present")
        return

    entries = parse_review()
    blocks = [SECTION, "",
              "*Words the owner ruled KEEP (whitelist) in the round-3 rare-word "
              "review (references/rare_word_round3_review.md). Each inflected form "
              "is protected. Folded into the whitelist by scripts/29_build_whitelist.py.*",
              ""]
    n_lemmas = n_forms = 0
    for lemma, forms, refs, ruling in entries:
        if "white list" not in ruling.lower() and "whitelist" not in ruling.lower():
            continue
        n_lemmas += 1
        first_ref = refs.split(";")[0].strip() if refs else "round-3"
        uses = ""
        for w in form_words(forms):
            n_forms += 1
            blocks += [
                f"## {w} → NO-SAFE-SWAP — {first_ref}",
                "- verdict: NO-SAFE-SWAP",
                f"- rationale: Round-3 rare-word review — owner ruled keep + "
                f"whitelist (lemma '{lemma}').",
                "- **OWNER RULING 2026-07-20: DO NOT CHANGE — round-3 owner keep.**",
                "- NEW: (no change — OLD text retained per owner ruling)",
                "",
            ]

    NSS.write_text(text.rstrip("\n") + "\n\n" + "\n".join(blocks) + "\n",
                   encoding="utf-8")
    print(f"rare_word_review_no_safe_swap.md: added {n_lemmas} lemmas / "
          f"{n_forms} forms as round-3 owner keeps")
    print("Now run: python3 scripts/29_build_whitelist.py")


if __name__ == "__main__":
    main()
