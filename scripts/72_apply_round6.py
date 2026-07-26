#!/usr/bin/env python3
"""72_apply_round6.py — APPLY the round-6 rare-word rulings (owner rulings
2026-07-26 in references/rare_word_round6_review.md; final wording taken
directly from the owner-edited references/rare_word_round6_apply_preview.md,
which the owner hand-corrected after scripts/71_round6_preview.py generated
it — several entries differ from a literal application of the review-file
ruling, e.g. Genesis 40:20 also swaps "chief" -> "head", I Kings 21:7 fixes
"arise" -> "Arise", I Samuel 30:31 rewords "were wont to haunt" -> "were to
dwell" rather than the literal "were wont to dwell"; the preview file's
"now" text is authoritative, not a re-derivation).

Layers touched (same as the round-5 apply, scripts/66):
  1. db/mandela.db — every changed verse becomes a superseding, owner-approved
     restoration (flaw_type='round6_review'). Idempotent: round6_review rows
     are deleted and re-inserted each run, and the current-text loader
     EXCLUDES this script's own flaw_type (else a re-run reads its own output
     back in, sees no change, and the DELETE wipes the rows — the scripts/55
     trap).
  2. references/rare_word_round6_replacements.md — blacklist source (removed
     word -> new reading, per verse) read by scripts/49_build_blacklist.py
     round6().
  3. references/rare_word_review_no_safe_swap.md — whitelist source; a
     round-6 section (after the round-5 one) is rewritten in full each run:
     WHITELIST-ruled keep words from the review file, plus newly introduced
     readings from the applied edits.

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
REVIEW = ROOT / "references" / "rare_word_round6_review.md"
PREVIEW = ROOT / "references" / "rare_word_round6_apply_preview.md"
BL_SRC = ROOT / "references" / "rare_word_round6_replacements.md"
NSS = ROOT / "references" / "rare_word_review_no_safe_swap.md"
NSS_MARK = "# Round-6 review words (2026-07-26)"
FLAW = "round6_review"

STOP = set("a an and the that this those these i thou he she it we ye you they me him "
           "her us them my thy his its our your their of to in on for with by at from "
           "unto into upon as is are was were be been am art shall will not no nor but "
           "or so if then than there here when why how which who whom whose what do "
           "doth did done have hath had haue also out up down over all any some more "
           "most let may can could would should o oh yea verily said he".split())

REF_HDR = re.compile(r"^## (.+?) (\d+):(\d+)\s*$")


def load_pre_round6(con):
    """current text per verse = base + highest-id approved restoration,
    EXCLUDING this migration's own round6_review rows (idempotency)."""
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
    """Parse the owner-edited apply-preview file: for each '## Book C:V'
    block, pull the 'was' and 'now' lines. The preview's 'now' text is
    authoritative (owner hand-edits included)."""
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


def keep_words():
    """Words whose owner ruling in the review file opens with WHITELIST
    (keep, no text change)."""
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
    con = sqlite3.connect(DB)
    cur = load_pre_round6(con)
    preview = parse_preview()

    changed, missing = [], []
    for ref, (was_preview, now) in preview.items():
        if ref not in cur:
            missing.append((ref, "verse not found in DB"))
            continue
        was_actual = cur[ref]
        if was_actual.strip() != was_preview.strip():
            missing.append((ref, "current DB text no longer matches preview 'was'"))
            continue
        if now.strip() != was_actual.strip():
            changed.append((ref, was_actual, now))
    if missing:
        raise SystemExit(f"REFUSING: {len(missing)} problem(s): {missing}")

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
             "Round-6 rare-word review (owner-ruled 2026-07-26; "
             "references/rare_word_round6_review.md, final wording per the "
             "owner-edited rare_word_round6_apply_preview.md). "
             "Merged onto current text.",
             "Round-6 owner per-word rulings.", 0.9, "approved"))
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

    # ---- blacklist source (builder 49 round6() reads this) -----------------
    bl_entries.sort(key=lambda e: (e[0], e[2]))
    src = ["# Rare Word Replacements — Round 6 (owner-ruled)", "",
           "*Round-6 rare-word review rulings (owner 2026-07-26). Removed word "
           "-> new reading, per verse. Read by `scripts/49_build_blacklist.py` "
           "(round6()) and folded into `word_blacklist.md`.*", ""]
    for old, new, refstr in bl_entries:
        src += [f"## {old} → {new} — {refstr}",
                "- source: round-6 owner ruling 2026-07-26", ""]
    BL_SRC.write_text("\n".join(src) + "\n", encoding="utf-8")

    # ---- whitelist source: rewrite the round-6 section of NSS ---------------
    wl_words = sorted((keep_words() | added_words)
                      - {e[0] for e in bl_entries})
    blk = [NSS_MARK, "",
           "*Words protected after the round-6 rare-word review (owner ruled "
           "2026-07-26): WHITELIST-keep words and newly introduced readings. "
           "Rewritten in full on each run of scripts/72_apply_round6.py.*", ""]
    for w in wl_words:
        blk += [f"## {w} → NO-SAFE-SWAP — round-6",
                "- verdict: NO-SAFE-SWAP",
                "- rationale: Round-6 owner ruling — keep + whitelist.",
                "- **OWNER RULING 2026-07-26: DO NOT CHANGE — round-6 review.**",
                "- NEW: (no change — round-6 protected word)", ""]
    text = NSS.read_text(encoding="utf-8")
    idx = text.find(NSS_MARK)
    if idx != -1:
        text = text[:idx].rstrip("\n") + "\n\n"
    else:
        text = text.rstrip("\n") + "\n\n"
    NSS.write_text(text + "\n".join(blk) + "\n", encoding="utf-8")

    con.close()
    print(f"round6_review restorations: {len(changed)} verses.")
    print(f"blacklist source: {len(bl_entries)} entries "
          f"({len({e[0] for e in bl_entries})} distinct removed words).")
    print(f"whitelist source: {len(wl_words)} protected words "
          f"(WHITELIST-keeps + introduced).")
    print("Now run: python3 scripts/49_build_blacklist.py && "
          "python3 scripts/29_build_whitelist.py && python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
