#!/usr/bin/env python3
"""13_propose_restorations.py — Phase 6: generate candidate restorations.

Candidate generation per Decision Log #5/#8, memory-led:
- Only memories with status 'corroborated' or 'artifact-supported' generate
  proposals (falsifiability anchor: unconfirmed memories are recorded, never
  restored).
- Where the memory names a mechanical target reading, a documented
  substitution rule (regex, applied ONLY to the memory's scope verses)
  produces proposed_text. Polysemy is respected (Decision Log #4): e.g.
  couch→crouch fires only on the verb ("couch in"), never the furniture noun.
- Where the memory is phrase-level (lion & lamb, Lord's Prayer wording),
  the row is created with the remembered fragment as guidance and
  flaw_type marked for KJV-voice phrasing by the king-james agent —
  proposed_text stays NULL until phrased.
- Every row: rationale + evidence (memory id, signal counts) + confidence
  (corroborated 0.85, artifact-supported 0.65; phrasing-pending 0.5) +
  status 'proposed'. NOTHING is final without owner review.

Idempotent: rebuilds `restorations` each run (owner-reviewed statuses on
prior rows are preserved by re-applying them from a saved copy keyed on
(verse_id, flaw_type, proposed_text)).
"""

import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"

# (memory-title keyword, flaw_type, [(pattern, replacement), ...])
# Patterns are case-sensitive and scoped to the memory's own verses.
SUB_RULES = [
    ("bottles", "word_substitution", [
        (r"\bbottles\b", "wineskins"), (r"\bbottle\b", "wineskin"),
        (r"\bBottles\b", "Wineskins"), (r"\bBottle\b", "Wineskin")]),
    ("matrix", "word_substitution", [(r"\bmatrix\b", "womb")]),
    ("couch", "missing_letter", [(r"\bcouch(?=\s+in\b)", "crouch")]),
    ("wizard", "word_substitution", [
        (r"\bwizards\b", "sorcerers"), (r"\bwizard\b", "sorcerer")]),
    ("thanksgiving", "word_substitution", [(r"\bthanksgivings\b", "thank offerings")]),
    ("tables", "missing_letter", [
        (r"\btables\b", "tablets"), (r"\btable\b(?=s? of stone)", "tablet")]),
    ("strait", "missing_letter", [
        (r"\bstrait\b", "straight"), (r"\bStrait\b", "Straight"),
        # owner amendment 2026-07-14: gate -> path in this memory's scope
        (r"\bgate\b", "path"), (r"\bGate\b", "Path")]),
    ("on earth", "word_substitution", [(r"\bin earth\b", "on earth")]),
    ("destroyed", "word_substitution", [
        (r"\bare destroyed for lack\b", "perish for lack")]),
    ("money", "phrase_change", [
        (r"\bthe love of money is the root\b", "money is the root")]),
    ("windows", "word_substitution", [
        (r"\bwindows (of|in) heaven\b", r"floodgates \1 heaven"),
        (r"\bwindow\b", "opening"), (r"\bwindows\b", "openings")]),
    ("capitalization", "capitalization", [
        (r"\bthe Holy Ghost\b", "the spirit of god"),
        (r"\bthe Holy Spirit\b", "the spirit of god"),
        (r"\bHoly Ghost\b", "spirit of god"),
        (r"\bHoly Spirit\b", "spirit of god")]),
    ("emoji", "punctuation", [
        (r"[;:][)(]", lambda m: m.group()[0]),   # ';)' -> ';'  (drop the paren)
        (r"\(", ""), (r"\)", "")]),              # remaining out-of-place parens
]

# OWNER-DIRECTED restorations (override the falsifiability anchor by direct
# owner ruling — the owner IS the rememberer; recorded in the Decision Log).
# (ref, flaw_type, proposed_text, rationale)
OWNER_DIRECTED = [
    ("Genesis 1:1", "punctuation",
     "In the beginning, God created the heavens and the earth.",
     "Owner ruling 2026-07-14: full remembered reading applied (comma + "
     "'heavens'). Memory was 'unconfirmed' in the corroboration report; the "
     "owner's direct testimony overrides per the evidence hierarchy. Advisory "
     "support: Hebrew שמים (shamayim) is grammatically plural/dual."),
    ("Acts 28:15", "word_substitution",
     "And from thence, when the brethren heard of us, they came to meet us as "
     "far as the market place of Appius, and The three taverns: whom when Paul "
     "saw, he thanked God, and took courage.",
     "Owner ruling 2026-07-15 (rescan review, group F2): 'Appii forum' is "
     "translated as 'the market place of Appius' — a phrase replacement, so it "
     "lives here rather than in the word-level alternates."),
    # Review session 7 (2026-07-15): community-reported memories from the
    # blog sweep, each alternate chosen by the owner.
    ("John 8:32", "word_substitution",
     "And ye shall know the truth, and the truth shall set you free.",
     "Review session 7 2026-07-15: remembered 'set you free'; owner approved "
     "for 8:32 and 8:36 (consistency)."),
    ("John 8:36", "word_substitution",
     "If the Son therefore shall set you free, ye shall be free indeed.",
     "Review session 7 2026-07-15: make->set extended to 8:36 for consistency "
     "(owner choice)."),
    ("Matthew 18:20", "word_substitution",
     "For where two or more are gathered together in my name, there am I in "
     "the midst of them.",
     "Review session 7 2026-07-15: remembered 'two or more'; owner approved."),
    ("Luke 19:23", "word_substitution",
     "Wherefore then gavest not thou my money to the exchangers, that at my "
     "coming I might have required mine own with usury?",
     "Review session 7 2026-07-15: 'bank' is anachronistic — Greek trapeza "
     "(money-changer's table); owner chose the KJV's own Matthew 25:27 "
     "rendering 'to the exchangers'."),
    ("Luke 17:31", "word_substitution",
     "In that day, he which shall be upon the housetop, and his goods in the "
     "house, let him not come down to take it away: and he that is in the "
     "field, let him likewise not return back.",
     "Review session 7 2026-07-15: 'stuff' -> 'goods' (Greek skeue); owner "
     "approved."),
    ("II Thessalonians 2:9", "phrase_change",
     "Even him, whose coming is after the working of Satan with all power and "
     "lying signs and wonders,",
     "Review session 7 2026-07-15: remembered word order 'lying signs and "
     "wonders'; owner approved."),
    ("Exodus 2:3", "word_substitution",
     "And when she could not longer hide him, she took for him a basket of "
     "bulrushes, and daubed it with slime and with pitch, and put the child "
     "therein; and she laid it in the flags by the river’s brink.",
     "Review session 7 2026-07-15: remembered 'basket'; owner chose 'basket "
     "of bulrushes' (minimal change, keeps the material)."),
    ("Exodus 34:14", "phrase_change",
     "For thou shalt worship no other god: for the LORD is a jealous God:",
     "Review session 7 2026-07-15: Hebrew qanna is an adjective, not a name; "
     "owner chose to drop the false 'whose name is Jealous' clause and "
     "restore LORD for YHWH (Decision Log #6)."),
    ("Luke 12:51", "word_substitution",
     "Suppose ye that I am come to give peace on earth? I tell you, Nay; but "
     "rather a sword:",
     "Review session 7 2026-07-15: parallel Matthew 10:34 reads 'a sword'; "
     "rememberers recall agreement; owner approved division -> a sword."),
]

# phrase-level memories: row created, phrasing delegated (proposed_text NULL)
PHRASING_PENDING = ["lion", "lord's prayer"]

# KJV-voice phrasings produced by the king-james-middle-english-expert agent
# (2026-07-14). Each entry replaces the pending NULL row for its memory with a
# concrete proposal at the correct verse. (title keyword, ref, proposed text,
# phrasing rationale)
PHRASED = [
    ("lion", "Isaiah 65:25",
     "The lion and the lamb shall lie down together, and dust shall be the "
     "serpent's meat. They shall not hurt nor destroy in all my holy mountain, "
     "saith the LORD.",
     "Agent phrasing: 'lie down together' carries the remembered pairing using "
     "the chapter's own verb (cf. Isaiah 11:6); serpent's-meat and holy-mountain "
     "clauses kept; 'saith the LORD' retained — WLC reads YHWH here (Decision "
     "Log #6 exception)."),
    ("lion", "Isaiah 11:6",
     "The lion also shall dwell with the lamb, and the leopard shall lie down "
     "with the kid; and the calf and the young lion and the fatling together; "
     "and a little child shall lead them.",
     "Agent phrasing: only wolf->lion per the remembered reading; KJV syntax "
     "untouched."),
    ("lord's prayer", "Matthew 6:12",
     "And forgive us our trespasses, as we forgive them that trespass against us.",
     "Agent phrasing: 'trespasses'/'them that trespass against us' drawn from "
     "the KJV's own Matthew 6:14-15 and the Book of Common Prayer form — the "
     "period-attested phrasing of the remembered 'trespassors'."),
]

CONFIDENCE = {"corroborated": 0.85, "artifact-supported": 0.65}

SCHEMA = """
CREATE TABLE IF NOT EXISTS restorations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id       INTEGER REFERENCES verses(id),
    flaw_type      TEXT,
    current_text   TEXT,
    proposed_text  TEXT,
    rationale      TEXT,
    evidence       TEXT,
    confidence     REAL,
    status         TEXT DEFAULT 'proposed'
);
"""


def base_text(con, vid, default):
    """Latest proposed text for a verse this run, so passes COMPOSE —
    a verse with a word substitution and a parenthesis fix must end with
    both applied, not whichever row the export applies last."""
    row = con.execute(
        "SELECT proposed_text FROM restorations WHERE verse_id=? AND "
        "proposed_text IS NOT NULL ORDER BY id DESC LIMIT 1", (vid,)).fetchone()
    return row[0] if row else default


def resolve(con, ref):
    book, cv = ref.rsplit(" ", 1)
    ch, vs = cv.split(":")
    row = con.execute(
        """SELECT v.id, v.text FROM verses v JOIN books b
           ON b.translation='KJV' AND b.id=v.book_id
           WHERE v.translation='KJV' AND b.name=? AND v.chapter=? AND v.verse=?""",
        (book, int(ch), int(vs))).fetchone()
    return row


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)
        saved = {(v, f, p): s for v, f, p, s in con.execute(
            "SELECT verse_id, flaw_type, proposed_text, status FROM restorations "
            "WHERE status != 'proposed'")}
        con.execute("DELETE FROM restorations")

        n_rows = 0
        for mid, title, status, scope in con.execute(
                "SELECT id, title, status, scope_refs FROM memories "
                "WHERE status IN ('corroborated','artifact-supported')"):
            t = title.lower()
            refs = list(filter(None, (scope or "").split(";")))
            sigs = con.execute(
                "SELECT COUNT(*) FROM memory_signals WHERE memory_id=? AND kind='artifact'",
                (mid,)).fetchone()[0]
            evidence = (f"memory #{mid} ({status}); {sigs} co-located artifact signal(s); "
                        "see memory_signals / corroboration_report.md")

            rule = next(((ft, subs) for kw, ft, subs in SUB_RULES if kw in t), None)
            # a memory stays "pending" only until its PHRASED entries exist
            pending = (any(kw in t for kw in PHRASING_PENDING)
                       and not any(kw in t for kw, *_ in PHRASED))

            phrased_refs = set()
            for kw, ref, proposed, why in PHRASED:
                if kw not in t:
                    continue
                row = resolve(con, ref)
                if not row:
                    continue
                vid, text = row
                phrased_refs.add(ref)
                st = saved.get((vid, "phrase_change", proposed), "proposed")
                con.execute(
                    "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                    "proposed_text, rationale, evidence, confidence, status) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (vid, "phrase_change", text, proposed,
                     f"Memory-led phrase restoration ({title[:60]}). {why}",
                     evidence, CONFIDENCE[status] * 0.9, st))
                n_rows += 1

            for ref in refs:
                if ref in phrased_refs:
                    continue
                row = resolve(con, ref)
                if not row:
                    continue
                vid, text = row
                if rule:
                    ft, subs = rule
                    new = text
                    for pat, rep in subs:
                        new = re.sub(pat, rep, new)
                    if new != text:
                        conf = CONFIDENCE[status]
                        rationale = (f"Memory-led substitution ({title[:60]}): rule(s) "
                                     f"{[p for p, _ in subs]} applied to scope verse {ref}. "
                                     "Advisory sources inform phrasing only (Decision Log #5).")
                        st = saved.get((vid, ft, new), "proposed")
                        con.execute(
                            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                            "proposed_text, rationale, evidence, confidence, status) "
                            "VALUES (?,?,?,?,?,?,?,?)",
                            (vid, ft, text, new, rationale, evidence, conf, st))
                        n_rows += 1
                elif pending:
                    rationale = (f"Phrase-level memory ({title[:60]}): remembered reading "
                                 "requires KJV-voice phrasing by the king-james-middle-english-"
                                 "expert agent before proposal. Row reserves the verse.")
                    st = saved.get((vid, "phrase_change", None), "proposed")
                    con.execute(
                        "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                        "proposed_text, rationale, evidence, confidence, status) "
                        "VALUES (?,?,?,NULL,?,?,?,?)",
                        (vid, "phrase_change", text, rationale, evidence, 0.5, st))
                    n_rows += 1
        for ref, ft, proposed, why in OWNER_DIRECTED:
            row = resolve(con, ref)
            if not row:
                continue
            vid, text = row
            st = saved.get((vid, ft, proposed), "proposed")
            con.execute(
                "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                "proposed_text, rationale, evidence, confidence, status) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (vid, ft, text, proposed, why,
                 "owner-directed ruling; see remembered_verses.md entry", 0.9, st))
            n_rows += 1

        # GLOBAL parenthesis/emoticon removal (owner ruling 2026-07-14):
        # emoticons ';)' / ':)' are irrelevant and parentheses — including
        # whole verses encapsulated in them — just need to be removed. Every
        # verse carrying a parenthesis or emoticon anomaly gets a proposal:
        # ';)'->';', ':)'->':', then all '(' ')' stripped (whitespace tidied).
        # Verses already fixed by the memory-scoped emoticon rule are skipped.
        for (vid,) in con.execute(
                """SELECT DISTINCT verse_id FROM anomalies
                   WHERE type='emoticon' OR (type='punctuation' AND token IN ('(',')'))"""):
            if con.execute(
                    "SELECT 1 FROM restorations WHERE verse_id=? AND "
                    "flaw_type='punctuation'", (vid,)).fetchone():
                continue
            text = base_text(con, vid, con.execute(
                "SELECT text FROM verses WHERE id=?", (vid,)).fetchone()[0])
            new = re.sub(r"([;:])[)]", r"\1", text)
            new = new.replace("(", "").replace(")", "")
            new = re.sub(r"\s{2,}", " ", new).strip()
            if new == text:
                continue
            st = saved.get((vid, "punctuation", new), "proposed")
            con.execute(
                "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                "proposed_text, rationale, evidence, confidence, status) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (vid, "punctuation", text, new,
                 "Global parenthesis/emoticon removal (owner ruling 2026-07-14): "
                 "emoticon patterns reduced to their true punctuation; all "
                 "parentheses removed.",
                 "punctuation/emoticon anomaly rows on this verse; owner ruling",
                 0.8, st))
            n_rows += 1

        # Owner-ruled anachronisms (Decision Log #9): every word_era row from
        # the owner ruling with an advised alternate generates a substitution
        # proposal on each verse carrying its anachronism anomaly. Confidence
        # is lower (0.55): alternates are Strong's-grounded headwords, so
        # inflection fit (e.g. -edst forms, possessives) must be checked at
        # review; each proposal still requires owner approval.
        for word, alt, src in con.execute(
                "SELECT word, alternate_word, first_use_source FROM word_era "
                "WHERE verdict IN ('suspect','typo') AND alternate_word IS NOT NULL"):
            pats = [(rf"\b{re.escape(word)}\b", alt),
                    (rf"\b{re.escape(word.capitalize())}\b", alt.capitalize())]
            for (vid,) in con.execute(
                    "SELECT DISTINCT verse_id FROM anomalies "
                    "WHERE type='anachronism' AND token=?", (word,)):
                text = base_text(con, vid, con.execute(
                    "SELECT text FROM verses WHERE id=?", (vid,)).fetchone()[0])
                new = text
                for pat, rep in pats:
                    new = re.sub(pat, rep, new)
                if new == text:
                    continue
                st = saved.get((vid, "word_substitution", new), "proposed")
                con.execute(
                    "INSERT INTO restorations (verse_id, flaw_type, current_text, "
                    "proposed_text, rationale, evidence, confidence, status) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (vid, "word_substitution", text, new,
                     f"Era-audit anachronism [{src}]: '{word}' flagged not-period; "
                     f"advised period alternate '{alt}' "
                     "(KJV's own rendering of the underlying word elsewhere). "
                     "Check inflection fit in context at review.",
                     f"word_era '{word}' (owner ruling 2026-07-14); anachronism "
                     "anomaly; see references/word_review_report.md",
                     0.55, st))
                n_rows += 1
        con.commit()

        print(f"restorations: {n_rows} rows (all status='proposed' pending owner review "
              "unless previously reviewed)")
        print("\nSample proposals:")
        for name, ch, vs, ft, cur, new in con.execute(
                """SELECT b.name, v.chapter, v.verse, r.flaw_type,
                          r.current_text, r.proposed_text
                   FROM restorations r
                   JOIN verses v ON v.id=r.verse_id
                   JOIN books b ON b.translation='KJV' AND b.id=v.book_id
                   WHERE r.proposed_text IS NOT NULL LIMIT 8"""):
            print(f"  {name} {ch}:{vs} [{ft}]")
            print(f"    - {cur[:90]}")
            print(f"    + {new[:90]}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
