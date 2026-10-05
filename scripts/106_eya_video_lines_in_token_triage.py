#!/usr/bin/env python3
"""106_eya_video_lines_in_token_triage.py — mark the token-triage groups whose
words the EYA Censored video speakers say they do not remember (owner request
2026-10-04), with the remembered earlier reading as a suggested replacement
where one was stated.

The words come from script 105's curated lists (read from all 64 video
transcripts): WITH_PRIOR and NAMES (a remembered reading was stated),
APPENDIX (the study-Bible appendix read in one video; its modern equivalent is
the suggestion) and NO_PRIOR (not remembered, no earlier reading given).
Phrases are skipped; only single-word forms are matched, case-insensitively,
against each `### word — N uses` group's forms in
references/word_lists/token_triage_summary_r2.md (headword plus its forms in
token_list_full.md, as script 101 does).

On a match the group's EYA_SUGGESTION line gains a suffix
    (EYA videos — not remembered: "word" at Verse — suggested replacement: X; …)
If the group has no EYA_SUGGESTION line yet (script 101 adds one only for
EYA-index words), one is inserted directly above `- **OWNER RULING:**`:
    - **EYA_SUGGESTION:** Kat does not remember this (EYA videos — …)

Nothing existing is removed or reworded. Idempotent: a line that already
carries "EYA videos" is left alone.
"""
import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIAGE = ROOT / "references" / "word_lists" / "token_triage_summary_r2.md"
TOKENS = ROOT / "references" / "word_lists" / "token_list_full.md"

sys.path.insert(0, str(ROOT / "scripts"))
videos = importlib.import_module("105_eya_transcript_unremembered_words")

ROW = re.compile(r"^\| \d+ \| (\S+) \| (\d+) \| (.*?) \|")   # as script 93
FORM = re.compile(r"(\S+) \(×\d+\)")
GROUP = re.compile(r"^### (\S+) — \d+ uses")
LABEL = "- **EYA_SUGGESTION:**"
TEXT = "Kat does not remember this"
MARK = "EYA videos"
WORD = re.compile(r"[a-z]+")


def suggestions():
    """form -> suggestion fragments, in list order (remembered readings first)."""
    out = {}

    def add(term, frag):
        for form in term.lower().split("/"):
            form = form.strip()
            if WORD.fullmatch(form):
                frags = out.setdefault(form, [])
                if frag not in frags:
                    frags.append(frag)

    def where(verses):
        return f" at {verses}" if verses else ""

    for word, verses, prior, _src, _note in videos.WITH_PRIOR:
        if prior.startswith("—"):
            add(word, f'"{word}"{where(verses)} (no earlier reading given)')
        else:
            add(word, f'"{word}"{where(verses)} — suggested replacement: {prior}')
    for word, verses, prior, _src in videos.NAMES:
        if not prior.startswith("—"):
            add(word, f'"{word}"{where(verses)} — suggested replacement: {prior}')
    for word, prior in videos.APPENDIX:
        add(word, f'"{word}" (study-Bible appendix) — suggested replacement: {prior}')
    for _theme, word, verses, _src in videos.NO_PRIOR:
        add(word, f'"{word}"{where(verses)} (no earlier reading given)')
    return out


def main():
    groups = {}
    for line in TOKENS.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            groups[m.group(1).lower()] = (
                {f.lower() for f in FORM.findall(m.group(3))} | {m.group(1).lower()})
    sugg = suggestions()

    lines = TRIAGE.read_text(encoding="utf-8").splitlines(keepends=True)
    out, head, eya_at = [], None, None
    added = extended = skipped = 0
    for line in lines:
        m = GROUP.match(line)
        if m:
            head, eya_at = m.group(1).lower(), None
        elif line.startswith(LABEL) and head:
            eya_at = len(out)
        elif line.startswith("- **OWNER RULING") and head:
            frags = []
            for form in sorted(groups.get(head, {head})):
                for f in sugg.get(form, []):
                    if f not in frags:
                        frags.append(f)
            if frags:
                suffix = f" ({MARK} — not remembered: {'; '.join(frags)})"
                if eya_at is None:
                    out.append(f"{LABEL} {TEXT}{suffix}\n")
                    added += 1
                elif MARK in out[eya_at]:
                    skipped += 1
                else:
                    out[eya_at] = out[eya_at].rstrip("\n") + suffix + "\n"
                    extended += 1
            head = None
        out.append(line)

    if added or extended:
        TRIAGE.write_text("".join(out), encoding="utf-8")
    print(f"{TRIAGE.relative_to(ROOT)}: {added} EYA lines added, "
          f"{extended} existing EYA lines extended, {skipped} already marked")


if __name__ == "__main__":
    main()
