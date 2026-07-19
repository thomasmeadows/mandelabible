#!/usr/bin/env python3
"""42_apply_round2.py — apply the owner-approved round-2 rare-word results
(owner directive 2026-07-18: "replacements and safe words seem to be
accurate. Fold the no-safe-words into the whitelist and update the
replacement verses.").

1. Whitelist fold: every word in
   references/rare_word_witness_batches_2/round2_whitelist_and_no_safe_swap.md
   (both WHITELIST and NO-SAFE-SWAP verdicts) is appended to
   references/word_whitelist.md as a new "Round-2 reviewed words" section,
   with per-word reasons (the agent's whitelist-case argument where given,
   else its rationale). Nothing existing in the whitelist is removed.

2. Replacement verses: every REPLACE entry in round2_ai_suggestions.md is
   applied as a restoration (flaw_type `rare_word_swap2`, approved —
   highest-id row wins in script 17's composition, so prior rows are
   superseded, never deleted). Round-2 NEW texts were written against the
   CUR (composed restored) text, so spans are diffed against that same
   base; multi-entry verses span-merge onto one evolving text, and
   overlapping spans with differing text are NOT applied — they go to
   references/rare_word_witness_batches_2/round2_merge_conflicts.md.

Idempotent: rare_word_swap2 rows are rebuilt each run; the whitelist
section is replaced in place if it already exists (never shrinking the
word list — generated-artifact guard).
"""
import difflib
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH_DIR = ROOT / "references" / "rare_word_witness_batches_2"
SRC_AI = BATCH_DIR / "round2_ai_suggestions.md"
SRC_WL = BATCH_DIR / "round2_whitelist_and_no_safe_swap.md"
WHITELIST = ROOT / "references" / "word_whitelist.md"
CONFLICTS = BATCH_DIR / "round2_merge_conflicts.md"
DB_PATH = ROOT / "db" / "mandela.db"

SECTION_HEAD = "### Round-2 reviewed words"
# Header variants: "## word → repl — Book C:V", "## word — Book C:V",
# optional trailing parenthetical note (e.g. "(DATA ANOMALY ...)").
HEADER_RE = re.compile(
    r"^## (.+?)(?: → (.*?))? — (.+?) (\d+):(\d+)(?:\s*\((.*)\))?\s*$")
BOOK_ALIASES = {"Revelation": "Revelation of John"}

STANDARD_NOTE = (
    "The word was replaced because it was unlikely to be both accurate for "
    "use during the period and because it was rarely used in the Bible, "
    "appearing only 1-2 times. The human who made this decision believes the "
    "word being replaced is accurate, but the replacement word has been "
    "selected by human, AI, or taste and is believed to be more likely "
    "correct for the period. Other translations have been considered, along "
    "with memories from before the Mandela effect. If you have a better "
    "replacement recommendation, create a GitHub issue with your sources: "
    "https://github.com/thomasmeadows/mandelabible/issues/new — be sure to "
    "search first to confirm your replacement appears in the KJV more than "
    "1-2 times."
)


def parse_entries(path):
    """[{word, repl, ref:(book,ch,vs), verdict, rationale, whitelist_case,
        new}] in file order."""
    entries, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEADER_RE.match(line)
        if m:
            book = BOOK_ALIASES.get(m.group(3).strip(), m.group(3).strip())
            cur = {"word": m.group(1).strip().lower(),
                   "repl": (m.group(2) or "").strip(),
                   "ref": (book, int(m.group(4)), int(m.group(5))),
                   "note": (m.group(6) or "").strip(),
                   "verdict": "", "rationale": "", "whitelist_case": "",
                   "new": ""}
            entries.append(cur)
        elif cur is not None:
            for field, key in (("- verdict:", "verdict"),
                               ("- rationale:", "rationale"),
                               ("- whitelist-case:", "whitelist_case"),
                               ("- NEW:", "new")):
                if line.startswith(field):
                    cur[key] = line[len(field):].strip()
    return entries


def slug(word):
    return re.sub(r"[^a-z0-9-]", "-", word)


def fold_whitelist():
    entries = [e for e in parse_entries(SRC_WL)
               if e["verdict"] in ("WHITELIST", "NO-SAFE-SWAP")
               and "DATA ANOMALY" not in e["note"]]
    reasons = defaultdict(list)
    for e in entries:
        reason = e["whitelist_case"] or e["rationale"]
        ref = f"{e['ref'][0]} {e['ref'][1]}:{e['ref'][2]}"
        reasons[e["word"]].append(f"- {ref} ({e['verdict']}): {reason}")
    words = sorted(reasons)

    text = WHITELIST.read_text(encoding="utf-8")
    if SECTION_HEAD in text:
        existing = len(re.findall(r"\[([a-z0-9'’–-]+)\]\(#round2-",
                                  text))
        if existing > len(words):
            raise SystemExit("REFUSING: existing round-2 section has more "
                             "words than the new fold")
        text = re.sub(
            re.escape(SECTION_HEAD) + r".*?(?=\n## |\Z)", "", text,
            flags=re.S)

    links = ", ".join(f"[{w}](#round2-{slug(w)})" for w in words)
    section = [
        "", SECTION_HEAD + f" ({len(words)})", "",
        "*Folded by `scripts/42_apply_round2.py` from the owner-approved "
        "`rare_word_witness_batches_2/round2_whitelist_and_no_safe_swap.md` "
        "(owner directive 2026-07-18). Includes both WHITELIST and "
        "NO-SAFE-SWAP verdicts; whitelist arguments do not rest on the KJV "
        "self-certifying.*", "",
        links, "",
    ]
    for w in words:
        section.append(f'#### <a name="round2-{slug(w)}"></a>{w}')
        section.extend(reasons[w])
        section.append("")
    WHITELIST.write_text(text.rstrip("\n") + "\n" + "\n".join(section) + "\n",
                         encoding="utf-8")
    print(f"whitelist: folded {len(words)} round-2 words "
          f"({sum(len(v) for v in reasons.values())} verse reasons)")
    return words


def spans(old, new):
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    return [(i1, i2, new[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes()
            if tag != "equal"]


def apply_replacements():
    con = sqlite3.connect(DB_PATH)
    books = dict(con.execute(
        "SELECT name, id FROM books WHERE translation='KJV'"))

    # Compose the current restored text (rows other than our own, so a
    # re-run diffs against the same base it was written for).
    base, vids, originals = {}, {}, {}
    for vid, book_id, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        vids[(book_id, ch, vs)] = vid
        originals[vid] = text
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type!='rare_word_swap2' ORDER BY id"):
        base[vid] = t

    by_verse = defaultdict(list)
    for e in parse_entries(SRC_AI):
        if e["verdict"] == "REPLACE" and e["new"]:
            by_verse[e["ref"]].append(e)

    con.execute("DELETE FROM restorations WHERE flaw_type='rare_word_swap2'")
    applied, conflicts, missing = 0, [], []
    for ref, sugg in sorted(by_verse.items()):
        book, ch, vs = ref
        vid = vids.get((books.get(book), ch, vs))
        if vid is None:
            missing.append(ref)
            continue
        cur_text = base.get(vid, originals[vid])
        all_ops = []
        for e in sugg:
            for op in spans(cur_text, e["new"]):
                all_ops.append(op + (e["word"],))
        all_ops.sort()
        ops, bad = [], False
        for op in all_ops:
            if ops and op[0] < ops[-1][1]:
                if (op[0], op[1], op[2]) != ops[-1][:3]:
                    bad = True
                    break
                continue
            if ops and op[:3] == ops[-1][:3]:
                continue
            ops.append(op)
        if bad:
            conflicts.append((ref, sugg))
            continue
        merged = cur_text
        for i1, i2, repl, _ in sorted(ops, reverse=True):
            merged = merged[:i1] + repl + merged[i2:]
        footnotes = "; ".join(
            f"{e['word']} -> {e['repl']}: {e['rationale']}" for e in sugg)
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "rare_word_swap2", cur_text, merged, footnotes,
             STANDARD_NOTE, 0.7, "approved"))
        applied += 1

    # Repair-by-supersession (scripts 37/38 pattern): defective round-1
    # artifacts baked into verse text, kept but superseded, never deleted:
    #   - Acts 19:9: stray "(unchanged) " prefix (batch artifact);
    #   - John 11:16: the rare-word swap deleted "fellow" out of the TSBC
    #     reading "fellow-disciples", leaving a dangling "his -disciples"
    #     (found 2026-07-19 by the residue proposal pass; the residue scan
    #     independently corroborates "fellow disciples").
    def repair(t):
        return (t.removeprefix("(unchanged) ")
                .replace("unto his -disciples", "unto his fellow-disciples"))

    for vid in [v for v, t in base.items() if t != repair(t)]:
        fixed = repair(base[vid])
        con.execute(
            "INSERT INTO restorations (verse_id, flaw_type, current_text, "
            "proposed_text, rationale, evidence, confidence, status) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (vid, "rare_word_swap2", base[vid], fixed,
             "Mechanical artifact repair (round-1 defects, superseded not "
             "deleted): stray '(unchanged) ' prefix stripped / dangling "
             "'his -disciples' restored to the TSBC reading "
             "'fellow-disciples'; wording otherwise untouched.",
             STANDARD_NOTE, 0.95, "approved"))
        applied += 1
        print(f"artifact repair: verse_id {vid}")
    con.commit()
    con.close()

    if conflicts:
        out = ["# Round-2 merge conflicts (owner resolution needed)", "",
               "*Generated by `scripts/42_apply_round2.py`.* Overlapping "
               "spans with differing text — no change applied.", ""]
        for ref, sugg in conflicts:
            out.append(f"## {ref[0]} {ref[1]}:{ref[2]}")
            for e in sugg:
                out += [f"- {e['word']} → {e['repl']}",
                        f"  - NEW: {e['new']}"]
            out.append("")
        CONFLICTS.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"replacements: {applied} verse restorations applied "
          f"(flaw_type rare_word_swap2); {len(conflicts)} conflicts -> "
          f"{CONFLICTS.name if conflicts else 'none'}; "
          f"{len(missing)} refs not found: {missing[:5]}")


def main():
    fold_whitelist()
    apply_replacements()


if __name__ == "__main__":
    main()
