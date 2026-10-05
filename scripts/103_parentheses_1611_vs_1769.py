#!/usr/bin/env python3
"""103_parentheses_1611_vs_1769.py — study how the 1769 Standard Oxford
Edition changed the parentheses of the 1611 King James text (owner request
2026-10-04: "to see punctuation and differences added in the oxford … to
better understand why oxford changed what was in the parentheses").

Inputs (read-only): `KJV1611` (script 102) and `KJV` (the 1769 Blayney base)
in db/mandela.db. Nothing in the restored text or any edition is touched.

Method. Each verse is split into words and punctuation marks. The two
editions' words are aligned with difflib on a spelling-folded form (u/v, i/j,
doubled letters and final -e folded, so *sonne* = *son*). For every
parentheses span in one edition, the punctuation the OTHER edition has at the
same two edges (just before the first word inside, just after the last) is
read off, giving a pattern such as 1611 `( … )` → 1769 `, … ,`. A span whose
edge words do not align is shifted to the nearest aligned word inside it;
if none aligns it is reported as unaligned. Parentheses can open in one
verse and close in the next; such verses are flagged "spans verses".

Each span is classed:
  kept      — 1769 keeps the parentheses (punctuation inside it may change)
  removed   — 1611 parentheses, none in 1769 (what replaced it is shown)
  added     — 1769 parentheses where 1611 had none (what 1611 had is shown)

Output: references/verses/parentheses_1611_vs_1769.md — summary tables, the
first-word evidence for why spans were kept or removed, then every verse
with both readings and its per-span change line. Overwrite guard refuses a
version listing fewer verses than the existing file. Advisory comparison
only (Premise Revision).
"""
import difflib
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "verses" / "parentheses_1611_vs_1769.md"

TOK = re.compile(r"[A-Za-zþÞ’'\-–]+|[(),;:.?!]")


def toks(s):
    return TOK.findall(s.replace("¶", ""))


def is_word(t):
    return t[0].isalpha() or t[0] in "þÞ"


def fold(w):
    w = (w.lower().replace("þ", "th").replace("’", "'").replace("v", "u")
         .replace("j", "i").replace("y", "i").replace("–", "-"))
    w = re.sub(r"(.)\1", r"\1", w)
    return re.sub(r"e$", "", w)


class Verse:
    def __init__(self, text):
        self.t = toks(text)
        self.w = [i for i, x in enumerate(self.t) if is_word(x)]

    def word(self, k):
        return self.t[self.w[k]]

    def gap(self, k):
        """Punctuation between word k-1 and word k (0 = verse start, len = end)."""
        lo = self.w[k - 1] + 1 if k > 0 else 0
        hi = self.w[k] if k < len(self.w) else len(self.t)
        return "".join(self.t[lo:hi])

    def spans(self):
        """(first word, last word) of each parentheses span, by word index."""
        pos = {i: k for k, i in enumerate(self.w)}
        out, start = [], None
        for i, x in enumerate(self.t):
            if x == "(":
                start = i
            elif x == ")":
                s = start if start is not None else -1
                inside = [pos[j] for j in range(s + 1, i) if j in pos]
                if inside:
                    out.append((inside[0], inside[-1]))
                start = None
        if start is not None:
            inside = [pos[j] for j in range(start + 1, len(self.t)) if j in pos]
            if inside:
                out.append((inside[0], inside[-1]))
        return out


def alignment(a, b):
    sm = difflib.SequenceMatcher(None, [fold(a.word(k)) for k in range(len(a.w))],
                                 [fold(b.word(k)) for k in range(len(b.w))],
                                 autojunk=False)
    m = {}
    for i, j, n in sm.get_matching_blocks():
        for d in range(n):
            m[i + d] = j + d
    return m


def edge(m, lo, hi, step):
    """Map word lo (scanning toward hi) to the other edition, shifting by the
    distance scanned so an unaligned edge word still lands in place."""
    k = lo
    while (k <= hi) if step > 0 else (k >= hi):
        if k in m:
            return m[k] - (k - lo)
        k += step
    return None


def pattern(before, after):
    return f"`{before or '·'} … {after or '·'}`"


def compare(src, dst):
    """For each span in src: (src pattern, dst pattern, kept?, first word)."""
    m = alignment(src, dst)
    out = []
    for a, b in src.spans():
        sp = pattern(src.gap(a), src.gap(b + 1))
        first = src.word(a).lower()
        ta, tb = edge(m, a, b, 1), edge(m, b, a, -1)
        if ta is None or tb is None or not (0 <= ta <= tb < len(dst.w)):
            out.append((sp, None, None, first))
            continue
        before, after = dst.gap(ta), dst.gap(tb + 1)
        out.append((sp, pattern(before, after), "(" in before or ")" in after, first))
    return out


def main():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    names = dict(con.execute("SELECT id, name FROM books WHERE translation='KJV'"))

    def texts(code):
        return {(b, c, v): t for b, c, v, t in con.execute(
            "SELECT book_id, chapter, verse, text FROM verses WHERE translation=?",
            (code,))}

    old, std = texts("KJV1611"), texts("KJV")
    con.close()

    def has(s):
        return "(" in s or ")" in s

    p_old = {k for k in old if has(old[k])}
    p_std = {k for k in std if has(std[k])}
    groups = [("In both editions", sorted(p_old & p_std)),
              ("In the 1611 text only", sorted(p_old - p_std)),
              ("In the 1769 Standard Oxford Edition only", sorted(p_std - p_old))]
    total = len(p_old | p_std)

    lines = {}            # verse -> change lines
    status = Counter()    # kept / kept, punctuation moved inside / removed / added / unaligned
    moves = Counter()     # (status, 1611 pattern, 1769 pattern)
    firsts = {"kept": Counter(), "removed": Counter(), "added": Counter()}
    for k in sorted(p_old | p_std):
        a, o = Verse(old[k]), Verse(std[k])
        out = []
        if k in p_old:
            m = alignment(a, o)
            for (sp, dp, kept, first), (fa, _) in zip(compare(a, o), a.spans()):
                if fa in m:
                    first = o.word(m[fa]).lower()
                if dp is None:
                    status["unaligned"] += 1
                    out.append(f"1611 {sp} → 1769: *could not align — compare by eye*")
                    continue
                st = "kept" if kept else "removed"
                firsts[st][first] += 1
                if kept:
                    inner = re.findall(r"([,;:.?!]+)\)", dp)
                    moved = bool(inner) and not re.search(r"[,;:.?!]\)", sp)
                    status["kept, punctuation moved inside" if moved else "kept"] += 1
                else:
                    status["removed"] += 1
                moves[(st, sp, dp)] += 1
                out.append(f"**{st}** — 1611 {sp} → 1769 {dp}")
        if k in p_std:
            for sp, dp, kept, first in compare(o, a):
                if dp is None:
                    if k not in p_old:
                        status["unaligned"] += 1
                        out.append(f"1769 {sp}: *could not align — compare by eye*")
                    continue
                if kept:
                    continue  # already reported from the 1611 side
                status["added"] += 1
                firsts["added"][first] += 1
                moves[("added", dp, sp)] += 1
                out.append(f"**added** — 1611 {dp} → 1769 {sp}")
        lines[k] = out

    def balanced(s):
        return s.count("(") == s.count(")")

    def entry(k):
        b, c, v = k
        flags = [f"{ed} spans verses" for ed, t, p in
                 (("1611", old[k], p_old), ("1769", std[k], p_std))
                 if k in p and not balanced(t)]
        head = f"### {names[b]} {c}:{v}" + (f" — *{'; '.join(flags)}*" if flags else "")
        body = [head, "", f"- **1611:** {old[k]}", f"- **1769:** {std[k]}"]
        body += [f"- Oxford change: {x}" for x in lines[k]]
        return body + [""]

    def top(st, n=8):
        rows = [(c, s, d) for (x, s, d), c in moves.most_common() if x == st][:n]
        return ["| 1611 | 1769 | Spans |", "|---|---|---|"] + \
               [f"| {s} | {d} | {c} |" for c, s, d in rows]

    def first_words(st, n=10):
        total_st = sum(firsts[st].values()) or 1
        return ", ".join(f"*{w}* {100 * c // total_st}%"
                         for w, c in firsts[st].most_common(n))

    RELATIVE = {"who", "which", "whom", "whose", "that", "where", "whereof"}
    STATEMENT = {"for", "now"}

    def share(st, group):
        n = sum(firsts[st].values()) or 1
        return 100 * sum(c for w, c in firsts[st].items() if w in group) // n

    kept_all = status["kept"] + status["kept, punctuation moved inside"]
    md = [
        "# Parentheses — 1611 King James vs 1769 Standard Oxford Edition",
        "",
        "Generated by `scripts/103_parentheses_1611_vs_1769.py` from "
        "`db/mandela.db`: `KJV1611` (the 1611 original-spelling transcription, "
        "script 102) and `KJV` (the 1769 Blayney text, the project's base). "
        "**A study of what Oxford changed — nothing in the restored text or "
        "the published editions is altered by it.** Neither text here includes "
        "this project's restorations.",
        "",
        f"**{total} verses: {len(groups[0][1])} with parentheses in both "
        f"editions, {len(groups[1][1])} in 1611 only, {len(groups[2][1])} in "
        "1769 only.**",
        "",
        "How to read a pattern: `( … )` shows the marks at the two edges of a "
        "bracketed passage, `…` standing for its words and `·` for no mark. "
        "So 1611 `( … )` → 1769 `, … ,` means Oxford replaced the brackets "
        "with commas. Spelling is ignored when matching the two editions "
        "(*sonne* = *son*).",
        "",
        "## What Oxford did",
        "",
        "| Outcome (per bracketed passage) | Count |",
        "|---|---|",
        f"| **Kept** the parentheses | {kept_all} |",
        f"|  …of which punctuation moved *inside* the closing bracket | "
        f"{status['kept, punctuation moved inside']} |",
        f"| **Removed** the parentheses (1611 had them) | {status['removed']} |",
        f"| **Added** parentheses (1611 had none) | {status['added']} |",
        f"| Could not align automatically | {status['unaligned']} |",
        "",
        "### Most common replacements when Oxford removed them",
        "",
        *top("removed"),
        "",
        "### Most common changes when Oxford kept them",
        "",
        *top("kept"),
        "",
        "### What 1611 had where Oxford added them",
        "",
        *top("added"),
        "",
        "## Why — the patterns in the evidence",
        "",
        "Blayney left no verse-by-verse reasons. His report to the Oxford "
        "Delegates (1769) describes the aims in general terms: correct the "
        "punctuation, the italics and the marginal references to one "
        "consistent standard. The patterns below are read from the data; the "
        "explanations are the usual account of 18th-century printing practice, "
        "not Blayney's own words.",
        "",
        "**1. Brackets became commas around clauses that belong to the "
        "sentence.** The 1611 printers used brackets freely, even around "
        "ordinary descriptive clauses (\"Lot, Abrams brothers sonne, (who dwelt "
        "in Sodome)\"). By the 18th century, brackets were kept for genuine "
        "interruptions, and a clause that grammatically belongs to the "
        "sentence took commas. The first word inside each passage shows the "
        "split:",
        "",
        f"- **Removed** (brackets → commas) — passages starting: {first_words('removed')}",
        f"- **Kept** — passages starting: {first_words('kept')}",
        f"- **Added** — passages starting: {first_words('added')}",
        "",
        "Grouped *(observed)*: passages opening with a statement word "
        f"(*for*, *now*) are {share('kept', STATEMENT)}% of kept and "
        f"{share('added', STATEMENT)}% of added passages, but only "
        f"{share('removed', STATEMENT)}% of removed ones; passages opening "
        f"with a relative word (*who*, *which*, *whom*, *whose*, *that*, "
        f"*where*, *whereof*) are {share('removed', RELATIVE)}% of removed "
        f"passages against {share('kept', RELATIVE)}% of kept ones. The "
        "tendency is real but not a strict rule — many *for* asides were "
        "still turned into commas, so Oxford was also judging how long and "
        "how separable each passage was.",
        "",
        "**2. Brackets were added around asides that stand as their own "
        "statement.** Narrator's background notes (John 4:8 \"(For his "
        "disciples were gone away unto the city to buy meat.)\", Numbers 13:22 "
        "\"(Now Hebron was built seven years before Zoan in Egypt.)\"), glosses "
        "(Romans 10:6 \"(that is, to bring Christ down from above:)\"), and "
        "Paul's asides (2 Corinthians 11:21, 11:23 \"(I speak as a fool)\"). "
        "The test is grammatical rather than about a phrase: Exodus 30:13 and "
        "Numbers 3:47 bracket \"the shekel is twenty gerahs\" because there it "
        "is a complete sentence of its own, while Numbers 18:16 \"…the shekel "
        "of the sanctuary, which is twenty gerahs\" stays unbracketed because "
        "there it is a relative clause *(observed)*.",
        "",
        "**3. Punctuation moved inside the closing bracket.** Where a bracket "
        "was kept, the mark that ends the clause around it was usually placed "
        "*inside* the bracket: 1611 \"(the same is Zoar) and\" → 1769 \"(the "
        "same is Zoar;) and\". This was a standard 18th-century printing "
        "convention, now obsolete, which is why the Oxford text has so many "
        "\"…;)\" and \"…:)\" endings. It is the most frequent *added* "
        "punctuation in the Oxford parentheses.",
        "",
        "**4. Heavier pointing at the edges.** Where 1611 had only a bracket, "
        "Oxford often added a comma, semicolon or colon beside it, in line "
        "with its generally heavier, more systematic punctuation (see "
        "`references/language/colon_versus_semicolon.md`).",
        "",
        "Advisory comparison only — under the Premise Revision both editions "
        "are written texts and neither outranks memory testimony. The 1611 "
        "text is a transcription: confirm any reading you rely on against the "
        "page facsimile. A verse marked *spans verses* holds only one half of "
        "a parentheses that opens or closes in a neighbouring verse.",
        "",
    ]
    for i, (title, keys) in enumerate(groups, 1):
        md += [f"## {i}. {title} ({len(keys)})", ""]
        for k in keys:
            md += entry(k)
    text = "\n".join(md)

    if OUT.exists():
        prev = OUT.read_text(encoding="utf-8")
        if prev == text:
            print(f"{OUT.relative_to(ROOT)}: already current")
            return
        prev_n = len(re.findall(r"^### (?!Most common|What 1611)", prev, re.M))
        if total < prev_n:
            print(f"REFUSED: {OUT.relative_to(ROOT)} lists {prev_n} verses; "
                  f"new version lists {total}.")
            return
    OUT.write_text(text, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {total} verses; " +
          ", ".join(f"{k} {v}" for k, v in status.items()))


if __name__ == "__main__":
    main()
