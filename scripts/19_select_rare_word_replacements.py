#!/usr/bin/env python3
"""19_select_rare_word_replacements.py — Phase 3/6: auto-select a replacement
for each rare word verse from 18_rare_word_alternatives.py's scope.

Owner directive 2026-07-16: for every rare word (<=2 uses, verdict 'period',
non-proper-noun) auto-select ONE replacement word per verse and emit an
OLD/NEW side-by-side review file. The owner will hand-edit the NEW lines or
delete entries entirely; a later script commits the survivors to the db.

Selection priority (owner's rules — same-testament KJV usage first, other
translations second):
  1. Positional alignment against near-KJV translations (Webster, then YLT,
     DRC): if the aligned verse swaps exactly the rare word for one other
     word in identical context, that word is grammatically correct by
     construction. Preferred when the aligned word already occurs in the
     same testament of the KJV.
  2. KJV's own renderings of the same Strong's word, preferring candidates
     whose inflection (suffix: -ing/-eth/-est/-ed/-s/base) matches the rare
     word's grammar AND that already occur in the SAME TESTAMENT of the KJV.
  3. If no surface candidate matches the grammar, try inflecting a candidate
     stem into the needed form (abase -> abasing) — accepted only if the
     inflected form itself occurs in the KJV (same testament preferred).
  4. An alignment word that never appears in the KJV (pure other-translation
     wording), then anything left, flagged for close review.
  5. If nothing plausible is found, the entry is emitted with NEW == OLD and
     tagged NO-REPLACEMENT-FOUND for manual attention.

Output: references/rare_word_replacements.md (generated — hand-editing the
NEW lines / deleting entries is the expected review workflow).
"""

import difflib
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
OUT = REPO_ROOT / "references" / "rare_word_replacements.md"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")
# translations verse-aligned with the KJV (same 31,102-verse scheme),
# in preference order: KJV revisions first (closest wording), YLT last
ALIGN_TRANS = ["Webster", "UKJV", "AKJV", "KJVPCE", "RNKJV", "YLT"]

STOP = set("""a an and the that this those these i thou he she it we ye you
they me him her us them my thy his its our your their of to in on for with
by at from unto into upon as is are was were be been am art shall will not
no nor but or so if then than there here when why how which who whom whose
what do doth did done have hath had haue also out up down over all any some
more most let may can could would should o oh yea verily fi
hast hath came come went gone according wherein whereby wherefore without
within because behold now even very own again against among things thing
one two both much many made make according therefore howbeit insomuch
shalt wilt didst dost doest art thereof thereto thereby moreover
whatsoever whosoever unto brought take taken give given get gat""".split())

SUFFIXES = ["ing", "eth", "est", "ed", "ly", "es", "s"]


def fold(form: str) -> str:
    return form.lower().replace("’", "'").replace("–", "-")


def suffix_of(word: str) -> str:
    for s in SUFFIXES:
        if word.endswith(s) and len(word) > len(s) + 2:
            return s
    return ""


def stems(word: str) -> set:
    """Rough stem guesses for an inflected form."""
    out = {word}
    s = suffix_of(word)
    if s:
        base = word[: len(word) - len(s)]
        out.add(base)
        out.add(base + "e")           # abas -> abase
        if len(base) > 2 and base[-1] == base[-2]:
            out.add(base[:-1])        # begge -> beg
    return out


def inflect(stem: str, suf: str) -> set:
    """Candidate surface forms of stem carrying suffix suf."""
    if not suf:
        return {stem}
    out = set()
    if stem.endswith("e") and suf in ("ing", "ed", "eth", "est"):
        out.add(stem[:-1] + suf)      # humble -> humbling
    if stem.endswith("y") and suf in ("ed", "es", "eth", "est"):
        out.add(stem[:-1] + "i" + suf)    # carry -> carried/carrieth
    out.add(stem + suf)
    if suf == "s" and stem.endswith(("s", "x", "z", "ch", "sh")):
        out.add(stem + "es")
    return out


def replace_token(text: str, old: str, new: str) -> str:
    """Case-preserving whole-word replacement of every occurrence of old."""
    def sub(m):
        tok = m.group(0)
        if tok[0].isupper():
            return new[0].upper() + new[1:]
        return new
    return re.sub(rf"\b{re.escape(old)}\b", sub, text, flags=re.IGNORECASE)


def main() -> None:
    con = sqlite3.connect(DB_PATH)

    rare = [w for (w,) in con.execute(
        """SELECT wc.word FROM word_counts wc JOIN word_era we ON we.word = wc.word
           WHERE wc.translation='KJV' AND wc.book_id IS NULL
             AND wc.tokenizer_version=2 AND wc.count <= 2
             AND we.verdict = 'period' ORDER BY wc.word""")]
    rare_set = set(rare)
    print(f"{len(rare)} rare words in scope")

    # KJV word inventories: bible-wide counts, and per-testament sets
    kjv_counts = Counter()
    ot_words, nt_words = set(), set()
    books = dict(con.execute("SELECT id, name FROM books WHERE translation='KJV'"))
    verses_of = defaultdict(list)
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        toks = [fold(t) for t in TOKEN_RE.findall(text)]
        tset = set(toks)
        kjv_counts.update(toks)
        (ot_words if bid <= 39 else nt_words).update(tset)
        for w in tset & rare_set:
            verses_of[w].append((bid, books[bid], ch, vs, vid, text))

    # Strong's maps (same construction as script 18)
    print("building Strong's maps...")
    word_strongs = defaultdict(set)
    strongs_words = defaultdict(Counter)
    for book, eword, strongs in con.execute(
            """SELECT e.book, e.word, o.strongs FROM bf_words_en e
               JOIN bf_words_orig o ON o.id = e.orig_id
               WHERE e.word != '' AND o.strongs > 0"""):
        lang = "H" if book <= 39 else "G"
        for tok in TOKEN_RE.findall(eword):
            f = fold(tok)
            word_strongs[f].add((lang, strongs))
            strongs_words[(lang, strongs)][f] += 1

    # verse texts of aligned translations, keyed by (translation, bid, ch, vs)
    print("loading aligned translations...")
    aligned = {}
    ph = ",".join("?" * len(ALIGN_TRANS))
    for trans, bid, ch, vs, text in con.execute(
            f"SELECT translation, book_id, chapter, verse, text FROM verses "
            f"WHERE translation IN ({ph})", ALIGN_TRANS):
        aligned[(trans, bid, ch, vs)] = text

    def align_word(kjv_text: str, alt_text: str, word: str):
        """Word the aligned translation puts where the KJV has `word`,
        accepted only as a clean one-for-one swap in identical context."""
        a = [fold(t) for t in TOKEN_RE.findall(kjv_text)]
        b = [fold(t) for t in TOKEN_RE.findall(alt_text)]
        sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "replace" and i2 - i1 == 1 and j2 - j1 == 1 \
                    and a[i1] == word:
                cand = b[j1]
                if cand != word and cand not in STOP and cand.isalpha() \
                        and len(cand) > 2:
                    return cand
        return None

    def pick(word: str, bid: int, ch: int, vs: int, text: str):
        """Return (replacement, source-note) or (None, note)."""
        suf = suffix_of(word)
        same_test = ot_words if bid <= 39 else nt_words

        # 1. positional alignment against near-KJV translations
        align_cands = []           # (translation, candidate)
        for trans in ALIGN_TRANS:
            alt = aligned.get((trans, bid, ch, vs))
            if alt:
                cand = align_word(text, alt, word)
                if cand:
                    align_cands.append((trans, cand))
        for trans, cand in align_cands:
            if cand in same_test and kjv_counts.get(cand, 0) > 2:
                return cand, f"{trans} alignment (word in KJV same testament)"
        for trans, cand in align_cands:
            if kjv_counts.get(cand, 0) > 2:
                return cand, f"{trans} alignment (word in KJV other testament)"

        # 2. KJV parallel renderings via Strong's, grammar-matched
        cands = Counter()
        for key in word_strongs.get(word, ()):
            for other, c in strongs_words[key].items():
                if other != word and other not in STOP and other.isalpha():
                    cands[other] += c

        def score(c):
            s = 0.0
            if suffix_of(c) == suf:
                s += 100
            if c in same_test:
                s += 50
            elif c in kjv_counts:
                s += 20
            s += min(cands.get(c, 0), 30)
            s -= 40 if kjv_counts.get(c, 0) <= 2 else 0  # avoid new rare words
            return s

        surface = [c for c in cands if suffix_of(c) == suf
                   and kjv_counts.get(c, 0) > 2]
        if surface:
            best = max(surface, key=score)
            where = "same testament" if best in same_test else "other testament"
            return best, f"KJV parallel rendering ({where}, matches grammar)"

        # 3. inflect candidate stems into the needed suffix
        inflected = Counter()
        for c, n in cands.items():
            for st in stems(c):
                for form in inflect(st, suf):
                    if form != word and kjv_counts.get(form, 0) > 2:
                        inflected[form] += n
        if inflected:
            best = max(inflected, key=lambda f: (f in same_test,
                                                 kjv_counts[f], inflected[f]))
            where = "same testament" if best in same_test else "other testament"
            return best, f"KJV parallel rendering, re-inflected ({where})"

        # 3b. unattested inflection of a strong candidate — standard English
        # grammar even if the KJV never happens to use the form
        if suf and cands:
            best_stem, n = cands.most_common(1)[0]
            if n >= 2:
                forms = sorted(f for st in stems(best_stem)
                               for f in inflect(st, suf) if f != word)
                if forms:
                    return forms[0], ("re-inflected from KJV rendering "
                                      "(form NOT in KJV — check style)")

        # 4. alignment word not attested in the KJV (other-translation wording)
        if align_cands:
            trans, cand = align_cands[0]
            return cand, f"{trans} alignment (word NOT in KJV — check style)"
        common = [c for c in cands if kjv_counts.get(c, 0) > 2]
        if common:
            best = max(common, key=score)
            return best, "KJV parallel rendering (grammar MISMATCH — check)"
        return None, "NO-REPLACEMENT-FOUND"

    lines = ["# Rare Word Replacements — owner review file",
             "",
             "*Generated by `scripts/19_select_rare_word_replacements.py`.*",
             "",
             "One auto-selected replacement per rare-word verse. Review "
             "workflow: edit the replacement word in the header or the NEW "
             "line where the choice is wrong; DELETE an entire entry (header "
             "through NEW line) to leave that verse unchanged. Entries tagged "
             "`NOT in KJV`, `grammar MISMATCH`, or "
             "`NO-REPLACEMENT-FOUND` need the closest attention. A follow-up "
             "script will commit surviving entries to the database.",
             ""]
    n_ok = n_flag = n_none = 0
    for w in rare:
        for bid, book, ch, vs, vid, text in verses_of.get(w, []):
            new_word, note = pick(w, bid, ch, vs, text)
            if new_word is None:
                n_none += 1
                new_text, header = text, f"{w} → ???"
            else:
                new_text = replace_token(text, w, new_word)
                header = f"{w} → {new_word}"
                if "MISMATCH" in note or "NOT in KJV" in note:
                    n_flag += 1
                else:
                    n_ok += 1
            lines.append(f"## {header} — {book} {ch}:{vs}")
            lines.append(f"- source: {note}")
            lines.append(f"- OLD: {text}")
            lines.append(f"- NEW: {new_text}")
            lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"-> {OUT}")
    print(f"confident: {n_ok}, flagged: {n_flag}, none found: {n_none}")
    con.close()


if __name__ == "__main__":
    main()
