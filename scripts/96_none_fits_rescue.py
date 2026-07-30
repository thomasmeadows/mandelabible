#!/usr/bin/env python3
"""96_none_fits_rescue.py — owner request 2026-07-29.

The king-james round-2 triage had to fill a **whitelist slot** for every group
in `references/word_lists/token_list_full.md`. In a number of groups it
answered "none fits" / "no whitelisted word carries this sense". This script
attacks those failures mechanically, to produce suggestions the agent could
not.

Method — **corpus-wide translation alignment**, not judgement. For a failed
word W:

  1. S = every verse of the restored text containing W (all of them, not a
     sample).
  2. For each of nine other translations T, count for every candidate word c
     the number of verses in S where T reads c and *we do not*  (`a`), against
     c's document frequency across all of T (`df`).
  3. score = (a / df) * log(1 + a) — precision times evidence. A true
     translation equivalent (brass for steel, trough for cistern) appears in
     many of W's verses and seldom elsewhere; a common word that merely
     wanders nearby scores near zero because its df is enormous.
  4. Keep only candidates that are **on `references/word_whitelist.md`**.

A surviving candidate is a whitelisted word that another translation uses
where we use W, repeatedly — exactly the slot-1 suggestion "none fits" claims
does not exist. Each is reported with its witness count, precision, and a
verse where the substitution is visible, so a human can judge it in seconds.

An earlier version of this script ranked candidates by position within a
handful of verses; that produced noise (`hast`, `kine`, `place`) and was
replaced. Positional matching cannot distinguish a synonym from a neighbour.

Corpus quirks handled (both learned in this project): the witness `_books`
tables carry duplicate rows per name (resolved with MIN(id) GROUP BY name),
and the `_verses` tables are duplicated ~7x (deduped on book/chapter/verse).

Read-only everywhere. Output: `references/word_lists/none_fits_rescue.md`.

Usage:
    python3 scripts/96_none_fits_rescue.py [--tag r2] [--min-hits 2]
"""
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
WITNESS_DIR = ROOT / "bible_databases" / "formats" / "sqlite"
TRIAGE_DIR = ROOT / "references" / "word_reviews" / "token_triage"
WHITELIST = ROOT / "references" / "word_whitelist.md"
OUT = ROOT / "references" / "word_lists" / "none_fits_rescue.md"

PERIOD = ["Geneva1599", "Tyndale", "Wycliffe"]
MODERN = ["ASV", "Darby", "YLT", "Webster", "DRC", "BSB"]

HDR = re.compile(r"^## (.+?)\s+—\s+(\d+) uses", re.I)
SLOT = re.compile(r"^-\s*(verdict|whitelist):\s*(.*)$", re.I)
NONE_FITS = re.compile(r"none fits|no whitelisted|nothing on the whitelist|"
                       r"none exact", re.I)
# an entry that names a real candidate before saying "no whitelisted X" is not
# a failure — it filled the slot and then qualified it
HAS_CANDIDATE = re.compile(r"\*\*[a-z][a-z' -]+\*\*", re.I)
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")

STOP = set("""a an the and or but if of to in on at by for with from unto into
upon out up down over under again also as is are was were be been being am
that this these those there here it its his her their our your my thine thy
thee thou ye you he she they them us we i not no nor so then than when while
where which who whom whose what shall will would should may can could do did
done doth hath have has had o yea verily lord god all any some every each
one two three now come came go went gone said say saith sayeth spake speak
made make man men people son sons house land king thing things after before
because therefore against about among between such same other another own
""".split())


def fold(w):
    return w.lower().replace("’", "'")


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def load_failures(tag):
    out, cur = [], None
    for path in sorted(TRIAGE_DIR.glob(f"batch_*{tag}_triage.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = HDR.match(line)
            if m:
                cur = {"word": m.group(1).strip().lower(),
                       "count": int(m.group(2)), "verdict": "",
                       "whitelist": "", "batch": path.stem}
                continue
            if not cur:
                continue
            s = SLOT.match(line)
            if not s:
                continue
            cur[s.group(1).lower()] = s.group(2).strip()
            if s.group(1).lower() == "whitelist":
                txt = cur["whitelist"]
                if NONE_FITS.search(txt) and not HAS_CANDIDATE.search(txt):
                    out.append(cur)
                cur = None
    return out


def whitelist_words():
    return {fold(w) for w in re.findall(
        r"^\[(.+?)\]\(#", WHITELIST.read_text(encoding="utf-8"), re.M)}


def restored_verses():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))
    final = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL ORDER BY id"):
        final[vid] = t
    out = {}
    for vid, bid, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        out[(books[bid], ch, vs)] = final.get(vid, orig)
    con.close()
    return out


def load_witness(name):
    """(ref -> token set, ref -> text, df Counter) or None."""
    path = WITNESS_DIR / f"{name}.db"
    if not path.exists():
        return None
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    ids = {r[1]: r[0] for r in con.execute(
        f"SELECT MIN(id), name FROM {name}_books GROUP BY name")}
    by_id = {v: k for k, v in ids.items()}
    seen, toks, texts, df = set(), {}, {}, Counter()
    for bid, ch, vs, txt in con.execute(
            f"SELECT book_id, chapter, verse, text FROM {name}_verses"):
        key = (bid, ch, vs)
        if key in seen or bid not in by_id:
            continue
        seen.add(key)
        ref = (by_id[bid], ch, vs)
        s = {fold(t) for t in TOKEN_RE.findall(txt)}
        toks[ref] = s
        texts[ref] = txt
        df.update(s)
    con.close()
    return toks, texts, df


def main():
    tag = "_" + arg("--tag", "r2").strip("_")
    min_hits = int(arg("--min-hits", "2"))

    failures = load_failures(tag)
    if not failures:
        sys.exit(f"no 'none fits' entries found in batch_*{tag}_triage.md")
    wl = whitelist_words()
    ours = restored_verses()
    our_toks = {ref: {fold(t) for t in TOKEN_RE.findall(txt)}
                for ref, txt in ours.items()}

    witnesses = {}
    for name in PERIOD + MODERN:
        w = load_witness(name)
        if w:
            witnesses[name] = w
    print(f"witness corpora loaded: {len(witnesses)}")

    # verses per failed word
    wanted = {f["word"] for f in failures}
    occ = defaultdict(list)
    for ref, toks in our_toks.items():
        for w in wanted & toks:
            occ[w].append(ref)

    rescued, empty = [], []
    for f in sorted(failures, key=lambda x: (-x["count"], x["word"])):
        word = f["word"]
        refs = occ.get(word, [])
        if not refs:
            empty.append(f)
            continue
        # forms of the failed word, so a witness that merely spells it
        # differently is not counted as substituting for it
        stem = word[:-1] if len(word) > 4 and word.endswith("s") else word
        stem = stem[:max(4, len(stem) - 3)]

        scores = {}
        for name, (toks, texts, df) in witnesses.items():
            hits = Counter()
            example = {}
            for ref in refs:
                wt = toks.get(ref)
                if not wt:
                    continue
                # the witness must render this verse WITHOUT our word — only
                # then is another word standing in its place
                if any(t.startswith(stem) for t in wt):
                    continue
                ot = our_toks[ref]
                for c in wt:
                    if (c in ot or c in STOP or c not in wl
                            or len(c) < 3 or c == word):
                        continue
                    hits[c] += 1
                    example.setdefault(c, ref)
            for c, a in hits.items():
                if a < min_hits:
                    continue
                prec = a / df[c]
                sc = prec * math.log(1 + a)
                rec = scores.setdefault(c, {"score": 0.0, "wits": {},
                                            "ex": example[c]})
                rec["score"] += sc
                rec["wits"][name] = (a, len(refs), prec)
        ranked = sorted(scores.items(), key=lambda kv: -kv[1]["score"])
        ranked = [(c, r) for c, r in ranked
                  if max(p for _, _, p in r["wits"].values()) >= 0.15][:4]
        (rescued if ranked else empty).append(
            (f, ranked) if ranked else f)

    lines = [
        "# \"None fits\" rescue — whitelisted candidates the triage missed",
        "",
        "*Generated by `scripts/96_none_fits_rescue.py` (owner request "
        "2026-07-29).*",
        "",
        f"The king-james round-2 triage answered **\"none fits\"** — no "
        f"protected word carries the sense — in **{len(failures)}** of its "
        "1,163 whitelist slots. This report tests that claim by corpus-wide "
        "alignment: for each failed word, every verse where it occurs is "
        "compared against nine other translations, and a candidate is kept "
        "only when a witness repeatedly reads it where we read the failed "
        "word, it is absent from our own rendering of those verses, and it is "
        "**on the whitelist**.",
        "",
        "`hits` = verses where that witness reads the candidate and we do "
        "not; `prec` = share of the candidate's *entire* appearances in that "
        "translation that fall on our word's verses — high precision means a "
        "genuine translation equivalent rather than a common word. Period "
        "witnesses (Geneva 1599, Tyndale, Wycliffe) are marked **P**, modern "
        "ones (ASV, Darby, YLT, Webster, DRC, BSB) **M**.",
        "",
        "Machine evidence only. Every candidate still needs a human ear "
        "before it becomes a swap, and nothing here is applied.",
        "",
        f"**{len(rescued)} of {len(failures)} failures yielded at least one "
        f"whitelisted candidate; {len(empty)} stand.**",
        "",
        "## Rescued", "",
    ]
    for f, ranked in rescued:
        lines.append(f"### {f['word']} — {f['count']} uses "
                     f"({f['verdict'] or 'no verdict'})")
        lines.append(f"- agent said: {f['whitelist'][:280]}")
        for c, r in ranked:
            tiers = "".join("P" if n in PERIOD else "M"
                            for n in sorted(r["wits"]))
            best = max(r["wits"].items(), key=lambda kv: kv[1][2])
            name, (a, tot, prec) = best
            ref = r["ex"]
            txt = witnesses[name][1].get(ref, "")
            lines.append(
                f"- **{c}** — {len(r['wits'])} witnesses [{tiers}], "
                f"{a}/{tot} verses in {name}, prec {prec:.2f} — "
                f"{ref[0]} {ref[1]}:{ref[2]}: \"{txt.strip()[:180]}\"")
        lines.append(f"- source: `{f['batch']}.md`")
        lines.append("- **OWNER RULING:**")
        lines.append("")
    if empty:
        lines += ["## No whitelisted candidate found", "",
                  "The agent's \"none fits\" stands for these.", "",
                  ", ".join(f"{f['word']} ({f['count']})" for f in empty), ""]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(failures)} failures — "
          f"{len(rescued)} rescued, {len(empty)} stand")


if __name__ == "__main__":
    main()
