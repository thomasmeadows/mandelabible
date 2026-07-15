#!/usr/bin/env python3
"""11_import_memories.py — Phase 5: import remembered_verses.md into `memories`
and produce the corroboration report.

`references/remembered_verses.md` stays the human-editable source of record;
this script re-imports it whenever new memories are added.

Parsing: each `## ` heading is one memory. Within a section, text under a
"Current"-type subheading becomes current_text; text under a Memory-type
subheading ("Memory", "What people remember", "Problems and what was
remembered", "Memory / Owner ruling") becomes remembered_text; References and
Advisory subsections go to evidence. Verse references (all KJV book names +
common aliases/typos) found anywhere in the section become scope_refs; the
first one in the Current block is the primary verse_ref.

memory_type is assigned from a documented title-keyword table (roadmap
Phase 5 decisions).

Corroboration (Decision Log #5): corroboration = independent memory agreement
and/or co-located alteration artifacts. This script scores:
  - artifact co-location: Phase 3 `anomalies` rows on the memory's scope
    verses, and `word_era` suspect/anachronism verdicts on suspicious tokens
    the memory names;
  - documented public memory: external reference links in the entry count as
    weak independent-memory evidence (they document unrelated rememberers);
  - witness readings (verse_diffs) are attached as ADVISORY context only —
    they neither confirm nor refute (Premise Revision).
Status: 'corroborated' if any artifact signal AND any memory-side signal;
'artifact-supported' if artifacts only; 'unconfirmed' otherwise.

Outputs: `memories` + `memory_signals` tables, and
`references/corroboration_report.md` (generated — do not hand-edit).

Idempotent: rebuilds both tables and the report each run.
"""

import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
MD_PATH = REPO_ROOT / "references" / "remembered_verses.md"
REPORT_PATH = REPO_ROOT / "references" / "corroboration_report.md"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")

TITLE_TYPES = [  # (title keyword, memory_type) — first match wins
    ("genesis 1:1", "punctuation"),
    ("bottles", "word_substitution"),
    ("lion", "phrase_change"),
    ("lord's prayer", "missing_phrase"),
    ("couch", "missing_letter"),
    ("diver", "missing_letter"),
    ("tables", "missing_letter"),
    ("error", "word_substitution"),
    ("charity", "word_substitution"),
    ("matrix", "word_substitution"),
    ("emoji", "emoticon"),
    ("eyes to see", "phrase_change"),
    ("destroyed", "word_substitution"),
    ("capitalization", "capitalization"),
    ("serpent", "phrase_change"),
    ("windows", "word_substitution"),
    ("thanksgiving", "word_substitution"),
    ("wizard", "word_substitution"),
    ("money", "phrase_change"),
    ("judge not", "phrase_change"),
    ("strait", "missing_letter"),
    ("on earth", "word_substitution"),
    ("philippians", "word_substitution"),
]

ALIASES = {  # md-file spellings -> KJV book names
    "1 samuel": "I Samuel", "2 samuel": "II Samuel", "1 kings": "I Kings",
    "2 kings": "II Kings", "1 chronicles": "I Chronicles", "2 chronicles": "II Chronicles",
    "1 timothy": "I Timothy", "2 timothy": "II Timothy", "1 john": "I John",
    "2 john": "II John", "3 john": "III John", "1 corinthians": "I Corinthians",
    "2 corinthians": "II Corinthians", "1 thessalonians": "I Thessalonians",
    "2 thessalonians": "II Thessalonians", "1 peter": "I Peter", "2 peter": "II Peter",
    "mathew": "Matthew", "hoseah": "Hosea", "revelation": "Revelation of John",
    "psalm": "Psalms",
}

MEMORY_HEADINGS = ("memory", "what people remember", "problems and what was remembered")

SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_ref      TEXT,      -- 'Genesis 1:1'; NULL for bible-wide memories
    memory_type    TEXT,
    title          TEXT,
    current_text   TEXT,
    remembered_text TEXT,
    evidence       TEXT,
    scope_refs     TEXT,      -- ';'-separated resolved refs
    status         TEXT       -- 'corroborated' | 'artifact-supported' | 'unconfirmed'
);
CREATE TABLE IF NOT EXISTS memory_signals (
    memory_id  INTEGER REFERENCES memories(id),
    kind       TEXT,   -- 'artifact' | 'public_memory' | 'advisory_witness'
    detail     TEXT
);
"""


def build_ref_regex(book_names):
    names = sorted(set(book_names) | set(ALIASES), key=len, reverse=True)
    alt = "|".join(re.escape(n) for n in names)
    return re.compile(rf"\b({alt})\s+(\d+):(\d+(?:[–-]\d+)?)", re.I)


def canon_book(name, book_names_lower):
    low = name.lower()
    if low in ALIASES:
        return ALIASES[low]
    return book_names_lower.get(low)


def split_sections(md):
    parts = re.split(r"^## ", md, flags=re.M)[1:]
    for part in parts:
        title, _, body = part.partition("\n")
        yield title.strip(), body


def subsections(body):
    out, current = {}, "_pre"
    out[current] = []
    for line in body.splitlines():
        if line.startswith("### ") or line.startswith("#### "):
            current = line.lstrip("# ").strip().lower()
            out.setdefault(current, [])
        else:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def classify(title):
    t = title.lower()
    for kw, typ in TITLE_TYPES:
        if kw in t:
            return typ
    return "unclassified"


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)
        book_names = [n for (n,) in con.execute(
            "SELECT name FROM books WHERE translation='KJV'")]
        book_lower = {n.lower(): n for n in book_names}
        ref_re = build_ref_regex(book_names)

        md = MD_PATH.read_text(encoding="utf-8")
        con.execute("BEGIN")
        con.execute("DELETE FROM memory_signals")
        con.execute("DELETE FROM memories")

        report = ["# Memory Corroboration Report",
                  "",
                  "*Generated by `scripts/11_import_memories.py` — do not hand-edit.*",
                  "",
                  "Corroboration per Decision Log #5: independent memory agreement and/or",
                  "co-located alteration artifacts. Witness readings are advisory only.",
                  ""]

        n_by_status = {}
        for title, body in split_sections(md):
            subs = subsections(body)
            current_text = "\n\n".join(
                v for k, v in subs.items() if k.startswith("current")) or None
            remembered = "\n\n".join(
                v for k, v in subs.items()
                if any(k.startswith(h) or h in k for h in MEMORY_HEADINGS)) or None
            evidence = "\n\n".join(
                v for k, v in subs.items()
                if k.startswith("reference") or k.startswith("advisory")
                or k.startswith("in addition")) or None

            # scope refs: resolve every verse reference in the title + section
            refs = []
            for m in ref_re.finditer(title + "\n" + body):
                book = canon_book(m.group(1), book_lower)
                if book:
                    ref = f"{book} {m.group(2)}:{m.group(3).split('–')[0].split('-')[0]}"
                    if ref not in refs:
                        refs.append(ref)
            primary = None
            if current_text:
                m = ref_re.search(current_text)
                if m:
                    book = canon_book(m.group(1), book_lower)
                    if book:
                        primary = f"{book} {m.group(2)}:{m.group(3).split('–')[0].split('-')[0]}"
            if primary is None and refs:
                primary = refs[0]

            cur = con.execute(
                "INSERT INTO memories (verse_ref, memory_type, title, current_text, "
                "remembered_text, evidence, scope_refs, status) VALUES (?,?,?,?,?,?,?,?)",
                (primary, classify(title), title, current_text, remembered,
                 evidence, ";".join(refs), "unconfirmed"))
            mid = cur.lastrowid

            # resolve scope refs -> verse ids
            vids = []
            for ref in refs:
                book, cv = ref.rsplit(" ", 1)
                ch, vs = cv.split(":")
                row = con.execute(
                    """SELECT v.id FROM verses v JOIN books b
                       ON b.translation='KJV' AND b.id=v.book_id
                       WHERE v.translation='KJV' AND b.name=? AND v.chapter=? AND v.verse=?""",
                    (book, int(ch), int(vs))).fetchone()
                if row:
                    vids.append((ref, row[0]))

            artifacts = 0
            for ref, vid in vids:
                for typ, tok, detail in con.execute(
                        "SELECT type, token, detail FROM anomalies WHERE verse_id=?", (vid,)):
                    con.execute("INSERT INTO memory_signals VALUES (?,?,?)",
                                (mid, "artifact", f"{ref}: [{typ}] {detail}"))
                    artifacts += 1

            # word_era artifacts on suspicious tokens the memory names in its title/current text
            check_words = {t.lower() for t in TOKEN_RE.findall(title)}
            for w in sorted(check_words):
                row = con.execute(
                    "SELECT verdict, cleared_by FROM word_era WHERE word=? "
                    "AND verdict IN ('suspect','anachronism')", (w,)).fetchone()
                if row:
                    con.execute("INSERT INTO memory_signals VALUES (?,?,?)",
                                (mid, "artifact",
                                 f"word_era: '{w}' verdict={row[0]} "
                                 "(attested in no local pre-1611 corpus)"))
                    artifacts += 1

            public = len(re.findall(r"https?://", body))
            if public:
                con.execute("INSERT INTO memory_signals VALUES (?,?,?)",
                            (mid, "public_memory",
                             f"{public} external reference link(s) documenting "
                             "unrelated rememberers"))

            witness_notes = 0
            for ref, vid in vids[:3]:  # advisory context for the primary refs
                for w, sim, notable in con.execute(
                        """SELECT witness, similarity, notable FROM verse_diffs
                           WHERE verse_id=? AND witness IN ('Geneva1599','Tyndale','Wycliffe')
                           AND witness_text IS NOT NULL""", (vid,)):
                    con.execute("INSERT INTO memory_signals VALUES (?,?,?)",
                                (mid, "advisory_witness", f"{ref} {w} (sim {sim}): {notable}"))
                    witness_notes += 1

            status = ("corroborated" if artifacts and public
                      else "artifact-supported" if artifacts
                      else "unconfirmed")
            con.execute("UPDATE memories SET status=? WHERE id=?", (status, mid))
            n_by_status[status] = n_by_status.get(status, 0) + 1

            report += [f"## {title}", "",
                       f"- **Type**: {classify(title)}  |  **Primary ref**: {primary or 'bible-wide'}"
                       f"  |  **Status**: **{status}**",
                       f"- Scope verses resolved: {len(vids)}/{len(refs)}",
                       f"- Co-located artifact signals: {artifacts}",
                       f"- Public memory documentation: {public} link(s)",
                       f"- Advisory witness readings attached: {witness_notes}", ""]
            top = con.execute(
                "SELECT detail FROM memory_signals WHERE memory_id=? AND kind='artifact' "
                "LIMIT 5", (mid,)).fetchall()
            if top:
                report.append("Top artifact signals:")
                report += [f"- {d}" for (d,) in top]
                report.append("")

        con.commit()
        REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

        total = sum(n_by_status.values())
        print(f"memories imported: {total}  {n_by_status}")
        print(f"signals: ", dict(con.execute(
            "SELECT kind, COUNT(*) FROM memory_signals GROUP BY kind")))
        print(f"report -> {REPORT_PATH}")
        for t, ref, st in con.execute(
                "SELECT title, verse_ref, status FROM memories ORDER BY id"):
            print(f"  [{st:18}] {ref or 'bible-wide':24} {t[:60]}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
