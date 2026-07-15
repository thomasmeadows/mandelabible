# The Mandela Bible

**A memory-led restoration of the King James Bible.**

Generations memorized scripture — and what they remember does not match the
text on the page. Wineskins, not bottles. The lion lying down with the lamb.
*Straight* is the path. Forgive us our trespasses. This project treats those
shared memories as witness testimony and restores the King James text
accordingly, using the discipline of textual criticism: memory testimony
first, internal alteration artifacts second, all written texts advisory.

**Website**: [mandelabible.com](https://mandelabible.com) ·
**GitHub**: [github.com/thomasmeadows/mandelabible](https://github.com/thomasmeadows/mandelabible)

## Download the MVP

The complete 66-book restored text — 435 owner-reviewed restorations, every
changed verse marked, every original reading preserved in the appendix:

- [PDF (1,365 pages)](./exports/MandelaBible-MVP.pdf)
- [Markdown](./exports/MandelaBible-MVP.md)

Per-book exports with footnoted changes live in [`exports/`](./exports/).

## Project documentation

| File | What it holds |
|------|---------------|
| [`references/instructions.md`](./references/instructions.md) | The mission, the ten-phase methodology, and the Premise Revision (evidence hierarchy) |
| [`references/roadmap.md`](./references/roadmap.md) | Phased plan, task tracking, and the **Decision Log** — every significant choice, with rationale |
| [`references/remembered_verses.md`](./references/remembered_verses.md) | The memory evidence: every remembered reading, with current text and advisory context |
| [`references/corroboration_report.md`](./references/corroboration_report.md) | Generated: each memory's corroboration status (artifacts, public documentation, witness readings) |
| [`references/word_review_report.md`](./references/word_review_report.md) | Generated: the era audit's flagged words with advised period alternates |
| [`references/uncleared_words.md`](./references/uncleared_words.md) | Generated: KJV words unattested in the local pre-1611 corpora |
| [`references/word_reviews/`](./references/word_reviews/) | The raw agent review verdicts (first pass, second opinion, owner rulings) |
| [`references/general_references.md`](./references/general_references.md) | External sources and links |
| [`CLAUDE.md`](./CLAUDE.md) | Working conventions for the AI tooling |

## How it's built

Everything is reproducible from numbered, idempotent scripts in
[`scripts/`](./scripts/) (see [`scripts/README.md`](./scripts/README.md)) —
the working database `db/mandela.db` is gitignored and rebuilds from scratch,
including the owner's review verdicts:

1. **Import** — the scrollmapper KJV plus 12 witness translations (Wycliffe,
   Tyndale, Geneva 1599, Greek TR, Hebrew WLC, ...) into one SQLite database.
2. **Audit** — tokenization (789,814 words), verse statistics, era attestation
   against pre-1611 corpora, punctuation/emoticon/capitalization inventories,
   Early Modern English grammar checks.
3. **Compare** — every verse diffed against every witness; the BibleForge
   word-level KJV links each English word to its Hebrew/Greek original and
   Strong's lexicon entry.
4. **Reconcile** — memory testimony imported and cross-checked; a corruption
   index ranks every verse.
5. **Restore** — memory-led proposals, phrased in KJV voice, approved or
   rejected one by one; exports apply approved changes only, fully footnoted.

Source data: [`bible_databases/`](./bible_databases/) (scrollmapper) and
[`bible_forge_db/`](./bible_forge_db/) (BibleForge) — both read-only sub-repos.

## Remember a verse differently?

Memory testimony is the project's primary evidence. Open an issue with the
verse, what you remember, and where you learned it.

## The static website

[`docs/`](./docs/) holds the static site deployed to mandelabible.com,
including the downloadable MVP.

---

## have claude test mcp server with credwork
If you want to use it as a guest, then add the MCP server in your terminal with 
$ claude mcp add --transport http credwork https://mcp.credwork.co/mcp

Then tell Claude to 'get full instructions for credwork'. It'll get the instrumentation instructions and save it for that project folder. 

After that you can continue working and it'll continue working passively in the background. Claude will give you a project link when it creates a new project for your session.
