#!/usr/bin/env python3
"""31_manual_word_changes.py — apply references/manual_word_changes_flagged.md
(roadmap task, owner list; applied 2026-07-18).

Corpus-wide word changes: threshingfloor→threshing floor, girdle(s)→apron(s)
with a/an fix, emoticons ;) :) → ), unicorn(s)→ox(en), salute→hail,
publican(s)→tax collector(s), divorcement→divorce, charity→love, bulls→oxen,
builded→built, divers→diverse.

Each affected verse gets one restoration row (flaw_type 'manual_word_change')
built on the verse's LATEST approved restoration text (script 17 takes the
highest-id approved row as the verse's complete final text, so these rows
compose with all earlier workstreams). Idempotent: prior manual_word_change
rows are rebuilt each run. Prints per-rule verse counts vs the owner's
expected counts from the flagged file.
"""
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

# (rule name, expected verse count, pattern, replacement) — order matters:
# multi-word/plural/article rules run before their bare-word fallbacks.
RULES = [
    ("threshingfloor -> threshing floor", 19,
     re.compile(r"\b([Tt])hreshingfloor(s?)\b"), r"\1hreshing floor\2"),
    ("girdles -> aprons", 6, re.compile(r"\b([Gg])irdles\b"), r"\1prons" ),
    ("a girdle -> an apron", 10,
     re.compile(r"\b([Aa]) girdle\b"), r"\1n apron"),
    ("girdle -> apron", 34, re.compile(r"\b([Gg])irdle\b"), r"\1pron"),
    ("winky emoji ;) -> )", 53, re.compile(r";\)"), ")"),
    ("smile emoji :) -> )", 40, re.compile(r":\)"), ")"),
    ("unicorns -> oxen", None, re.compile(r"\b([Uu])nicorns\b"),
     lambda m: "Oxen" if m.group(1) == "U" else "oxen"),
    ("unicorn -> ox", None, re.compile(r"\b([Uu])nicorn\b"),
     lambda m: "Ox" if m.group(1) == "U" else "ox"),
    ("salute -> hail", 57, re.compile(r"\b([Ss])alute\b"),
     lambda m: "Hail" if m.group(1) == "S" else "hail"),
    ("publicans -> tax collectors", 17,
     re.compile(r"\b([Pp])ublicans\b"),
     lambda m: ("Tax" if m.group(1) == "P" else "tax") + " collectors"),
    ("publican -> tax collector", 6,
     re.compile(r"\b([Pp])ublican\b"),
     lambda m: ("Tax" if m.group(1) == "P" else "tax") + " collector"),
    ("saluted -> greeted", None, re.compile(r"\b([Ss])aluted\b"),
     lambda m: "Greeted" if m.group(1) == "S" else "greeted"),
    ("saluteth -> greeteth", None, re.compile(r"\b([Ss])aluteth\b"),
     lambda m: "Greeteth" if m.group(1) == "S" else "greeteth"),
    ("salutation(s) -> greeting(s)", None,
     re.compile(r"\b([Ss])alutation(s?)\b"),
     lambda m: ("Greeting" if m.group(1) == "S" else "greeting") + m.group(2)),
    ("divorcement -> divorce", 6,
     re.compile(r"\b([Dd])ivorcement(s?)\b"), r"\1ivorce\2"),
    ("charity -> love", 28, re.compile(r"\b([Cc])harity\b"),
     lambda m: "Love" if m.group(1) == "C" else "love"),
    ("bulls -> oxen", 10, re.compile(r"\b([Bb])ulls\b"),
     lambda m: "Oxen" if m.group(1) == "B" else "oxen"),
    ("builded -> built", 59, re.compile(r"\b([Bb])uilded\b"),
     lambda m: "Built" if m.group(1) == "B" else "built"),
    ("divers -> diverse", 61, re.compile(r"\b([Dd])ivers\b"),
     lambda m: "Diverse" if m.group(1) == "D" else "diverse"),
]
# combined expected count for the unicorn pair from the flagged file
UNICORN_EXPECTED = 9

EVIDENCE = (
    "Owner manual word-change list (references/manual_word_changes_flagged.md, "
    "applied 2026-07-18): inconsistent archaic forms, era-inappropriate words, "
    "and emoticon punctuation artifacts corrected corpus-wide. If you have a "
    "better replacement recommendation, create a GitHub issue with your "
    "sources: https://github.com/thomasmeadows/mandelabible/issues/new"
)


def main():
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM restorations WHERE flaw_type='manual_word_change'")
    # latest approved text per verse (excluding our own rows, just deleted)
    base = {}
    for vid, text in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL ORDER BY id"):
        base[vid] = text
    counts = Counter()
    applied = 0
    for vid, orig in con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV'"):
        text = base.get(vid, orig)
        new, hits = text, []
        for name, _, pat, repl in RULES:
            new2 = pat.sub(repl, new)
            if new2 != new:
                counts[name] += 1
                hits.append(name)
                new = new2
        if new != text:
            applied += 1
            con.execute(
                "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                "proposed_text, rationale, evidence, confidence, status) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (vid, "manual_word_change", text, new,
                 "Owner manual list: " + "; ".join(hits), EVIDENCE, 0.95,
                 "approved"))
    con.commit()
    print(f"{applied} verses changed")
    uni = counts["unicorns -> oxen"] + counts["unicorn -> ox"]
    for name, expected, _, _ in RULES:
        if name.startswith("unicorn"):
            continue
        flag = "" if expected in (None, counts[name]) else \
            f"  <-- expected {expected}"
        print(f"{counts[name]:4d}  {name}{flag}")
    flag = "" if uni == UNICORN_EXPECTED else f"  <-- expected {UNICORN_EXPECTED}"
    print(f"{uni:4d}  unicorn(s) -> ox(en){flag}")


if __name__ == "__main__":
    main()
