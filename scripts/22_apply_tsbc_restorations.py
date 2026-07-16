#!/usr/bin/env python3
"""22_apply_tsbc_restorations.py — Phase 6: apply TSBC memories to the MVP.

Owner ruling 2026-07-16 (Decision Log #11): everything in the TSBC Scribe
database is auto-accepted as verifiable fact; the website citation itself is
the verification; the MVP updates automatically; inaccuracies are revisited
later.

For every harvested TSBC memory with a restoredText (script 21):
  - map its change's (book, chapter, verse) to the KJV verse;
  - pick one restored text per verse when several memories propose one
    (most residue images wins, then the most common text, then the latest
    memory) — all contributing memory IDs are cited;
  - insert an 'approved' restoration citing the TSBC engine URL, unless the
    verse already carries an earlier approved restoration from other
    evidence, in which case the TSBC row is stored 'proposed' and logged
    for owner reconciliation (Decision Log #11 conflict guard).

Idempotent: rows with flaw_type='tsbc_memory' (created only by this script)
are rebuilt on each run. Finishes by noting that script 17 must be re-run
to regenerate the MVP export.
"""

import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
ENGINE = "https://search.thesupernaturalbiblechanges.com"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower()).replace("’", "'")


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    residue_count = dict(con.execute(
        "SELECT memory_id, COUNT(*) FROM tsbc_residue GROUP BY memory_id"))

    # candidate texts per KJV verse
    per_verse = defaultdict(list)   # verse_id -> [(memory_row, change_row)]
    unmapped = 0
    for m in con.execute(
            """SELECT m.*, c.book, c.chapter, c.verse, c.book_name, c.notes
                      AS change_notes
               FROM tsbc_memories m JOIN tsbc_changes c ON c.id = m.change_id
               WHERE TRIM(COALESCE(m.restored_text,'')) != ''"""):
        v = con.execute(
            "SELECT id, text FROM verses WHERE translation='KJV' AND "
            "book_id=? AND chapter=? AND verse=?",
            (m["book"], m["chapter"], m["verse"])).fetchone()
        if v is None:
            unmapped += 1
            continue
        per_verse[v["id"]].append((m, v["text"]))

    # rebuild this script's rows
    con.execute("DELETE FROM restorations WHERE flaw_type='tsbc_memory'")

    n_approved = n_conflict = n_same = 0
    for verse_id, entries in sorted(per_verse.items()):
        current = entries[0][1]
        texts = Counter(norm(m["restored_text"]) for m, _ in entries)

        def rank(entry):
            m, _ = entry
            return (residue_count.get(m["id"], 0),
                    texts[norm(m["restored_text"])],
                    m["memory_date"] or "")
        best, _ = max(entries, key=rank)
        proposed = best["restored_text"].strip()
        if norm(proposed) == norm(current):
            n_same += 1
            continue

        mem_ids = ", ".join(f"#{m['id']}" for m, _ in entries)
        n_residue = sum(residue_count.get(m["id"], 0) for m, _ in entries)
        evidence = (f"TSBC Scribe engine (auto-accepted per Decision Log "
                    f"#11): {ENGINE}/changeDetail/{best['change_id']} via "
                    f"{ENGINE}/changes — change #{best['change_id']}, "
                    f"memory {mem_ids}"
                    + (f", {n_residue} residue image(s) of the original text"
                       if n_residue else ""))
        rationale = (f"TSBC memory testimony: {best['book_name']} "
                     f"{best['chapter']}:{best['verse']} restored per "
                     f"documented public memory"
                     + (f". Notes: {best['notes'].strip()}"
                        if (best["notes"] or "").strip() else ""))

        prior = con.execute(
            "SELECT id FROM restorations WHERE verse_id=? AND "
            "status='approved' AND flaw_type!='tsbc_memory'",
            (verse_id,)).fetchone()
        status = "proposed" if prior else "approved"
        if prior:
            n_conflict += 1
            print(f"  conflict: verse_id {verse_id} ({best['book_name']} "
                  f"{best['chapter']}:{best['verse']}) already has approved "
                  f"restoration #{prior['id']} — TSBC row left 'proposed'")
        else:
            n_approved += 1
        con.execute(
            """INSERT INTO restorations (verse_id, flaw_type, current_text,
               proposed_text, rationale, evidence, confidence, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (verse_id, "tsbc_memory", current, proposed, rationale,
             evidence, 0.85 if n_residue else 0.75, status))

    con.commit()
    print(f"verses with TSBC restored text: {len(per_verse)}")
    print(f"approved: {n_approved}, conflicts (left proposed): {n_conflict}, "
          f"identical to current text (skipped): {n_same}, "
          f"unmapped verses: {unmapped}")
    print("now re-run scripts/17_export_full.py to regenerate the MVP")
    con.close()


if __name__ == "__main__":
    main()
