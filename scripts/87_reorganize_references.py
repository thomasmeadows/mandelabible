#!/usr/bin/env python3
"""87_reorganize_references.py — file the references/ folder into subfolders
(owner directive 2026-07-27: "Clean up references folder and place like items
in subfolders. Rounds should have their own sub folder. Update all scripts to
point to new file locations as needed.").

Idempotent: every move checks current state first, so a re-run is a no-op.
Nothing is deleted — this only moves files (git mv when the file is tracked)
and rewrites the paths that name them.

What stays at references/ root (owner ruling): roadmap.md, instructions.md,
general_references.md, sources.md, remembered_verses.md, word_whitelist.md,
word_blacklist.md — the entry points CLAUDE.md sends every agent to.

Path rewriting covers scripts/*.py, CLAUDE.md, README.md, docs/*.html and the
markdown under references/. Two forms are rewritten:
  - pathlib segments:  ROOT / "references" / "foo.md"
  - literal paths:     references/foo.md   (prose, links, code fences)
Bare filenames with no `references/` prefix are left alone — they are prose,
not paths.
"""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"

# ---------------------------------------------------------------- the mapping
# destination subfolder -> files (relative to references/)
MOVES = {
    "source_texts": [
        "2015.168333.A-Middle-English-Reader.pdf",
        "Interlinear Greek-English Septuagint Old Testament - print.pdf",
        "King James Writing Sample - The Essayes of a Prentise in the Divine "
        "Art of Poesie.txt",
        "Middle English - The Book of Quinte Essence or the Fifth Being.txt",
        "Middle English - The Canterbury Tales.txt",
        "Middle English - The Wright's Chaste Wife.txt",
        "The October Testament - Matthews Bible.pdf",
        "Understand Middle English - A middle English Reader.txt",
    ],
    "language": [
        "Inflection_English_vs_Early_Modern_English.md",
        "middle_english_to_early_modern.md",
        "colon_versus_semicolon.md",
    ],
    "rounds/round1": [
        "rare_word_replacements.md",
        "rare_word_ai_suggestions.md",
        "rare_word_alternatives.md",
        "rare_word_proposed_reconciliation.md",
        "rare_word_merge_conflicts.md",
        "rare_word_fold_back_conflicts.md",
        "rare_word_witness_batches",           # directory (228 files)
    ],
    "rounds/round2": [
        "rare_word_witness_batches_2",         # directory (23 files)
    ],
    "rounds/round3": [
        "rare_word_round3_review.md",
        "rare_word_round3_replacements.md",
        "rare_word_round3_applied.md",
        "rare_word_round3_replace_preview.md",
    ],
    "rounds/round4": [
        "rare_word_round4_review.md",
        "rare_word_round4_replacements.md",
        "rare_word_round4_apply_preview.md",
        "rare_word_round4_restoration_review.md",
    ],
    "rounds/round5": [
        "rare_word_round5_review.md",
        "rare_word_round5_replacements.md",
        "rare_word_round5_apply_preview.md",
        "rare_word_round5_apply_preview_owner_annotated.md",
        "kj_round5_suggestions_01_50.md",
        "kj_round5_suggestions_51_100.md",
    ],
    "rounds/round6": [
        "rare_word_round6_review.md",
        "rare_word_round6_replacements.md",
        "rare_word_round6_apply_preview.md",
        "kj_round6_suggestions_01_50.md",
        "kj_round6_suggestions_51_100.md",
    ],
    "rounds/round7": [
        "rare_word_round7_review.md",
        "kj_round7_suggestions_01_50.md",
        "kj_round7_suggestions_51_100.md",
    ],
    "word_lists": [
        "rare_word_review_no_safe_swap.md",
        "rare_words_restored.md",
        "token_list_full.md",
        "tokenlist_manual_whitelist.md",
        "uncleared_words.md",
        "manual_blacklist_that_should_be_whitelist.md",
        "manual_whitelist_that_should_be_blacklist.md",
        "kj_whitelist_review_remaining.md",
        "kj_whitelist_suggestions.md",
        "kj_whitelist_suggestions_batch1.md",
        "kj_whitelist_suggestions_batch2.md",
        "kj_whitelist_suggestions_batch3.md",
        "kj_whitelist_suggestions_batch4.md",
        "kj_whitelist_suggestions_batch5.md",
    ],
    "word_reviews": [                          # joins the existing .tsv batches
        "word_review_report.md",
        "word_review_chief_head.md",
        "word_review_chief_head_apply_preview.md",
        "chief_head_replacements.md",
        "global_word_swaps.md",
        "hail_review.md",
        "mixed_inflections.md",
        "anachronism_proposals.md",
        "rescan_proposals.md",
    ],
    "names": [
        "name_normalization.md",
        "name_variants.md",
    ],
    "verses": [
        "verses_famous.md",
        "verses_wheat.md",
        "verses_wheat_apply.md",
        "manual_verse_corrections.md",
        "manual_word_changes_flagged.md",
        "parenthesis_review.md",
    ],
    "residue": [
        "tsbc_residue.md",
        "tsbc_residue_placements.md",
        "residuals_ocr.md",
        "residue_verse_proposals_1.md",
        "residue_verse_proposals_2.md",
        "tsbc_residue",                        # directory (206 images)
        "residuals",                           # directory (1 image)
    ],
    "evidence": [
        "corroboration_report.md",
        "Rather Exhaustive List of Mandela Effect Affected Scriptures _ "
        "Truth Farmer.pdf",
        "kjvrestore_comparison.md",
        "kjvrestore_pages",                    # directory (81 html pages)
        "blog_search_references",              # directory (5 files)
    ],
}

# directory moves that also rename (old name -> new leaf name)
RENAME = {
    "rare_word_witness_batches": "witness_batches",
    "rare_word_witness_batches_2": "witness_batches",
}

# files deliberately left at references/ root
KEEP_AT_ROOT = {
    "roadmap.md", "instructions.md", "general_references.md", "sources.md",
    "remembered_verses.md", "word_whitelist.md", "word_blacklist.md",
    "removed_words",
}

REWRITE_GLOBS = [
    ("scripts", "*.py"),
    ("references", "*.md"),
    ("references", "**/*.md"),
    ("docs", "*.html"),
    (".claude", "agents/*.md"),
    (".claude", "agent-memory/**/*.md"),
    (".", "CLAUDE.md"),
    (".", "README.md"),
]


def build_map():
    """old references-relative path -> new references-relative path."""
    out = {}
    for dest, names in MOVES.items():
        for name in names:
            leaf = RENAME.get(name, name)
            out[name] = f"{dest}/{leaf}"
    return out


def tracked(path):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)],
                       cwd=ROOT, capture_output=True)
    return r.returncode == 0


def move(old, new):
    """Move references/<old> -> references/<new>. Returns 'moved'|'done'."""
    src, dst = REF / old, REF / new
    if not src.exists():
        return "done" if dst.exists() else "MISSING"
    if dst.exists():
        return "CONFLICT"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if tracked(src):
        subprocess.run(["git", "mv", str(src.relative_to(ROOT)),
                        str(dst.relative_to(ROOT))], cwd=ROOT, check=True)
    else:
        shutil.move(str(src), str(dst))
    return "moved"


def rewrite_paths(mapping):
    """Rewrite both path spellings in every consumer file."""
    # longest first: "rare_word_witness_batches_2" before "..._batches"
    ordered = sorted(mapping.items(), key=lambda kv: -len(kv[0]))
    seg_pats = []
    for old, new in ordered:
        # ROOT / "references" / "old.md"  ->  ... / "rounds" / "round3" / "old.md"
        new_segs = " / ".join(f'"{p}"' for p in new.split("/"))
        seg_pats.append((
            re.compile(r'("references"\s*/\s*)"' + re.escape(old) + r'"'),
            r"\1" + new_segs))
        # references/old.md -> references/rounds/round3/old.md
        seg_pats.append((
            re.compile(r'(references/)' + re.escape(old) + r'\b'),
            r"\1" + new))

    changed = []
    seen = set()
    for sub, glob in REWRITE_GLOBS:
        for f in sorted((ROOT / sub).glob(glob)):
            if not f.is_file() or f in seen:
                continue
            seen.add(f)
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            new_text = text
            for pat, repl in seg_pats:
                new_text = pat.sub(repl, new_text)
            if new_text != text:
                f.write_text(new_text, encoding="utf-8")
                changed.append(f.relative_to(ROOT))
    return changed


def main():
    mapping = build_map()
    stats = {"moved": 0, "done": 0}
    problems = []
    for old, new in mapping.items():
        r = move(old, new)
        if r in stats:
            stats[r] += 1
        else:
            problems.append(f"{r}: {old} -> {new}")

    changed = rewrite_paths(mapping)

    print(f"references reorg: {stats['moved']} moved, "
          f"{stats['done']} already in place, {len(mapping)} mapped")
    print(f"path rewrites: {len(changed)} file(s) updated")
    for c in changed:
        print(f"  {c}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(f"  {p}")
    leftovers = sorted(p.name for p in REF.iterdir()
                       if p.name not in KEEP_AT_ROOT
                       and p.name not in {d.split("/")[0] for d in MOVES}
                       and not p.name.startswith("."))
    if leftovers:
        print(f"unfiled at references/ root ({len(leftovers)}):")
        for l in leftovers:
            print(f"  {l}")


if __name__ == "__main__":
    main()
