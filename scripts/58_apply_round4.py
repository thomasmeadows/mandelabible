#!/usr/bin/env python3
"""58_apply_round4.py — APPLY the round-4 restoration re-review rulings
(owner: "it is safe to apply the changes now") plus the global owner directive
"change all instances of girded to adorned" (2026-07-21).

Builds on scripts/57_round4_preview.py — that module holds the reviewed edit
table (EDITS), the gpron typo scan, and the current-text loader; this script
imports them so the applied text is identical to the previewed text, then folds
in girded -> adorned across the whole corpus.

What it touches (same layers as the round-3 apply, owner directive 2026-07-21):
  1. db/mandela.db — every changed verse becomes a superseding, owner-approved
     restoration (flaw_type='round4_review'); reverts are written as a
     restoration whose proposed_text IS the base KJV reading. Idempotent: all
     round4_review rows are deleted and re-inserted each run.
  2. references/rare_word_round4_replacements.md — blacklist source (removed
     word -> new word, per verse) read by scripts/49_build_blacklist.py round4().
  3. references/rare_word_review_no_safe_swap.md — whitelist source; a rewritten
     round-4 section protects every KEEP-white-list word, every newly introduced
     word, and the owner's explicit additions.

After running:
    python3 scripts/49_build_blacklist.py
    python3 scripts/29_build_whitelist.py
    python3 scripts/17_export_full.py
"""
import difflib
import importlib.util
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
REVIEW = ROOT / "references" / "rare_word_round4_restoration_review.md"
BL_SRC = ROOT / "references" / "rare_word_round4_replacements.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
NSS_MARK = "# Round-4 review words (2026-07-21)"
FLAW = "round4_review"

STOP = set("a an and the that this those these i thou he she it we ye you they me him "
           "her us them my thy his its our your their of to in on for with by at from "
           "unto into upon as is are was were be been am art shall will not no nor but "
           "or so if then than there here when why how which who whom whose what do "
           "doth did done have hath had haue also out up down over all any some more "
           "most let may can could would should o oh yea verily said he".split())

# Owner-named whitelist extras that won't necessarily surface from the diff
# (singular forms, words present on both sides of an edit, etc.).
EXTRA_WHITELIST = {
    "abide", "abideth", "greet", "greets", "greeteth", "grievance", "grievances",
    "rejoice", "chip", "spider", "cheese", "herbs", "blower", "brawlers",
    "subverting", "striker", "speckled", "spotted", "asses", "riches", "adorned",
    "crooked", "backbiting", "gladness", "murderers", "lesser", "ropes", "temples",
    "rampart", "hook", "seagull", "neighing", "diverse", "borders", "brake",
    "spake", "offereth", "apron", "aprons", "committeth", "meddleth", "ministry",
    "saith", "shew", "cometh", "blacker",
}


def load57():
    spec = importlib.util.spec_from_file_location(
        "round4_preview", ROOT / "scripts" / "57_round4_preview.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_pre_round4(con):
    """current text per verse = base + highest-id approved restoration, but
    EXCLUDING this migration's own round4_review rows. Without this exclusion a
    re-run reads the round-4 text back in, sees final==current, changes nothing,
    then the DELETE wipes the rows (same idempotency trap as scripts/55)."""
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL AND flaw_type != ? ORDER BY id", (FLAW,)):
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


def keep_words():
    """Words whose owner ruling is KEEP WHITE LIST (protect, no text change)."""
    out, cur = set(), None
    for ln in REVIEW.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^#### <a name="[^"]+"></a>(.+?) — \d+ uses$', ln)
        if m:
            cur = m.group(1)
        elif cur and ln.startswith("- owner ruling:"):
            if "keep white list" in ln.lower():
                out.add(cur.lower())
            cur = None
    return out


def main():
    m57 = load57()
    con = sqlite3.connect(DB)
    cur, base = load_pre_round4(con)

    def round4_text(ref):
        if ref in m57.EDITS:
            kind, payload, _ = m57.EDITS[ref]
            if kind == "revert":
                return base[ref]
            if kind == "set":
                return payload
            t, _ = m57.apply_ops(cur[ref], payload)
            return t
        t = cur[ref]
        if "gpron" in t.lower():
            for tok, repl in m57.GPRON_SCAN.items():
                t = m57.wb(tok).sub(repl, t)
                t = m57.wb(tok.capitalize()).sub(repl.capitalize(), t)
        return t

    def girded(t):
        t = m57.wb("girded").sub("adorned", t)
        t = m57.wb("Girded").sub("Adorned", t)
        return t

    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    vidmap = {(names[bid], ch, vs): vid for vid, bid, ch, vs in con.execute(
        "SELECT id, book_id, chapter, verse FROM verses WHERE translation='KJV'")}

    changed = []          # (ref, was_current, final)
    for ref, was in cur.items():
        final = girded(round4_text(ref))
        if final.strip() != was.strip():
            changed.append((ref, was, final))

    # ---- write DB (idempotent) ---------------------------------------------
    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for ref, was, final in changed:
        vid = vidmap[ref]
        is_revert = m57.EDITS.get(ref, (None,))[0] == "revert"
        rationale = ("Round-4 re-review (owner-approved 2026-07-21; "
                     "references/rare_word_round4_restoration_review.md + "
                     "rare_word_round4_apply_preview.md); global girded->adorned. "
                     + ("Reverted to base KJV reading." if is_revert else
                        "Merged onto current text."))
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, FLAW, was, final, rationale,
             "Round-4 owner per-word rulings.", 0.9, "approved"))
    con.commit()

    # ---- derive blacklist (removed) / whitelist (added) per verse ----------
    bl_entries = []       # (old, new, ref_str)
    added_words = set()
    seen = set()
    for ref, was, final in changed:
        b, c, v = ref
        refstr = f"{b} {c}:{v}"
        sm = difflib.SequenceMatcher(a=was.split(), b=final.split(), autojunk=False)
        bj, fj = was.split(), final.split()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ("replace", "insert"):
                for x in fj[j1:j2]:
                    w = re.sub(r"[^A-Za-z']", "", x).lower()
                    if w and w not in STOP:
                        added_words.add(w)
            if tag == "replace":
                cleaned = [re.sub(r"^[^A-Za-z']+|[^A-Za-z']+$", "", x) for x in fj[j1:j2]]
                cleaned = [c2 for c2 in cleaned if c2]
                while cleaned and cleaned[0].lower() in ("a", "an", "the"):
                    cleaned = cleaned[1:]
                new_phrase = " ".join(cleaned) or "(deleted)"
                for ox in bj[i1:i2]:
                    o = re.sub(r"[^A-Za-z']", "", ox).lower()
                    if o and o not in STOP and (o, new_phrase, refstr) not in seen:
                        seen.add((o, new_phrase, refstr))
                        bl_entries.append((o, new_phrase, refstr))

    # ---- blacklist source (builder 49 round4() reads this) -----------------
    bl_entries.sort(key=lambda e: (e[0], e[2]))
    src = ["# Rare Word Replacements — Round 4 (owner-ruled)", "",
           "*Round-4 re-review rulings + global girded->adorned "
           "(owner-approved 2026-07-21). Removed word -> new reading, per verse. "
           "Read by `scripts/49_build_blacklist.py` (round4()) and folded into "
           "`word_blacklist.md`.*", ""]
    for old, new, refstr in bl_entries:
        src += [f"## {old} → {new} — {refstr}",
                "- source: round-4 owner ruling 2026-07-21", ""]
    BL_SRC.write_text("\n".join(src) + "\n", encoding="utf-8")

    # ---- whitelist source: rewrite the round-4 section of NSS ---------------
    wl_words = sorted((keep_words() | added_words | EXTRA_WHITELIST)
                      - {e[0] for e in bl_entries})
    blk = [NSS_MARK, "",
           "*Words protected after the round-4 re-review (owner ruled "
           "2026-07-21): KEEP-white-list words, newly introduced readings, and "
           "the owner's explicit additions. Rewritten in full on each run of "
           "scripts/58_apply_round4.py.*", ""]
    for w in wl_words:
        blk += [f"## {w} → NO-SAFE-SWAP — round-4",
                "- verdict: NO-SAFE-SWAP",
                "- rationale: Round-4 owner ruling — keep + whitelist.",
                "- **OWNER RULING 2026-07-21: DO NOT CHANGE — round-4 review.**",
                "- NEW: (no change — round-4 protected word)", ""]
    text = NSS.read_text(encoding="utf-8")
    idx = text.find(NSS_MARK)
    if idx != -1:
        text = text[:idx].rstrip("\n") + "\n\n"
    else:
        text = text.rstrip("\n") + "\n\n"
    NSS.write_text(text + "\n".join(blk) + "\n", encoding="utf-8")

    con.close()
    print(f"round4_review restorations: {len(changed)} verses "
          f"(incl. girded->adorned).")
    print(f"blacklist source: {len(bl_entries)} entries "
          f"({len({e[0] for e in bl_entries})} distinct removed words).")
    print(f"whitelist source: {len(wl_words)} protected words "
          f"(KEEP + introduced + extras).")
    print("Now run: python3 scripts/49_build_blacklist.py && "
          "python3 scripts/29_build_whitelist.py && python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
