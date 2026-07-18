#!/usr/bin/env python3
"""36_retokenize_restored.py — tokenize the RESTORED text & re-list rare words.

Owner directive 2026-07-18: re-tokenize the text as already restored (each
verse's latest approved restoration composed over the base KJV — the same
composition script 17 exports), not the old corrupted KJV, and regenerate
the rare-word list with three exclusions:

1. Whitelisted words (`references/word_whitelist.md` — the 165 owner-reviewed
   no-safe-swap words; the proper-noun section is covered by #2).
2. People and places: `word_era` verdict='proper_noun' (script 05 heuristic)
   PLUS any word whose every surface form in the restored corpus is
   capitalized (catches spellings the restoration introduced, e.g. Perez,
   Elizabeth, Zarephath).
3. Inflectional variants: forms differing only by an inflectional suffix
   (plural, possessive, -ed, -eth/-est, -ing, -en, -er/-iest, script 24's
   rules) are grouped with their base word; rarity is judged on the GROUP's
   total count, so an inflection of a common word is not a deviation.

Tokenizer: v2 rules (scripts/03_tokenize.py) verbatim. Counts stored in
word_counts/word_forms under translation 'KJV_restored' (per-book rows +
bible-wide NULL rows, tokenizer_version 2); rows for that translation are
replaced on each run (idempotent).

Output: `references/rare_words_restored.md` — groups whose total count <= 2
(the rare-word workstream's threshold), alphabetical, with surface forms
and verse references. Refuses to overwrite with a report that has fewer
entries (generated-artifact guard).
"""
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
WHITELIST = ROOT / "references" / "word_whitelist.md"
OUT_PATH = ROOT / "references" / "rare_words_restored.md"

TRANSLATION = "KJV_restored"
TOKENIZER_VERSION = 2
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")
RARE_MAX = 2


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

    # Compose the restored text (same rule as script 17: latest approved
    # restoration wins; rows are already cumulative).
    final = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        final[vid] = t

    counts = Counter()                     # (word, book_id) -> n
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
            counts[(w, book_id)] += 1
            totals[w] += 1
            forms[(w, tok)] += 1
            if len(refs[w]) < 8:
                refs[w].append(ref)
            if tok[0].isupper():
                caps_only.setdefault(w, True)
            else:
                caps_only[w] = False

    # Store counts under KJV_restored.
    con.execute("DELETE FROM word_counts WHERE translation=?", (TRANSLATION,))
    con.execute("DELETE FROM word_forms WHERE translation=?", (TRANSLATION,))
    con.executemany(
        "INSERT INTO word_counts VALUES (?,?,?,?,?)",
        [(TRANSLATION, w, b, n, TOKENIZER_VERSION)
         for (w, b), n in counts.items()])
    con.executemany(
        "INSERT INTO word_counts VALUES (?,?,NULL,?,?)",
        [(TRANSLATION, w, n, TOKENIZER_VERSION) for w, n in totals.items()])
    con.executemany(
        "INSERT INTO word_forms VALUES (?,?,?,?,?)",
        [(TRANSLATION, w, f, n, TOKENIZER_VERSION)
         for (w, f), n in forms.items()])
    con.commit()

    # Exclusions.
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

    rare = []
    for base, members in groups.items():
        if any(excluded(m) for m in members):
            continue
        total = sum(totals[m] for m in members)
        if total <= RARE_MAX:
            rare.append((base, sorted(members), total))
    rare.sort()

    total_words = sum(totals.values())
    lines = [
        "# Rare Words in the RESTORED Text",
        "",
        "Generated by `scripts/36_retokenize_restored.py` (owner directive "
        "2026-07-18). The restored text (all approved restorations composed, "
        "same as the MVP export) was re-tokenized (v2 rules, stored as "
        f"translation `KJV_restored`): **{total_words:,} words**, "
        f"{len(totals):,} distinct forms, {len(groups):,} inflection groups.",
        "",
        "Excluded from rarity: whitelist words (`word_whitelist.md`), proper "
        "nouns (script 05 heuristic + capitalized-only in the restored "
        "corpus), and inflectional variants — forms differing only by an "
        "inflectional suffix are grouped with their base word and judged on "
        "the group's total count, so an inflection of a common word is not "
        "a deviation.",
        "",
        f"**Rare groups (total count <= {RARE_MAX}): {len(rare)}**",
        "",
    ]
    for base, members, total in rare:
        surface = ", ".join(
            f"{m} (×{totals[m]})" for m in members)
        where = "; ".join(dict.fromkeys(
            r for m in members for r in refs[m]))
        lines.append(f"- **{base}** — {surface} — {where}")
    lines.append("")
    out = "\n".join(lines)

    import sys
    if OUT_PATH.exists() and "--allow-shrink" not in sys.argv:
        old = OUT_PATH.read_text(encoding="utf-8").count("\n- **")
        if out.count("\n- **") < old:
            raise SystemExit(
                f"REFUSING to overwrite {OUT_PATH}: {out.count(chr(10)+'- **')} "
                f"entries < existing {old}. If the shrink is legitimate "
                f"(restorations removed rare words), re-run with "
                f"--allow-shrink.")
    OUT_PATH.write_text(out, encoding="utf-8")
    print(f"{total_words:,} words tokenized ({len(totals):,} distinct); "
          f"{len(rare)} rare groups -> {OUT_PATH.name}")


if __name__ == "__main__":
    main()
