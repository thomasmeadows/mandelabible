#!/usr/bin/env python3
"""53_leasing_to_lies.py — supersede the round-1 "leasing → falsehood" swap
with "leasing → lies" (owner directive 2026-07-20).

Round 1 replaced the Middle English survival "leasing" (Psalm 4:2, 5:6) with
"falsehood" (AI-decided, confidence 0.7, matched Webster's 1833 revision).
The King James agent's Middle English survivals audit (2026-07-20) found a
better-evidenced replacement: **lies**. "leasing" continues Middle English
"leesyng/leesing" (OE lēasung) and is absent from both Early Modern English
witnesses (Tyndale, Geneva); Geneva 1599 — the KJV translators' primary
working text — renders the identical Hebrew (kazab) at BOTH verses as "lyes".
So the KJV reached back past its own era's living usage to an older word;
"lies" restores the reading Geneva actually used and is common KJV vocabulary.

Axis-1 (translation-era) advisory evidence per the Premise Revision — it does
not override any memory; no remembered verse touches Psalm 4:2 or 5:6.

This is a migration: it does not edit the builder scripts. It updates every
layer so a future rebuild agrees, and patches the already-generated blacklist.
Idempotent — re-running makes no further changes.

  1. db/mandela.db: restorations #6058, #6059 proposed_text falsehood -> lies
     (+ updated rationale/evidence/confidence).
  2. references/rare_word_replacements.md: the two "leasing → falsehood"
     entries -> "leasing → lies" (round-1 source the blacklist builds from).
  3. references/word_blacklist.md: the generated "leasing → falsehood" entry.

Downstream (run separately): python3 scripts/17_export_full.py
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
R1 = ROOT / "references" / "rare_word_replacements.md"
BL = ROOT / "references" / "word_blacklist.md"

RIDS = {6058: "Psalms 4:2", 6059: "Psalms 5:6"}
RATIONALE = (
    'leasing -> lies: King James agent Middle English survivals audit '
    '2026-07-20. "leasing" is a Middle English survival (OE lēasung, '
    '"falsehood"); Geneva 1599 reads "lyes" at this exact verse (same Hebrew '
    'kazab). Supersedes round-1 "falsehood" (Webster-based). "lies" is common '
    'KJV vocabulary. Axis-1 translation-era advisory (Premise Revision).')
EVIDENCE = (
    "King James agent audit (.claude/agent-memory/king-james-middle-english-"
    "expert/kjv-me-survivals-audit.md); Geneva 1599 \"lyes\" at Psalm 4:2 & "
    "5:6; \"leasing\" absent from Tyndale/Geneva corpora; Middle English "
    "Reader glossary lists leesyng (OE lēasung).")


def step_db():
    con = sqlite3.connect(DB)
    changed = 0
    for rid in RIDS:
        row = con.execute(
            "SELECT proposed_text FROM restorations WHERE id=?", (rid,)).fetchone()
        if not row:
            print(f"  DB: restoration #{rid} not found — skipped")
            continue
        if "falsehood" not in row[0]:
            print(f"  DB: restoration #{rid} already superseded (no 'falsehood')")
            continue
        new = row[0].replace("falsehood", "lies")
        con.execute(
            "UPDATE restorations SET proposed_text=?, rationale=?, evidence=?, "
            "confidence=0.9 WHERE id=?", (new, RATIONALE, EVIDENCE, rid))
        changed += 1
        print(f"  DB: restoration #{rid} ({RIDS[rid]}) falsehood -> lies")
    con.commit()
    con.close()
    return changed


def step_rare_word_replacements():
    text = R1.read_text(encoding="utf-8")
    if "## leasing → lies —" in text:
        print("  rare_word_replacements.md: already lies")
        return
    for ref in ("Psalms 4:2", "Psalms 5:6"):
        text = text.replace(f"## leasing → falsehood — {ref}",
                            f"## leasing → lies — {ref}")
    text = text.replace(
        "## leasing → lies — Psalms 4:2\n- source: Webster alignment (word in KJV same testament)",
        "## leasing → lies — Psalms 4:2\n- source: King James agent audit 2026-07-20 "
        "— Geneva 1599 reads \"lyes\" here; supersedes round-1 \"falsehood\" (Webster)")
    text = text.replace(
        "## leasing → lies — Psalms 5:6\n- source: Webster alignment (word in KJV same testament)",
        "## leasing → lies — Psalms 5:6\n- source: King James agent audit 2026-07-20 "
        "— Geneva 1599 reads \"lyes\" here; supersedes round-1 \"falsehood\" (Webster)")
    # the NEW: lines still say falsehood — flip just within the leasing entries
    text = text.replace("seek after falsehood? Selah.", "seek after lies? Selah.")
    text = text.replace("them that speak falsehood: the Lord",
                        "them that speak lies: the Lord")
    R1.write_text(text, encoding="utf-8")
    print("  rare_word_replacements.md: leasing → lies (2 entries)")


def step_blacklist():
    text = BL.read_text(encoding="utf-8")
    old = ('#### <a name="leasing"></a>leasing → falsehood\n'
           "- **falsehood** (Psalms 4:2; rare word, round 1) — Webster alignment "
           "(word in KJV same testament)\n"
           "  - decided by: AI agent (king-james), owner-approved\n"
           "- **falsehood** (Psalms 5:6; rare word, round 1) — Webster alignment "
           "(word in KJV same testament)\n"
           "  - decided by: AI agent (king-james), owner-approved")
    new = ('#### <a name="leasing"></a>leasing → lies\n'
           "- **lies** (Psalms 4:2; rare word, round 1) — King James agent audit "
           "2026-07-20: Geneva 1599 reads \"lyes\" here; supersedes round-1 "
           "\"falsehood\" (Webster)\n"
           "  - decided by: AI agent (king-james), owner-approved\n"
           "- **lies** (Psalms 5:6; rare word, round 1) — King James agent audit "
           "2026-07-20: Geneva 1599 reads \"lyes\" here; supersedes round-1 "
           "\"falsehood\" (Webster)\n"
           "  - decided by: AI agent (king-james), owner-approved")
    if new.split("\n")[0] in text:
        print("  word_blacklist.md: already lies")
    elif old in text:
        BL.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("  word_blacklist.md: leasing entry updated to lies")
    else:
        print("  word_blacklist.md: leasing/falsehood block not found — skipped")


def main():
    print("Superseding leasing → falsehood with leasing → lies (Psalm 4:2, 5:6)")
    step_db()
    step_rare_word_replacements()
    step_blacklist()
    print("Done. Run scripts/17_export_full.py to propagate to the export.")


if __name__ == "__main__":
    main()
