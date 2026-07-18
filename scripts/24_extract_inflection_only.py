#!/usr/bin/env python3
"""24_extract_inflection_only.py — triage rare-word entries that are rare only
by inflection, and export excluded proper nouns for research.

Owner directive 2026-07-17:
1. A flagged word that is merely an *inflected* form (plural, possessive,
   tense, past tense, progressive, past participle, comparative, superlative)
   of a base word common in the KJV is not genuinely rare. Move those entries
   out of references/rare_word_replacements.md into
   references/rare_word_inflection_only.md, each annotated
   "Removed: Inflection Deviation" with the base word and its KJV frequency.
   Derivational forms (-ness, -ly, -tion, -ment, ...) do NOT qualify.
2. Proper nouns (people/places) excluded from the rare list by script 05 are
   exported to references/rare_word_proper_nouns_research.md for research.

Only entries AFTER the owner-audited line (132) are moved; qualifying entries
inside the audited region are listed in the new file under a "not moved"
section for the owner to rule on. Batch files are not touched.

Idempotent: re-running after the move finds no further qualifying entries.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "references" / "rare_word_replacements.md"
OUT_INFLECTION = ROOT / "references" / "removed_words" / "rare_word_inflection_only.md"
OUT_PROPER = ROOT / "references" / "removed_words" / "rare_word_proper_nouns_research.md"
DB_PATH = ROOT / "db" / "mandela.db"
AUDITED_THROUGH_LINE = 132
RARE_THRESHOLD = 2  # a base word appearing more than this is "common"

HEADER_RE = re.compile(r"^## (.+?) — (.+?) (\d+):(\d+)\s*$")


def load_kjv_counts():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    counts = {}
    # word_counts holds per-book rows AND a bible-wide row (book_id IS NULL)
    # for each tokenizer_version; use only the bible-wide rows of the latest
    # version or every count is inflated ~4x.
    (latest,) = con.execute(
        "SELECT MAX(tokenizer_version) FROM word_counts").fetchone()
    for w, c in con.execute(
            "SELECT word, count FROM word_counts WHERE translation='KJV' "
            "AND book_id IS NULL AND tokenizer_version=?", (latest,)):
        counts[w] = c
    proper = con.execute(
        "SELECT word FROM word_era WHERE verdict='proper_noun' ORDER BY word"
    ).fetchall()
    con.close()
    return counts, [w for (w,) in proper]


def base_candidates(word):
    """Candidate (base, inflection-name) pairs for pure-inflection suffixes."""
    out = []

    def add(b, kind):
        if b and b != word and len(b) >= 2:
            out.append((b, kind))

    # possessive
    if word.endswith("'s"):
        add(word[:-2], "possessive")
    elif word.endswith("'"):
        add(word[:-1], "possessive (plural)")
    # plural / 3rd-person -s
    if word.endswith("ies"):
        add(word[:-3] + "y", "plural")
    if word.endswith("es"):
        add(word[:-2], "plural")
    if word.endswith("s") and not word.endswith("ss"):
        add(word[:-1], "plural")
    # past tense / past participle -ed
    if word.endswith("ied"):
        add(word[:-3] + "y", "past tense")
    if word.endswith("ed"):
        add(word[:-2], "past tense")
        add(word[:-2] + "e", "past tense")
        add(word[:-1], "past tense")
        if len(word) > 4 and word[-3] == word[-4]:
            add(word[:-3], "past tense (doubled)")
    # archaic verb inflections -eth / -est (also superlative -est)
    for suf, kind in (("eth", "tense (-eth)"), ("est", "tense/superlative (-est)")):
        if word.endswith(suf):
            add(word[:-3], kind)
            add(word[:-3] + "e", kind)
            add(word[:-2], kind)
            if len(word) > 5 and word[-4] == word[-5]:
                add(word[:-4], kind + " (doubled)")
    # progressive -ing
    if word.endswith("ing"):
        add(word[:-3], "progressive")
        add(word[:-3] + "e", "progressive")
        if len(word) > 5 and word[-4] == word[-5]:
            add(word[:-4], "progressive (doubled)")
    # past participle -en
    if word.endswith("en"):
        add(word[:-2], "past participle")
        add(word[:-1], "past participle")
    # comparative -er
    if word.endswith("ier"):
        add(word[:-3] + "y", "comparative")
    if word.endswith("er"):
        add(word[:-2], "comparative")
        add(word[:-1], "comparative")
    return out


def parse_entries(lines):
    """Split file into (preamble, entries); entry = dict with lines block."""
    entries, preamble, cur = [], [], None
    for lineno, line in enumerate(lines, 1):
        m = HEADER_RE.match(line)
        if m:
            cur = {"line": lineno, "title": m.group(1),
                   "ref": f"{m.group(2)} {m.group(3)}:{m.group(4)}",
                   "block": [line]}
            entries.append(cur)
        elif cur is None:
            preamble.append(line)
        else:
            cur["block"].append(line)
    return preamble, entries


def classify(entry, counts):
    """Return (rare_word, base, kind, base_count) if inflection-only rare."""
    rare_part = entry["title"].split(" → ")[0].strip().lower()
    for token in rare_part.split():
        token = token.strip(",.;:'\"").lower() if not token.endswith("'") else token.lower()
        if counts.get(token, 0) > RARE_THRESHOLD or len(token) < 3:
            continue  # not the rare token
        for base, kind in base_candidates(token):
            c = counts.get(base, 0)
            if c > RARE_THRESHOLD:
                return token, base, kind, c
    return None


def main():
    counts, proper = load_kjv_counts()
    text = MD_PATH.read_text(encoding="utf-8")
    preamble, entries = parse_entries(text.splitlines())

    # -er and -en are ambiguous: comparative/past-participle (inflection,
    # e.g. blacker, overtaken) vs. agent noun / adjective->verb (derivation,
    # e.g. accuser, darken). Without part-of-speech data those cannot be
    # auto-moved; they are listed for owner review instead.
    AMBIGUOUS = ("comparative", "past participle")
    moved, kept_blocks, audited_flagged, ambiguous = [], [], [], []
    for e in entries:
        hit = classify(e, counts)
        if hit and hit[2].startswith(AMBIGUOUS):
            kept_blocks.append(e["block"])
            ambiguous.append((e, hit))
        elif hit and e["line"] > AUDITED_THROUGH_LINE:
            moved.append((e, hit))
        else:
            kept_blocks.append(e["block"])
            if hit:
                audited_flagged.append((e, hit))

    # Preservation guard (owner directive 2026-07-17): never overwrite an
    # existing output with an emptier one — generated review files are
    # expensive artifacts and must not be lost on an idempotent re-run.
    if not moved and OUT_INFLECTION.exists():
        print("nothing to move; existing output files left untouched")
        return

    # write the inflection-only file
    out = ["# Rare words removed: Inflection Deviation", "",
           "*Generated by `scripts/24_extract_inflection_only.py` (owner "
           "directive 2026-07-17).* Each word below is rare only as an "
           "inflected form (plural, possessive, tense, past tense, "
           "progressive, past participle, comparative, superlative) of a "
           "base word common in the KJV, so it was removed from "
           "`rare_word_replacements.md` rather than replaced.", ""]
    for e, (tok, base, kind, c) in moved:
        out += e["block"]
        if out[-1].strip():
            out.append("")
        out.append(f"- removed: Inflection Deviation ({kind}) — base word "
                   f"`{base}` appears {c} times in the KJV")
        out.append("")
    if ambiguous:
        out += ["", "## Ambiguous -er/-en candidates (NOT moved — could be "
                "derivation, owner ruling needed)", "",
                "*-er may be comparative (inflection: blacker) or agent noun "
                "(derivation: accuser); -en may be past participle "
                "(inflection: overtaken) or adjective→verb (derivation: "
                "darken).*", ""]
        for e, (tok, base, kind, c) in ambiguous:
            out.append(f"- line {e['line']}: **{e['title']}** — {e['ref']} — "
                       f"{kind} of `{base}` ({c} KJV uses)")
        out.append("")
    if audited_flagged:
        out += ["", "## Audited-region candidates (NOT moved — owner ruling "
                "needed)", ""]
        for e, (tok, base, kind, c) in audited_flagged:
            out.append(f"- line {e['line']}: **{e['title']}** — {e['ref']} — "
                       f"{kind} of `{base}` ({c} KJV uses)")
        out.append("")
    OUT_INFLECTION.write_text("\n".join(out) + "\n", encoding="utf-8")

    # rewrite the replacements file without moved entries
    new_lines = preamble + [l for block in kept_blocks for l in block]
    MD_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    # proper-noun research file
    pn = ["# Proper nouns excluded from the rare-word list — research file", "",
          "*Generated by `scripts/24_extract_inflection_only.py` (owner "
          "directive 2026-07-17).* People and places were excluded from "
          "rare-word replacement by script 05's proper-noun heuristic (every "
          "surface form capitalized). Listed here with KJV occurrence counts "
          "for name-restoration research (roadmap Decision Log #8 "
          "retranslation direction).", ""]
    for w in proper:
        pn.append(f"- {w} — {counts.get(w, 0)} KJV occurrence(s)")
    OUT_PROPER.write_text("\n".join(pn) + "\n", encoding="utf-8")

    print(f"moved {len(moved)} entries to {OUT_INFLECTION.name}; "
          f"{len(audited_flagged)} audited-region candidates flagged; "
          f"{len(proper)} proper nouns exported")


if __name__ == "__main__":
    main()
