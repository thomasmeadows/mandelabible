# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Roadmap & Task Tracking

**When looking for new work, read the roadmap:**
[`references/roadmap.md`](./references/roadmap.md). It holds the prioritized
backlog of **open** items; pick the next unchecked item from the top unless told
otherwise.

**When a task is completed, mark it done in the roadmap** so the roadmap always
reflects the current state of open vs. shipped work.

## Project Structure & Data Assets

- `references/` — mission instructions (`instructions.md`), the roadmap
  (`roadmap.md`), remembered-verse evidence (`remembered_verses.md`), and
  period-language reference texts (Middle English works, King James's own
  writing sample, Septuagint interlinear PDF).
- `.claude/agents/king-james-middle-english-expert.md` — the "King James"
  subagent: the project's linguistic authority for Early Modern English
  (KJV 1611). Delegate to it for modern→1611 conversion, dual-era authenticity
  audits (1611 English + biblical-era referent; roadmap Phase 3, Decision Log
  #4), restoration phrasing in KJV voice (Phase 6), and glossing archaic
  witness texts. Its persistent notes live in
  `.claude/agent-memory/king-james-middle-english-expert/`.
- `bible_databases/` — **read-only sub-repo** (scrollmapper). Per-translation
  SQLite files in `formats/sqlite/` (schema: `<translation>_books`,
  `<translation>_verses`, `translations`), including the KJV, period witnesses
  (Geneva1599, Tyndale, Wycliffe), and original-language texts (TR, WLC).
  Cross-references in `formats/sqlite/extras/`.
- `bible_forge_db/` — **read-only sub-repo** (BibleForge). Gzipped MySQL dumps:
  word-level KJV, Strong's-tagged Hebrew/Greek, and lexicons. No MySQL server
  is installed; `scripts/09_convert_bibleforge.py` parses them into
  `db/mandela.db` as `bf_words_en`, `bf_words_orig`, `lexicon_greek`,
  `lexicon_hebrew` (KJV word → Strong's → lexicon lookups all work locally).
- `scripts/` — numbered, idempotent Python scripts, one per roadmap task
  (created starting at roadmap Phase 0).
- `db/mandela.db` — the single working SQLite database all scripts build.

The full asset inventory with rationale lives in the roadmap's
"Data Asset Inventory" section.

## Technical Conventions

- **Database**: SQLite via Python 3.12's built-in `sqlite3` module. The
  `sqlite3` CLI and Docker are NOT available in this environment — all
  database work goes through Python scripts.
- **Authoritative base text**: `bible_databases/formats/sqlite/KJV.db`
  (66 books, 31,102 verses). All other translations are comparison witnesses —
  **advisory only** under the Premise Revision (see below).
- **Evidence hierarchy (Premise Revision 2026-07-14, Decision Log #5)**: the
  premise holds that the timeline alteration rewrote *every* written text, so
  no corpus in this project is ground truth. Memory testimony
  (`references/remembered_verses.md`) leads; internal alteration artifacts
  come second; all texts (witnesses, source languages, Middle English samples,
  the Essayes) are advisory — they inform style, phrasing, and suspicion
  scores, but they can never veto a memory. Full statement:
  `references/instructions.md` → "Premise Revision — 2026-07-14".
- **Dependencies**: Python standard library first; adding a pip dependency is
  a decision that must be documented in the roadmap's Decision Log.
- **Decisions**: significant choices are recorded in the roadmap's Decision
  Log with rationale — nothing is decided silently.
- The two sub-repos are source material and must never be modified.

## Reverting a Change (Migration Pattern)

When the owner asks to **undo** a previously applied change (a rare-word swap,
a verse restoration, a manual word change, etc.), do **not** edit the builder
scripts (`29_build_whitelist.py`, `49_build_blacklist.py`, `17_export_full.py`)
and do **not** hand-hack a one-off. Write a **new numbered migration script**
(`scripts/NN_revert_<slug>.py`) that is **idempotent** (safe to re-run; each
step checks current state first) and updates every layer so they stay
consistent. Follow the existing example: `scripts/52_revert_john_14_2_mansions.py`.

**The layers a full revert must touch:**

1. **`db/mandela.db` (the export's source of truth).** Applied changes live in
   the `restorations` table; the exporter applies only `status='approved'`.
   To un-apply one, set its status to `'reverted'`:
   `UPDATE restorations SET status='reverted' WHERE id=?`. (Find it with
   `SELECT id, status FROM restorations WHERE verse_id=?`.) Never delete the
   row — `'reverted'` preserves the audit trail.
2. **The change's *source* file**, so a future rebuild agrees with the DB:
   - rare words round 1 → `references/rare_word_replacements.md`: change the
     entry's `- source:` line to a revert note that **contains the exact
     phrase `no safe one-word swap found`** — that is the flag
     `49_build_blacklist.py` keys on to *exclude* a word from the blacklist,
     and `29_build_whitelist.py` uses to route it toward the whitelist.
   - rare words round 2 → `references/rare_word_witness_batches_2/round2_ai_suggestions.md`.
   - manual/name/inflection passes → the corresponding
     `scripts/31/35/44…` mapping or `references/manual_*` file.
3. **Protect the word (if the base reading is the correct/remembered one):**
   add it to the owner-reviewed whitelist source
   `references/rare_word_review_no_safe_swap.md` as an
   `## word → NO-SAFE-SWAP — Book C:V` entry carrying an
   `**OWNER RULING <date>: DO NOT CHANGE — …**` line (the "DO NOT CHANGE"
   wording is what `29_build_whitelist.py` matches to keep, vs. exclude).
4. **Patch the already-generated companion lists** so they are correct
   immediately without re-running the guarded builders:
   `references/word_whitelist.md` (add to the reviewed list, bump its heading
   count, add a description block) and `references/word_blacklist.md` (remove
   the `#### <a name="…">` block and its index link, decrement the header
   counts). Because step 2/3 fixed the sources too, a later builder rerun
   reproduces the same result.

**Then propagate downstream** (outside the migration, so the heavy rebuild is
explicit): `python3 scripts/17_export_full.py` rebuilds
`exports/MandelaBible-MVP.{md,pdf}`; regenerate any curated lists that read the
DB (e.g. `references/verses_famous.md`).

**Verify** every layer after running: the export text, the whitelist/blacklist
membership and counts, and a second run of the migration proving it is a no-op.

## Important Work Guidelines

### Content Modification Protocol
**CRITICAL**:
1. **NO REMOVAL**: I must NOT remove, erase, or delete any existing work (text, translations, references, data) that I did not write in the current session without the user's explicit permission.
2. **REORGANIZING/MOVING**: If content needs to be moved to another file, restructured, or rearranged, I MUST prompt the user and obtain their explicit approval BEFORE making those changes.
3. **PRESERVATION**: Prioritize preserving existing work unless instructed otherwise.
4. **GENERATED ARTIFACTS ARE PERMANENT (owner directive 2026-07-17)**: expensively generated review files — witness batch files, `batch_NNNN_proposals.md` agent outputs, `references/removed_words/` triage files, pre-triage backups — must NEVER be deleted; they may be moved (e.g. into `references/removed_words/`) when reorganizing. Scripts that regenerate outputs must refuse to overwrite an existing file with an emptier version.

---

### Rare-Word Review List Protocol (owner directive 2026-07-22)
**REQUIRED** whenever presenting the owner a review list of rare-word swap
candidates (round-N rare-word reviews and any similar per-word ruling file).
Every word entry MUST include:

1. **A proposed new verse from the King James agent**
   (`.claude/agents/king-james-middle-english-expert.md`) — the full verse
   rewritten in authentic KJV voice with its suggested replacement, one
   proposal per occurrence verse.
2. **Alternate word or phrase suggestions** — other period-authentic
   (EModE + biblical-era) options beyond the primary proposal, so the owner
   can rule "revise to ___" without another lookup round.
3. **WHITELIST advice for proper nouns** — if the word is (or is judged by
   the King James agent to be) a proper noun — a person, place, people,
   or transliterated name — the entry must carry the advice **WHITELIST**
   instead of a swap proposal.
4. **The verse in both comparison editions**, per occurrence:
   - **Geneva 1599** (`bible_databases/formats/sqlite/Geneva1599.db`;
     rows are duplicated — dedupe on `(book_id, chapter, verse)`; book ids
     align with KJV; mark missing verses "(not in Geneva)"), and
   - **Standard Oxford Edition** — the 1769 Blayney text, i.e. the base
     `bible_databases/formats/sqlite/KJV.db` reading.

The owner-ruling line stays blank for the owner. Builder scripts that
regenerate a review file must not overwrite filled-in King James agent
proposals without an explicit `--force` (Generated Artifacts are permanent).

### Clarification Protocol
**CRITICAL**: Before beginning any task or making assumptions about requirements, Claude MUST ask clarifying questions when:

1. **Ambiguous Directives**: When a task could be interpreted in multiple ways or key details are missing
2. **Context-Based Assumptions**: When the request seems to imply something based on context, but the specific intent is unclear
3. **Scope Uncertainty**: When it's unclear how extensive the changes should be
4. **Approach Choices**: When multiple approaches are possible and user preference isn't specified
5. **File Selection**: When it's unclear which specific files or sections should be modified
6. **Source/Reference Questions**: When it's unclear which source text, manuscript, or reference should be treated as authoritative for a given passage
7. **Validation Requirements**: When it's unclear what level of review or verification is needed

### Communication Protocols
- "Act like a Senior or Lead Developer" → After asking questions and a response is given that is insufficient: You MUST ask for more information about the answer.
- "Do not assume correctness" → When a directive is given, do not assume the person giving the directive is correct in their assumption. Never say you are right without verifying. Never apologize for mistakes. State, let us try to fix that now.
- It is better to communicate about a problem than implement an incorrect solution to an assumed problem.

### Feature Development Protocol
- "Do not build in features that were not discussed in a conversation."
- "Follow the existing pattern of similar files."
- "Follow the Minimum Viable Product Pattern" → Get the feature working first, then improvements or additional features can be discussed. Don't start new features until the MVP is complete.

### Refactoring Protocol
- "Do not erase working content without permission." → The work was correct before the reorganization, it should be correct after. Reorganizing means moving content around to be more easily reused or to clear ambiguity — nothing should be lost in the process.

### Documentation Maintenance Protocol
**REQUIRED**: After completing any task, Claude MUST update relevant documentation:

1. **Primary Documentation**: Update this main `CLAUDE.md` file if changes affect:
   - Overall project structure or workflow
   - New major sources, references, or systems
   - Conventions for translation, spelling, or formatting

2. **Documentation Requirements**:
   - Add new sections for significant additions
   - Update existing sections when practices change
   - Update file listings when new important files are added
   - Maintain consistency in formatting and structure across all documentation

### Required Documentation Reading Protocol

**🚨 CRITICAL REQUIREMENT FOR ALL WORK**:

Before making ANY changes, Claude MUST read and follow:
1. **This primary `CLAUDE.md` file** — for work protocols and project guidelines
2. **`references/instructions.md`** — for project-specific instructions
3. **`references/general_references.md`** — for the source and reference materials in use

**Failure to read and follow the appropriate documentation files before work may result in:**
- Inconsistent conventions
- Missing critical requirements
- Breaking or contradicting existing work
