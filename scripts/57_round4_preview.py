#!/usr/bin/env python3
"""57_round4_preview.py — build a was/now PREVIEW of the round-4 restoration
re-review rulings (references/rare_word_round4_restoration_review.md), owner
directive 2026-07-21. NO DATABASE WRITES.

Round 4 re-reviewed every restoration-introduced, non-whitelisted word. Most
rulings are "KEEP WHITE LIST" (protect the introduced word, no text change).
This preview handles the ~60 verses whose text the owner wants changed:
  - single-word revises (e.g. has -> hath, says -> saith)
  - reverts to the base KJV reading (e.g. darker -> blacker)
  - partial reverts (restore one word, keep sibling changes) — smiter -> striker
  - phrase edits and a few full verse rewrites
Several verses receive more than one ruling and are merged.

Owner clarifications (2026-07-21):
  - smiter: restore 'striker' ONLY (keep stubborn / railer) — partial revert.
  - Rev 19:7: DROP 'exult' ("Let us rejoice and give him glory...").
  - Gen 25:16: erase 'chiefs' ("...twelve according to their tribes.").

Output: references/rare_word_round4_apply_preview.md (owner reviews wording,
then scripts/58 applies to the DB + blacklist/whitelist + rebuilds the export).

Anchoring: every edit is applied to the ACTUAL current DB text (base KJV + the
highest-id approved restoration per verse). If an expected substring is not
found, the verse is FLAGGED in the preview instead of silently skipped.
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "rare_word_round4_apply_preview.md"


def load_current(con):
    """current text per (book, ch, vs) = base + highest-id approved restoration,
    plus the pure base text (for reverts)."""
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


def wb(word):
    """word-boundary regex for a token that may contain ' - or spaces."""
    return re.compile(r"(?<![A-Za-z])" + re.escape(word) + r"(?![A-Za-z])")


# ---------------------------------------------------------------------------
# EDIT TABLE.  Each entry: (book, ch, vs): (kind, payload, note)
#   kind 'replace'        payload = [(old, new), ...] literal, in order
#   kind 'revert'         payload = None            -> now = base KJV
#   kind 'partial_revert' payload = [(old, new)]    -> restore base word, keep siblings
#   kind 'set'            payload = "full text"     -> full verse rewrite
# ---------------------------------------------------------------------------
B = "Genesis"
EDITS = {
    # ---- single-word revises ------------------------------------------------
    ("I Corinthians", 13, 13): ("replace", [("abides", "abideth")],
        "abides -> abideth (keep rest); whitelist abide/abideth + inflections"),
    ("Galatians", 2, 21): ("replace", [("attainable", "cometh")],
        "attainable is modern, not period; -> cometh"),
    ("Hosea", 10, 7): ("replace", [("the chip upon", "the chip of wood upon")],
        "chip -> 'chip of wood'; whitelist chip"),
    ("John", 14, 6): ("replace", [("comes", "cometh")],
        "comes -> cometh (KJV inflection)"),
    ("Matthew", 5, 32): ("replace", [("commits", "committeth")],
        "commits -> committeth; whitelist committeth"),
    ("Leviticus", 2, 7): ("replace", [("cooked in a pot", "baken in a pan")],
        "cooked/pot -> baken/pan"),
    ("II Samuel", 3, 34): ("replace", [("so cruellest thou", "so didst thou fall")],
        "cruellest/fellest -> 'so didst thou fall'"),
    ("Leviticus", 21, 18): ("replace", [("deformed", "crooked")],
        "deformed -> crooked; whitelist crooked"),
    ("Psalms", 105, 27): ("replace", [("his effective signs", "his signs")],
        "remove 'effective' (nonsensical)"),
    ("Colossians", 4, 10): ("replace", [("hails", "greets")],
        "hails -> greets; whitelist greet/greets"),
    ("Psalms", 106, 5): ("replace", [("happiness", "gladness")],
        "happiness -> gladness; whitelist gladness"),
    ("I John", 4, 6): ("replace", [("leads astray", "maketh astray")],
        "leads -> maketh"),
    ("Job", 30, 8): ("set",
        "They were children of fools and vile: they were forced out of their land.",
        "owner full rewrite"),
    ("Proverbs", 18, 1): ("replace", [("meddles", "meddleth")],
        "meddles -> meddleth; whitelist meddleth"),
    ("I Corinthians", 12, 5): ("replace", [("ministries", "ministry")],
        "ministries -> ministry; whitelist ministry"),
    ("Numbers", 17, 8): ("replace", [("produced", "brought forth")],
        "produced -> brought forth"),
    ("Colossians", 2, 2): ("replace", [("richest", "riches")],
        "richest -> riches; whitelist riches, blacklist richest"),
    ("Matthew", 5, 22): ("replace", [("says", "saith")],
        "says -> saith; whitelist saith"),
    ("Isaiah", 5, 26): ("replace", [("show", "shew")],
        "show -> shew; whitelist shew"),
    ("I Timothy", 1, 9): ("replace", [("slayers", "murderers")],
        "slayers -> murderers; whitelist murderers"),
    ("Numbers", 33, 54): ("replace", [("smaller", "lesser")],
        "smaller -> lesser; whitelist lesser"),
    ("Jude", 1, 13): ("replace", [("streaming", "crying")],
        "streaming -> crying"),
    ("Isaiah", 33, 23): ("replace", [("tackle", "ropes")],
        "tackle -> ropes; whitelist ropes"),
    ("II Chronicles", 34, 6): ("replace", [("tools", "temples")],
        "tools -> temples"),
    ("Genesis", 43, 30): ("replace", [("towards", "upon")],
        "towards -> upon"),
    ("Ecclesiastes", 10, 15): ("replace", [("vexeth", "adorned")],
        "vexeth -> adorned"),
    ("Judges", 5, 22): ("replace", [("prancings", "galloping")],
        "prancings -> galloping (x2); whitelist galloping"),
    ("Genesis", 36, 15): ("set",
        "These were the sons of Esau: the sons of Eliphaz the firstborn son of "
        "Esau; Teman, Omar, Zepho, Kenaz,",
        "owner rewrite per other translations"),
    ("Genesis", 25, 16): ("replace", [("twelve chiefs according", "twelve according")],
        "erase 'chiefs' (owner ruling)"),

    # ---- reverts to base ----------------------------------------------------
    ("Jeremiah", 6, 29): ("revert", None, "blower -> base (bellows); whitelist blower"),
    ("Lamentations", 4, 8): ("revert", None, "darker -> base (blacker); whitelist blacker"),
    ("Mark", 2, 7): ("revert", None, "does -> base (doth)"),
    ("Proverbs", 25, 23): ("revert", None, "evil-speaking -> base (backbiting); whitelist backbiting"),
    ("Psalms", 105, 35): ("revert", None, "herbage -> base; whitelist herbs"),
    ("Titus", 3, 2): ("revert", None, "railers -> base (brawlers); whitelist brawlers"),
    ("II Timothy", 2, 14): ("revert", None, "overthrowing -> base (subverting); whitelist subverting"),
    ("Acts", 15, 24): ("revert", None, "overthrowing -> base (subverting); whitelist subverting"),
    ("Job", 8, 14): ("revert", None, "lizard's -> base (spider's); whitelist spider"),
    ("I Samuel", 17, 18): ("revert", None, "curd -> base (cheeses); whitelist cheese"),
    ("II Samuel", 17, 29): ("revert", None, "curd -> base (cheese); whitelist cheese"),
    ("Job", 10, 10): ("revert", None, "curd -> base (cheese); whitelist cheese"),

    # ---- partial reverts (restore base word, keep siblings) -----------------
    ("Titus", 1, 7): ("partial_revert", [("no smiter", "no striker")],
        "restore striker (keep stubborn); whitelist striker"),
    ("I Timothy", 3, 3): ("partial_revert", [("no smiter", "no striker")],
        "restore striker (keep railer); whitelist striker"),

    # ---- awl -> a needle ----------------------------------------------------
    ("Exodus", 21, 6): ("replace", [("with an awl", "with a needle")], "awl -> needle"),
    ("Deuteronomy", 15, 17): ("replace", [("take an awl", "take a needle")], "awl -> needle"),

    # ---- bulwark -> rampart -------------------------------------------------
    ("Lamentations", 2, 8): ("replace", [("the bulwark and the wall", "the rampart and the wall")],
        "bulwark -> rampart; whitelist rampart"),
    ("Nahum", 3, 8): ("replace", [("whose bulwark was", "whose rampart was")],
        "bulwark -> rampart; whitelist rampart"),

    # ---- fork -> hook -------------------------------------------------------
    ("I Samuel", 2, 13): ("replace", [("with a fork of three teeth", "with a hook of three teeth")],
        "fork -> hook"),
    ("I Samuel", 2, 14): ("replace", [("all that the fork brought", "all that the hook brought")],
        "fork -> hook"),

    # ---- sea-mew -> seagull -------------------------------------------------
    ("Leviticus", 11, 16): ("replace", [("sea-mew", "seagull")], "sea-mew -> seagull; whitelist seagull"),
    ("Deuteronomy", 14, 15): ("replace", [("sea-mew", "seagull")], "sea-mew -> seagull; whitelist seagull"),

    # ---- donkeys -> asses (plural only; singular 'donkey' Gen49:14 kept) ----
    ("Genesis", 44, 3): ("replace", [("their donkeys", "their asses")],
        "donkeys -> asses; whitelist asses (NB: singular 'donkey' Gen49:14 kept)"),
    ("Genesis", 43, 24): ("replace", [("their donkeys fodder", "their asses fodder")],
        "donkeys -> asses; whitelist asses"),

    # ---- prancing -> neighing (Nahum 3:2; 'bounding' kept) ------------------
    ("Nahum", 3, 2): ("replace", [("the prancing horses", "the neighing horses")],
        "prancing -> neighing; whitelist neighing"),

    # ---- pressing -> turning (3 verses) -------------------------------------
    ("Mark", 5, 31): ("replace", [("multitude pressing thee", "multitude turning thee")],
        "pressing -> turning"),
    ("Proverbs", 30, 33): ("replace", [("the pressing of milk", "the turning of milk")],
        "pressing -> turning"),
    ("Luke", 6, 1): ("replace", [("pressing them in their hands", "turning them in their hands")],
        "pressing -> turning"),

    # ---- threats -> grievances (3 verses) -----------------------------------
    ("Acts", 4, 29): ("replace", [("their threats", "their grievances")],
        "threats -> grievances; whitelist grievance/grievances"),
    ("Acts", 9, 1): ("replace", [("out threats", "out grievances")],
        "threats -> grievances; whitelist grievance/grievances"),
    ("Ephesians", 6, 9): ("replace", [("forbearing threats", "forbearing grievances")],
        "threats -> grievances; whitelist grievance/grievances"),

    # ---- thyselves -> 'thine own self' (4 verses) ---------------------------
    ("Romans", 6, 16): ("replace", [("thyselves", "thine own self")], "thyselves -> thine own self"),
    ("Romans", 6, 11): ("replace", [("thyselves", "thine own self")], "thyselves -> thine own self"),
    ("Romans", 6, 13): ("replace", [("thyselves", "thine own self")], "thyselves -> thine own self"),
    ("Colossians", 3, 18): ("replace", [("thyselves", "thine own self")], "thyselves -> thine own self"),

    # ---- has -> hath (7 verses; Rev 19:7 handled in its merged entry) --------
    ("Mark", 4, 9): ("replace", [("has", "hath")], "has -> hath"),
    ("Matthew", 11, 15): ("replace", [("has", "hath")], "has -> hath"),
    ("Matthew", 4, 16): ("replace", [("has", "hath")], "has -> hath"),
    ("Mark", 4, 23): ("replace", [("has", "hath")], "has -> hath"),
    ("Matthew", 13, 9): ("replace", [("has", "hath")], "has -> hath"),
    ("Matthew", 13, 43): ("replace", [("has", "hath")], "has -> hath"),
    ("Mark", 7, 16): ("replace", [("has", "hath")], "has -> hath"),

    # ---- greeted -> greeteth (9 verses) -------------------------------------
    ("Acts", 21, 19): ("replace", [("greeted", "greeteth")], "greeted -> greeteth; whitelist greet + inflections"),
    ("Luke", 1, 40): ("replace", [("greeted", "greeteth")], "greeted -> greeteth (keep name normalization)"),
    ("Mark", 9, 15): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),
    ("II Kings", 10, 15): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),
    ("Acts", 21, 7): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),
    ("I Samuel", 17, 22): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),
    ("Acts", 18, 22): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),
    ("I Samuel", 30, 21): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),
    ("Judges", 18, 15): ("replace", [("greeted", "greeteth")], "greeted -> greeteth"),

    # ---- multi-ruling merged verses -----------------------------------------
    ("Psalms", 105, 31): ("replace",
        [("various", "diverse"), ("boundary", "borders"), ("spoke", "spake")],
        "various->diverse, boundary->borders, spoke->spake (gnats/insects kept)"),
    ("Psalms", 105, 33): ("replace",
        [("broke", "brake"), ("boundary", "borders")],
        "broke->brake, boundary->borders (fig-trees kept)"),
    ("Psalms", 105, 34): ("replace", [("spoke", "spake")],
        "spoke->spake (crickets kept)"),
    ("Leviticus", 7, 9): ("replace",
        [("the cooking pot, or in a pan", "the pot, or in the pan"), ("offers", "offereth")],
        "erase 'cooking' -> 'in the pot, or in the pan'; offers->offereth (whitelist offereth)"),
    ("Psalms", 106, 6): ("replace",
        [("wickedly, have done wrongly", "wickedly, we have done wrongly")],
        "'have done wrongly' -> 'we have done wrongly' (acted kept)"),
    ("Revelation of John", 19, 7): ("replace",
        [("rejoice and exult and give", "rejoice and give"),
         ("Lamb has come", "Lamb hath come"),
         ("Bride has made", "Bride hath made")],
        "drop 'exult'; has->hath x2 (whitelist rejoice)"),
}

# ring-streaked (7 tokens across 6 verses) -> spotted, except Gen 30:35 -> speckled
RING = {
    ("Genesis", 30, 39): "spotted", ("Genesis", 30, 40): "spotted",
    ("Genesis", 31, 8): "spotted", ("Genesis", 31, 10): "spotted",
    ("Genesis", 31, 12): "spotted", ("Genesis", 30, 35): "speckled",
}
for ref, tgt in RING.items():
    EDITS[ref] = ("replace", [("ring-streaked", tgt)],
                  f"ring-streaked -> {tgt}; whitelist speckled/spotted")

# gpron / gprons typo -> apron / aprons.  Found by scanning the DB so all
# 26 + 7 occurrences are caught regardless of the review file's listing.
GPRON_SCAN = {"gprons": "aprons", "gpron": "apron"}


def apply_ops(text, ops):
    out = text
    missing = []
    for old, new in ops:
        if old not in out:
            missing.append(old)
            continue
        out = out.replace(old, new)
    return out, missing


def main():
    con = sqlite3.connect(DB)
    cur, base = load_current(con)
    con.close()

    rows = []      # (ref, was, now, note, flag)
    flags = 0

    # explicit table
    for ref, (kind, payload, note) in EDITS.items():
        was = cur.get(ref)
        if was is None:
            rows.append((ref, "(verse not found)", "", note, "MISSING-VERSE"))
            flags += 1
            continue
        if kind == "revert":
            now, flag = base[ref], ""
        elif kind == "set":
            now, flag = payload, ""
        else:  # replace / partial_revert
            now, missing = apply_ops(was, payload)
            flag = ("NOT-FOUND: " + "; ".join(missing)) if missing else ""
            if missing:
                flags += 1
        rows.append((ref, was, now, note, flag))

    # gpron scan (skip refs already handled explicitly, though none overlap)
    for ref, was in cur.items():
        if ref in EDITS:
            continue
        if "gpron" in was.lower():
            now = was
            for tok, repl in GPRON_SCAN.items():
                now = wb(tok).sub(repl, now)
                now = wb(tok.capitalize()).sub(repl.capitalize(), now)
            rows.append((ref, was, now, "girdle->apron typo fix (gpron->apron)", ""))

    # sort by book order as they appear in DB, then ch/vs
    rows.sort(key=lambda r: (str(r[0][0]), r[0][1], r[0][2]))

    changed = [r for r in rows if r[2] and r[1] != r[2]]
    out = [
        "# Round 4 — Restoration Re-review: APPLY PREVIEW (not yet applied)",
        "",
        f"*{len(changed)} verses proposed for change from the owner rulings in "
        "`rare_word_round4_restoration_review.md`. Computed against the ACTUAL "
        "current DB text (base KJV + approved restorations). NO DATABASE WRITES "
        "yet. Review the wording — especially FLAGGED rows — then scripts/58 "
        "applies to the DB, updates the blacklist/whitelist sources, and rebuilds "
        "the export.*",
        "",
        f"**Flags needing attention: {flags}.** "
        "KEEP-WHITE-LIST rulings are not shown here (no text change).",
        "",
    ]
    for ref, was, now, note, flag in rows:
        if not (now and was != now):
            continue
        b, c, v = ref
        out.append(f"## {b} {c}:{v}")
        out.append(f"- ruling: {note}")
        if flag:
            out.append(f"- ⚠️ **FLAG:** {flag}")
        out.append(f"- was: {was}")
        out.append(f"- now: {now}")
        out.append("")

    # no-op / flagged section
    problems = [r for r in rows if r[4]]
    if problems:
        out.append("## ⚠️ Flagged (anchor not found — needs a look)")
        out.append("")
        for ref, was, now, note, flag in problems:
            b, c, v = ref
            out.append(f"- **{b} {c}:{v}** — {flag} — ruling: {note}")
        out.append("")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(changed)} changed verses, {flags} flags")


if __name__ == "__main__":
    main()
