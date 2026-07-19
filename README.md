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

The complete 66-book restored text — 534 owner-reviewed restorations, every
changed verse marked, every original reading preserved in the appendix:

- [PDF (1,373 pages)](./exports/MandelaBible-MVP.pdf)
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
| [`references/sources.md`](./references/sources.md) | **Comprehensive source list** — every data set, reference text, and public Mandela-effect-Bible source catalogued so far |
| [`references/blog_search_references/`](./references/blog_search_references/) | Raw multi-engine blog/website search results (public memory literature) |
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

## Contributing

### Memory contribution instructions

Anyone can create a github account and open issues.  Please follow the instructions.  Look at the following to determine if a verse should be updated, even more so if you disagree with a memory that already exist and has updated a verse.  This is a memory led project and while memories before the mandela effect are the primary resources, other factors are taken into consideration.

1)  Consider the rarity of the word you are replacing and word you believe to be accurate.  (IE. couch, which is actually crouch and attested for by other translations.  Before the mandela effect, KJV had no mispelled words known.  It is possible crouch isn't accurate either though since it only appears twice otherwise in the KJV, but is the better replacement until a better word is found that would have been used when the KJV was written)
2)  Consider other translations and how the verse you want to fix is being used in other translations.  While these translations also have been affected by the mandela affect, clues can also be gathered as to how the original verse was written in the KJV before the mandela effect. 
3)  Consider the period authenticity.  Not only should the word your adding be authentic to Early Modern English during the time the KJV was written, it should also refelect the period in which Jesus was living or the time before that.  [Early Modern English](https://en.wikipedia.org/wiki/Early_Modern_English)
4)  Memory co-oberation.  If more than one person agrees with your memory, it helps to attest to the change you are presenting.
5)  Verify against our [word white-list](https://raw.githubusercontent.com/thomasmeadows/mandelabible/refs/heads/main/references/word_whitelist.md)</a> and [word black-list](https://raw.githubusercontent.com/thomasmeadows/mandelabible/refs/heads/main/references/word_blacklist.md) that a word you have used has been guaranteed KJV or guaranteed against KJV
6)  Do not submit your request on the first day (a full 24 hours) of finding a change that should be made.  Meditate on your verse throughout a full day. Meditate on what we have, and what you believe the verse should be.  Before going to bed, pray that the Lord guide you unto the correct wording and make sure you have a writing pencil, pen, or phone to gather the knowledge given to you by the spirit. Then, submit your spirit led verse on github or send on discord.


### Database

Having the databse is not necessary to contribute, you can contribute to white list or with memories and residuals.  However if you intend to use AI for validation or more research, the database is below
[current sqlite db](https://github.com/thomasmeadows/mandelabible/tree/38_owner_overrides.py/db)
The current sqlite db is up to date through 38_owner_overrides.py.  Any other changes may not be applied yet until I up date the db export.  It is on a second branch so it is not under version control and is very large.  You will need 7-zip or another known method to extract a multi file zip.