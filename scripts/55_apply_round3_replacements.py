#!/usr/bin/env python3
"""55_apply_round3_replacements.py — apply the owner-approved round-3 word
replacements (owner directive 2026-07-21).

Source of truth: references/rare_word_round3_replace_preview.md, which the owner
reviewed and edited (context choices, article fixes, deletions). This migration
reads the final ("now:" / context) text for every verse, MERGES verses that
receive more than one change onto the current post-fix base, applies the one
outstanding article fix (Deut 14:21 "an stranger" -> "a stranger"), and writes
each as an owner-approved restoration.

Merge semantics (owner directive): each verse merges with whatever already
exists. The preview's base text is the current post-fix text (base KJV + all
approved restorations), so each final text already incorporates prior changes;
the new restoration (highest id) supersedes and therefore contains everything.

Idempotent: all round-3 rows (flaw_type='rare_word_swap3') are deleted and
re-inserted on each run. Emits references/rare_word_round3_applied.md (durable
record) and a machine map for the blacklist/whitelist step (script 56).

After running:  python3 scripts/17_export_full.py
"""
import sqlite3, re, difflib, json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
PREVIEW = ROOT / "references" / "rare_word_round3_replace_preview.md"
RECORD = ROOT / "references" / "rare_word_round3_applied.md"
MAPOUT = ROOT / "scripts" / "__pycache__" / "round3_replacement_map.json"
ARTICLE_FIX = {"Deuteronomy 14:21": ("an stranger", "a stranger")}
FLAW = "rare_word_swap3"


def load_base(con):
    resto = {}
    # exclude this migration's own rows so the base is the pre-round-3 post-fix
    # text — otherwise a re-run reads round-3 back in, sees final==base, and
    # skips everything (then the DELETE wipes the rows). Keeps it idempotent.
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL AND flaw_type != 'rare_word_swap3' ORDER BY id"):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    base, vidmap = {}, {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        key = (names[bid], ch, vs)
        base[key] = resto.get(vid, text)
        vidmap[key] = vid
    return base, vidmap


def parse_ref(s):
    m = re.match(r"^(.*)\s+(\d+):(\d+)$", s.strip())
    return (m.group(1), int(m.group(2)), int(m.group(3)))


def parse_preview():
    doc = PREVIEW.read_text(encoding="utf-8").split("\n")
    sections = defaultdict(list)
    word = None
    i = 0
    while i < len(doc):
        ln = doc[i]
        m = re.match(r"^## (.+?) — ", ln)
        if m:
            word = m.group(1).strip(); i += 1; continue
        md = re.match(r"^- \*\*(.+?)\*\*\s*$", ln)
        if md and word:
            now = None
            for j in range(i + 1, min(i + 4, len(doc))):
                mn = re.match(r"^\s*- now: (.*)$", doc[j])
                if mn:
                    now = mn.group(1); break
            if now is not None:
                sections[word].append((md.group(1), now)); i += 1; continue
        mc = re.match(r"^- \*\*(.+?)\*\*\s*—\s*(.*)$", ln)
        if mc and word:
            sections[word].append((mc.group(1), mc.group(2).replace("**", "").strip()))
        i += 1
    return sections


def merge(base_text, finals):
    """Apply the (non-equal) word-opcodes of every final onto base_text."""
    b = base_text.split()
    ops = []
    for final in finals:
        sm = difflib.SequenceMatcher(a=b, b=final.split(), autojunk=False)
        fj = final.split()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                ops.append((i1, i2, fj[j1:j2]))
    merged = list(b)
    for i1, i2, rep in sorted(ops, reverse=True):
        merged[i1:i2] = rep
    return " ".join(merged)


def main():
    con = sqlite3.connect(DB)
    base, vidmap = load_base(con)
    sections = parse_preview()

    byverse = defaultdict(list)
    for w, items in sections.items():
        for ref, final in items:
            byverse[ref].append((w, final))

    applied = []          # (ref, base, final, [words])
    repl_map = defaultdict(set)   # old_word -> {new_word}
    for ref, changes in byverse.items():
        key = parse_ref(ref)
        b = base.get(key)
        if b is None:
            print(f"  !! base not found for {ref} — skipped"); continue
        finals = [f for _, f in changes]
        # article fix
        if ref in ARTICLE_FIX:
            old, new = ARTICLE_FIX[ref]
            finals = [f.replace(old, new) for f in finals]
        final = merge(b, finals) if len(finals) > 1 else finals[0]
        if final.strip() == b.strip():
            continue  # owner kept it unchanged
        applied.append((ref, b, final, [w for w, _ in changes]))
        # derive old->new word pairs for blacklist/whitelist
        sm = difflib.SequenceMatcher(a=b.split(), b=final.split(), autojunk=False)
        bj, fj = b.split(), final.split()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "replace":
                for ow in bj[i1:i2]:
                    ow_c = re.sub(r"[^A-Za-z']", "", ow).lower()
                    news = [re.sub(r"[^A-Za-z']", "", x).lower() for x in fj[j1:j2]]
                    if ow_c:
                        repl_map[ow_c].update(n for n in news if n)

    # write DB
    con.execute("DELETE FROM restorations WHERE flaw_type=?", (FLAW,))
    for ref, b, final, words in applied:
        vid = vidmap[parse_ref(ref)]
        rationale = (f"Round-3 rare-word replacement ({', '.join(sorted(set(words)))}): "
                     f"owner-approved 2026-07-21 (references/rare_word_round3_review.md; "
                     f"edits in rare_word_round3_replace_preview.md). Merged onto current text.")
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, proposed_text, "
            "rationale, evidence, confidence, status) VALUES (?,?,?,?,?,?,?,?)",
            (vid, FLAW, b, final, rationale,
             "Round-3 review; owner per-verse rulings.", 0.9, "approved"))
    con.commit()

    # durable record
    rec = ["# Round-3 Replacements — applied", "",
           f"*{len(applied)} verses changed, owner-approved 2026-07-21. Applied as "
           f"restorations (flaw_type '{FLAW}') by scripts/55_apply_round3_replacements.py "
           "from the owner-edited rare_word_round3_replace_preview.md. Merged onto the "
           "current post-fix text.*", ""]
    for ref, b, final, words in sorted(applied, key=lambda x: x[0]):
        rec += [f"## {ref}  [{', '.join(sorted(set(words)))}]",
                f"- was: {b}", f"- now: {final}", ""]
    RECORD.write_text("\n".join(rec) + "\n", encoding="utf-8")

    MAPOUT.parent.mkdir(exist_ok=True)
    MAPOUT.write_text(json.dumps({k: sorted(v) for k, v in repl_map.items()},
                                 ensure_ascii=False, indent=0), encoding="utf-8")
    con.close()
    print(f"applied {len(applied)} verse restorations (flaw_type={FLAW})")
    print(f"record: {RECORD.relative_to(ROOT)}")
    print(f"old->new word pairs: {len(repl_map)} (for script 56)")
    print("Now run: python3 scripts/17_export_full.py")


if __name__ == "__main__":
    main()
