# Roadmap

These are major milestones and should be broken down and planned in more detail.  Decisions should be heavily documented and planned.  Think deeply about order and decisions before moving forward.  Read all md files and documentation and look in folders for databases and existing formats.  Make best case judgements based on data that exist and ask for help or to gather more information if needed to complete the project.

## How This Roadmap Is Organized

Work is organized into **phases**. Each phase has its own detailed section below containing:

- **Decisions** — choices made (or still open), with rationale, so nothing is decided silently.
- **Tasks** — the checkbox items to execute, in order.
- **Schema** — sketches of the database tables the phase produces.
- **Acceptance criteria** — how we know the phase is actually done.

Per `CLAUDE.md`, when a task is completed it must be checked off here. The original nine milestones are all preserved below (marked *[orig #N]*) — they have been regrouped into phases, not removed.

## Milestone Checklist

### Phase 0 — Foundations
- [x] Decide database engine (PostgreSQL-via-Docker vs SQLite) *[orig #1, decision part]* — **DECIDED: SQLite** (see Decision Log)
- [x] Decide authoritative base text — **DECIDED: scrollmapper KJV.db** (see Decision Log)
- [ ] Create repo layout: `scripts/` for Python tooling, `db/` for the working database

### Phase 1 — Database & KJV Import (MVP)
- [ ] Create a Database - Choose the most effective solution, either postgresql database created through docker or use sql lite. *[orig #1]*
- [ ] Insert KJV in english into the database as MVP *[orig #2]*

### Phase 2 — Tokenization & Verse Statistics
- [ ] Tokenize KJV counting occurances of word by book and total throughout the bible and save in tables *[orig #3]*
- [ ] Count characters in each verse and store them in a database, identify outliers and long or short sentances. *[orig #4]*

### Phase 3 — Anomaly Detection
- [ ] Identify rare words that don't belong in the KJV and words that did not see significant use during the era the KJV was written *[orig #5]*
- [ ] Identify all parentheses and emojis that should not exist in the bible, place them in a database *[orig #6]*
- [ ] Identify grammar errors where a sentance is written in a way that would not occur during the time the KJV was written *[orig #7]*

### Phase 4 — Cross-Translation Comparison
- [ ] Convert the BibleForge MySQL dumps (word-level KJV, Strong's-tagged originals, lexicons) into the SQLite database
- [ ] Identify and circle back to other bible translations and compare them to KJV. *[orig #8]*

### Phase 5 — Memory Reconciliation
- [ ] Import `references/remembered_verses.md` into a structured `memories` table and cross-check each memory against the translation witnesses

### Phase 6 — Reconstruction
- [ ] Start reconstructing the bible based on memories, outliers, and words that don't belong.  Document decisions and reasons made.  Every flaw should be documented such as missing letters, bad punctuation *[orig #9]*

---

## Decision Log

Decisions confirmed with the project owner on 2026-07-14:

1. **Database engine: SQLite.**
   - Docker is not available in this WSL2 distro (Docker Desktop WSL integration not enabled), so PostgreSQL-via-Docker would block all work behind environment setup.
   - Python 3.12's built-in `sqlite3` module is verified working; no new dependencies needed.
   - The scrollmapper `bible_databases` repo already ships every translation as a ready-made SQLite file, so import is a file-attach, not an ETL project.
   - A single-file database (`db/mandela.db`) is easy to back up, inspect, and version.
   - Note: the `sqlite3` **command-line client is not installed** — all database work goes through Python scripts.

2. **Authoritative base text: scrollmapper `KJV.db`** (`bible_databases/formats/sqlite/KJV.db`).
   - This is THE "current/corrupted" text that all analysis and restoration runs against.
   - Verified contents: `KJV_books` (66 rows), `KJV_verses` (31,102 rows; columns `id, book_id, chapter, verse, text`), `translations` (metadata).
   - KJVPCE (Pure Cambridge Edition), the BibleForge word-level KJV, and all other translations are **comparison/enrichment witnesses**, not the base.

3. **Roadmap restructure approved** — all nine original milestones preserved, regrouped into phases; the duplicated "Identify all parentheses" heading from the old file was consolidated into one section.

4. **Dual-era authenticity criterion** (owner decision, 2026-07-14).
   - A word in the base text is authentic only if it passes two independent tests: **(a) translation era** — the English word existed and was usable in 1611 (the existing `word_era` check); **(b) source era** — the thing the word names, in the sense used in that verse, existed in the world of the underlying text (OT: the ancient Near East of the Hebrew authors, roughly 0 AD and earlier; NT: the first-century AD eastern Mediterranean).
   - Rationale: a faithful 1611 translator would not name an object the biblical authors could not have known — `instructions.md` requires vocabulary fit for both the original composition era and Early Modern English. Good 1611 English naming a post-biblical referent is a corruption signature, not a clearance.
   - Rulings are made on the sense-in-context, never the bare headword (polysemy: "couch" the verb at Job 38:40 ≠ "couch" the furniture noun), and start from the underlying Hebrew/Greek word (`WLC.db`/`TR.db`; Strong's data after Phase 4).
   - Owner-supplied source-era facts recorded with this decision: rigid **bottles** were rare/elite luxuries before 0 AD, while **wineskins** existed and were the heavily-used vessel of the period (relevant to Matthew 9:17 etc., where the Greek ἀσκός names a skin vessel).
   - Implemented in the `king-james-middle-english-expert` agent (Capability 2 now returns two-axis verdicts) and in Phase 3's `word_era` schema via a `source_verdict` column. When the two axes disagree, both verdicts are recorded and the rendering choice goes to the Phase 6 owner-review workflow.

5. **Premise revision: the alteration reached everything written** (owner decision, 2026-07-14; narrative recorded in `instructions.md` → "Premise Revision — 2026-07-14").
   - **Scope**: the timeline rewrite altered ALL texts — every Bible translation and manuscript (TR, WLC, Septuagint, Wycliffe, Tyndale, Geneva, modern versions) and secular works (Chaucer, the Essayes, dictionaries). No written corpus is ground truth; all are **advisory**. Witness agreement with the KJV clears nothing, and the Middle English samples may not be good enough to determine the truth of a word's history.
   - **Evidence hierarchy for restorations** (highest first): (1) corroborated memory — independent agreement among unrelated rememberers and/or co-located alteration artifacts; (2) internal alteration artifacts (character-count seams, style/grammar anomalies, punctuation); (3) advisory texts (witnesses, era attestation, source languages) for phrasing and internal-consistency work only — never a veto over memory.
   - **Falsifiability anchor**: a memory with no corroboration stays `unconfirmed` — recorded, not restored. Owner review remains required for every restoration.
   - **Effect on earlier decisions**: Decision Log #4's dual-era audit survives as an **advisory signal generator** — its verdicts feed the corruption index but no longer clear or veto anything. Phase 5's corroboration report now scores memory-vs-memory agreement and artifact co-location; witness readings are recorded as advisory context. Phase 6 candidate generation stays memory-led.

6. **Capitalization ruling: doctrinal capitalization is a corruption signature** (owner decision, 2026-07-14).
   - "Holy Spirit" and "Holy Ghost" are out of period; the target reading is **"spirit of god"**. Mid-verse doctrinal title-casing (Spirit, Ghost, and similar) and ALL-CAPS words should never occur. Trinitarian proper-name treatment of the spirit is a specific doctrinal convention, not something the < 100 AD authors wrote.
   - Structural basis: the original languages are caseless — Hebrew has no letter case, and first-century Greek was written in a single case — so every capitalization pattern in the English text is a translator/printer artifact and prime alteration surface.
   - Base-text facts recorded with this decision: KJV.db has "Holy Ghost" 89 / "Holy Spirit" 7; "Spirit" 159 vs "spirit" 374; ALL-CAPS survives in only 9 verses, all quoted inscriptions (LORD ×6, GOD ×2, JEHOVAH ×1) — internally inconsistent and flagged as seam candidates.
   - Phase 3 gains a **capitalization audit** (anomaly type `capitalization`). Restoration phrasing (King James agent, Capabilities 1/3) renders divine references lowercase per this ruling — a deliberate divergence from KJV.db casing conventions.
   - **Sub-decision resolved (owner, 2026-07-14): LORD stays — as the exception, not the rule** (provisional; could change later). The divine-name distinction is preserved: "LORD" for the name YHWH and "Lord" for the title Adonai when they stand apart, and the customary combined forms where they meet ("LORD God" for YHWH Elohim, "Lord GOD" for Adonai YHWH). This is the sole exception to the no-ALL-CAPS rule.
   - **Recovery mechanism** (the base KJV.db collapsed the distinction to "Lord"): the WLC Hebrew re-derives which "Lord" is which — verified locally: יהוה (YHWH) in 5,790 verses, אדני (Adonai) in 753, both together in 379 (e.g., Ezekiel 2:4 "adonai yhwh") — supplemented by the BibleForge word-level KJV's `divine` marker column once Phase 4 parses it.
   - **Backlog option (owner request)**: an alternate export with the Hebrew names themselves — "Yahweh" and "Adonai" — inserted in place of LORD/Lord, for readers who want the true Hebrew names.

---

## Data Asset Inventory

What already exists in this repo and what each asset is for:

### `bible_databases/` (scrollmapper, 2025 schema) — sub-repo
- `formats/sqlite/<Translation>.db` — one SQLite file per translation (140 total). Schema per file: `<translation>_books`, `<translation>_verses`, `translations`.
- **Base text**: `KJV.db`.
- **English witnesses** (KJV lineage & era): `KJVPCE.db` (Pure Cambridge), `AKJV.db`, `RNKJV.db`, `UKJV.db`, `MKJV.db`, `Webster.db`, `YLT.db`, `DRC.db` (Douay-Rheims), `Geneva1599.db` (the translation the KJV translators leaned on), `Tyndale.db` (1526), `Wycliffe.db` (1382, Middle English), `BSB.db`, `ASV.db`, `LEB.db` and others.
- **Original-language witnesses**: `TR.db` (Textus Receptus — the Greek NT the KJV was translated from), `Byz.db` (Byzantine textform), `StatResGNT.db`, `WLC.db` (Westminster Leningrad Codex — Hebrew Masoretic), `MapM.db`, `SP.db` (Samaritan Pentateuch).
- `formats/sqlite/extras/cross_references_0.db` … `cross_references_6.db` — openbible.info cross-reference data, split across 7 files.
- Other formats (csv/json/md/txt/yaml) exist in `formats/` if ever needed; `sources/en/KJV/KJV.json` is the JSON source.

### `bible_forge_db/` (BibleForge) — sub-repo, **MySQL dumps (gzipped), require conversion**
- `bible_en_all.sql.gz` — table `bible_en`: **word-level KJV**, one row per word with `verseID, book, chapter, verse, word, head, divine` (divine-name marker), `red` (red-letter/words of Christ), `implied` (translator-supplied words — the 1611 italics), `paragraph`, and `orig_id` linking each English word to the original-language word.
- `bible_original.sql.gz` — table `bible_original`: **word-level Hebrew/Greek** with `word, pronun, strongs` (Strong's number), `morph` (morphology), keyed by verse.
- `lexicon_greek.sql.gz`, `lexicon_hebrew.sql.gz` — full Strong's lexicons.
- No MySQL server is installed; a Python script must parse the `INSERT` statements and load them into SQLite (Phase 4).

### `references/`
- `remembered_verses.md` — 11 documented memory anchors (Genesis 1:1, bottles/wineskins, lion & lamb, Lord's Prayer, couch/crouch, divers/diverse, tables/tablets, spirit of error, charity/love, matrix/womb, parentheses/emoticons, eyes-to-see, destroyed/perish, serpent's head). **Primary reconstruction evidence** (Phase 5).
- `King James Writing Sample - The Essayes of a Prentise in the Divine Art of Poesie.txt` — King James's own writing; period-authentic Early Modern English vocabulary evidence.
- Middle English texts (`The Canterbury Tales`, `The Book of Quinte Essence`, `The Wright's Chaste Wife`, the Middle English Reader) — a word attested in these existed **before** 1611, useful for first-attestation dating (Phase 3).
- `Interlinear Greek-English Septuagint Old Testament - print.pdf` — Septuagint witness for OT passages.
- `Rather Exhaustive List of Mandela Effect Affected Scriptures _ Truth Farmer.pdf` — candidate passage list to seed Phase 5.
- `instructions.md` — mission framing and the ten-phase restoration methodology this roadmap implements.
- `general_references.md` — external links.

---

## Phase 0 — Foundations

Goal: lock in the environment and layout so every later phase has a known home.

### Decisions
- SQLite + Python 3.12 stdlib (see Decision Log). Prefer the standard library (`sqlite3`, `json`, `re`, `collections`, `unicodedata`) — no pip dependencies until a phase concretely needs one, and that need gets documented here first.
- Repo layout:
  - `scripts/` — numbered Python scripts, one per roadmap task (e.g. `01_create_db.py`, `02_import_kjv.py`), each runnable standalone and idempotent (safe to re-run).
  - `db/mandela.db` — the single working database all phases write into.
- The two sub-repos stay read-only source material; we never modify them.

### Tasks
- [ ] Create `scripts/` and `db/` directories with a short `scripts/README.md` explaining the numbering convention
- [ ] Decide whether `db/mandela.db` is committed to git or gitignored-and-rebuildable (lean: gitignore it; every table must be rebuildable from scripts, which keeps scripts honest)

### Acceptance criteria
- Directories exist, convention documented, `.gitignore` updated if the rebuildable option is chosen.

---

## Phase 1 — Create the Database & Insert the KJV (MVP)

Covers *[orig #1]* "Create a Database" and *[orig #2]* "Insert KJV in english into the database as MVP".

### Decisions
- Engine: SQLite (Decision Log #1). Source: scrollmapper `KJV.db` (Decision Log #2).
- Import method: Python `sqlite3` with `ATTACH DATABASE` on the scrollmapper file, then `INSERT INTO ... SELECT` — no text parsing, no chance of transcription errors.
- Keep a schema very close to scrollmapper's so their documentation and query examples keep working, but generalize for multiple translations in ONE database (their layout is one file per translation; ours is one database with a `translation` column).

### Schema
```sql
CREATE TABLE translations (
    translation TEXT PRIMARY KEY,   -- 'KJV', 'Geneva1599', ...
    title       TEXT,
    license     TEXT
);
CREATE TABLE books (
    id          INTEGER,            -- scrollmapper book id (1=Genesis ... 66=Revelation)
    translation TEXT REFERENCES translations(translation),
    name        TEXT,
    PRIMARY KEY (translation, id)
);
CREATE TABLE verses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    translation TEXT REFERENCES translations(translation),
    book_id     INTEGER,
    chapter     INTEGER,
    verse       INTEGER,
    text        TEXT,
    UNIQUE (translation, book_id, chapter, verse)
);
```

### Tasks
- [ ] `scripts/01_create_db.py` — creates `db/mandela.db` with the schema above
- [ ] `scripts/02_import_kjv.py` — ATTACHes scrollmapper `KJV.db`, copies books + verses + translation metadata

### Acceptance criteria
- `translations` contains KJV; `books` has **66** rows; `verses` has **31,102** rows.
- Spot checks return the expected current (corrupted) text:
  - Genesis 1:1 = "In the beginning God created the heaven and the earth."
  - John 3:16 present; Revelation 22:21 is the final verse.

---

## Phase 2 — Tokenize & Count Characters

Covers *[orig #3]* tokenization/word counts and *[orig #4]* character counts and outliers.

### Decisions
- **Tokenizer rules must be written down before running** (they affect every downstream count):
  - Case-fold to lowercase for counting, but preserve original-case forms in a separate column (capitalization anomalies are themselves evidence — e.g. divine names).
  - Strip surrounding punctuation; keep internal apostrophes (`serpent's`) and hyphens as part of the token.
  - Store the tokenizer version with the results so counts can be regenerated if rules change.
- Outlier definition: per-book mean and standard deviation of verse length (characters and words); flag verses beyond ±2σ within their book, and globally rank longest/shortest. Per-book matters because Psalms and Chronicles have naturally different rhythm than Mark.

### Schema
```sql
CREATE TABLE word_counts (          -- one row per (word, book); book_id NULL = whole-bible total
    translation TEXT,
    word        TEXT,               -- case-folded token
    book_id     INTEGER,            -- NULL for bible-wide totals
    count       INTEGER
);
CREATE TABLE verse_stats (
    verse_id            INTEGER REFERENCES verses(id),
    char_count          INTEGER,    -- including whitespace (the corruption engine's constraint!)
    char_count_no_ws    INTEGER,
    word_count          INTEGER,
    book_zscore_chars   REAL,       -- how unusual this verse is within its book
    is_outlier          INTEGER DEFAULT 0
);
```
- Note on `char_count`: per `instructions.md`, the corrupting AI had to preserve character counts including whitespace — this column is the direct measurement of that constraint and feeds Phase 8-style artifact detection later.

### Tasks
- [ ] `scripts/03_tokenize.py` — tokenize all KJV verses, fill `word_counts` (per-book and totals)
- [ ] `scripts/04_verse_stats.py` — fill `verse_stats`, compute per-book z-scores, mark outliers
- [ ] Document the tokenizer rules actually implemented (in the script docstring and here)

### Acceptance criteria
- Sum of bible-wide `word_counts` ≈ 790,000 (the KJV's well-known word count; exact number depends on tokenizer rules — record ours).
- "the", "and", "of" are the top tokens (sanity check).
- Every verse has a `verse_stats` row; outlier list produced and eyeballed (Esther 8:9 should surface as the famously longest verse).

---

## Phase 3 — Anomaly Detection

Covers *[orig #5]* rare/era-inappropriate words, *[orig #6]* parentheses & emojis, and *[orig #7]* grammar errors. This is the corruption-detection heart of the project (instructions.md Phases 2, 5, 8).

### Decisions
- **Rare words**: start with hapax legomena (words appearing exactly once bible-wide) and words appearing ≤5 times — `remembered_verses.md` already observes that "matrix" appears only 5 times, so low frequency is a validated corruption signal.
- **Era dating** (first attestation): a word is *cleared* if it appears in any pre-1611 witness we hold locally — Wycliffe (1382), Tyndale (1526), Geneva (1599), the Middle English texts, or King James's own essays. Words cleared by none of these become candidates for manual dating. *(Decision Log #5: "cleared" is advisory — attestation lowers a word's corruption-index contribution but cannot overrule memory testimony, since the attestation corpora are themselves altered-timeline texts.)*
  - Open sub-decision (document before implementing): source for external first-use dates — options are a Wiktionary etymology extract, hand-checking flagged words against Merriam-Webster/OED first-known-use (the method `remembered_verses.md` already uses, e.g. "matrix" 1555, "diver" 1511), or both. Hand-checking is fine at first: the flagged list should be small.
- **Source-era referent check (Decision Log #4)**: era dating above only clears a word for 1611 English (Axis 1). A second, independent test asks whether the word's referent — in the sense used in that verse — existed in the world of the underlying text, checked against the original-language word (`WLC.db`/`TR.db`; Strong's after Phase 4). Judgment calls are delegated to the `king-james-middle-english-expert` agent; verdicts land in `word_era.source_verdict`. A word can be perfectly period 1611 English and still be flagged (e.g. "bottles" where the Greek ἀσκός names a wineskin).
- **Punctuation audit**: inventory ALL of `( ) ; : ! ?` plus any character outside the expected 1611 set (any non-ASCII symbol, emoji range, em-dashes, curly quotes). Parentheses get special attention per `remembered_verses.md` ("emoticon" artifacts like `;)` produced by `...God;)`).
- **Grammar checks** (Early Modern English rules, each check documented with its rule):
  - `its` — essentially absent from the 1611 KJV (period English used "his"/"thereof"); any occurrence is suspect.
  - Second-person consistency: thou/thee/thy (singular) vs ye/you/your (plural, object) usage patterns; "your" where "thy" belongs is the exact signature remembered in the Lord's Prayer entry.
  - Verb endings: third-person `-eth` (he loveth), second-person `-est` (thou lovest); bare modern forms ("he loves") are anachronisms.
  - Modern idioms/phrasal constructions flagged by n-gram comparison against the Geneva/Tyndale corpora.
- **Capitalization audit (Decision Log #6)**: inventory ALL-CAPS tokens (only 9 verses survive in the base text — all quoted inscriptions — an internal inconsistency), mid-verse capitalized words, and doctrinal title-casing ("Holy Ghost" 89, "Holy Spirit" 7, "Spirit" 159 vs "spirit" 374). The original languages are caseless, so all casing is translator/printer artifact and scores as alteration surface.

### Schema
```sql
CREATE TABLE word_era (
    word              TEXT PRIMARY KEY,
    cleared_by        TEXT,     -- 'Wycliffe', 'Tyndale', 'Geneva1599', 'KJ-Essayes', 'MiddleEnglish', NULL
    first_use_year    INTEGER,  -- from manual/external dating when not cleared
    first_use_source  TEXT,     -- e.g. 'merriam-webster'
    verdict           TEXT,     -- 'period', 'suspect', 'anachronism' (Axis 1: 1611 English)
    source_verdict    TEXT      -- 'source-era', 'source-suspect', 'source-anachronism' (Axis 2: biblical-era referent; Decision Log #4)
);
CREATE TABLE anomalies (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id  INTEGER REFERENCES verses(id),
    type      TEXT,    -- 'rare_word' | 'anachronism' | 'punctuation' | 'emoticon' | 'grammar' | 'length_outlier' | 'capitalization'
    token     TEXT,    -- the offending word/character/pattern, if applicable
    detail    TEXT,    -- human-readable explanation incl. the rule that fired
    score     REAL     -- severity/confidence contribution to the corruption index
);
```

### Tasks
- [ ] `scripts/05_word_era.py` — build the cleared-word list from local pre-1611 corpora; emit the uncleared list for dating
- [ ] `scripts/06_punctuation_audit.py` — character/parenthesis/emoticon inventory into `anomalies`, plus the capitalization audit (Decision Log #6)
- [ ] `scripts/07_grammar_checks.py` — the EME rule checks into `anomalies`
- [ ] Manually date the uncleared word list; record year + source in `word_era`

### Acceptance criteria
- Known plants from `remembered_verses.md` are caught by the machinery **without hardcoding them**: "matrix" flagged (rare + late first use), "bottles" flagged (source-era referent mismatch — the Greek ἀσκός names a wineskin; Decision Log #4), `(For ... ;)` emoticon patterns flagged, "your/you" in Matthew 6:9–13 flagged by the grammar check, "Holy Ghost"/"Holy Spirit" title-casing and the 9 ALL-CAPS inscription verses flagged by the capitalization audit (Decision Log #6).
- Every anomaly row carries a human-readable `detail` — no bare flags.

---

## Phase 4 — Cross-Translation Comparison

Covers *[orig #8]* "Identify and circle back to other bible translations and compare them to KJV", plus the BibleForge conversion that unlocks word-level and Strong's data.

### Decisions
- **Witness set (initial)**: Geneva1599, Tyndale, Wycliffe, KJVPCE, AKJV, Webster, RNKJV, UKJV, YLT, DRC for English; TR and WLC for originals. Rationale: the KJV lineage + what its translators actually worked from. More can be attached later — the import script should take a translation list.
- **BibleForge conversion**: no MySQL server exists, so `scripts/` gets a dump parser that reads the gzipped SQL, extracts `INSERT` tuples, and loads SQLite tables (`bf_words_en`, `bf_words_orig`, `lexicon_greek`, `lexicon_hebrew`). The `orig_id` column ties each English word to its Hebrew/Greek word — this gives us KJV-word → Strong's-number → lexicon-gloss lookups, the backbone of translation-anomaly detection ("does this English word match what the Greek actually says?").
- Verse alignment: by (book_id, chapter, verse) — the scrollmapper schema is consistent across translations. Missing/merged verses in older translations (Wycliffe especially) get logged, not force-aligned.

### Schema
```sql
-- verses/books tables already hold all witnesses via the translation column
CREATE TABLE bf_words_en (      -- word-level KJV from BibleForge
    verse_ref  TEXT,            -- 'book.chapter.verse'
    word_num   INTEGER, word TEXT,
    implied    INTEGER,         -- 1611 italics: translator-supplied
    divine     INTEGER, red INTEGER, paragraph INTEGER,
    orig_id    INTEGER          -- FK into bf_words_orig
);
CREATE TABLE bf_words_orig (
    orig_id  INTEGER PRIMARY KEY, verse_ref TEXT,
    word TEXT, pronun TEXT, strongs INTEGER, morph TEXT
);
CREATE TABLE verse_diffs (
    verse_id     INTEGER,       -- KJV verse
    witness      TEXT,          -- which translation
    witness_text TEXT,
    similarity   REAL,          -- e.g. token-overlap or difflib ratio
    notable      TEXT           -- summary of key word substitutions
);
```

### Tasks
- [ ] `scripts/08_import_witnesses.py` — attach & copy the witness translations into `verses`/`books`
- [ ] `scripts/09_convert_bibleforge.py` — parse the MySQL dumps into the `bf_*` and lexicon tables
- [ ] `scripts/10_verse_diffs.py` — align and diff every KJV verse against each witness

### Acceptance criteria
- All witness translations queryable in the one database; row counts recorded per translation.
- BibleForge word-level KJV row count ≈ 814,7xx (per dump AUTO_INCREMENT), originals ≈ 447,3xx.
- Matthew 9:17 diff against Geneva/Tyndale visibly surfaces the bottles-vs-wineskins divergence (validation against a known case).

---

## Phase 5 — Memory Reconciliation

New milestone (from `instructions.md` Phase 7): the remembered verses are witness testimony and must live in the database, not just in markdown.

### Decisions
- `references/remembered_verses.md` stays the human-editable source of record; a script imports it, so re-running after new memories are added is the workflow.
- Each memory gets typed: `word_substitution` (bottles→wineskins), `missing_letter` (couch→crouch, divers→diverse, tables→tablets), `punctuation` (Genesis 1:1 comma), `missing_phrase` (Lord's Prayer doxology), `phrase_change` (lion & lamb), `emoticon`.

### Schema
```sql
CREATE TABLE memories (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_ref      TEXT,      -- 'Genesis 1:1'; NULL for bible-wide memories (e.g. charity→love)
    memory_type    TEXT,
    current_text   TEXT,
    remembered_text TEXT,
    evidence       TEXT,      -- references/links from the md file
    scope_refs     TEXT       -- other affected verses listed in the entry
);
```

### Tasks
- [ ] `scripts/11_import_memories.py` — parse `remembered_verses.md` into `memories`
- [ ] Cross-check every memory against Phase 4 witnesses and Phase 3 anomalies; record corroboration per Decision Log #5 — corroboration means independent memory agreement and/or co-located alteration artifacts; witness readings are logged as advisory context only (agreement with the KJV neither confirms nor refutes a memory)

### Acceptance criteria
- All entries from `remembered_verses.md` present in `memories` with correct type and scope verses.
- A corroboration report exists: for each memory, its corroboration status (independent memories / artifact signals) plus the advisory witness readings.

---

## Phase 6 — Reconstruction

Covers *[orig #9]*: "Start reconstructing the bible based on memories, outliers, and words that don't belong.  Document decisions and reasons made.  Every flaw should be documented such as missing letters, bad punctuation."

### Decisions
- **Corruption index** per verse = weighted sum of signals: anachronism score + rarity + punctuation/emoticon flags + grammar flags + witness divergence + memory testimony. Weights are a documented decision to make when the signals exist; memory testimony weighs heaviest, scaled by its corroboration per Decision Log #5 — independent memory agreement and co-located artifacts, not witness confirmation (instructions.md Phase 7 + Premise Revision).
- **Candidate generation** priority order (Decision Log #5): (1) remembered text, weighted by corroboration (independent memory agreement and/or co-located alteration artifacts); (2) advisory — the wording of period witnesses (Geneva/Tyndale) adapted to KJV conventions; (3) advisory — Strong's-guided retranslation of the underlying Hebrew/Greek word. Advisory sources shape phrasing and fill gaps; they never veto a memory. The system proposes; a human approves — no restoration is final without review (`status` column).
- Every restoration row must be reproducible: which anomalies and witnesses drove it, and why the chosen reading won.

### Schema
```sql
CREATE TABLE restorations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id       INTEGER REFERENCES verses(id),
    flaw_type      TEXT,     -- 'missing_letter' | 'word_substitution' | 'punctuation' | 'missing_phrase' | ...
    current_text   TEXT,
    proposed_text  TEXT,
    rationale      TEXT,     -- the documented decision & reasons
    evidence       TEXT,     -- anomaly ids, witness readings, memory ids, lexicon entries
    confidence     REAL,     -- Bayesian-style: probability this is the original reading
    status         TEXT DEFAULT 'proposed'  -- 'proposed' | 'approved' | 'rejected'
);
```

### Tasks
- [ ] `scripts/12_corruption_index.py` — score every verse; ranked review queue
- [ ] `scripts/13_propose_restorations.py` — generate candidate readings for the top-scored verses, starting with the 11 memory-anchored passages
- [ ] Review workflow: walk proposals with the project owner, approve/reject, record rationale
- [ ] `scripts/14_export_restored.py` — emit the restored text per book (markdown), diffable against the current KJV

### Acceptance criteria
- The 11 memory-anchored passages each have a restoration row with rationale, evidence, confidence, and an owner-reviewed status.
- Restored output for at least one complete book (suggest starting with a Gospel) exported and readable.
- Zero undocumented changes: every difference between current and restored text traces to a `restorations` row.

---

## Backlog / Future Ideas (not scheduled)

- Stylometric author fingerprinting and multi-author book separation (instructions.md Phases 3–4) — needs Phases 2–4 data first.
- Alternate export with the Hebrew divine names inserted — "Yahweh" (יהוה) and "Adonai" (אדני) in place of LORD/Lord — as an optional reader's version (owner request 2026-07-14; Decision Log #6). Needs the same WLC/BibleForge divine-name alignment as the LORD recovery.
- Septuagint (Brenton) as an additional OT witness — PDF interlinear exists in `references/`; a machine-readable source would be needed.
- Cross-reference data (`formats/sqlite/extras/cross_references_*.db`) for parallel-passage consistency checks (instructions.md Phase 9).
- Character-count-preservation artifact search (instructions.md Phase 8) — `verse_stats.char_count` already collects the raw data.
