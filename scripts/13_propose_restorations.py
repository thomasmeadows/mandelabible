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
        (r"\bstrait\b", "straight"), (r"\bStrait\b", "Straight")]),
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

# phrase-level memories: row created, phrasing delegated (proposed_text NULL)
PHRASING_PENDING = ["lion", "lord's prayer"]

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
            pending = any(kw in t for kw in PHRASING_PENDING)

            for ref in refs:
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
