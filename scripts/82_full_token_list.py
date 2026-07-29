#!/usr/bin/env python3
"""82_full_token_list.py — the complete token list of the restored text.

Owner request 2026-07-26: output the entire tokenized word list of the text as
it now stands (base KJV + every `status='approved'` restoration composed, the
same text `17_export_full.py` exports), sorted from fewest occurrences to most,
with whitelisted words excluded.

Same tokenizer, exclusions, and inflection grouping as
`36_retokenize_restored.py` (v2 rules from `03_tokenize.py`; whitelist +
proper nouns excluded; inflectional variants judged on their group's total).
The differences:

- no rare threshold — every surviving group is listed, not just those at or
  under 2 occurrences;
- sorted by group total ascending (then alphabetically), per the request;
- read-only — it does not write `word_counts` / `word_forms`; script 36 owns
  those rows under translation `KJV_restored`.

Output: `references/word_lists/token_list_full.md`. Refuses to overwrite an existing
report with fewer entries (generated-artifact guard).

Owner directive 2026-07-29 ("these lists are too large… generate the smaller
list unless asked otherwise"): the default report is the **condensed** shape —
`# | word | count | forms`, one row per inflection group, with the bulky verse
**reference column dropped**. Pass `--full` for the wide report that carries
references for groups of REF_MAX (8) occurrences or fewer. Switching an existing
wide report to the condensed shape archives it to
`references/removed_words/pre_triage_backups/` first (generated artifacts are
permanent).
"""
import re
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
WHITELIST = ROOT / "references" / "word_whitelist.md"
OUT_PATH = ROOT / "references" / "word_lists" / "token_list_full.md"

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")
REF_MAX = 8          # list verse refs for groups no more common than this
# Owner directive 2026-07-29: the condensed report (no reference column) is
# the default; --full restores the wide one.
WITH_REFS = "--full" in sys.argv


def fold(form):
    return form.lower().replace("’", "'").replace("–", "-")


def base_candidates(word):
    """(base, kind) pairs for pure-inflection suffixes (script 24 rules)."""
    out = []

    def add(b, kind):
        if b and b != word and len(b) >= 2:
            out.append((b, kind))

    if word.endswith("'s"):
        add(word[:-2], "possessive")
    elif word.endswith("'"):
        add(word[:-1], "possessive (plural)")
    if word.endswith("ies"):
        add(word[:-3] + "y", "plural")
    if word.endswith("es"):
        add(word[:-2], "plural")
    if word.endswith("s") and not word.endswith("ss"):
        add(word[:-1], "plural")
    if word.endswith("ied"):
        add(word[:-3] + "y", "past tense")
    if word.endswith("ed"):
        add(word[:-2], "past tense")
        add(word[:-2] + "e", "past tense")
        add(word[:-1], "past tense")
        if len(word) > 4 and word[-3] == word[-4]:
            add(word[:-3], "past tense (doubled)")
    for suf, kind in (("eth", "tense (-eth)"), ("est", "tense/superlative (-est)")):
        if word.endswith(suf):
            add(word[:-3], kind)
            add(word[:-3] + "e", kind)
            add(word[:-2], kind)
            if len(word) > 5 and word[-4] == word[-5]:
                add(word[:-4], kind + " (doubled)")
    if word.endswith("ing"):
        add(word[:-3], "progressive")
        add(word[:-3] + "e", "progressive")
        if len(word) > 5 and word[-4] == word[-5]:
            add(word[:-4], "progressive (doubled)")
    if word.endswith("en"):
        add(word[:-2], "past participle")
        add(word[:-1], "past participle")
    if word.endswith("ier"):
        add(word[:-3] + "y", "comparative")
    if word.endswith("er"):
        add(word[:-2], "comparative")
        add(word[:-1], "comparative")
    return out


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))

    # Compose the restored text (same rule as script 17: rows are cumulative,
    # latest approved restoration wins).
    final = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        final[vid] = t

    totals = Counter()                     # word -> n
    forms = Counter()                      # (word, surface form) -> n
    refs = defaultdict(list)               # word -> verse refs
    caps_only = {}                         # word -> True while never lowercase

    for vid, book_id, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        text = final.get(vid, orig)
        ref = f"{books[book_id]} {ch}:{vs}"
        for tok in TOKEN_RE.findall(text):
            w = fold(tok)
            totals[w] += 1
            forms[(w, tok)] += 1
            if len(refs[w]) < REF_MAX:
                refs[w].append(ref)
            if tok[0].isupper():
                caps_only.setdefault(w, True)
            else:
                caps_only[w] = False

    # Exclusions (script 36's rules).
    whitelist = set(re.findall(r"\[([a-z'’–-]+)\]\(#",
                               WHITELIST.read_text(encoding="utf-8")))
    proper = {w for (w,) in con.execute(
        "SELECT word FROM word_era WHERE verdict='proper_noun'")}
    proper |= {w for w, c in caps_only.items() if c}

    def excluded(w):
        if w in whitelist or w in proper:
            return True
        if w.endswith("'s") and w[:-2] in proper:   # possessive of a name
            return True
        return w.endswith("'") and w[:-1] in proper

    # Group inflections: attach each word to the most frequent existing base.
    group_of = {}
    for w in totals:
        best, best_n = w, -1
        for b, _ in base_candidates(w):
            if b in totals and totals[b] > best_n:
                best, best_n = b, totals[b]
        group_of[w] = best if best_n >= 0 else w
    # Collapse chains (e.g. walkings -> walking -> walk).
    for w in list(group_of):
        g = group_of[w]
        while group_of.get(g, g) != g:
            g = group_of[g]
        group_of[w] = g

    groups = defaultdict(list)
    for w in totals:
        groups[group_of[w]].append(w)

    listed = []
    for base, members in groups.items():
        if any(excluded(m) for m in members):
            continue
        listed.append((sum(totals[m] for m in members), base, sorted(members)))
    listed.sort(key=lambda row: (row[0], row[1]))

    total_words = sum(totals.values())
    lines = [
        "# Full Token List — Restored Text",
        "",
        "Generated by `scripts/82_full_token_list.py` (owner request "
        "2026-07-26). The restored text (all approved restorations composed, "
        "same as the MVP export) tokenized under the v2 rules of "
        "`scripts/03_tokenize.py`: "
        f"**{total_words:,} words**, {len(totals):,} distinct forms, "
        f"{len(groups):,} inflection groups.",
        "",
        "Excluded, as in `rare_words_restored.md`: whitelist words "
        "(`word_whitelist.md`) and proper nouns (script 05 heuristic plus any "
        "token capitalized everywhere it appears in the restored corpus). "
        "Inflectional variants are grouped with their base word and counted "
        "as a group.",
        "",
        f"**{len(listed):,} groups listed**, sorted fewest occurrences first, "
        "then alphabetically. " + (
            f"Verse references are given for groups occurring {REF_MAX} times "
            "or fewer."
            if WITH_REFS else
            "Condensed shape (owner directive 2026-07-29): one row per "
            "inflection group, no verse references — re-run script 82 with "
            "`--full` for the wide report that carries them."),
        "",
        "| # | word | count | forms |" + (" references |" if WITH_REFS else ""),
        "|---|---|---|---|" + ("---|" if WITH_REFS else ""),
    ]
    for i, (total, base, members) in enumerate(listed, 1):
        surface = ", ".join(f"{m} (×{totals[m]})" for m in members)
        row = f"| {i} | {base} | {total} | {surface} |"
        if WITH_REFS:
            where = ("; ".join(dict.fromkeys(r for m in members for r in refs[m]))
                     if total <= REF_MAX else "")
            row += f" {where} |"
        lines.append(row)
    lines.append("")

    # Generated-artifact guard: never replace a report with an emptier one.
    # A whitelist expansion legitimately shrinks this list (whitelisted words
    # are excluded), so --allow-shrink overrides the guard — same pattern as
    # scripts/36 and scripts/49. The prior report is archived first, since
    # generated artifacts are permanent (CLAUDE.md).
    if OUT_PATH.exists():
        prior_text = OUT_PATH.read_text(encoding="utf-8")
        prior = sum(1 for ln in prior_text.splitlines()
                    if re.match(r"\| \d+ \|", ln))
        # Dropping the reference column loses content the wide report carried,
        # so archive it once before the shape changes.
        if not WITH_REFS and "| references |" in prior_text:
            keep = (ROOT / "references" / "removed_words" /
                    "pre_triage_backups" /
                    f"token_list_full_with_refs_{prior}rows.md")
            if not keep.exists():
                keep.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(OUT_PATH, keep)
                print(f"archived prior wide report ({prior} rows) to "
                      f"{keep.relative_to(ROOT)}")
        if prior > len(listed):
            if "--allow-shrink" not in sys.argv:
                raise SystemExit(
                    f"refusing to overwrite {OUT_PATH.name}: existing report has "
                    f"{prior} rows, new one has {len(listed)}. Re-run with "
                    "--allow-shrink if the shrink is legitimate (e.g. the "
                    "whitelist grew).")
            backup = (ROOT / "references" / "removed_words" /
                      "pre_triage_backups" /
                      f"token_list_full_pre_shrink_{prior}rows.md")
            if not backup.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(OUT_PATH, backup)
                print(f"archived prior report ({prior} rows) to "
                      f"{backup.relative_to(ROOT)}")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUT_PATH.relative_to(ROOT)}: {len(listed):,} groups listed "
          f"({len(groups) - len(listed):,} excluded, "
          f"{total_words:,} words total)")


if __name__ == "__main__":
    main()
