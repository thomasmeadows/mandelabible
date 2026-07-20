#!/usr/bin/env python3
"""52_revert_john_14_2_mansions.py — revert the John 14:2 rare-word swap and
protect "mansions" (owner directive 2026-07-20).

Round 1 changed John 14:2 "mansions" -> "habitations" (restoration #5506).
"Mansions" is the correct, widely-remembered KJV reading of this famous verse,
so the owner has reverted the change and ruled the word DO NOT CHANGE.

This is a migration: it does NOT edit the builder scripts (29/49/17). It edits
the sources of truth so any future rebuild agrees, and it patches the already-
generated companion lists so they are correct immediately. Fully idempotent —
re-running makes no further changes.

Actions
  1. db/mandela.db: restoration #5506 status 'approved' -> 'reverted'
     (the exporter applies only status='approved', so the export now reads
     "mansions" again).
  2. references/rare_word_replacements.md: mark the mansions entry reverted so
     scripts/49_build_blacklist.py excludes it (it skips "no safe one-word
     swap found" sources) and scripts/29_build_whitelist.py won't double-list
     it (already covered by the owner-reviewed source below).
  3. references/rare_word_review_no_safe_swap.md: append a mansions
     OWNER RULING: DO NOT CHANGE entry (the owner-reviewed whitelist source).
  4. references/word_whitelist.md: add "mansions" to the reviewed list + a
     description block.
  5. references/word_blacklist.md: remove the mansions -> habitations entry
     and its index link, and adjust the header counts.

Downstream (run separately to propagate the reverted text):
    python3 scripts/17_export_full.py     # rebuild the MVP export
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
R1 = ROOT / "references" / "rare_word_replacements.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
WL = ROOT / "references" / "word_whitelist.md"
BL = ROOT / "references" / "word_blacklist.md"

RESTORATION_ID = 5506
VERSE = "John 14:2"


def step_db():
    con = sqlite3.connect(DB)
    row = con.execute("SELECT status FROM restorations WHERE id=?",
                      (RESTORATION_ID,)).fetchone()
    if not row:
        print(f"  DB: restoration #{RESTORATION_ID} not found — skipped")
    elif row[0] == "reverted":
        print(f"  DB: restoration #{RESTORATION_ID} already reverted")
    else:
        con.execute("UPDATE restorations SET status='reverted' WHERE id=?",
                    (RESTORATION_ID,))
        con.commit()
        print(f"  DB: restoration #{RESTORATION_ID} {row[0]} -> reverted")
    con.close()


def step_rare_word_replacements():
    text = R1.read_text(encoding="utf-8")
    old = ("## mansions → habitations — John 14:2\n"
           "- source: King James agent selection\n")
    new = ("## mansions → habitations — John 14:2\n"
           "- source: REVERTED 2026-07-20 (owner) — no safe one-word swap "
           "found; \"mansions\" is the remembered KJV reading and is now "
           "whitelisted (see rare_word_review_no_safe_swap.md). "
           "Original text retained.\n")
    if new.split("\n")[1] in text:
        print("  rare_word_replacements.md: already reverted")
    elif old in text:
        R1.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("  rare_word_replacements.md: mansions entry marked reverted")
    else:
        print("  rare_word_replacements.md: mansions source line not found "
              "— skipped")


def step_nss():
    text = NSS.read_text(encoding="utf-8")
    if re.search(r"^## mansions ", text, re.M):
        print("  rare_word_review_no_safe_swap.md: mansions already present")
        return
    entry = (
        "\n## mansions → NO-SAFE-SWAP — John 14:2\n"
        "- **OWNER RULING 2026-07-20: DO NOT CHANGE — \"mansions\" stays.** "
        "It is the correct, widely-remembered KJV reading of this famous "
        "verse (\"In my Father's house are many mansions\"); round 1's "
        "swap to \"habitations\" (restoration #5506) has been reverted.\n"
        "- verdict: NO-SAFE-SWAP\n"
        "- NEW: (no change — OLD text retained per owner ruling)\n")
    NSS.write_text(text.rstrip("\n") + "\n" + entry, encoding="utf-8")
    print("  rare_word_review_no_safe_swap.md: mansions DO NOT CHANGE added")


def step_whitelist():
    text = WL.read_text(encoding="utf-8")
    if "[mansions](#mansions)" in text:
        print("  word_whitelist.md: mansions already listed")
        return
    # 1. reviewed alphabetical list: mallows < mansions < mast
    text = text.replace("[mallows](#mallows), [mast](#mast)",
                        "[mallows](#mallows), [mansions](#mansions), "
                        "[mast](#mast)", 1)
    # 2. bump the reviewed-count heading
    text = re.sub(r"(### Reviewed no-safe-swap words \()(\d+)(\))",
                  lambda m: f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}",
                  text, count=1)
    # 3. description block, inserted before ### mast
    block = ("### mansions\n"
             "- John 14:2: OWNER RULING 2026-07-20 — DO NOT CHANGE. "
             "\"Mansions\" is the correct, widely-remembered KJV reading of "
             "this famous verse; round 1's swap to \"habitations\" "
             "(restoration #5506) was reverted (scripts/"
             "52_revert_john_14_2_mansions.py).\n"
             "  - **OWNER RULING 2026-07-20: DO NOT CHANGE — mansions stays.**"
             "\n\n")
    text = text.replace("### mast\n", block + "### mast\n", 1)
    WL.write_text(text, encoding="utf-8")
    print("  word_whitelist.md: mansions added (reviewed list + description)")


def step_blacklist():
    text = BL.read_text(encoding="utf-8")
    block = ('#### <a name="mansions"></a>mansions → habitations\n'
             "- **habitations** (John 14:2; rare word, round 1) — King James "
             "agent selection\n"
             "  - decided by: AI agent (king-james), owner-approved\n\n")
    if block not in text:
        print("  word_blacklist.md: mansions entry already removed")
        return
    text = text.replace(block, "", 1)
    text = text.replace("[mansions](#mansions), ", "", 1)
    # header counts: total and AI-decided each drop by one (mansions was AI)
    def dec_counts(m):
        total, human, ai = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (f"**{total - 1} blacklisted words** ({human} with a human "
                f"ruling, {ai - 1} AI-decided with owner approval).")
    text = re.sub(
        r"\*\*(\d+) blacklisted words\*\* \((\d+) with a human ruling, "
        r"(\d+) AI-decided with owner approval\)\.",
        dec_counts, text, count=1)
    BL.write_text(text, encoding="utf-8")
    print("  word_blacklist.md: mansions entry removed, counts adjusted")


def main():
    print(f"Reverting {VERSE} (mansions) — restoration #{RESTORATION_ID}")
    step_db()
    step_rare_word_replacements()
    step_nss()
    step_whitelist()
    step_blacklist()
    print("Done.")


if __name__ == "__main__":
    main()
