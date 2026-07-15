#!/usr/bin/env python3
"""15_record_reviews.py — Phase 6: apply owner review decisions to `restorations`.

The database is gitignored and rebuildable, so review verdicts must live in
a script under version control. This file IS the review record: each entry
below documents an owner decision (who/when/what), and running the script
re-applies those statuses idempotently after any rebuild.

Review session 2026-07-14 (batch-by-memory walkthrough with the owner):
every substitution group was APPROVED. Group 6 (strait) was approved WITH
AMENDMENT: gate→path in addition to strait→straight ("Straight is the path,
narrow is the way") — amendment applied in 13_propose_restorations.py and
remembered_verses.md before approval, so the approved rows carry the amended
text. Phrase-level rows (lion & lamb, Lord's Prayer — proposed_text NULL)
remain 'proposed' pending KJV-voice phrasing.

Matching: a decision applies to rows whose rationale contains the memory
title keyword and whose proposed_text is non-NULL. Rows created after this
review (new memories, new scope verses) stay 'proposed' until a new review
entry is added here.
"""

import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"

# (memory title keyword, decided status, decision note)
REVIEWS_2026_07_14 = [
    ("Bottles", "approved", "owner approved all 11 (wineskins)"),
    ("matrix", "approved", "owner approved all 5 (womb)"),
    ("On earth", "approved", "owner approved both (on earth)"),
    ("Couch", "approved", "owner approved (crouch, Job 38:40)"),
    ("tables", "approved", "owner approved (tablets, Exodus 34:1)"),
    ("Strait", "approved", "owner approved WITH AMENDMENT gate->path"),
    ("Emojis", "approved", "owner approved all 3 (paren/emoticon removal)"),
    ("Destroyed", "approved", "owner approved (perish, Hosea 4:6)"),
    ("Windows", "approved", "owner approved all 15 (floodgates/openings)"),
    ("Thanksgivings", "approved", "owner approved both as-is (thank offerings)"),
    ("Wizards", "approved", "owner approved all 11 (sorcerers)"),
    ("capitalization", "approved", "owner approved all 3 (spirit of god)"),
    ("Money", "approved", "owner approved (I Timothy 6:10)"),
    # phrase-level rows, phrased by the king-james agent, owner-approved later
    # the same day (2026-07-14 review session 2):
    ("Lion and The Lamb", "approved",
     "owner approved both phrased verses (Isaiah 65:25, 11:6)"),
    ("lord's prayer", "approved",
     "owner approved trespasses phrasing (Matthew 6:12)"),
    # review session 3 (2026-07-14): the 69 anachronism proposals generated
    # from the Decision Log #9 owner-ruled word list — approved in full
    # ("Approve all 69"), individual rejections may follow later.
    # (matcher updated when the rescan landed: proposals now carry the
    # word's source in the rationale, so only the owner-ruled words'
    # substitutions auto-approve; rescan-flagged words await review.)
    ("Era-audit anachronism [owner ruling 2026-07-14]", "approved",
     "owner approved all 69 anachronism substitutions"),
    # review session 4 (2026-07-14): Genesis 1:1 owner-directed — full
    # remembered reading (comma + heavens) confirmed by the owner.
    ("Owner ruling 2026-07-14: full remembered reading", "approved",
     "owner approved Genesis 1:1 'In the beginning, God created the heavens...'"),
    # review session 5 (2026-07-14): global parenthesis/emoticon removal —
    # owner-directed ("emojis need to be removed; parentheses just need to be
    # removed"), applied bible-wide.
    ("Global parenthesis/emoticon removal", "approved",
     "owner directed bible-wide paren/emoticon removal"),
    # review session 6 (2026-07-15): rescan-flagged words reviewed in six
    # thematic groups (typos, formations, compounds, stumbling family,
    # fauna/flora, gopher/forum) — all approved, with owner corrections:
    # wraths->wrath, stumbling family unfused, gopher->cypress, forum
    # phrase-translated (Acts 28:15 OWNER_DIRECTED row).
    ("Era-audit anachronism [KJ-agent 2026-07-14]", "approved",
     "owner approved all rescan substitution groups (sessions A-F)"),
    ("Owner ruling 2026-07-15 (rescan review, group F2)", "approved",
     "owner chose 'the market place of Appius' for Acts 28:15"),
    # review session 7 (2026-07-15): community-reported blog-sweep memories,
    # all eight approved with owner-chosen alternates (set-you-free ×2,
    # two-or-more, exchangers, goods, lying-signs order, basket, Exodus 34:14
    # name clause dropped, Luke sword).
    ("Review session 7 2026-07-15", "approved",
     "owner approved all eight blog-sweep restorations"),
]


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    try:
        total = 0
        for kw, status, note in REVIEWS_2026_07_14:
            cur = con.execute(
                """UPDATE restorations SET status=?
                   WHERE proposed_text IS NOT NULL AND status='proposed'
                   AND rationale LIKE '%' || ? || '%'""", (status, kw))
            if cur.rowcount:
                print(f"{kw}: {cur.rowcount} row(s) -> {status}  ({note})")
                total += cur.rowcount
        con.commit()
        print(f"\n{total} row(s) updated this run")
        for st, c in con.execute(
                "SELECT status, COUNT(*) FROM restorations GROUP BY status"):
            print(f"  {st}: {c}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
