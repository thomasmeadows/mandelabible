#!/usr/bin/env python3
"""74_chief_head_preview.py — build a was/now PREVIEW of the owner rulings on
`references/word_review_chief_head.md` (277 "chief"/"chiefest" occurrences,
owner rulings 2026-07-26). NO DATABASE WRITES.

Unlike round 5/6 (rarity rounds with a handful of distinct words), this is a
single targeted word sweep with 277 occurrences, so the EDITS table is built
programmatically by parsing the review file's `- owner ruling:` lines rather
than hand-typed. Ruling shapes:

  - "swap"            -> accept the entry's own `- KJ proposal:` verse verbatim
                          (kind='set'). 180 occurrences.
  - "chief -> X" /
    "chiefest -> X" /
    "chief men -> X" /
    "chief governor -> X" / etc.
                       -> apply the substitution to the verse's actual CURRENT
                          text (base KJV + approved restorations), not the
                          pre-written KJ proposal (which assumed "head").
                          Case of the matched word/phrase is preserved on the
                          replacement's first letter. ~90 occurrences.
  - "delete chief" /
    "delete chieef" (typo)
                       -> remove the word "chief" and collapse the resulting
                          double space. 6 occurrences.
  - comma-separated multi-part rulings (e.g. "chiefest -> greatest, chief ->
    ruler") -> each part's OLD side is tried against the verse; only the part
    whose OLD literally occurs is applied (I Ezra 8:17 has "chief", not
    "chiefest", so only the "chief -> ruler" half fires).
  - ordinal-prefixed parts (e.g. "chief men -> heads of the house, 2nd chief
    men -> heads", I Chronicles 24:4) -> apply to the Nth occurrence of that
    phrase specifically.
  - one bespoke phrase rewrite, Acts 17:4 ("and of the head women not a few >
    and women") -> per the task's own reading instruction, this describes a
    delete-chief-style edit against the verse's ACTUAL text ("...and of the
    chief women not a few." -> "...and of women not a few."), hardcoded below.

Output: references/word_review_chief_head_apply_preview.md (owner reviews
wording, then a future apply step writes the DB + blacklist/whitelist +
export, mirroring 71_round6_preview.py -> a future 75_apply script).
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
SRC = ROOT / "references" / "word_review_chief_head.md"
OUT = ROOT / "references" / "word_review_chief_head_apply_preview.md"


def load_current(con):
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL ORDER BY id"):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    cur, base = {}, {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        key = (names[bid], ch, vs)
        base[key] = text
        cur[key] = resto.get(vid, text)
    return cur, base


# ---------------------------------------------------------------------------
# Parse references/word_review_chief_head.md into entries.
# ---------------------------------------------------------------------------
FIELD_RE = re.compile(r'^-\s*([\w \(\)\.]+?):\s*(.*)$')


def parse_source():
    text = SRC.read_text(encoding="utf-8")
    blocks = text.split("\n## ")[1:]
    entries = []
    for b in blocks:
        lines = b.split("\n")
        ref = lines[0].strip()
        m = re.match(r'^(.+) (\d+):(\d+)$', ref)
        if not m:
            continue
        book, ch, vs = m.group(1), int(m.group(2)), int(m.group(3))
        d = {}
        for l in lines[1:]:
            fm = FIELD_RE.match(l)
            if fm:
                d[fm.group(1).strip().lower()] = fm.group(2).strip()
        entries.append(((book, ch, vs), d))
    return entries


def preserve_case(matched, new):
    if matched[:1].isupper():
        return new[:1].upper() + new[1:]
    return new


def clean_spacing(s):
    s = re.sub(r'  +', ' ', s)
    s = re.sub(r' ([,.;:])', r'\1', s)
    return s.strip()


def apply_ruling(was, ruling):
    """Return (now, flags) for a non-'swap' ruling applied to the verse's
    actual current text."""
    ruling = ruling.strip()
    flags = []

    if ruling.lower() in ("delete chief", "delete chieef"):
        new, n = re.subn(r'\bchief\b ?', '', was, count=0, flags=re.I)
        if n == 0:
            return was, ["NOT-FOUND: chief (delete)"]
        new = clean_spacing(new)
        # Deleting "chief" out of an idiom like "chief of X" (-> "with chief
        # of all spices" becomes "with of all spices") leaves a dangling
        # double preposition — needs a human call, not a guess.
        if re.search(
                r'\b(in|with|by|to|from|at|unto|upon|among|between|through|for)\s+of\b',
                new, re.I):
            flags.append("DANGLING-PREPOSITION: deleting 'chief' left a "
                          "double preposition — needs manual phrasing")
        return new, flags

    now = was
    raw_pieces = [p.strip() for p in ruling.split(",")]
    parsed = []
    for piece in raw_pieces:
        occ = None
        om = re.match(r'^(\d+)(?:st|nd|rd|th)\s+(.*)$', piece)
        if om:
            occ = int(om.group(1))
            piece = om.group(2)
        parsed.append((occ, piece))
    # If any piece names an explicit ordinal occurrence of the same OLD phrase
    # as another piece, the non-ordinal piece means occurrence 1 (not "all").
    olds_with_ordinal = set()
    for occ, piece in parsed:
        if occ is not None and "->" in piece:
            olds_with_ordinal.add(piece.split("->", 1)[0].strip().lower())
    fixed = []
    for occ, piece in parsed:
        if occ is None and "->" in piece and piece.split("->", 1)[0].strip().lower() in olds_with_ordinal:
            occ = 1
        fixed.append((occ, piece))
    parsed = fixed

    has_ordinal = any(occ is not None for occ, _ in parsed)
    any_success = False
    pending = []  # flags for parts that failed; only surfaced if nothing succeeded
    # Planned edits as (start, end, replacement_text), computed against the
    # ORIGINAL `was` string so ordinal indices (1st/2nd occurrence) are never
    # thrown off by an earlier piece's substitution shifting the string.
    planned = []
    for occ, piece in parsed:
        if piece.lower() == "principal":
            old, new = "chief", "principal"
        elif "->" in piece:
            old, new = [x.strip() for x in piece.split("->", 1)]
        else:
            pending.append(f"UNPARSED-RULING: {piece}")
            continue

        alts = [a.strip() for a in re.split(r'\s*/\s*', old) if a.strip()]
        chosen = None
        for a in alts:
            if re.search(r'\b' + re.escape(a) + r'\b', was, re.I):
                chosen = a
                break
        if chosen is None:
            # Fallback for descriptive multi-word OLD phrases (e.g. "chief of
            # the fathers", "chief of the governors") whose exact wording
            # varies verse-to-verse (e.g. "their fathers" not "the fathers"),
            # and for "chiefest -> X" where the verse actually reads plain
            # "chief": retry on just the phrase's headword.
            for a in alts:
                headword = a.split()[0]
                candidates = [headword]
                if headword.lower() == "chiefest":
                    candidates.append("chief")
                elif headword.lower() == "chief":
                    candidates.append("chiefest")
                for cand in candidates:
                    if re.search(r'\b' + re.escape(cand) + r'\b', was, re.I):
                        chosen = cand
                        break
                if chosen:
                    break
        if chosen is None:
            pending.append(f"NOT-FOUND: {old}")
            continue

        pattern = re.compile(re.escape(chosen), re.I)
        matches = list(pattern.finditer(was))
        if occ is not None:
            idx = occ - 1
            if idx >= len(matches):
                pending.append(f"OCC-NOT-FOUND: {occ} {old}")
                continue
            targets = [matches[idx]]
        else:
            targets = matches
        for mtc in targets:
            planned.append((mtc.start(), mtc.end(), preserve_case(mtc.group(), new)))
        any_success = True

    # Apply planned edits back-to-front so earlier offsets stay valid.
    planned.sort(key=lambda t: t[0], reverse=True)
    for start, end, repl in planned:
        now = now[:start] + repl + now[end:]

    # A multi-part ruling names both a word-family variant (chief/chiefest)
    # and a specific verse's actual word only carries one of them — that's
    # expected, not an error, as long as at least one part applied.
    if has_ordinal or not any_success or len(parsed) == 1:
        flags += pending

    return now, flags


# Bespoke override for the one phrase-level ruling that doesn't fit the
# generic "OLD -> NEW" parser (Acts 17:4). Per task instruction: the ruling
# text names "head women" but the owner is describing the was->now shape
# against the verse's ACTUAL current text, which reads "chief women" — this
# is functionally a "delete chief" edit on that verse.
BESPOKE = {
    ("Acts", 17, 4): lambda was: (
        was.replace("of the chief women not a few", "of women not a few")
        if "of the chief women not a few" in was else None
    ),
}

VOWEL_SOUND = re.compile(r'^[aeiouAEIOU]')


def article_flags(was, now):
    """Heuristic scan for a/an mismatches introduced BY THIS EDIT specifically
    (only near the changed span — pre-existing KJV 'an house'/'an hundred'
    style elsewhere in the verse is period-authentic and not our concern)."""
    import difflib
    out = []
    sm = difflib.SequenceMatcher(None, was, now)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        # word immediately before the inserted/changed span in `now`
        before = now[:j1]
        wm = re.search(r'\b([Aa]n?)\s*$', before)
        if not wm:
            continue
        # first word of the new span (or the word right after, if span is a deletion)
        after = now[j1:] if j1 < j2 else now[j2:]
        fw = re.match(r"[\w']+", after)
        if not fw:
            continue
        word = fw.group(0)
        art = wm.group(1)
        starts_vowel = bool(VOWEL_SOUND.match(word))
        if art.lower() == "a" and starts_vowel:
            out.append(f"ARTICLE: 'a {word}' may need 'an {word}'")
        elif art.lower() == "an" and not starts_vowel and word.lower() not in (
                "hundred", "house", "hair", "husband", "harlot", "hair's",
                "hungred", "hired", "high", "help", "helper", "hole",
                "handful", "hen", "hypocrite"):
            out.append(f"ARTICLE: 'an {word}' may need 'a {word}'")
    return out


def main():
    con = sqlite3.connect(DB)
    cur, base = load_current(con)
    con.close()

    entries = parse_source()

    rows = []  # (ref, was, now, ruling, flags:list[str])
    ruling_kind_counts = {"swap": 0, "override": 0, "delete": 0, "noop": 0}
    missing_owner_ruling = 0

    for ref, d in entries:
        book, ch, vs = ref
        ruling = d.get("owner ruling", "").strip()
        if not ruling:
            missing_owner_ruling += 1
            continue

        was = cur.get(ref)
        flags = []
        if was is None:
            rows.append((ref, d.get("text", ""), "", ruling, ["MISSING-VERSE (not in current DB text)"]))
            continue

        # Sanity: does the file's recorded 'text' match the live DB text?
        file_text = d.get("text", "")
        if file_text and file_text.strip() != was.strip():
            flags.append("TEXT-DRIFT: review file's '- text:' differs from current DB text (using DB text)")

        is_swap = False
        if ref in BESPOKE:
            now = BESPOKE[ref](was)
            if now is None:
                flags.append("NOT-FOUND: bespoke anchor phrase")
                now = was
            else:
                ruling_kind_counts["override"] += 1
                flags += article_flags(was, now)
        elif ruling.lower() == "swap":
            is_swap = True
            now = d.get("kj proposal", "")
            if not now:
                flags.append("MISSING: KJ proposal text")
                now = was
            else:
                ruling_kind_counts["swap"] += 1
        elif ruling.lower() in ("delete chief", "delete chieef"):
            now, dflags = apply_ruling(was, ruling)
            flags += dflags
            if now != was:
                ruling_kind_counts["delete"] += 1
                flags += article_flags(was, now)
        else:
            now, oflags = apply_ruling(was, ruling)
            flags += oflags
            if now != was:
                flags += article_flags(was, now)
            if now != was:
                ruling_kind_counts["override"] += 1

        if now == was:
            ruling_kind_counts["noop"] += 1

        rows.append((ref, was, now, ruling, flags))

    rows.sort(key=lambda r: (str(r[0][0]), r[0][1], r[0][2]))
    changed = [r for r in rows if r[2] and r[1] != r[2]]
    flagged = [r for r in rows if r[4]]
    total_flags = sum(len(r[4]) for r in rows)

    out = [
        "# chief / chiefest -> head — Word Review APPLY PREVIEW (not yet applied)",
        "",
        f"*{len(changed)} verses proposed for change from the owner rulings in "
        "`word_review_chief_head.md` (2026-07-26), computed against the ACTUAL "
        "current DB text (base KJV + all approved restorations). "
        f"{missing_owner_ruling} entries had a blank owner ruling (should be 0). "
        "NO DATABASE WRITES yet.*",
        "",
        f"**Changed verses: {len(changed)}** — "
        f"swap: {ruling_kind_counts['swap']}, "
        f"override: {ruling_kind_counts['override']}, "
        f"delete: {ruling_kind_counts['delete']}.",
        "",
        f"**Flags needing attention: {total_flags}** (across {len(flagged)} verses).",
        "",
        "## Open questions for the owner",
        "",
        "- Acts 17:4: owner ruling text reads 'and of the head women not a few "
        "> and women', naming \"head women\" — but the verse's actual current "
        "text reads \"chief women\", not \"head women\". Read per task "
        "instruction as a delete-chief-style edit against the real text: "
        "\"and of the chief women not a few.\" -> \"and of women not a few.\" "
        "Flagged here for owner confirmation this reading is correct.",
        "- Any ⚠️ FLAG lines below (article a/an heuristic, anchor-not-found, "
        "or text drift between the review file's recorded '- text:' and the "
        "live DB) are surfaced rather than auto-guessed.",
        "- Ezekiel 27:22 ('chief -> delete'): removing \"chief\" from \"with "
        "chief of all spices\" leaves a dangling double preposition (\"with "
        "of all spices\") — flagged below rather than guessed; needs the "
        "owner's phrasing (e.g. \"with all spices\" or \"with the finest of "
        "all spices\").",
        "- Proverbs 16:28 ('chief -> amongst'): \"a talebearer separateth "
        "chief friends\" -> \"a talebearer separateth amongst friends\" is "
        "grammatically valid but semantically odd (loses the sense of "
        "\"close/intimate friends\") — applied literally per the owner's "
        "ruling, flagged here for the owner's eye.",
        "- Acts 28:7 ('chief man -> rulers'): the owner's replacement is "
        "plural where the source is singular (\"the chief man\" -> \"the "
        "rulers\", article/number now mismatched) — applied literally per "
        "the owner's own wording.",
        "",
    ]

    for ref, was, now, ruling, flags in rows:
        if not (now and was != now):
            continue
        b, c, v = ref
        out.append(f"## {b} {c}:{v}")
        out.append(f"- ruling: {ruling}")
        for f in flags:
            out.append(f"- ⚠️ **FLAG:** {f}")
        out.append(f"- was: {was}")
        out.append(f"- now: {now}")
        out.append("")

    unresolved = [r for r in rows if r[4] and not (r[2] and r[1] != r[2])]
    if unresolved:
        out.append("## ⚠️ Flagged — no change produced (needs a look)")
        out.append("")
        for ref, was, now, ruling, flags in unresolved:
            b, c, v = ref
            out.append(f"- **{b} {c}:{v}** — ruling: {ruling} — " + "; ".join(flags))
        out.append("")

    noops = [r for r in rows if r[2] == r[1] and not r[4]]
    if noops:
        out.append(f"## No-op verses ({len(noops)}) — ruling produced no textual change")
        out.append("")
        for ref, was, now, ruling, flags in noops:
            b, c, v = ref
            out.append(f"- **{b} {c}:{v}** — ruling: {ruling}")
        out.append("")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(changed)} changed, {total_flags} flags, "
          f"{len(noops)} no-ops, {missing_owner_ruling} missing owner ruling")
    print("kind breakdown:", ruling_kind_counts)


if __name__ == "__main__":
    main()
