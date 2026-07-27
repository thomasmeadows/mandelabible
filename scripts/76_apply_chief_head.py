#!/usr/bin/env python3
"""76_apply_chief_head.py — APPLY the chief/chiefest word review rulings
(owner rulings 2026-07-26 in references/word_reviews/word_review_chief_head.md; final
wording taken directly from the owner-edited
references/word_reviews/word_review_chief_head_apply_preview.md — the owner hand-
corrected the 3 flagged verses directly in the preview, same pattern as
scripts/72_apply_round6.py: the preview file's "now" text is authoritative,
not a re-derivation).

Layers touched (same as the round-6 apply, scripts/72):
  1. db/mandela.db — every changed verse becomes a superseding, owner-approved
     restoration (flaw_type='chief_head_review'). Idempotent: this script's
     own rows are deleted and re-inserted each run, and the current-text
     loader EXCLUDES this script's own flaw_type (the scripts/55 trap).
  2. references/word_reviews/chief_head_replacements.md — blacklist source (removed word
     -> new reading, per verse) read by scripts/49_build_blacklist.py
     chief_head().
  3. references/word_lists/rare_word_review_no_safe_swap.md — whitelist source; not
     used here (all 277 rulings were swap/override/delete, none WHITELIST).

After running:
    python3 scripts/49_build_blacklist.py
    python3 scripts/29_build_whitelist.py
    python3 scripts/17_export_full.py
"""
import difflib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
PREVIEW = ROOT / "references" / "word_reviews" / "word_review_chief_head_apply_preview.md"
BL_SRC = ROOT / "references" / "word_reviews" / "chief_head_replacements.md"
FLAW = "chief_head_review"

STOP = set("a an and the that this those these i thou he she it we ye you they me him "
           "her us them my thy his its our your their of to in on for with by at from "
           "unto into upon as is are was were be been am art shall will not no nor but "
           "or so if then than there here when why how which who whom whose what do "
           "doth did done have hath had haue also out up down over all any some more "
           "most let may can could would should o oh yea verily said he".split())

REF_HDR = re.compile(r"^## (.+?) (\d+):(\d+)\s*$")


def load_pre_chief_head(con):
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


def parse_preview():
    entries = {}
    ref = was = now = None

    def commit():
        if ref is not None and now is not None:
            entries[ref] = (was, now)

    for ln in PREVIEW.read_text(encoding="utf-8").splitlines():
        m = REF_HDR.match(ln)
        if m:
            commit()
            ref, was, now = (m.group(1), int(m.group(2)), int(m.group(3))), None, None
        elif ln.startswith("- was:"):
            was = ln[len("- was:"):].strip()
        elif ln.startswith("- now:"):
            now = ln[len("- now:"):].strip()
    commit()
    return entries


def main():
    con = sqlite3.connect(DB)
    cur = load_pre_chief_head(con)
    preview = parse_preview()

    changed, missing = [], []
    for ref, (was_preview, now) in preview.items():
        if ref not in cur:
            missing.append((ref, "verse not found in DB"))
            continue
        was_actual = cur[ref]
        if was_actual.strip() == was_preview.strip():
            if now.strip() != was_actual.strip():
                changed.append((ref, was_actual, now))
            continue
        # DB text has moved on since the preview was generated (e.g. the
        # scripts/75 pronoun-swap pass ran after this preview) — re-derive
        # the chief-specific edit from (was_preview -> now) and replay it
        # onto the actual current text, rather than clobbering unrelated
        # downstream edits with the stale preview text.
        sm = difflib.SequenceMatcher(a=was_preview, b=now, autojunk=False)
        ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
        if not ops:
            continue
        i1, i2 = ops[0][1], ops[-1][2]
        j1, j2 = ops[0][3], ops[-1][4]
        old_span, new_span = was_preview[i1:i2], now[j1:j2]
        if was_actual.count(old_span) != 1:
            missing.append((ref, f"chief-edit span {old_span!r} not found "
                             f"exactly once in current DB text"))
            continue
        final = was_actual.replace(old_span, new_span)
        changed.append((ref, was_actual, final))
    if missing:
        raise SystemExit(f"REFUSING: {len(missing)} problem(s): {missing}")

    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    vidmap = {(names[bid], ch, vs): vid for vid, bid, ch, vs in con.execute(
        "SELECT id, book_id, chapter, verse FROM verses WHERE translation='KJV'")}

    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for ref, was, final in changed:
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vidmap[ref], FLAW, was, final,
             "chief/chiefest word review (owner-ruled 2026-07-26; "
             "references/word_reviews/word_review_chief_head.md, final wording per the "
             "owner-edited word_review_chief_head_apply_preview.md). "
             "Merged onto current text.",
             "Owner per-verse rulings on the chief->head review.", 0.9, "approved"))
    con.commit()

    bl_entries, seen = [], set()
    for ref, was, final in changed:
        b, c, v = ref
        refstr = f"{b} {c}:{v}"
        final_words = {re.sub(r"[^A-Za-z']", "", x).lower() for x in final.split()}
        bj, fj = was.split(), final.split()
        sm = difflib.SequenceMatcher(a=bj, b=fj, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
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
            elif tag == "delete":
                for ox in bj[i1:i2]:
                    o = re.sub(r"[^A-Za-z']", "", ox).lower()
                    if (o and o not in STOP and o not in final_words
                            and (o, "(deleted)", refstr) not in seen):
                        seen.add((o, "(deleted)", refstr))
                        bl_entries.append((o, "(deleted)", refstr))

    bl_entries.sort(key=lambda e: (e[0], e[2]))
    src = ["# chief/chiefest Word Review Replacements (owner-ruled)", "",
           "*chief/chiefest word review rulings (owner 2026-07-26). Removed "
           "word -> new reading, per verse. Read by "
           "`scripts/49_build_blacklist.py` (chief_head()) and folded into "
           "`word_blacklist.md`.*", ""]
    for old, new, refstr in bl_entries:
        src += [f"## {old} → {new} — {refstr}",
                "- source: chief/chiefest word review, owner ruling 2026-07-26", ""]
    BL_SRC.write_text("\n".join(src) + "\n", encoding="utf-8")

    con.close()
    print(f"chief_head_review restorations: {len(changed)} verses.")
    print(f"blacklist source: {len(bl_entries)} entries "
          f"({len({e[0] for e in bl_entries})} distinct removed words).")
    print("Now run: python3 scripts/49_build_blacklist.py && "
          "python3 scripts/29_build_whitelist.py && python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
