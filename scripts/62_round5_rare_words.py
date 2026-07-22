#!/usr/bin/env python3
"""62_round5_rare_words.py — Round 5 rare-word review (owner directive
2026-07-21): recompute the rarest words over the CURRENT output (base KJV + all
approved restorations, now including rounds 3-4, girded->adorned, corn->wheat,
the wheat verse edits, and hail->greet), collapse inflections per Early Modern
English, and list the 100 rarest lemmas.

Excludes, per the owner: whitelisted words, names, and locations. Those come
from three sources:
  - references/word_whitelist.md — every linked index word + the "Proper names
    and places" block,
  - word_era.verdict = 'proper_noun' (the corpus proper-noun scan),
  - name_like() — words that are ALWAYS capitalized across every occurrence
    (catches memory/variant-spelled names word_era missed).

Also skips inflections of common words (a form whose stripped base occurs > 8x).
Report only (no DB writes). Mirrors the round-4 builder; output:
references/rare_word_round5_review.md. **src** flags base-KJV vs restoration-
introduced.
"""
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "rare_word_round5_review.md"
COMMON = 8
TOKEN = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")


def fold(f):
    return f.lower().replace("’", "'").replace("–", "-")


def base_candidates(word):
    out = []

    def add(b):
        if b and b != word and len(b) >= 3:
            out.append(b)
    if word.endswith("'s"):
        add(word[:-2])
    elif word.endswith("'"):
        add(word[:-1])
    if word.endswith('ies'):
        add(word[:-3] + 'y')
    if word.endswith('es'):
        add(word[:-2])
    if word.endswith('s') and not word.endswith('ss'):
        add(word[:-1])
    if word.endswith('ied'):
        add(word[:-3] + 'y')
    if word.endswith('ed'):
        add(word[:-2]); add(word[:-2] + 'e'); add(word[:-1])
    for suf in ('eth', 'est'):
        if word.endswith(suf):
            add(word[:-3]); add(word[:-3] + 'e'); add(word[:-2])
    if word.endswith('ing'):
        add(word[:-3]); add(word[:-3] + 'e')
    if word.endswith('en'):
        add(word[:-2]); add(word[:-1])
    if word.endswith('ier'):
        add(word[:-3] + 'y')
    if word.endswith('er'):
        add(word[:-2]); add(word[:-1])
    return out


def main():
    con = sqlite3.connect(DB)
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL ORDER BY id"):
        resto[vid] = new
    bn = {i: n for i, n in con.execute("SELECT id, name FROM books WHERE translation='KJV'")}
    counts, occ, capcount, base_forms = Counter(), defaultdict(list), Counter(), set()
    curtext = {}
    for vid, bid, ch, vs, btext in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        for t in TOKEN.findall(btext):
            base_forms.add(fold(t))
        cur = resto.get(vid, btext)
        curtext[(bid, ch, vs)] = cur
        for t in TOKEN.findall(cur):
            f = fold(t); counts[f] += 1; occ[f].append((bid, ch, vs))
            if t[:1].isupper():
                capcount[f] += 1

    # ---- exclusions: whitelist + proper names/places + word_era proper nouns
    wl = (ROOT / "references" / "word_whitelist.md").read_text(encoding="utf-8")
    excl = set(m.lower() for m in re.findall(r'\[([^\]]+)\]\(#', wl))
    pn = re.search(r'### Proper names and places.*?\n\n(.*?)\n\n## Why', wl, re.S)
    if pn:
        for w in pn.group(1).replace('\n', ' ').split(','):
            w = w.strip().lower()
            if w:
                excl.add(w)
    excl |= set(w for (w,) in con.execute(
        "SELECT word FROM word_era WHERE verdict='proper_noun'"))
    con.close()

    def name_like(w):
        return counts[w] > 0 and capcount[w] == counts[w]

    def infl_of_common(w):
        return any(counts.get(b, 0) > COMMON for b in base_candidates(w))

    cand = [w for w in counts if w not in excl and not name_like(w)
            and not any(b in excl for b in base_candidates(w))
            and not infl_of_common(w)]

    # ---- collapse inflections (union-find on shared bases) -----------------
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            hi = ra if counts.get(ra, 0) >= counts.get(rb, 0) else rb
            lo = rb if hi == ra else ra
            parent[lo] = hi

    candset = set(cand)
    basekey = defaultdict(list)
    for w in cand:
        parent.setdefault(w, w)
        for b in base_candidates(w):
            basekey[b].append(w)
            if b in candset:
                union(w, b)
    for b, ws in basekey.items():
        for w in ws[1:]:
            union(ws[0], w)

    groups = defaultdict(list)
    for w in cand:
        groups[find(w)].append(w)
    rows = []
    for rep, members in groups.items():
        total = sum(counts[m] for m in members)
        label = max(members, key=lambda m: (counts[m], -len(m)))
        src = 'base' if any(m in base_forms for m in members) else 'RESTORED'
        rows.append((label, total, sorted(members, key=lambda m: (-counts[m], m)), src))
    rows.sort(key=lambda r: (r[1], r[0]))
    top = rows[:100]

    print("eligible lemmas:", len(rows),
          "| count1:", sum(1 for r in rows if r[1] == 1),
          "| count2:", sum(1 for r in rows if r[1] == 2))
    print("top-100 restoration-introduced:", sum(1 for r in top if r[3] == 'RESTORED'),
          "| base-KJV:", sum(1 for r in top if r[3] == 'base'))

    def anchor(w):
        return re.sub(r"[^a-z0-9]+", "-", w.lower()).strip("-")

    L = ["# Round 5 — Rare Word Review (rarest first)", "",
         "*The 100 rarest lemmas over the current output (base KJV + all approved "
         "restorations through the hail→greet pass). Inflections collapsed (EModE); "
         "whitelisted words, names, places, and always-capitalized proper nouns "
         "skipped. For each word: its form counts, and every verse it appears in "
         "with the current text, then a blank owner ruling. **src** flags whether "
         "the lemma is native to the base KJV or was introduced by a restoration. "
         "Nothing changed.*", "",
         f"**{len(top)} words (rarest first); {len(rows)} eligible lemmas total.**", "",
         ",\n".join(f"[{lab}](#{anchor(lab)})" for lab, _, _, _ in top), "",
         "## Entries", ""]
    for lab, total, members, src in top:
        L.append(f'#### <a name="{anchor(lab)}"></a>{lab} — {total} '
                 f'use{"s" if total != 1 else ""}  ·  src: {src}')
        L.append("- forms: " + ", ".join(f"{m} ({counts[m]})" for m in members))
        seen = []
        for m in members:
            for (bid, ch, vs) in occ[m]:
                k = (bid, ch, vs)
                if k in seen:
                    continue
                seen.append(k)
                L.append(f"- **{bn[bid]} {ch}:{vs}**")
                L.append(f"  - text: {curtext[k]}")
        L.append("- owner ruling: _____ (keep / whitelist / revise to ___)")
        L.append("")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
