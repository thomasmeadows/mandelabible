#!/usr/bin/env python3
"""14_export_restored.py — Phase 6: export restored text per book (markdown).

Usage: python3 scripts/14_export_restored.py <BookName> [--include-proposed]

Default policy (Decision Log #8): only 'approved' restorations are applied.
--include-proposed additionally applies 'proposed' rows, each marked with a
footnote, for owner preview — the review workflow, not a final text.

Output: exports/<BookName>.md — every applied change footnoted with its
restoration id, flaw type, confidence, and status, so the export is fully
diffable and traceable (zero undocumented changes).
"""

import sys
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
EXPORT_DIR = REPO_ROOT / "exports"


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    include_proposed = "--include-proposed" in sys.argv
    if not args:
        sys.exit("usage: 14_export_restored.py <BookName> [--include-proposed]")
    book = args[0]

    con = sqlite3.connect(DB_PATH)
    try:
        statuses = ("approved", "proposed") if include_proposed else ("approved",)
        ph = ",".join("?" * len(statuses))
        resto = {}
        for vid, rid, ft, new, conf, st in con.execute(
                f"""SELECT r.verse_id, r.id, r.flaw_type, r.proposed_text,
                           r.confidence, r.status
                    FROM restorations r WHERE r.status IN ({ph})
                    AND r.proposed_text IS NOT NULL""", statuses):
            resto.setdefault(vid, []).append((rid, ft, new, conf, st))

        rows = con.execute(
            """SELECT v.id, v.chapter, v.verse, v.text FROM verses v
               JOIN books b ON b.translation='KJV' AND b.id=v.book_id
               WHERE v.translation='KJV' AND b.name=?
               ORDER BY v.chapter, v.verse""", (book,)).fetchall()
        if not rows:
            sys.exit(f"book not found: {book!r}")

        lines = [f"# {book} — Restored",
                 "",
                 f"*Exported by scripts/14_export_restored.py; statuses applied: "
                 f"{', '.join(statuses)}. Every change is footnoted; zero undocumented "
                 "changes (roadmap Phase 6).*", ""]
        notes, applied, ch_cur = [], 0, None
        for vid, ch, vs, text in rows:
            if ch != ch_cur:
                lines += [f"## Chapter {ch}", ""]
                ch_cur = ch
            out = text
            marks = ""
            for rid, ft, new, conf, st in resto.get(vid, []):
                out = new
                marks += f"[^r{rid}]"
                notes.append(
                    f"[^r{rid}]: {ch}:{vs} — {ft}, confidence {conf}, status {st}. "
                    f"Was: “{text}”")
                applied += 1
            lines.append(f"**{vs}** {out}{marks}")
        lines += [""] + notes

        EXPORT_DIR.mkdir(exist_ok=True)
        out_path = EXPORT_DIR / f"{book.replace(' ', '_')}.md"
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{out_path}: {len(rows)} verses, {applied} restoration(s) applied "
              f"({', '.join(statuses)})")
    finally:
        con.close()


if __name__ == "__main__":
    main()
