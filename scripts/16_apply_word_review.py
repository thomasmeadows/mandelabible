#!/usr/bin/env python3
"""16_apply_word_review.py — Phase 3: ingest the king-james agent word review.

Reads references/word_reviews/batch_*.tsv (produced by the
king-james-middle-english-expert agent, owner directive 2026-07-14: review
all uncleared non-proper-noun words for period accuracy AND possible
letter-level typos; advise alternates on strong belief).

TSV format: word<TAB>verdict<TAB>alternate<TAB>note
  verdict: period | suspect | typo

Updates `word_era`: verdict (typo stored as 'typo'), first_use_source
'KJ-agent 2026-07-14', plus alternate_word / review_note columns (added
here if missing). Only rows still carrying verdict 'suspect' are touched —
the corpus-attested and proper-noun verdicts from script 05 stand.

Emits references/word_review_report.md: every word the agent holds a strong
belief against, with its advised alternate.

Idempotent: re-applies the TSVs and regenerates the report each run.
"""

import re
import sqlite3
from pathlib import Path

TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’–-][A-Za-z]+)*")  # tokenizer v2


def fold(form: str) -> str:
    return form.lower().replace("’", "'").replace("–", "-")

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
REVIEW_DIR = REPO_ROOT / "references" / "word_reviews"
REPORT = REPO_ROOT / "references" / "word_review_report.md"
SOURCE = "KJ-agent 2026-07-14"
VALID = {"period", "suspect", "typo"}


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(word_era)")}
        if "alternate_word" not in cols:
            con.execute("ALTER TABLE word_era ADD COLUMN alternate_word TEXT")
        if "review_note" not in cols:
            con.execute("ALTER TABLE word_era ADD COLUMN review_note TEXT")

        # Layer order (later overrides earlier): first-pass batches, the
        # second-opinion pass, then the 2026-07-15 RESCAN (run under the
        # owner rule that KJV occurrence can never ground a 'period' verdict
        # — see the agent memory file kjv-not-authenticity-evidence.md).
        # The owner-ruling layer below still runs last.
        files = sorted(REVIEW_DIR.glob("batch_*.tsv"))
        second = REVIEW_DIR / "second_opinion.tsv"
        if second.exists():
            files.append(second)
        files += sorted(REVIEW_DIR.glob("rescan_batch_*.tsv"))
        rows, bad = [], []
        for tsv in files:
            for ln in tsv.read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                parts = ln.split("\t")
                if len(parts) < 2 or parts[1].strip().lower() not in VALID:
                    bad.append(f"{tsv.name}: {ln[:60]}")
                    continue
                parts += [""] * (4 - len(parts))
                word, verdict, alt, note = (p.strip() for p in parts[:4])
                rows.append((word.lower(), verdict.lower(), alt or None, note or None))

        counts = {"period": 0, "suspect": 0, "typo": 0, "unmatched": 0}
        for word, verdict, alt, note in rows:
            cur = con.execute(
                """UPDATE word_era SET verdict=?, first_use_source=?,
                   alternate_word=?, review_note=?
                   WHERE word=? AND (first_use_source IS NULL OR first_use_source=?)""",
                (verdict, SOURCE, alt, note, word, SOURCE))
            if cur.rowcount:
                counts[verdict] += 1
            else:
                counts["unmatched"] += 1
        con.commit()

        # Owner corrections to the RESCAN alternates (review session 6,
        # 2026-07-15): wraths keeps the singular; the stumbling family is
        # unfused rather than reworded; gopher becomes cypress; forum is
        # handled as a phrase replacement in script 13 (OWNER_DIRECTED), so
        # its word-level alternate is cleared.
        for w, alt in [("wraths", "wrath"),
                       ("stumblingblock", "stumbling block"),
                       ("stumblingblocks", "stumbling blocks"),
                       ("stumblingstone", "stumbling stone"),
                       ("gopher", "cypress"),
                       ("forum", None)]:
            con.execute(
                "UPDATE word_era SET alternate_word=?, review_note="
                "COALESCE(review_note,'') || '; owner correction 2026-07-15' "
                "WHERE word=?", (alt, w))
        con.commit()

        # OWNER RULING layer (2026-07-14, Decision Log #9) — overrides the
        # second opinion: every word the first pass flagged "should not exist
        # in the KJV" (owner-confirmed examples: gravity, heinous,
        # jurisdiction). First-pass verdicts are reinstated; alternates come
        # from the first pass or owner_alternates.tsv (KJV-translation-habit
        # grounded); the second opinion survives only as an advisory note.
        alt_file = REVIEW_DIR / "owner_alternates.tsv"
        owner_alts = {}
        if alt_file.exists():
            for ln in alt_file.read_text(encoding="utf-8").splitlines():
                p = (ln.split("\t") + ["", ""])[:3]
                owner_alts[p[0].strip().lower()] = (p[1].strip(), p[2].strip())

        first_flags = {}
        for tsv in sorted(REVIEW_DIR.glob("batch_*.tsv")):
            for ln in tsv.read_text(encoding="utf-8").splitlines():
                p = (ln.split("\t") + [""] * 4)[:4]
                if p[1].strip().lower() in ("suspect", "typo"):
                    first_flags[p[0].strip().lower()] = (
                        p[1].strip().lower(), p[2].strip(), p[3].strip())

        # Owner corrections to the ruling (2026-07-14): "instructors" IS the
        # valid term (both forms cleared); "schoolmaster" is the corruption —
        # Galatians 3:24-25 render the same Greek παιδαγωγός (G3807) that the
        # KJV gives as "instructors" at 1 Corinthians 4:15.
        for w in ("instructor", "instructors"):
            first_flags.pop(w, None)
            con.execute(
                "UPDATE word_era SET verdict='period', "
                "first_use_source='owner ruling 2026-07-14', alternate_word=NULL, "
                "review_note='owner: valid term (παιδαγωγός G3807)' WHERE word=?", (w,))
        first_flags["schoolmaster"] = (
            "suspect", "instructor",
            "owner: schoolmaster needs to be removed; G3807 = instructors at 1Cor 4:15")
        con.execute(
            """INSERT INTO word_era (word, verdict, first_use_source, alternate_word,
               review_note) VALUES ('schoolmaster','suspect','owner ruling 2026-07-14',
               'instructor','owner: to be removed; G3807 rendered instructors at 1Cor 4:15')
               ON CONFLICT(word) DO UPDATE SET verdict='suspect',
               first_use_source='owner ruling 2026-07-14', alternate_word='instructor',
               review_note='owner: to be removed; G3807 rendered instructors at 1Cor 4:15'""")

        for word, (verdict, alt, note) in first_flags.items():
            oa, oa_note = owner_alts.get(word, ("", ""))
            alternate = alt or oa or None
            full_note = "; ".join(filter(None, [
                note, oa_note, "second-opinion (advisory): period",
                "owner ruling 2026-07-14: should not exist in KJV"]))
            con.execute(
                """UPDATE word_era SET verdict=?, first_use_source=?,
                   alternate_word=?, review_note=? WHERE word=?""",
                (verdict, "owner ruling 2026-07-14", alternate, full_note, word))
        con.commit()

        # anachronism anomalies for verses containing ANY currently-suspect
        # word (owner-ruled or rescan-flagged), feeding the corruption index
        con.execute("DELETE FROM anomalies WHERE type='anachronism'")
        alts = dict(con.execute(
            "SELECT word, alternate_word FROM word_era "
            "WHERE verdict IN ('suspect','typo')"))
        n_anach = 0
        for vid, text in con.execute(
                "SELECT id, text FROM verses WHERE translation='KJV'").fetchall():
            hits = {fold(t) for t in TOKEN_RE.findall(text)} & set(alts)
            for word in sorted(hits):
                alt = alts.get(word)
                con.execute(
                    "INSERT INTO anomalies (verse_id, type, token, detail, score) "
                    "VALUES (?,?,?,?,?)",
                    (vid, "anachronism", word,
                     f"'{word}' flagged not-period (owner ruling / rescan)"
                     + (f"; advised alternate '{alt}'" if alt else ""), 0.5))
                n_anach += 1
        con.commit()
        print(f"owner ruling applied: {len(first_flags)} words reinstated; "
              f"{n_anach} anachronism anomaly rows")

        # report from FINAL state (all layers included)
        flagged = [(w, v, a or "", n or "", c or 0) for w, v, a, n, c in con.execute(
            """SELECT we.word, we.verdict, we.alternate_word, we.review_note, wc.count
               FROM word_era we
               LEFT JOIN word_counts wc ON wc.word=we.word AND wc.book_id IS NULL
                 AND wc.tokenizer_version=2
               WHERE we.first_use_source IN (?, 'owner ruling 2026-07-14')
                 AND we.verdict IN ('suspect','typo')""",
            (SOURCE,))]

        flagged.sort(key=lambda x: (-x[4], x[0]))
        lines = ["# Word Review Report — king-james agent, 2026-07-14",
                 "",
                 "*Generated by `scripts/16_apply_word_review.py` — do not hand-edit.*",
                 "",
                 "Three layers: (1) 8 parallel first-pass agent batches over the "
                 "2,060 uncleared words; (2) a verse-verified second-opinion pass "
                 "over the first pass's flags; (3) OWNER RULING 2026-07-14 "
                 "(Decision Log #9) — the flagged words 'should not exist in the "
                 "KJV'; first-pass flags reinstated, second opinion kept as an "
                 "advisory note, alternates grounded in the KJV's own rendering "
                 "of the same Strong's word elsewhere.",
                 "",
                 "Words held with STRONG BELIEF against, with advised period alternates",
                 "(advisory evidence per Decision Log #5 — memory still leads):",
                 "",
                 "| word | KJV count | verdict | advised alternate | note |",
                 "|------|-----------|---------|-------------------|------|"]
        lines += [f"| {w} | {c} | {v} | {a} | {n} |" for w, v, a, n, c in flagged]
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"applied: {counts}")
        if bad:
            print(f"skipped {len(bad)} malformed line(s), e.g. {bad[:3]}")
        print(f"{len(flagged)} words with strong-belief alternates -> {REPORT}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
