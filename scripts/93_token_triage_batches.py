#!/usr/bin/env python3
"""93_token_triage_batches.py — owner request 2026-07-29.

Split what is left of the token list — the 1,164 inflection groups in
`references/word_lists/token_list_full.md` that the whitelist and the
proper-noun exclusions do NOT protect — into batches for the king-james agent
to triage (KEEP / WHITELIST / REPLACE per group).

This is the same shape as `scripts/84_remaining_words_for_kj.py` (which fed the
whitelist review): a read-only builder that produces agent input files, one per
batch, under `references/word_reviews/token_triage/`. Each group carries its
forms, its corpus count, and up to EXAMPLES occurrence verses **from the
restored text** (base KJV + every approved restoration composed, the same text
the export ships) so the agent rules on the reading as it now stands.

Read-only with respect to db/mandela.db. Idempotent: refuses to overwrite an
existing batch file unless --force, since agent-facing artifacts under
references/ are permanent (CLAUDE.md → Generated Artifacts).

Usage:
    python3 scripts/93_token_triage_batches.py [--batches 6] [--force]
"""
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
TOKENS = ROOT / "references" / "word_lists" / "token_list_full.md"
OUT_DIR = ROOT / "references" / "word_reviews" / "token_triage"

ROW = re.compile(r"^\| \d+ \| (\S+) \| (\d+) \| (.*?) \|")
FORM = re.compile(r"(\S+) \(×\d+\)")
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")
EXAMPLES = 3          # occurrence verses quoted per group


def arg(name, default):
    if name in sys.argv:
        return int(sys.argv[sys.argv.index(name) + 1])
    return default


def tag():
    """--tag r2 → batch_N_r2_input.md, so a re-run under revised instructions
    never overwrites the previous round's permanent artifacts."""
    if "--tag" in sys.argv:
        return "_" + sys.argv[sys.argv.index("--tag") + 1].strip("_")
    return ""


def fold(form):
    return form.lower().replace("’", "'").replace("–", "-")


def load_groups():
    groups = []
    for ln in TOKENS.read_text(encoding="utf-8").splitlines():
        m = ROW.match(ln)
        if not m:
            continue
        base, count = m.group(1).lower(), int(m.group(2))
        forms = sorted({f.lower() for f in FORM.findall(m.group(3))}
                       | {base})
        groups.append((base, count, forms))
    return groups


def restored_text(con):
    """(ref, text) per verse of the composed restored text — script 82's rule."""
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))
    final = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL ORDER BY id"):
        final[vid] = t
    out = []
    for vid, book_id, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        out.append((f"{books[book_id]} {ch}:{vs}", final.get(vid, orig)))
    return out


def main():
    n_batches = arg("--batches", 6)
    force = "--force" in sys.argv

    groups = load_groups()
    if not groups:
        sys.exit(f"no rows parsed from {TOKENS.name} — aborting")

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    verses = restored_text(con)
    con.close()

    wanted = {f for _, _, forms in groups for f in forms}
    examples = defaultdict(list)          # form -> [(ref, text)]
    for ref, text in verses:
        seen = {fold(t) for t in TOKEN_RE.findall(text)}
        for f in seen & wanted:
            if len(examples[f]) < EXAMPLES:
                examples[f].append((ref, text))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    size = -(-len(groups) // n_batches)
    written = []
    for i in range(n_batches):
        chunk = groups[i * size:(i + 1) * size]
        if not chunk:
            continue
        path = OUT_DIR / f"batch_{i + 1}{tag()}_input.md"
        if path.exists() and not force:
            print(f"skip (exists): {path.relative_to(ROOT)}")
            continue
        lines = [
            f"# Token triage — batch {i + 1} of {n_batches}",
            "",
            f"{len(chunk)} inflection groups from "
            "`references/word_lists/token_list_full.md` (the words the "
            "whitelist and proper-noun exclusions do NOT protect), counts "
            f"{chunk[0][1]}–{chunk[-1][1]}. Verses are the **restored text** "
            "as it now stands.",
            "",
        ]
        for base, count, forms in chunk:
            lines.append(f"## {base} — {count} uses — forms: "
                         + ", ".join(forms))
            for f in forms:
                for ref, text in examples.get(f, []):
                    lines.append(f"- {f} — {ref}: {text.strip()}")
            lines.append("")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written.append((path, len(chunk)))
        print(f"{path.relative_to(ROOT)}: {len(chunk)} groups")

    print(f"{len(groups)} groups total, {len(written)} batch files written")


if __name__ == "__main__":
    main()
