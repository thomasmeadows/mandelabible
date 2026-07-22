#!/usr/bin/env python3
"""59_corn_to_wheat.py — global owner directive 2026-07-21: "replace all
instances of corn with wheat." Word-level, case-preserving, whole-word only
(so Cornelius, corner(s)/cornerstone, cornet(s) are untouched).

Same layers as the girded->adorned / round-4 pass:
  1. db/mandela.db — each changed verse becomes a superseding, owner-approved
     restoration (flaw_type='corn_to_wheat'), carrying every prior change plus
     corn->wheat (the exporter uses one highest-id row per verse, so the latest
     row must contain the full cumulative text). Idempotent: all corn_to_wheat
     rows are deleted and re-inserted each run, and the base loader EXCLUDES this
     flaw_type (see load_pre — the scripts/55 & 58 idempotency trap).
  2. references/global_word_swaps.md — blacklist source (corn -> wheat, per
     verse) read by scripts/49_build_blacklist.py global_swaps().
  3. references/rare_word_review_no_safe_swap.md — whitelist: a self-contained
     "Global word swaps" section (spliced BEFORE the round-4 marker so a re-run
     of scripts/58 leaves it intact) protects 'wheat'.

After running:
    python3 scripts/49_build_blacklist.py
    python3 scripts/29_build_whitelist.py
    python3 scripts/17_export_full.py
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
BL_SRC = ROOT / "references" / "global_word_swaps.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
NSS_MARK = "# Global word swaps — whitelist (2026-07-21)"
R4_MARK = "# Round-4 review words (2026-07-21)"
FLAW = "corn_to_wheat"

_corn = re.compile(r"(?<![A-Za-z])corn(?![A-Za-z])")
_Corn = re.compile(r"(?<![A-Za-z])Corn(?![A-Za-z])")


def swap(t):
    return _Corn.sub("Wheat", _corn.sub("wheat", t))


def load_pre(con):
    """current text per (book,ch,vs) EXCLUDING this migration's own rows."""
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL AND flaw_type != ? ORDER BY id", (FLAW,)):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    cur, vidmap = {}, {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        key = (names[bid], ch, vs)
        cur[key] = resto.get(vid, text)
        vidmap[key] = vid
    return cur, vidmap


def main():
    con = sqlite3.connect(DB)
    cur, vidmap = load_pre(con)

    changed = []
    for ref, was in cur.items():
        final = swap(was)
        if final != was:
            changed.append((ref, was, final))

    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for ref, was, final in changed:
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vidmap[ref], FLAW, was, final,
             "Global owner directive 2026-07-21: replace all instances of corn "
             "with wheat (whole-word, case-preserving). Merged onto current text.",
             "Owner global word directive.", 0.9, "approved"))
    con.commit()
    con.close()

    # ---- blacklist source (builder 49 global_swaps() reads this) -----------
    src = ["# Global Word Swaps (owner-ruled)", "",
           "*Bible-wide single-word directives (owner-approved). Removed word -> "
           "new reading, per verse. Read by `scripts/49_build_blacklist.py` "
           "(global_swaps()) and folded into `word_blacklist.md`.*", ""]
    for ref, _was, _final in sorted(changed, key=lambda x: (str(x[0][0]), x[0][1], x[0][2])):
        b, c, v = ref
        src += [f"## corn → wheat — {b} {c}:{v}",
                "- source: global owner directive 2026-07-21 (corn -> wheat)", ""]
    BL_SRC.write_text("\n".join(src) + "\n", encoding="utf-8")

    # ---- whitelist: splice a 'wheat' section before the round-4 marker ------
    block = "\n".join([
        NSS_MARK, "",
        "*Words protected by bible-wide owner word directives (2026-07-21). "
        "Placed before the round-4 marker so scripts/58 re-runs leave it "
        "untouched.*", "",
        "## wheat → NO-SAFE-SWAP — global",
        "- verdict: NO-SAFE-SWAP",
        "- rationale: Global directive corn -> wheat; wheat is the kept reading.",
        "- **OWNER RULING 2026-07-21: DO NOT CHANGE — global word directive.**",
        "- NEW: (no change — global swap target)", "",
    ])
    text = NSS.read_text(encoding="utf-8")
    head, sep, tail = text.partition(R4_MARK)
    if NSS_MARK in head:                      # drop a prior copy of our block
        head = head[:head.index(NSS_MARK)]
    head = head.rstrip("\n") + "\n\n" + block + "\n"
    NSS.write_text(head + sep + tail if sep else head, encoding="utf-8")

    print(f"corn_to_wheat restorations: {len(changed)} verses")
    print(f"blacklist source: references/global_word_swaps.md ({len(changed)} entries)")
    print("whitelist: 'wheat' protected in rare_word_review_no_safe_swap.md")
    print("Now run: python3 scripts/49_build_blacklist.py && "
          "python3 scripts/29_build_whitelist.py && python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
