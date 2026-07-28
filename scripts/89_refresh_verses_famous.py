#!/usr/bin/env python3
"""89_refresh_verses_famous.py — refresh the curated famous-verse list
(`references/verses/verses_famous.md`) for the verses a given migration touched.

`references/verses/verses_famous.md` shows, for each of its curated verses, the
**current Mandela Bible reading** (base KJV + every `status='approved'`
restoration, as `scripts/17_export_full.py` builds it) plus whether that verse
differs from the base KJV, and if so the base "was" reading. Those are derived
data: any migration that writes to `restorations` can make them stale.
CLAUDE.md's revert/migration protocol calls for regenerating the curated lists
that read the DB after such a change; this is that step.

**Scoped on purpose.** The file also carries owner hand-edits that intentionally
diverge from the database (Genesis 1:26 is one), and blanket-regenerating it
would erase them — forbidden by CLAUDE.md's Content Modification Protocol. So
this script only rewrites entries whose verse was changed by the migration named
with `--flaw` (default: the 2026-07-27 word-swap migration, scripts/88). Every
*other* entry that disagrees with the database is reported, never touched.

Per refreshed entry it rewrites the `> ` quoted reading, the `- **Changed:**`
line, the `- **Base KJV (was):**` line, and the `*` changed-marker on the
heading and the index link. Curated selection, order, prose and anchors are
never touched.

Idempotent: a second run reports "already current" and rewrites nothing.

Usage:
    python3 scripts/89_refresh_verses_famous.py
    python3 scripts/89_refresh_verses_famous.py --dry-run
    python3 scripts/89_refresh_verses_famous.py --flaw <flaw_type>
"""
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
DOC_PATH = ROOT / "references" / "verses" / "verses_famous.md"
DEFAULT_FLAW = "word_swaps_talk_glad_tarry"

HEADING_RE = re.compile(r'^#### <a name="([^"]+)"></a>(.+?)(\*?)$')
INDEX_RE = re.compile(r'^\[(.+?)(\*?)\]\(#([^)]+)\),?\s*$')
TALLY_RE = re.compile(
    r'^\*\*(\d+) verses\*\* — (\d+) changed from base KJV, (\d+) unchanged\.')
CHANGED_LINE = "- **Changed:** yes — differs from the base KJV."
UNCHANGED_LINE = "- **Changed:** no — matches the base KJV."
WAS_PREFIX = "- **Base KJV (was):** "

# The document writes numbered books as "1 Samuel"; the database uses Roman
# numerals ("I Samuel"). Same books, two spellings.
ARABIC_TO_ROMAN = {"1": "I", "2": "II", "3": "III"}
# Books the document names differently from the database.
BOOK_ALIASES = {"Revelation": "Revelation of John"}


def db_ref(ref):
    """'1 Samuel 16:7' -> 'I Samuel 16:7'; other refs pass through."""
    book, _, rest = ref.rpartition(" ")
    if book in BOOK_ALIASES:
        ref = f"{BOOK_ALIASES[book]} {rest}"
    head = ref.split(" ", 1)
    if len(head) == 2 and head[0] in ARABIC_TO_ROMAN:
        return f"{ARABIC_TO_ROMAN[head[0]]} {head[1]}"
    return ref


def load_texts(con, flaw):
    """base text, current restored text, and the refs touched by `flaw`."""
    base, current, touched = {}, {}, set()
    for name, ch, vs, txt in con.execute(
            "SELECT b.name, v.chapter, v.verse, v.text FROM verses v "
            "JOIN books b ON b.id = v.book_id AND b.translation = v.translation "
            "WHERE v.translation='KJV'"):
        base[f"{name} {ch}:{vs}"] = txt
    for name, ch, vs, txt, ftype in con.execute(
            "SELECT b.name, v.chapter, v.verse, r.proposed_text, r.flaw_type "
            "FROM restorations r JOIN verses v ON v.id = r.verse_id "
            "JOIN books b ON b.id = v.book_id AND b.translation = v.translation "
            "WHERE r.status='approved' AND r.proposed_text IS NOT NULL "
            "ORDER BY r.id"):
        ref = f"{name} {ch}:{vs}"
        current[ref] = txt
        if ftype == flaw:
            touched.add(ref)
    merged = dict(base)
    merged.update(current)
    return base, merged, touched


def main():
    dry_run = "--dry-run" in sys.argv
    flaw = DEFAULT_FLAW
    if "--flaw" in sys.argv:
        flaw = sys.argv[sys.argv.index("--flaw") + 1]

    con = sqlite3.connect(DB_PATH)
    base, current, touched = load_texts(con, flaw)
    con.close()

    lines = DOC_PATH.read_text(encoding="utf-8").split("\n")
    out = []
    i = 0
    marked_changed = set()  # refs carrying the * marker after this run
    updated, stale, unknown = [], [], []

    while i < len(lines):
        m = HEADING_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        anchor, ref, marker = m.group(1), m.group(2), m.group(3)
        j = i + 1
        entry = []
        while j < len(lines) and not HEADING_RE.match(lines[j]):
            entry.append(lines[j])
            j += 1

        key = db_ref(ref)
        if key not in current:
            unknown.append(ref)
            out.append(lines[i])
            out.extend(entry)
            i = j
            continue

        cur_text, base_text = current[key], base[key]
        quoted = next((l[2:] for l in entry if l.startswith("> ")), None)

        if key not in touched:
            # Not this migration's business: keep verbatim, but report drift.
            if quoted is not None and quoted.rstrip() != cur_text.rstrip():
                stale.append(ref)
            if marker:
                marked_changed.add(ref)
            out.append(lines[i])
            out.extend(entry)
            i = j
            continue

        is_changed = cur_text != base_text
        if is_changed:
            marked_changed.add(ref)

        quote_seen = False
        rebuilt = []
        for line in entry:
            if line.startswith("> ") and not quote_seen:
                quote_seen = True
                rebuilt.append("> " + cur_text)
            elif line.startswith("- **Changed:**"):
                rebuilt.append(CHANGED_LINE if is_changed else UNCHANGED_LINE)
            elif line.startswith(WAS_PREFIX):
                if is_changed:
                    rebuilt.append(WAS_PREFIX + base_text)
            else:
                rebuilt.append(line)
        if is_changed and not any(l.startswith(WAS_PREFIX) for l in rebuilt):
            for k, line in enumerate(rebuilt):
                if line.startswith("- **Changed:**"):
                    rebuilt.insert(k + 1, WAS_PREFIX + base_text)
                    break

        heading = f'#### <a name="{anchor}"></a>{ref}' + ("*" if is_changed else "")
        if heading != lines[i] or rebuilt != entry:
            updated.append(ref)
        out.append(heading)
        out.extend(rebuilt)
        i = j

    # Index links: keep the * markers in step with the headings.
    for k, line in enumerate(out):
        m = INDEX_RE.match(line)
        if not m:
            continue
        ref, _marker, anchor = m.group(1), m.group(2), m.group(3)
        star = "*" if ref in marked_changed else ""
        tail = "," if line.rstrip().endswith(",") else ""
        out[k] = f"[{ref}{star}](#{anchor}){tail}"

    # Header tally, counted off the markers actually present in the document
    # (which includes the untouched owner-edited entries).
    entries = re.findall(r'^#### <a name="[^"]+"></a>(.+?)(\*?)$',
                         "\n".join(out), re.M)
    total, n_changed = len(entries), sum(1 for _, mk in entries if mk)
    for k, line in enumerate(out):
        if TALLY_RE.match(line):
            out[k] = TALLY_RE.sub(
                f"**{total} verses** — {n_changed} changed from base KJV, "
                f"{total - n_changed} unchanged.", line)
            break

    new_doc = "\n".join(out)

    if unknown:
        print(f"WARNING: {len(unknown)} refs not found in the DB: {unknown[:5]}")
    if stale:
        print(f"NOTE: {len(stale)} entries outside this migration disagree with "
              f"the database and were left untouched (owner edits / earlier "
              f"migrations): {', '.join(stale[:8])}"
              f"{' …' if len(stale) > 8 else ''}")
    if new_doc == DOC_PATH.read_text(encoding="utf-8"):
        print(f"verses_famous.md: already current for flaw_type '{flaw}'.")
        return
    print(f"verses_famous.md: {len(updated)} entries refreshed for flaw_type "
          f"'{flaw}'{' (dry run — nothing written)' if dry_run else ''}")
    for ref in updated:
        print(f"  {ref}")
    if not dry_run:
        DOC_PATH.write_text(new_doc, encoding="utf-8")


if __name__ == "__main__":
    main()
