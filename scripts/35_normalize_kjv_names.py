#!/usr/bin/env python3
"""35_normalize_kjv_names.py — unify KJV-internal name spellings (2026-07-18).

The KJV spells the same person/place multiple ways (OT "Elijah" vs NT
"Elias"; "Hagar" vs Galatians' "Agar"; "Zion" vs "Sion"). Owner directive
2026-07-18: conform every such name to its most common modern spelling
(which for these pairs matches the dominant KJV form — see
`references/name_variants.md` for the witness-spelling evidence).

Mechanics (same composition rules as scripts 32/34): each affected verse
gets an approved restoration (flaw_type `name_normalization`) whose text is
the verse's LATEST approved restoration with the variant tokens replaced.
Idempotent: prior name_normalization rows are rebuilt each run.

Trap cases handled:
- Sion at Deuteronomy 4:48 is Mount Hermon, NOT Zion — excluded.
- Jonas at John 21:15-17 is Simon Peter's father (modern texts read
  "John"), not the prophet — excluded, left for owner ruling.
- Jesus at Acts 7:45 and Hebrews 4:8 renders Greek Ἰησοῦς meaning JOSHUA
  (the successor of Moses) — verse-scoped fix to "Joshua".

Ambiguous pairs (Aram/Ram, Heber/Eber, Bosor/Beor, Sarepta/Zarephath,
Enos/Enosh, Oshea, Jona, Elisabeth) are NOT applied; they are listed in
`references/name_normalization.md` for owner ruling.

Output: `references/name_normalization.md` — every mapping with verse
counts plus the deferred list. Refuses to overwrite with an emptier file.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
OUT_PATH = ROOT / "references" / "name_normalization.md"

# variant (KJV spelling) -> canonical modern spelling (also a KJV spelling)
MAPPING = {
    "Agar": "Hagar", "Elias": "Elijah", "Eliseus": "Elisha",
    "Esaias": "Isaiah", "Jeremias": "Jeremiah", "Jeremy": "Jeremiah",
    "Osee": "Hosea", "Noe": "Noah", "Core": "Korah", "Jonas": "Jonah",
    "Sara": "Sarah", "Rebecca": "Rebekah", "Rachab": "Rahab",
    "Booz": "Boaz", "Roboam": "Rehoboam", "Abia": "Abijah",
    "Josaphat": "Jehoshaphat", "Ozias": "Uzziah", "Joatham": "Jotham",
    "Achaz": "Ahaz", "Ezekias": "Hezekiah", "Manasses": "Manasseh",
    "Josias": "Josiah", "Jechonias": "Jeconiah",
    "Salathiel": "Shealtiel", "Zorobabel": "Zerubbabel",
    "Sadoc": "Zadok", "Esrom": "Hezron", "Naasson": "Nahshon",
    # Pharez -> Perez bible-wide (owner ruling 2026-07-18): matches the
    # TSBC-approved modern form at Matthew 1:3
    "Phares": "Perez", "Pharez": "Perez",
    "Zara": "Zerah", "Zarah": "Zerah",
    "Gedeon": "Gideon", "Jephthae": "Jephthah", "Balac": "Balak",
    "Cis": "Kish", "Nineve": "Nineveh", "Sina": "Sinai",
    "Charran": "Haran", "Chanaan": "Canaan", "Madian": "Midian",
    "Sodoma": "Sodom", "Gomorrha": "Gomorrah", "Rama": "Ramah",
    "Sion": "Zion", "Zidon": "Sidon", "Tyrus": "Tyre",
    "Juda": "Judah", "Zabulon": "Zebulun", "Nephthalim": "Naphtali",
    "Aser": "Asher", "Aminadab": "Amminadab",
    "Melchisedec": "Melchizedek", "Timotheus": "Timothy",
    "Marcus": "Mark", "Lucas": "Luke", "Urias": "Uriah",
    "Zacharias": "Zechariah", "Henoch": "Enoch", "Ragau": "Reu",
    "Saruch": "Serug", "Phalec": "Peleg", "Sala": "Salah",
    "Mathusala": "Methuselah", "Maleleel": "Mahalaleel", "Sem": "Shem",
    "Thara": "Terah", "Nachor": "Nahor",
    # formerly deferred; owner ruling 2026-07-18: apply
    "Elisabeth": "Elizabeth", "Enos": "Enosh", "Bosor": "Beor",
    "Sarepta": "Zarephath", "Oshea": "Joshua",
}

# (variant, book name, chapter, verse) combinations NOT to touch globally
# (John 21 Jonas is Simon Peter's father — handled by SPECIAL as -> John)
EXCLUDE = {
    ("Sion", "Deuteronomy", 4, 48),    # Mount Sion = Hermon, not Zion
    ("Jonas", "John", 21, 15),
    ("Jonas", "John", 21, 16),
    ("Jonas", "John", 21, 17),
}

# Verse-scoped fixes: (book, chapter, verse, variant, canonical).
# Aram/Heber/Jona(s) applied only where the person is meant (owner ruling
# 2026-07-18): Aram elsewhere names Syria; Heber in Judges is a different
# person; Jona(s) in John's Gospel is Simon Peter's father = modern "John".
SPECIAL = [
    ("Acts", 7, 45, "Jesus", "Joshua"),      # Greek Ἰησοῦς = Joshua here
    ("Hebrews", 4, 8, "Jesus", "Joshua"),
    ("Matthew", 1, 3, "Aram", "Ram"),
    ("Matthew", 1, 4, "Aram", "Ram"),
    ("Luke", 3, 33, "Aram", "Ram"),
    ("Luke", 3, 35, "Heber", "Eber"),
    ("John", 1, 42, "Jona", "John"),
    ("John", 21, 15, "Jonas", "John"),
    ("John", 21, 16, "Jonas", "John"),
    ("John", 21, 17, "Jonas", "John"),
]

DEFERRED = []  # all 8 formerly-deferred pairs applied per owner ruling

EVIDENCE = (
    "KJV-internal name-spelling unification (owner directive 2026-07-18; "
    "witness evidence in references/name_variants.md). If you have "
    "evidence for a different reading, create a GitHub issue with your "
    "sources: https://github.com/thomasmeadows/mandelabible/issues/new"
)


def main():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'"))
    con.execute(
        "DELETE FROM restorations WHERE flaw_type='name_normalization'")
    base = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        base[vid] = t

    patterns = {v: re.compile(rf"\b{v}\b") for v in MAPPING}
    special = {(b, c, vs): (var, canon) for b, c, vs, var, canon in SPECIAL}
    applied = {}   # variant -> [verse count, example ref]
    n_verses = 0

    for vid, book_id, ch, vs, orig in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        book = books[book_id]
        text = base.get(vid, orig)
        merged = text
        hits = []
        for var, pat in patterns.items():
            if (var, book, ch, vs) in EXCLUDE:
                continue
            if pat.search(merged):
                merged = pat.sub(MAPPING[var], merged)
                hits.append((var, MAPPING[var]))
        sp = special.get((book, ch, vs))
        if sp and re.search(rf"\b{sp[0]}\b", merged):
            merged = re.sub(rf"\b{sp[0]}\b", sp[1], merged)
            hits.append((sp[0], f"{sp[1]} (verse-scoped)"))
        if merged == text:
            continue
        ref = f"{book} {ch}:{vs}"
        note = "; ".join(f"{v} -> {c}" for v, c in hits)
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "name_normalization", text, merged,
             f"Name spelling unified: {note}", EVIDENCE, 0.9, "approved"))
        n_verses += 1
        for var, canon in hits:
            if var not in applied:
                applied[var] = [canon.split(" ")[0], 0, ref]
            applied[var][1] += 1
    con.commit()

    lines = [
        "# KJV-Internal Name Normalization — applied mappings & open rulings",
        "",
        "Generated by `scripts/35_normalize_kjv_names.py` (owner directive "
        "2026-07-18). Each variant spelling below was replaced with its "
        "most common modern form in every affected verse (approved "
        "restorations, flaw_type `name_normalization`). Witness-spelling "
        f"evidence: `references/name_variants.md`. **{n_verses} verses "
        "changed.**", "",
        "## Applied", "",
        "| Variant | Canonical | Verses | Example |",
        "|---|---|---|---|",
    ]
    for var in sorted(applied):
        canon, cnt, ref = applied[var]
        lines.append(f"| {var} | {canon} | {cnt} | {ref} |")
    lines += [
        "", "## Verse-scoped rulings (owner-approved 2026-07-18)", "",
        "- **Sion** kept at Deuteronomy 4:48 (Mount Sion = Hermon, a "
        "different place than Zion).",
        "- **Jesus** changed to **Joshua** only at Acts 7:45 and Hebrews "
        "4:8, where the Greek Ἰησοῦς names Moses' successor.",
        "- **Jona/Jonas** → **John** at John 1:42 and John 21:15-17 "
        "(Simon Peter's father, the modern reading); the prophet stays "
        "**Jonah** everywhere else.",
        "- **Aram** → **Ram** only in the genealogies (Matthew 1:3-4, "
        "Luke 3:33); Aram-the-region (Syria) untouched elsewhere.",
        "- **Heber** → **Eber** at Luke 3:35 only; Heber in Judges 4-5 "
        "is a different person and keeps his spelling.",
        "- **Oshea** → **Joshua** (Numbers 13:8, 13:16) per owner ruling, "
        "including the renaming verse.",
        "",
    ]
    out = "\n".join(lines)

    if OUT_PATH.exists():
        old_rows = OUT_PATH.read_text(encoding="utf-8").count("\n| ")
        if out.count("\n| ") < old_rows:
            raise SystemExit(
                f"REFUSING to overwrite {OUT_PATH}: fewer mapping rows "
                f"than existing file")
    OUT_PATH.write_text(out, encoding="utf-8")
    print(f"{n_verses} verses normalized; report: {OUT_PATH}")


if __name__ == "__main__":
    main()
