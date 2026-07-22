#!/usr/bin/env python3
"""66_apply_round5.py — APPLY the round-5 rare-word rulings (owner rulings
2026-07-22 in references/rare_word_round5_review.md, wording approved via the
owner-annotated references/rare_word_round5_apply_preview_owner_annotated.md).

Builds on scripts/65_round5_preview.py — that module holds the reviewed edit
table (EDITS) and the current-text loader; this script imports it so the
applied text is identical to the previewed text.

Layers touched (same as the round-4 apply, scripts/58):
  1. db/mandela.db — every changed verse becomes a superseding, owner-approved
     restoration (flaw_type='round5_review'). Idempotent: round5_review rows
     are deleted and re-inserted each run, and the current-text loader EXCLUDES
     this script's own flaw_type (else a re-run reads its own output back in,
     sees no change, and the DELETE wipes the rows — the scripts/55 trap).
  2. references/rare_word_round5_replacements.md — blacklist source (removed
     word -> new reading, per verse) read by scripts/49_build_blacklist.py
     round5(). Entries whose removed word still appears in the verse's final
     text (e.g. 'divisions' at Judges 5:16, moved not removed) are skipped.
  3. references/rare_word_review_no_safe_swap.md — whitelist source; the
     round-5 section (after the round-4 one) is rewritten in full each run:
     WHITELIST-ruled keep words from the review file, newly introduced
     readings, and the owner's explicitly named additions.

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
REVIEW = ROOT / "references" / "rare_word_round5_review.md"
BL_SRC = ROOT / "references" / "rare_word_round5_replacements.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
NSS_MARK = "# Round-5 review words (2026-07-22)"
FLAW = "round5_review"

STOP = set("a an and the that this those these i thou he she it we ye you they me him "
           "her us them my thy his its our your their of to in on for with by at from "
           "unto into upon as is are was were be been am art shall will not no nor but "
           "or so if then than there here when why how which who whom whose what do "
           "doth did done have hath had haue also out up down over all any some more "
           "most let may can could would should o oh yea verily said he".split())

# Owner-named whitelist words that won't necessarily surface from the diff
# (singular/inflected forms, review-file "add X to whitelist" rulings).
EXTRA_WHITELIST = {
    "glutton", "gluttonous", "gluttons", "revilings", "sneezed", "rebuketh",
    "scoffings", "musicians", "elements", "selfwill", "selfwilled",
    "pleasers", "betrayeth", "blasphemy", "swimmeth", "swimmest",
}


def load65():
    spec = importlib.util.spec_from_file_location(
        "round5_preview", ROOT / "scripts" / "65_round5_preview.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_pre_round5(con):
    """current text per verse = base + highest-id approved restoration,
    EXCLUDING this migration's own round5_review rows (idempotency)."""
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL AND flaw_type != ? ORDER BY id", (FLAW,)):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    cur = {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        cur[(names[bid], ch, vs)] = resto.get(vid, text)
    return cur


def keep_words():
    """Words whose owner ruling opens with WHITELIST (keep, no text change)."""
    out, cur = set(), None
    for ln in REVIEW.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^#### <a name="[^"]+"></a>(\S+) — \d+ uses?', ln)
        if m:
            cur = m.group(1)
        elif cur and ln.startswith("- owner ruling:"):
            if ln[len("- owner ruling:"):].strip().lower().startswith("whitelist"):
                out.add(cur.lower())
            cur = None
    return out


def main():
    m65 = load65()
    con = sqlite3.connect(DB)
    cur = load_pre_round5(con)

    changed = []          # (ref, was_current, final)
    missing = []
    for ref, (kind, payload, note) in m65.EDITS.items():
        was = cur[ref]
        if kind == "set":
            final = payload
        else:
            final = was
            for old, new in payload:
                if old not in final:
                    missing.append((ref, old))
                    continue
                final = final.replace(old, new)
        if final.strip() != was.strip():
            changed.append((ref, was, final))
    if missing:
        raise SystemExit(f"REFUSING: anchors not found: {missing}")

    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    vidmap = {(names[bid], ch, vs): vid for vid, bid, ch, vs in con.execute(
        "SELECT id, book_id, chapter, verse FROM verses WHERE translation='KJV'")}

    # ---- write DB (idempotent) ---------------------------------------------
    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for ref, was, final in changed:
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vidmap[ref], FLAW, was, final,
             "Round-5 rare-word review (owner-ruled 2026-07-22; "
             "references/rare_word_round5_review.md + owner-annotated "
             "rare_word_round5_apply_preview_owner_annotated.md). "
             "Merged onto current text.",
             "Round-5 owner per-word rulings.", 0.9, "approved"))
    con.commit()

    # ---- derive blacklist (removed) / whitelist (added) per verse ----------
    bl_entries, added_words, seen = [], set(), set()
    for ref, was, final in changed:
        b, c, v = ref
        refstr = f"{b} {c}:{v}"
        final_words = {re.sub(r"[^A-Za-z']", "", x).lower() for x in final.split()}
        bj, fj = was.split(), final.split()
        sm = difflib.SequenceMatcher(a=bj, b=fj, autojunk=False)
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
                    if (o and o not in STOP and o not in final_words
                            and (o, new_phrase, refstr) not in seen):
                        seen.add((o, new_phrase, refstr))
                        bl_entries.append((o, new_phrase, refstr))

    # ---- blacklist source (builder 49 round5() reads this) -----------------
    bl_entries.sort(key=lambda e: (e[0], e[2]))
    src = ["# Rare Word Replacements — Round 5 (owner-ruled)", "",
           "*Round-5 rare-word review rulings (owner 2026-07-22). Removed word "
           "-> new reading, per verse. Read by `scripts/49_build_blacklist.py` "
           "(round5()) and folded into `word_blacklist.md`.*", ""]
    for old, new, refstr in bl_entries:
        src += [f"## {old} → {new} — {refstr}",
                "- source: round-5 owner ruling 2026-07-22", ""]
    BL_SRC.write_text("\n".join(src) + "\n", encoding="utf-8")

    # ---- whitelist source: rewrite the round-5 section of NSS ---------------
    wl_words = sorted((keep_words() | added_words | EXTRA_WHITELIST)
                      - {e[0] for e in bl_entries})
    blk = [NSS_MARK, "",
           "*Words protected after the round-5 rare-word review (owner ruled "
           "2026-07-22): WHITELIST-keep words, newly introduced readings, and "
           "the owner's explicitly named additions. Rewritten in full on each "
           "run of scripts/66_apply_round5.py.*", ""]
    for w in wl_words:
        blk += [f"## {w} → NO-SAFE-SWAP — round-5",
                "- verdict: NO-SAFE-SWAP",
                "- rationale: Round-5 owner ruling — keep + whitelist.",
                "- **OWNER RULING 2026-07-22: DO NOT CHANGE — round-5 review.**",
                "- NEW: (no change — round-5 protected word)", ""]
    text = NSS.read_text(encoding="utf-8")
    idx = text.find(NSS_MARK)
    if idx != -1:
        text = text[:idx].rstrip("\n") + "\n\n"
    else:
        text = text.rstrip("\n") + "\n\n"
    NSS.write_text(text + "\n".join(blk) + "\n", encoding="utf-8")

    con.close()
    print(f"round5_review restorations: {len(changed)} verses.")
    print(f"blacklist source: {len(bl_entries)} entries "
          f"({len({e[0] for e in bl_entries})} distinct removed words).")
    print(f"whitelist source: {len(wl_words)} protected words "
          f"(WHITELIST-keeps + introduced + extras).")
    print("Now run: python3 scripts/49_build_blacklist.py && "
          "python3 scripts/29_build_whitelist.py && python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
