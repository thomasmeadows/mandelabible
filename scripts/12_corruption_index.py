#!/usr/bin/env python3
"""12_corruption_index.py — Phase 6: score every verse; ranked review queue.

Corruption index per verse (weights: Decision Log #8):
  memory testimony (heaviest, scaled by corroboration status):
      corroborated 10.0 | artifact-supported 6.0 | unconfirmed 2.0
      (a verse in scope of multiple memories sums them)
  + internal artifacts: sum of `anomalies.score` on the verse, capped at 5.0
  + length outlier (|z| > 2 within book): 0.3
  + witness divergence (ADVISORY, light): (1 - median similarity across
      Geneva1599/Tyndale/Wycliffe) * 1.0 — period witnesses only; the KJV-
      lineage witnesses are near-copies and would only add noise.

Rationale: memory testimony must dominate (Premise Revision — it is the only
evidence the alteration could not rewrite); internal artifacts are the
second tier; witness divergence is advisory and capped at 1.0 so it can
re-rank within a tier but never lift a verse across tiers.

Idempotent: rebuilds `corruption_index` each run.
"""

import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"

MEMORY_WEIGHT = {"corroborated": 10.0, "artifact-supported": 6.0, "unconfirmed": 2.0}
ANOMALY_CAP = 5.0
OUTLIER_W = 0.3
WITNESS_W = 1.0
PERIOD_WITNESSES = ("Geneva1599", "Tyndale", "Wycliffe")

SCHEMA = """
CREATE TABLE IF NOT EXISTS corruption_index (
    verse_id   INTEGER PRIMARY KEY REFERENCES verses(id),
    score      REAL,
    components TEXT      -- human-readable breakdown
);
"""


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA)

        mem_score = defaultdict(float)
        mem_titles = defaultdict(list)
        for title, status, scope in con.execute(
                "SELECT title, status, scope_refs FROM memories"):
            w = MEMORY_WEIGHT[status]
            for ref in filter(None, (scope or "").split(";")):
                book, cv = ref.rsplit(" ", 1)
                ch, vs = cv.split(":")
                row = con.execute(
                    """SELECT v.id FROM verses v JOIN books b
                       ON b.translation='KJV' AND b.id=v.book_id
                       WHERE v.translation='KJV' AND b.name=? AND v.chapter=? AND v.verse=?""",
                    (book, int(ch), int(vs))).fetchone()
                if row:
                    mem_score[row[0]] += w
                    mem_titles[row[0]].append(f"{title[:30]} ({status})")

        anom = dict(con.execute(
            "SELECT verse_id, SUM(score) FROM anomalies GROUP BY verse_id"))
        outlier = {vid for (vid,) in con.execute(
            "SELECT verse_id FROM verse_stats WHERE is_outlier=1")}

        wit = defaultdict(list)
        ph = ",".join("?" * len(PERIOD_WITNESSES))
        for vid, sim in con.execute(
                f"SELECT verse_id, similarity FROM verse_diffs "
                f"WHERE witness IN ({ph}) AND similarity IS NOT NULL",
                PERIOD_WITNESSES):
            wit[vid].append(sim)

        rows = []
        for (vid,) in con.execute("SELECT id FROM verses WHERE translation='KJV'"):
            parts = []
            s_mem = mem_score.get(vid, 0.0)
            if s_mem:
                parts.append(f"memory {s_mem:.1f} [{'; '.join(mem_titles[vid])}]")
            s_anom = min(anom.get(vid, 0.0), ANOMALY_CAP)
            if s_anom:
                parts.append(f"anomalies {s_anom:.2f}")
            s_out = OUTLIER_W if vid in outlier else 0.0
            if s_out:
                parts.append(f"length-outlier {s_out}")
            sims = wit.get(vid)
            s_wit = (1 - statistics.median(sims)) * WITNESS_W if sims else 0.0
            if s_wit:
                parts.append(f"witness-divergence {s_wit:.2f} (advisory)")
            score = s_mem + s_anom + s_out + s_wit
            rows.append((vid, round(score, 4), "; ".join(parts)))

        con.execute("DELETE FROM corruption_index")
        con.executemany("INSERT INTO corruption_index VALUES (?,?,?)", rows)
        con.commit()

        print(f"corruption_index: {len(rows)} verses scored")
        print("\nTop 15 review queue:")
        for name, ch, vs, score, comp in con.execute(
                """SELECT b.name, v.chapter, v.verse, c.score, c.components
                   FROM corruption_index c
                   JOIN verses v ON v.id=c.verse_id
                   JOIN books b ON b.translation='KJV' AND b.id=v.book_id
                   ORDER BY c.score DESC LIMIT 15"""):
            print(f"  {score:7.2f}  {name} {ch}:{vs} — {comp[:100]}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
