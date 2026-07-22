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
- [x] Create repo layout: `scripts/` for Python tooling, `db/` for the working database

### Phase 1 — Database & KJV Import (MVP)
- [x] Create a Database - Choose the most effective solution, either postgresql database created through docker or use sql lite. *[orig #1]*
- [x] Insert KJV in english into the database as MVP *[orig #2]*

### Phase 2 — Tokenization & Verse Statistics
- [x] Tokenize KJV counting occurances of word by book and total throughout the bible and save in tables *[orig #3]*
- [x] Count characters in each verse and store them in a database, identify outliers and long or short sentances. *[orig #4]*

### Phase 3 — Anomaly Detection
- [x] Identify rare words that don't belong in the KJV and words that did not see significant use during the era the KJV was written *[orig #5]* (machinery done; manual dating of the 2,815 uncleared words remains — see Phase 3 tasks)
- [x] Identify all parentheses and emojis that should not exist in the bible, place them in a database *[orig #6]*
- [x] Identify grammar errors where a sentance is written in a way that would not occur during the time the KJV was written *[orig #7]*

### Phase 4 — Cross-Translation Comparison
- [x] Convert the BibleForge MySQL dumps (word-level KJV, Strong's-tagged originals, lexicons) into the SQLite database
- [x] Identify and circle back to other bible translations and compare them to KJV. *[orig #8]*

### Phase 5 — Memory Reconciliation
- [x] Import `references/remembered_verses.md` into a structured `memories` table and cross-check each memory against the translation witnesses

### Phase 6 — Reconstruction
- [x] Start reconstructing the bible based on memories, outliers, and words that don't belong.  Document decisions and reasons made.  Every flaw should be documented such as missing letters, bad punctuation *[orig #9]* (machinery complete; owner review of the 62 proposals is the open loop — see Phase 6 tasks)

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
   - **Amended (owner, 2026-07-15): the correct verbatim is "spirit of the Lord"** — not "spirit of god" — and it applies bible-wide: all 96 Holy Ghost / Holy Spirit verses are replaced (review session 8; global pass in script 13).
   - **Sub-decision resolved (owner, 2026-07-14): LORD stays — as the exception, not the rule** (provisional; could change later). The divine-name distinction is preserved: "LORD" for the name YHWH and "Lord" for the title Adonai when they stand apart, and the customary combined forms where they meet ("LORD God" for YHWH Elohim, "Lord GOD" for Adonai YHWH). This is the sole exception to the no-ALL-CAPS rule.
   - **Recovery mechanism** (the base KJV.db collapsed the distinction to "Lord"): the WLC Hebrew re-derives which "Lord" is which — verified locally: יהוה (YHWH) in 5,790 verses, אדני (Adonai) in 753, both together in 379 (e.g., Ezekiel 2:4 "adonai yhwh") — supplemented by the BibleForge word-level KJV's `divine` marker column once Phase 4 parses it.
   - **Backlog option (owner request)**: an alternate export with the Hebrew names themselves — "Yahweh" and "Adonai" — inserted in place of LORD/Lord, for readers who want the true Hebrew names.

7. **Proper nouns excluded from era dating; names to be retranslated from Hebrew/Greek** (owner decision, 2026-07-14).
   - Names of people AND places (Noah, Jesus, Mary, Egypt, Jerusalem, Beth–el, ...) are transliterations, not English vocabulary, so first-attestation dating does not apply. They are removed from `references/uncleared_words.md` and carry verdict `proper_noun` in `word_era`.
   - Detection heuristic: a word whose every surface form in the KJV is capitalized (3,602 words). Words that also exist as common nouns (e.g. "mark", "job" appears capitalized only) keep their normal era verdict when lowercase uses exist.
   - **Retranslation direction**: names should derive from the original Hebrew/Greek forms rather than modernized/anglicized spellings (e.g. Noah ← נח Noach, Jesus ← Ἰησοῦς/ישוע). This needs the Phase 4 Strong's/original-language alignment; scheduled as a Phase 6 restoration workstream alongside the Yahweh/Adonai export (Decision Log #6 backlog).

8. **Phase 6 weights, candidate rules, and export policy** (Claude decision per owner delegation, 2026-07-14 — "you make the decision and continue; we will iterate over the MVP as necessary").
   - **Corruption index weights**: memory testimony dominates and is scaled by corroboration — corroborated 10.0, artifact-supported 6.0, unconfirmed 2.0 (summed if a verse is in multiple memories' scope); + internal anomaly scores summed per verse, capped at 5.0; + 0.3 for length outliers; + witness divergence (1 − median Jaccard vs Geneva/Tyndale/Wycliffe only) capped at 1.0 and marked advisory. Rationale: witness divergence can re-rank within a tier but never lift a verse across evidence tiers (Premise Revision).
   - **Candidate generation**: only corroborated and artifact-supported memories generate proposals (falsifiability anchor — unconfirmed memories are recorded, never restored; this is why Genesis 1:1 currently has no proposal despite its fame). Mechanical substitutions are regexes applied ONLY to the memory's scope verses, polysemy-guarded (couch→crouch fires only on "couch in", never the furniture noun). Phrase-level memories (lion & lamb, Lord's Prayer) get reserved rows with proposed_text NULL pending KJV-voice phrasing by the king-james agent. Confidence: corroborated 0.85, artifact-supported 0.65, phrasing-pending 0.5.
   - **Export policy**: `14_export_restored.py` applies only `approved` rows by default; `--include-proposed` produces an owner-preview with every change footnoted (id, flaw type, confidence, status, original text) — zero undocumented changes.
   - **Finding recorded during implementation**: the base KJV.db at Matthew 6:9–13 already reads thy/thy AND contains the doxology ("For thine is the kingdom, and the power, and the glory, for ever. Amen.") — the "Current KJV" quote in the Lord's Prayer memory entry was from a modern translation, not our base. Remaining deltas vs. memory: "in earth"→"on earth" (proposed) and debts→trespasses (phrasing-pending).

9. **Owner ruling on the agent word review: first-pass flags stand** (owner decision, 2026-07-14).
   - The two agent passes disagreed: the first pass flagged 64 of the 2,060 uncleared words; the second, verse-verified pass judged all 64 genuine 1611 vocabulary. The owner ruled the first pass correct — gravity (1 Timothy 3:4), heinous (Job 31:11), jurisdiction (Luke 23:7) and the rest **should not exist in the KJV** — consistent with the Premise Revision: presence in the base text and witness agreement prove nothing, since all texts are altered-timeline products; the second pass's evidence was textual, therefore advisory.
   - All 64 first-pass flags reinstated (verdict suspect/typo, source `owner ruling 2026-07-14`); the second opinion is preserved as an advisory note on each word. Every word carries an advised period alternate, preferring the KJV's own rendering of the same underlying Hebrew/Greek word elsewhere (gravity→honesty, heinous→lewdness, jurisdiction→authority, inflammation→burning, nephews→children, ...).
   - These words now generate `anachronism` anomalies (73 verses), feeding the corruption index. Their 69 substitution proposals were generated (script 13) and **owner-approved in full** (2026-07-14 review session 3, recorded in script 15) — **131 approved restorations total**.
   - **Owner correction (same day)**: "instructor"/"instructors" removed from the list — instructors IS the valid term. Instead, **"schoolmaster" is the corruption to remove** (Galatians 3:24–25): both render Greek παιδαγωγός (G3807), which the KJV itself gives as "instructors" at 1 Corinthians 4:15 — internal inconsistency supporting the ruling. schoolmaster → alternate "instructor". Final tally: 63 flagged words.

10. **MVP publication: PDF export + static website** (owner request, 2026-07-14).
   - `scripts/17_export_full.py` emits the full 66-book restored text as `exports/MandelaBible-MVP.pdf` (1,359 pages: title page, all books with changed verses marked `*`, and a Restoration Appendix listing every change with its original reading) plus `exports/MandelaBible-MVP.md`.
   - **PDF via a pure-stdlib writer** (built-in Times/Helvetica, WinAnsi encoding, Flate compression) — no PDF library exists in this environment and pip dependencies require a logged decision; a ~150-line internal writer keeps the stdlib-first rule.
   - `docs/` (GitHub Pages convention; renamed from `webpage/` by the owner, CNAME mandelabible.com) is the static site for **mandelabible.com** (owner-purchased): index.html + style.css (self-contained, responsive, light/dark), owner's `Logo.png` wired at `assets/logo.png`, downloads at `docs/downloads/`, GitHub repo linked (github.com/thomasmeadows/mandelabible — to be publicized later). README.md rewritten to link website, GitHub, downloads, and all reference files.

11. **TSBC Scribe auto-accept ruling** (owner decision, 2026-07-16).
   - Everything in the TSBC Scribe database (https://search.thesupernaturalbiblechanges.com/changes) is **auto-accepted as verifiable fact** — its memories rank as corroborated public memory testimony, its residue images as documented artifacts of the pre-change text.
   - **Verification = citation**: each accepted item cites the engine itself (`https://search.thesupernaturalbiblechanges.com/changeDetail/<changeID>` via the `/changes` search engine) in the restoration's `evidence` field; no independent verification pass is required.
   - **MVP updates automatically**: TSBC memories with a `restoredText` become `approved` restorations (script 22) and the MVP export (script 17) is regenerated without a per-verse owner review.
   - **Revisit-later clause**: any item later found inaccurate is revisited and reversed individually; the citation trail makes every TSBC-sourced change identifiable and revocable as a class.
   - Conflict guard: where a verse already carries an earlier approved restoration, the TSBC row is stored as `proposed` and logged for owner reconciliation rather than silently overwriting prior work (Content Modification Protocol).

12. **Rare-word replacement second pass: local witnesses over BibleGateway scraping** (owner-approved, 2026-07-16).
   - Owner audit of `references/rare_word_replacements.md` through line 132 found the auto-selected choices only ~50% acceptable; a second, evidence-backed pass was needed for the remaining 4,559 entries.
   - **Rejected**: scraping biblegateway.com verse-comparison pages (ToS/copyright issues with modern versions; slower; duplicates locally-held public-domain texts). **Chosen**: `scripts/23_rare_word_witnesses.py` pulls each unaudited verse from 13 local English witnesses (Wycliffe, Tyndale, Geneva1599, DRC, Webster, RWebster, YLT, Darby, ASV, UKJV, ACV, BBE, BSB) into `db/mandela.db` table `rare_word_witnesses`, and exports 40-entry review batches to `references/rare_word_witness_batches/batch_NNNN.md`.
   - The king-james agent re-selects per batch with the witness renderings as evidence, writing `batch_NNNN_proposals.md` (verdict KEEP/REVISE + rationale + full NEW verse). **Replacements need not be one-for-one** — a word may become several words or a rephrased clause where clarity requires (owner directive 2026-07-16). Surrounding function words must change with the new word: auxiliaries agree with its part of speech ("are accustomed" → "have learned", Jeremiah 13:23 owner ruling), a/an with its initial sound, and thee/thou inflections must survive (rules stored in the king-james agent's memory). **The flagged rare word must always be replaced with a genuinely different word or phrase** — keeping it or merely re-inflecting it ("accuser → accusers") is invalid, since under the premise the rare word is itself the suspected alteration artifact; where no period-authentic alternative exists the verdict is NO-SAFE-SWAP (owner ruling 2026-07-16). Modern witnesses inform meaning; period witnesses inform 1611 phrasing.
   - Batch 1 result: 17 KEEP / 23 REVISE — matching the owner's ~50% estimate. Proposals are advisory until owner review; surviving choices feed back into `rare_word_replacements.md` and then the db via the existing commit script.
   - **Inflection Deviation triage (owner directive 2026-07-17)**: a flagged word that is rare only as an *inflected* form (plural, possessive, tense, past tense, progressive, past participle, comparative, superlative) of a KJV-common base word is not genuinely rare and needs no replacement. `scripts/24_extract_inflection_only.py` moved 1,484 such unaudited entries from `rare_word_replacements.md` to `references/removed_words/rare_word_inflection_only.md` (the `removed_words/` folder holds all triaged-out-for-later-review files, owner request 2026-07-17), each annotated with the inflection kind, base word, and base KJV frequency (from `word_counts` bible-wide rows, latest tokenizer_version — per-book + per-version rows otherwise inflate counts ~4x). Ambiguous -er/-en forms (comparative-vs-agent-noun, participle-vs-verbification) and 10 audited-region candidates are listed in that file for owner ruling, NOT moved. Derivational forms (-ness, -ly, -tion, ...) never qualify. Proper nouns excluded by script 05's heuristic (3,602 words) are exported to `references/removed_words/rare_word_proper_nouns_research.md` for the Decision Log #8 name-restoration research. The same triage applied to `references/uncleared_words.md` (`scripts/25_uncleared_inflection_triage.py`, the owner's primary intent): 559 words moved to `references/removed_words/uncleared_words_inflection_only.md`, 30 ambiguous -er/-en forms flagged, 1,501 genuinely uncleared words remain for Phase 3 manual dating. Batch files/agent passes were deliberately left untouched at triage time; scripts 26/27 later moved the moot entries out of the batch and proposal files into `removed_words/` archives (append-only, provenance kept). **Further owner rulings 2026-07-17**: (a) NO-SAFE-SWAP verdicts are ~90-95% accepted as factual — the flagged word stays; (b) era kinship words are only husband/wife/brother/sister/father/mother, so compound the rest (grandmother → "mother's mother", II Tim 1:5); horseleach → probably "leach"; Jacob's ladder (Gen 28:12) is NOT changed; (c) new binding agent rule: never invert a verse's meaning — meaning-changing swaps are NO-SAFE-SWAP. When all batches complete, `scripts/28_split_proposals_for_review.py` splits proposals into `references/rare_word_review_no_safe_swap.md` (owner rulings) and `references/rare_word_ai_suggestions.md` (KEEP/REVISE suggestions). The fold-back step must skip proposals for moved entries.

13. **KJV-internal name spellings unified to the most common modern form** (owner directive 2026-07-18).
   - The KJV spells the same person/place multiple ways (OT Elijah/Isaiah vs NT Elias/Esaias; Hagar vs Galatians' Agar; Zion/Sion; Tyre/Tyrus; Zidon→Sidon). `scripts/35_normalize_kjv_names.py` applies a curated 68-pair variant→canonical mapping (validated: both spellings exist in KJV `word_counts`) as approved restorations, flaw_type `name_normalization` — **197 verses**, composed onto each verse's latest approved restoration. Report + evidence trail: `references/name_normalization.md`; witness-spelling evidence: `references/name_variants.md` (script 33).
   - Trap cases: Sion kept at Deuteronomy 4:48 (= Hermon, a different mountain); Jonas kept at John 21:15–17 (Simon Peter's father — ruling pending); Jesus→**Joshua** verse-scoped at Acts 7:45 and Hebrews 4:8 (Greek Ἰησοῦς names Moses' successor there).
   - **Owner ruling (2026-07-18): all 8 deferred pairs applied** — Elisabeth→Elizabeth, Enos→Enosh, Bosor→Beor, Sarepta→Zarephath, Oshea→Joshua globally; Aram→Ram verse-scoped to the genealogies (Matthew 1:3–4, Luke 3:33; Aram-the-region untouched), Heber→Eber at Luke 3:35 only (Judges' Heber untouched), Jona/Jonas→John at John 1:42 and 21:15–17 (Simon Peter's father; the prophet stays Jonah). Total now **216 verses**; export regenerated (3,560 restored verses, 1,649 pages), docs/downloads updated.
   - **Pharez→Perez applied bible-wide (owner ruling 2026-07-18)**, matching the TSBC-approved modern form at Matthew 1:3 (Phares also now → Perez). Total **226 verses**; export regenerated (3,570 restored verses, 1,650 pages), docs/downloads updated.

14. **Residue evidence rank** (owner ruling 2026-07-19).
   - Residual images/scans (TSBC residue and similar) **cannot be assumed pre-Mandela-effect** — some may be, some may not. A residue reading is *considered but not ranked above the current text* unless it either (a) **covers a large section** — a multi-word/whole-verse restructuring, not a single-word swap — or (b) has been **confirmed to lean toward memories** of the verse (agrees with rows in `memories`/`remembered_verses.md`).
   - Worked example: the Psalms 105–106 block was accepted because it is grammatically correct, appears in the format the KJV was well known for, and is far more than a single-word replacement.
   - What residuals are truly for: **drastic changes to what currently exists in the KJV**, where the residue reading is **confirmed to NOT belong to another bible version** — a residue that matches ASV/Geneva/Darby/etc. is most likely a quotation of that version, not pre-change KJV residue. Version-attribution is therefore a required check on every residue variant (implemented in `scripts/46_tsbc_residue_scan.py`).
   - Consequence for the 63 VARIANT entries in `tsbc_residue_placements.md`: single-word variants (cloak/corn/bottle/test/afresh etc.) are NOT automatic restoration candidates even where they echo pre-rare-word-swap readings; they stay advisory unless memory-confirmed.

15. **Blacklist "no safe swap" noise → whitelist** (owner directive 2026-07-20).
   - The owner spotted that `word_blacklist.md` contained entries whose description said "King James agent: no safe one-word swap found — edit or delete this entry" — round-1 boilerplate meaning the word was flagged for review but **never actually replaced**. Listing it in a *blacklist of changed words* was wrong; a word that was never changed belongs on the whitelist, or nowhere if already there.
   - Fix: `scripts/49_build_blacklist.py`'s `round1()` now excludes any row carrying that boilerplate (249 rows / 184 words dropped: 2,619→2,435 words, 3,576→3,327 entries; re-run with the new `--allow-shrink` flag, since a legitimate correction can shrink the count). `scripts/29_build_whitelist.py` gained a third source — orphaned round-1 no-safe-swap flags not already in the owner-reviewed `rare_word_review_no_safe_swap.md` — added under a distinct "Orphaned round-1 no-safe-swap flags" heading (165 reviewed + **95 orphaned** + 3,602 proper nouns).
   - Of the 196 no-safe-swap words found: 101 were exact duplicates of words already on the whitelist (pure noise, dropped); 95 had never been owner-reviewed anywhere and are now whitelisted with their round-1 OLD-verse-text as evidence, pending owner spot-check.

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
- `remembered_verses.md` — the documented memory anchors (Genesis 1:1, bottles/wineskins, lion & lamb, Lord's Prayer, couch/crouch, divers/diverse, tables/tablets, spirit of error, charity/love, matrix/womb, parentheses/emoticons, eyes-to-see, destroyed/perish, capitalization/Holy Ghost, serpent's head, windows/floodgates-of-heaven, thanksgivings, money/love-of-money, judge-not-lest, strait/straight, in-earth/on-earth, Philippians-4:13-who/which, wizards/sorcerers). **Primary reconstruction evidence** (Phase 5).
- `King James Writing Sample - The Essayes of a Prentise in the Divine Art of Poesie.txt` — King James's own writing; period-authentic Early Modern English vocabulary evidence.
- Middle English texts (`The Canterbury Tales`, `The Book of Quinte Essence`, `The Wright's Chaste Wife`, the Middle English Reader) — a word attested in these existed **before** 1611, useful for first-attestation dating (Phase 3).
- `Interlinear Greek-English Septuagint Old Testament - print.pdf` — Septuagint witness for OT passages.
- `Rather Exhaustive List of Mandela Effect Affected Scriptures _ Truth Farmer.pdf` — candidate passage list to seed Phase 5.
- `instructions.md` — mission framing and the ten-phase restoration methodology this roadmap implements.
- `general_references.md` — external links.
- `sources.md` — comprehensive source list (all data sets, reference texts, and public Mandela-effect-Bible literature; compiled 2026-07-15).
- `blog_search_references/` — raw multi-engine search results (chatgpt ×2, claude, grok, leo) cataloguing the public bible-changes literature; fed 9 new community-reported entries into `remembered_verses.md` on 2026-07-15 (two-or-more, name-is-Jealous, lying-signs word order, set-you-free, Luke bank/stuff, Moses' basket, sword/division, prophetic-frame verses).

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
- [x] Create `scripts/` and `db/` directories with a short `scripts/README.md` explaining the numbering convention
- [x] Decide whether `db/mandela.db` is committed to git or gitignored-and-rebuildable — **DECIDED: gitignored-and-rebuildable** (`.gitignore` updated; every table must be rebuildable from `scripts/`)

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
- [x] `scripts/01_create_db.py` — creates `db/mandela.db` with the schema above
- [x] `scripts/02_import_kjv.py` — ATTACHes scrollmapper `KJV.db`, copies books + verses + translation metadata (all acceptance checks pass; note: scrollmapper names book 66 "Revelation of John")

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
- [x] `scripts/03_tokenize.py` — tokenize all KJV verses, fill `word_counts` (per-book and totals)
- [x] `scripts/04_verse_stats.py` — fill `verse_stats`, compute per-book z-scores, mark outliers
- [x] Document the tokenizer rules actually implemented (in the script docstring and here)

### Tokenizer v1 — rules as implemented & results (2026-07-14)

- Token = maximal run of letters plus **internal** apostrophes/hyphens:
  `[A-Za-z]+(?:['-][A-Za-z]+)*` — "serpent's" and "Baal-zebub" are single
  tokens; all surrounding punctuation is stripped.
- Counting is lowercase in `word_counts`; original-case surface forms are
  preserved in a `word_forms` table (schema addition beyond the sketch above —
  capitalization is evidence per Decision Log #6).
- Every row stores `tokenizer_version = 1`.
- **Measured results**: total word count **792,364** (≈790k ✓); 12,456
  distinct lowercase words; top tokens the (63,944), and (51,701), of
  (34,626) ✓. `verse_stats` has 31,102 rows, 1,214 outliers at |z| > 2
  within book. Longest verse: **Esther 8:9** (528 chars) ✓; shortest:
  John 11:35 "Jesus wept." (11 chars).

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
- [x] `scripts/05_word_era.py` — build the cleared-word list from local pre-1611 corpora; emit the uncleared list for dating
- [x] `scripts/06_punctuation_audit.py` — character/parenthesis/emoticon inventory into `anomalies`, plus the capitalization audit (Decision Log #6)
- [x] `scripts/07_grammar_checks.py` — the EME rule checks into `anomalies`
- [x] Date/validate the uncleared word list — **done via king-james agent review + owner ruling (2026-07-14, Decision Log #9)**: 8 parallel first-pass batches over all 2,060 words flagged 64 words; a verse-verified second-opinion pass argued all 64 were period; the **owner overruled the second opinion** — the flagged words "should not exist in the KJV" — so the 64 stand as suspect (63) / typo (1), each with a period alternate grounded in the KJV's own rendering of the same Strong's word elsewhere (gravity→honesty via G4587 "honesty" at 1 Tim 2:2; heinous→lewdness via H2154 ×14; jurisdiction→authority). The remaining 1,996 words are period (corpus-coverage gaps, not corruption). Verdicts + layered notes in `word_era`; TSVs in `references/word_reviews/` (batches, second_opinion, owner_alternates); report `references/word_review_report.md`; 73 `anachronism` anomaly rows now feed the corruption index.
- [ ] Owner review of `references/rare_word_alternatives.md` (owner directive 2026-07-15; generated by `scripts/18_rare_word_alternatives.py`): all 3,460 remaining 1–2-use words with KJV same-Strong's parallel renderings and per-witness other-bible alternatives — rulings feed back as word_era verdicts / restoration proposals
- [ ] Owner review of `references/rare_word_replacements.md` (owner directive 2026-07-16; generated by `scripts/19_select_rare_word_replacements.py` + king-james agent pass): one auto-selected replacement per rare-word verse, OLD/NEW side by side. Selection priority: aligned KJV-family translations (Webster/UKJV/AKJV) and same-testament KJV Strong's parallels first, other translations second; 1,333 heuristic-flagged entries re-picked by the king-james agent (340 marked no-safe-swap). Owner edits/deletes entries; a follow-up script commits survivors to the db. **Audited through line 132 (2026-07-16)**; remaining entries go through the witness second pass below (Decision Log #12)
- [x] **Fold-back DONE 2026-07-18** (`scripts/41_fold_back_proposals.py`): the approved suggestions (`rare_word_ai_suggestions.md`, the file script 30 applied) were span-merged per verse and folded into `rare_word_replacements.md` — 2,455 verses merged, 2,053 `- NEW:` lines updated (only NEW-line content changed; line numbers preserved for the batches' `md line:` references); pre-fold backup kept at `references/removed_words/pre_triage_backups/rare_word_replacements_pre_foldback_2026-07-18.md`. 5 span conflicts left unapplied in `references/rare_word_fold_back_conflicts.md`: 4 are the already-owner-resolved 2026-07-17 verses (db carries the owner texts), and **Matthew 13:8 (thirtyfold/sixtyfold overlap) is NEW and needs an owner ruling**. Original item follows: Rare-word witness second pass (Decision Log #12): run the king-james agent over `references/rare_word_witness_batches/batch_NNNN.md` batches (114 batches of 40; generated by `scripts/23_rare_word_witnesses.py --export FIRST LAST`), producing `batch_NNNN_proposals.md` for owner review — **ALL 114 batches complete 2026-07-17**; proposal batches 1–20 audited by the owner (approved or removed); split files generated and **owner-reviewed**; **AI suggestions APPLIED 2026-07-17** (`scripts/30_apply_rare_word_suggestions.py`): 2,455 verse restorations (flaw_type `rare_word_swap`, span-merged per verse — multi-entry verses like I Samuel 13:21 compose correctly), each carrying the per-word AI footnotes (rationale) plus the owner's standard replacement note with the GitHub-issue link (evidence); the 109 prior-restoration collisions were auto-merged onto the memory/prior text (75 clean, 34 conflicts owner-audited in `rare_word_proposed_reconciliation.md`) and **all approved 2026-07-18** with a notation block recording that each verse varies slightly from its prior restoration due to a rare-word violation, the 4 overlapping-span conflicts owner-resolved and applied 2026-07-17 (Daniel 11:20, Isaiah 24:2, Isaiah 59:5, Malachi 3:2 — `rare_word_merge_conflicts.md`); MVP export regenerated (1,597 pages, 3,143 restorations) and docs/downloads updated; when complete, run `scripts/28_split_proposals_for_review.py` then fold approved proposals back into `rare_word_replacements.md`. **Fold-back must MERGE multi-entry verses, not overwrite (owner directive 2026-07-17)**: each proposal's NEW is the full verse with only its own word swapped, and 335 verses carry 2-6 proposal entries each (745 entries; e.g. Deuteronomy 18:11, I Samuel 13:21 ×6) — the fold-back script must compute each proposal's changed span (diff of its OLD vs NEW) and apply all spans onto one evolving verse text, flagging overlapping/conflicting spans for owner resolution instead of applying either
- [x] **Priority subset (owner directive 2026-07-14): validate every non-proper-noun word with 1–2 occurrences bible-wide for period accuracy** — covered by the same agent review (every 1–2-occurrence non-proper word is either corpus-cleared or in the 2,060 reviewed); the wizard/magician/thanksgiving families remain the standing suspects via memory + era artifacts
- [x] **DONE 2026-07-18** (owner directive; `scripts/36_retokenize_restored.py`): re-tokenize the RESTORED text (all approved restorations composed, same composition as the MVP export — not the old KJV) and regenerate the rare-word list. Counts stored as translation `KJV_restored` in `word_counts`/`word_forms` (790,409 words, 10,889 distinct, tokenizer v2). Exclusions per directive: whitelist words, proper nouns (script 05 heuristic + capitalized-only in the restored corpus, catching restoration-introduced names like Perez/Elizabeth), and inflectional variants grouped with their base word (script 24 suffix rules) — rarity judged on group totals, so inflections of common words are not deviations. Result: **341 rare groups (count ≤ 2)** in `references/rare_words_restored.md`. **Finding**: some rare words were introduced BY restorations themselves (acacia Exodus 25:10, alert Genesis 1:26, artisan Exodus 39:3, attack Esther 8:11, across I Kings 6:21 — from TSBC/rare-word swap texts); these are owner-review candidates for a follow-up pass
- [x] **DONE 2026-07-18** (`scripts/37_sampson_gen40_fixes.py`, flaw_type `owner_memory_fix3`, 38 verses): **Samson → Sampson bible-wide** (owner memory; corroborated by the TSBC Judges 13:24 change record "originally spelled Sampson, with a letter 'p'" and Wycliffe's 32 Sampson readings) — all Judges occurrences + Hebrews 11:32; **two defective restoration rows repaired by supersession** (never deleted): the TSBC Judges 13:24 row had stored the change *description* as verse text, and the Genesis 40:17 rare-word merge had produced "of all manner of d goods" — both reset to owner-supplied full-verse readings ("...all manner of goods..."). Memories recorded in `remembered_verses.md`; export regenerated (3,602 restored verses, 1,653 pages), docs/downloads + index.html updated; rare-word list regenerated (337 groups; script 36 gained `--allow-shrink` for legitimate shrinks). **Owner ruling 2026-07-18: "lean towards the TSBC, until told otherwise"** — restoration row 3808 (Mark 15:34, TSBC) reads just the bare quote «"Father, Father, why hath thou forsaken me?"»; per the ruling the TSBC text STANDS as-is (this generalizes: TSBC readings are kept even when partial/unusual, revisited only on explicit owner instruction — consistent with Decision Log #11's revisit-later clause)
- [x] **DONE 2026-07-18** (`scripts/38_owner_overrides.py`, flaw_type `owner_override` — the standing home for future owner full-verse overrides of TSBC/prior rows): **Genesis 1:2 owner override of TSBC row 3598** — TSBC's "darkness was upon the surface of the waters ... moved upon the surface of the waters" replaced by the owner's remembered "And the earth was void and without form; and darkness was upon the face of the deep: and the Spirit of God moved upon the waters." (first exercise of the revisit-later clause); memory recorded in `remembered_verses.md`; export regenerated (3,602 restorations, 1,654 pages), docs/downloads + index.html updated
- [x] **DONE 2026-07-18** — Rare-word round 2 (restored-text list): `scripts/39_rare_word_witnesses_round2.py` exported the 337 `rare_words_restored.md` groups as 9 witness batches (40 groups each, CUR = composed restored text + 13 witnesses) into `references/rare_word_witness_batches_2/`; king-james agent audited every group under **revised owner rules (2026-07-18)**: every entry must carry BOTH a best-effort replacement suggestion (common-KJV word/phrase, corpus-frequency-checked against `KJV_restored`) AND, where warranted, a separate whitelist argument — and the whitelist argument may NOT cite the KJV itself as authentic (the KJV cannot self-certify under the Premise Revision; valid grounds: unique referent, memory-restoration testimony, irreplaceable wordplay). Outputs preserved per the generated-artifact directive: `batch_NNNN_proposals_v2.md` (revised-rules run, all 9 complete) alongside the first-run `batch_0001/0002/0009_proposals.md` (superseded, kept). `scripts/40_split_round2_proposals.py` split the v2 set into two owner-review files in the same folder: `round2_ai_suggestions.md` (361 REPLACE) and `round2_whitelist_and_no_safe_swap.md` (19 WHITELIST + 21 NO-SAFE-SWAP)
- [x] **Owner-approved & APPLIED 2026-07-18** (`scripts/42_apply_round2.py`; owner ruling: "replacements and safe words seem to be accurate — fold the no-safe-words into the whitelist and update the replacement verses"): 31 words (19 WHITELIST + NO-SAFE-SWAP verdicts, both folded) added to `word_whitelist.md` as the "Round-2 reviewed words" section with per-verse reasons; 351 verse restorations applied (flaw_type `rare_word_swap2`, span-merged against the composed restored base, 0 conflicts), including a repair-by-supersession of Acts 19:9's stray "(unchanged) " prefix (round-1 batch artifact baked into rows 3959/6767; defective rows kept). Two agent-flagged DATA ANOMALY entries excluded from the fold: "surface" Genesis 1:2 (stale — the owner override had already removed the word) and "unchanged" Acts 19:9 (the artifact above; its separate "speaking council" vs unanimous-witness "school" observation stands per the round-1 approval). Rare-word list regenerated: **337 → 10 rare groups** (residuals are mostly round-2 replacement words that themselves landed at 1–2 uses: cunningly, evil-speaking, fork, uncertain, vulture, etc. — candidates for a small round 3 or whitelisting). MVP export regenerated (1,684 pages, **3,657 restorations**); docs/downloads + index.html updated
- [x] **DONE 2026-07-22** — Rare-word round 5 (100 rarest lemmas over current output, `scripts/62_round5_rare_words.py` review file + KJ agent proposals merged by 63/64): owner ruled every entry in `references/rare_word_round5_review.md`; wording questions settled via the owner-annotated preview (`references/rare_word_round5_apply_preview_owner_annotated.md`, preserved; regenerated preview by `scripts/65_round5_preview.py`). Applied by `scripts/66_apply_round5.py` (flaw_type `round5_review`, own-flaw-type-excluded loader for idempotency, verified no-op on re-run): **91 verse restorations** (incl. Galatians 5:21 owner rewrite, Acts 26:5 owner rewrite, Judges 5:16 tribes/divisions, Colossians 1:22 collapsed to single "blameless", Matthew 3:12 storehouse+everlasting), blacklist source `rare_word_round5_replacements.md` (97 entries, 70 words; `49_build_blacklist.py` round5() added → 2,583 words/3,910 entries), round-5 whitelist section in `rare_word_review_no_safe_swap.md` (113 protected: 34 WHITELIST-keeps incl. adders/seraphims/witch/sorceress/vulture + introduced readings + owner-named glutton/gluttonous/revilings/sneezed/rebuketh/scoffings/musicians/elements/selfwill/selfwilled/pleasers/betrayeth; whitelist now 566 reviewed). Export regenerated (1,772 pages, **4,311 restorations**)
- [ ] Source-era referent verdicts (Axis 2, Decision Log #4): run the `king-james-middle-english-expert` agent over flagged senses; fill `word_era.source_verdict` (the "bottles" acceptance check lands here)

### Phase 3 — results as measured (2026-07-14, tokenizer v2)

- **Tokenizer v2 note**: the base text uses curly apostrophes (’ ×1,996,
  "wife’s") and en-dashes (– ×786, "Beth–el"); v1 split these — v2 treats
  them as internal joiners and normalizes to ASCII. Total word count is now
  **789,814**. The raw non-ASCII characters remain flagged as `punctuation`
  anomalies (1611 printing used ' and -).
- `word_era`: 12,747 words — 3,602 proper nouns (excluded from dating,
  Decision Log #7), 7,085 cleared (advisory), 2,060 uncleared →
  `references/uncleared_words.md` for manual dating. "matrix" is *attested*
  in Tyndale (altered-timeline text, advisory only) but still rare-flagged 5×.
- `anomalies`: rare_word 10,401 (proper-noun-only words excluded), punctuation
  2,881 (incl. 222 `(` + 222 `)` pairs), emoticon **93** (e.g. `...Zoar;)`),
  grammar 413 (R1 `its` ×1 — Leviticus 25:5; R2 mixed second-person ×385 —
  fires on Matthew 6:9 ✓; R3 modern bare verbs ×27), capitalization 349.
- **Measured vs Decision Log #6 estimates**: exact-case "Holy Ghost" = 90
  (not 89), exact "Holy Spirit" = 1 (the other 6 are "holy Spirit", caught by
  the mid-verse Spirit check), ALL-CAPS LORD/GOD/JEHOVAH verses = 8 (not 9;
  the log's 9th is a non-divine ALL-CAPS token also captured). The audit's
  numbers are authoritative; the log's were exploratory estimates.
- Documented gap in 07: full -eth/-est conjugation checking and n-gram idiom
  comparison deferred (need POS tagging / n-gram models) until the simple
  rules' output is reviewed.

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
- [x] `scripts/08_import_witnesses.py` — attach & copy the witness translations into `verses`/`books`
- [x] `scripts/09_convert_bibleforge.py` — parse the MySQL dumps into the `bf_*` and lexicon tables
- [x] `scripts/10_verse_diffs.py` — align and diff every KJV verse against each witness

### Phase 4 — results as measured (2026-07-14)

- All 12 witnesses imported; row counts recorded by script 08 (Geneva1599
  31,064 / Wycliffe 31,378 / Tyndale 7,888 — Tyndale ships 23,214 empty rows
  for books he never translated, skipped; TR 7,957 NT verses; WLC 23,213 OT
  verses). Witness book ids are remapped to KJV ids **by book name** —
  verified necessary: Wycliffe's own file numbers books differently.
  Wycliffe/DRC apocrypha (Tobit … Laodiceans) have no KJV counterpart and are
  logged as unmapped, not force-aligned.
- BibleForge conversion: `bf_words_en` 814,695 rows ✓, `bf_words_orig`
  446,232 rows, `lexicon_greek` 5,523, `lexicon_hebrew` 9,289. The `divine`
  marker covers 6,888 word rows (feeds the LORD/Adonai recovery, Decision
  Log #6).
- `verse_diffs`: every KJV verse diffed against each English witness
  (similarity = token-set Jaccard; TR/WLC excluded — cross-language string
  similarity is meaningless). Missing verses logged per witness (Wycliffe
  858, DRC 810, Geneva 39, KJVPCE 4).
- **Acceptance validation passed**: Matthew 9:17 vs Geneva/Tyndale/Wycliffe
  surfaces "bottles" as KJV-only (Wycliffe reads "botels"), and the word-level
  chain resolves KJV "bottles" → ἀσκοὺς → Strong's G779 → lexicon "a leathern
  (or skin) bag" — the wineskin memory's source-language support, now
  queryable.

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
- [x] `scripts/11_import_memories.py` — parse `remembered_verses.md` into `memories`
- [x] Cross-check every memory against Phase 4 witnesses and Phase 3 anomalies; record corroboration per Decision Log #5 — corroboration means independent memory agreement and/or co-located alteration artifacts; witness readings are logged as advisory context only (agreement with the KJV neither confirms nor refutes a memory)
- [x] **DONE 2026-07-18** (`scripts/31_manual_word_changes.py`: 242 verses, flaw_type `manual_word_change`, composed onto each verse's latest approved restoration; emoticons were already fixed by the punctuation workstream; charity partly pre-converted by TSBC rows; inflected forms owner-ruled 2026-07-18: saluted→greeted, saluteth→greeteth, salutation(s)→greeting(s) (261 verses total); buildedst (1) and girdedst (2, whitelisted) remain; `scripts/32_owner_memory_fixes.py` applied the owner memory overrides — I John 4:6 "spirit of error"→"spirit that leads astray" (memory #77) and the nine eyes-to-see/ears-to-hear verses (memory #81, rulings 3a–3i: John 8:11, Luke 14:35, Luke 8:8, Mark 7:16, Mark 4:23, Mark 4:9, Matthew 13:43, 13:9, 11:15), both memories now status `owner-confirmed`; export regenerated 3,368 restorations) — Update all verses using the manual_word_changes_flagged.md item list
- [x] **DONE 2026-07-18** (`scripts/34_owner_memory_fixes2.py`, flaw_type `owner_memory_fix2`): four owner-supplied Genesis memories applied as approved restorations and recorded in `remembered_verses.md` — Genesis 2:20 "an help meet for him"→"a helper fit for him", Genesis 2:24 "one flesh"→"as one flesh", Genesis 3:24 "to keep the way of the tree of life"→"to guard the way to the tree of life", Genesis 4:15 "should kill him"→"should smite him"; MVP export regenerated (3,372 restorations, 1,631 pages) and docs/downloads updated
- [x] **DONE 2026-07-18** (`scripts/33_name_variants.py` → `references/name_variants.md`: 2,846 of 3,503 proper-noun forms have at least one variant spelling across the 10 English witnesses; per-name, per-witness variant + count + example ref; difflib similarity ≥ 0.72 heuristic, advisory only — feeds the Decision Log #7 name-retranslation research; validated on agar→hagar: Wycliffe/DRC "Agar" listed under Hagar; overwrite guard refuses an emptier regeneration) — Create a list of all locations and names and any variances of those names in other translations.  (ie. agar -> hagar)
- [x] **DONE 2026-07-18** (Decision Log #13; `scripts/35_normalize_kjv_names.py`): unify KJV-internal name spellings to the most common modern form — 197 verses, 68 mappings + 2 verse-scoped Jesus→Joshua fixes, trap-case exclusions honored; report `references/name_normalization.md`; MVP export regenerated (3,543 restored verses, 1,648 pages) and docs/downloads updated; 8 ambiguous pairs deferred for owner ruling
- [x] **APPLIED 2026-07-18** (`scripts/44_apply_mixed_inflections.py`, flaw_type `mixed_inflection`, 220 verses; owner ruling: all report recommendations, ties ruled **sprang → sprung** and **drave → drove**, **girdedst de-whitelisted → girded** (whitelist link removed 165→164, reason section annotated, entry kept)): all 22 groups unified onto the majority form (incl. begun→began ×13, doest→dost ×45, drunk→drank ×30, gat+gotten→got ×45, stricken→struck ×18, shone→shined ×8, show→shew ×2); post-apply detector finds 0 groups; report preserved with APPLIED annotation
- [x] **DONE 2026-07-18** (`scripts/45_manual_verse_corrections.py`, flaw_type `manual_verse_correction`, 42 rows): the 39 owner-supplied full-verse readings in `references/manual_verse_corrections.md` applied as approved restorations (Genesis 1:2/2:2/2:3, Revelation 1:5/19:7, Isaiah 11:6–9, Psalms 105:21–44, 106:1–6 — the Genesis 1:2 "face of the earth" reading supersedes script 38's "face of the deep" override, newest owner ruling wins) plus **Alleluia → Hallelujah** bible-wide (owner ruling; Revelation 19:1/3/4 swapped, 19:6 already read Hallelujah). MVP export regenerated (1,706 pages, **3,884 restorations**), docs/downloads + index.html updated. Note: the manual corrections introduce 12 new 1–2-count words into `rare_words_restored.md` (now 22 groups: boundary, detective, displayed, eternity, exult, fig-trees, gnats, happiness, herbage, insects, reseted, various, wrongly...) — memory-sourced wording, so left untouched pending owner direction; "reseted" (Genesis 2:2) was **owner-confirmed a typo and corrected to "rested"** (md fixed, re-applied, list now 21 groups); "detective signs" (Psalms 105:27) was **owner-confirmed a bad OCR scan and corrected to "effective signs"** (md fixed, re-applied)
- [x] **DONE 2026-07-18** (`scripts/43_mixed_inflections.py` → `references/mixed_inflections.md`, report only): **22 mixed-inflection groups** in the composed restored corpus, three detectors — curated irregular past-tense doublets (begun/began, gat+gotten/got, holpen/helped, holden/held, stricken/struck, shined/shone, sung/sang, drunk/drank, lien/lain, wringed/wrung, shew×229/show×2), archaic 2nd-person -edst alongside the plain past (calledst, commandedst, deliveredst, girdedst [whitelisted, marked do-not-change], promisedst, stainedst, trustedst), and contracted -st vs full -est (dost×56/doest×45). Each minority form gets a → majority recommendation with verse refs; two exact **TIES flagged for owner ruling** (drave×13/drove×13, sprung×7/sprang×7). Cautions for the owner pass: several doublets carry sense distinctions (drunk as adjective vs drank as past; "stricken in years" idiom), and "builded/built" no longer appears — builded was already resolved by earlier passes. -eth vs -s pairs deliberately excluded (would be noise without POS data; noted in the script docstring). Original item: Create a list of words that are using mixed Inflection.  (IE built and builded, cursed and cursedst).  Builded is the archiach use of the past tense of build and the modern equivelent is built.  Most of the bible uses built, so builded should be scrapped in place of the modern built.
- [x] **DONE 2026-07-19** (`scripts/50_strait_to_straight.py`, flaw_type `strait_straight`, 12 verses; owner directive): **strait/straits → straight/straights** bible-wide, case-preserving (e.g. Matthew 7:13-14 "straight gate"). Derived forms deliberately untouched pending owner ruling — straitly ×13, straitened ×8, straitness ×5, straitest ×1 carry the sense "strictly/constrained" where "straightened" would change meaning. Blacklist entry added — Change all instances of strait to straight. (Counts corrected after the kjvrestore fold repair: **11 verses**, rebuilt after the folds; current export 1,719 pages, 3,988 restorations)
- [x] **DONE 2026-07-19** (`scripts/49_build_blacklist.py` → `references/word_blacklist.md`; owner request 2026-07-19): companion to the whitelist — **2,618 blacklisted words, 3,575 change entries** aggregated from every word-level pass with replacement, reason, and decider (Human owner ruling vs AI agent with owner approval): rare words round 1 (3,100 entries, decider parsed from each entry's source line — User/Owner rulings marked Human), round 2 (361, AI king-james), mixed inflections (22, incl. the 3 owner rulings sprang/drave/girdedst), owner manual word changes (18 incl. Alleluia→Hallelujah; emoji cleanups excluded as not words), name normalization (74, Decision Log #13). Alphabetical anchor-linked index; overwrite guard refuses a smaller regeneration — Create a black list of words that were changed and why they should be changed and if the decision was by an AI agent or human
- [x] **CORRECTED 2026-07-20** (Decision Log #15): owner spotted "no safe one-word swap found" noise on the blacklist (words never actually changed). `round1()` now excludes those rows; blacklist is now **2,435 words, 3,327 entries**. The 196 affected words: 101 were duplicates of existing whitelist entries (dropped outright), 95 were never owner-reviewed and are now on the whitelist instead (`scripts/29_build_whitelist.py`, new "Orphaned round-1 no-safe-swap flags" source, 165 reviewed + 95 orphaned + 3,602 proper nouns). `--allow-shrink` flag added to 49's overwrite guard for this kind of deliberate correction.
- [x] **DONE 2026-07-17** (`scripts/29_build_whitelist.py` → `references/word_whitelist.md`: 165 owner-reviewed no-safe-swap words with per-word rationale + 3,602 proper names/places with shared rationale; regenerate after any further NSS review edits) — Create a whitelist of words that should not be changed or only changed in tense because they are proper names or locations or common fruts, foods, herbs, or trees.  List the words at the top in alphabetical order and link to a description in the area below the list on why the word shouldn't be altered unless modernizing.  This can also include rare words and rare forms of words and the decision behind not altering the word.
- [x] **DONE 2026-07-19** (`scripts/47_harvest_kjvrestore.py` → `references/kjvrestore_comparison.md`; owner crawl intel 2026-07-19: pages at `?page_id=###`, WordPress SSR, restored readings in `<span style="background-color: #ffff00;">`): all **80 pages** discovered via nav BFS and cached permanently in `references/kjvrestore_pages/` (server 406s short User-Agents — full browser UA required); **3,032 verses across 28 partially-restored books** parsed into `kjvr_pages`/`kjvr_verses`/`kjvr_highlights` (rebuilt each run from the caches); **232 highlighted restored readings** compared against our KJV base + composed restored text: **20 AGREES-WITH-OURS** (independent corroboration, e.g. Genesis 1:1 "heavens"), **178 DIVERGES** (their reading differs from base and ours — owner-review candidates; **12 collide with `memories` refs** incl. Matthew 6:9/6:10, Matthew 9:17 ×4, Genesis 3:15 ×2, 2 Thessalonians 2:9 "lying signs and wonders"), 32 MATCHES-BOTH, 2 THEY-KEPT-BASE (Leviticus 2:7 "pan", Isaiah 11:7 deletion marker). Site convention: a highlighted literal "X" marks a word they deleted. **FOLDED IN 2026-07-19** (owner directive: "Fold in all kjvrestore_comparison.md items in the file, make sure to remove the stars \*\*"; `scripts/48_fold_kjvrestore.py`, flaw_type `kjvrestore_fold`): all 180 DIVERGES/THEY-KEPT-BASE entries applied as approved restorations — **143 verses** (multi-highlight entries collapse; \*\* stripped; literal X deletion markers removed with whitespace cleanup; report parse guards refuse if same-verse entries disagree). **CORRECTED 2026-07-19 after owner flag ("you broke some things… you did not re-read the file and respect my changes")**: the owner had *curated* the report before the fold (DIVERGES section only, 5 defective entries deleted) — I misdiagnosed the curated file as a truncated write, regenerated the report over the owner's edits, and folded all 180 entries including THEY-KEPT-BASE. Repair: fold restricted to **DIVERGES only** with a **multi-verse contamination guard** (script 47's verse parser had swallowed following verses into six "their verse" lines — Genesis 5:2, Isaiah 3:2, Isaiah 11:6 [was overriding the owner's memory correction], Matthew 2:17, Matthew 7:7, Revelation 2:21 — a reading >1.5× our verse length is skipped and reported); `strait_straight` rows rebuilt after the folds since the Matthew 7:7 contamination had leaked into one. Final: **135 folded verses**; export regenerated (1,719 pages, **3,988 restorations**), docs/downloads + index.html updated. The owner's exact curated file could not be recovered (working-tree only, overwritten); lesson recorded in agent memory: owner-reviewed files are re-read, never regenerated. Advisory corroboration only per the Premise Revision — original item: Cross-reference **The KJV Restoration Project** (https://kjvrestore.org/ + companion Amos8.org; owner directive 2026-07-16, catalogued in `sources.md` §IV) — a fellow recreation/restoration project: harvest its claimed-change list, per-change articles, and any restored readings; compare against `remembered_verses.md` (new independent-rememberer corroboration candidates) and our restoration proposals. Advisory corroboration only — never a veto (Premise Revision)
- [ ] **Harvest the TSBC Scribe database** (https://search.thesupernaturalbiblechanges.com/changes; owner directive 2026-07-16, API details in `sources.md` §IV — 355 changes, **398 new memories**, **249 residual images** of the pre-change text). Action items:
  - [x] `scripts/21_harvest_tsbc.py` — **done 2026-07-16**: 355/355 changes, 363 memories (35 of the server's 398 are not linked to any change and no API endpoint exposes them), 209 residue records into `tsbc_changes`/`tsbc_memories`/`tsbc_residue`; idempotent re-run
  - [x] Download residual images into `references/tsbc_residue/` — **done 2026-07-16**: 206 of 209 linked files downloaded (3 are 404 on the server; the server counts 249 images total, the rest belong to the unlinked memories)
  - [x] **Apply TSBC memories to the MVP** (`scripts/22_apply_tsbc_restorations.py`, auto-accept per Decision Log #11) — **done 2026-07-16**: 300 verses had a TSBC `restoredText`; 259 approved restorations inserted (engine citation in `evidence`), 20 conflicts with earlier approved restorations left `proposed` for owner reconciliation, 21 identical to current text skipped; MVP re-exported via script 17 (793 restorations applied, 1,395 pages) and copied to `docs/downloads/`
  - [x] **DONE 2026-07-18** (`scripts/46_tsbc_residue_scan.py` → `references/tsbc_residue_placements.md`, report only): the owner's OCR scans of all TSBC residue images (`references/tsbc_residue.md`, 205 blocks) placed against the current restored text — **45 MATCH** (residue corroborates the current text), **63 VARIANT** (residue quotes the verse but reads differently — owner-review candidates, each with word-level diff + collision columns: existing restorations by flaw_type, `memories` rows, `tsbc_changes` rows), **97 UNPLACED** (book covers, quiz pages, sermon prose with no verse quote). Per **Decision Log #14 (owner ruling 2026-07-19)** the scan performs version-attribution (residue vs all 13 witnesses) and a drastic-change measure on every VARIANT: **12 attributed to another bible version** (likely quotations of that version, not KJV residue — sunk to the bottom), **51 unattributed**, sorted most-drastic-first (top candidates: Matthew 15:22 ~106% changed, Matthew 11:2, Matthew 18:20 ×2 including one memory-aligned, I Corinthians 13:13, Genesis 22:1 res4, Matthew 6:9 memory-aligned). Single-word variants echoing pre-rare-word-swap readings (cloak/corn/bottle/test/afresh) remain advisory per the ruling — not restoration candidates unless memory-confirmed. Some variant diffs are OCR artifacts, not readings ("je sus", "un to", stray lead-in words says/states/read)
  - [x] **DONE 2026-07-19** — Residue verse-proposal pass (owner directive; king-james agent over all 63 VARIANT placements): `references/residue_verse_proposals_1.md` (32 most-drastic: 2 ADOPT-RESIDUE — Numbers 23:22 "unicorn", John 15:22 "cloke", both verified verbatim vs KJV.db/Geneva; 3 BLEND — Matthew 3:12, Matthew 28:20 "alway", Luke 2:46 "doctors"; 27 KEEP-CURRENT) and `references/residue_verse_proposals_2.md` (31 remaining: 7 ADOPT-RESIDUE, 1 BLEND, 23 KEEP-CURRENT). **Awaiting owner ruling per entry.** Agent cross-findings: version-attribution can't distinguish "quotes that version" from "shares the true AV wording with that version" (Mark 1:19, Isaiah 13:21, Genesis 3:15, John 15:22 flagged); open tensions for owner — Matthew 18:20 "two or three" (memory+KJV.db) vs current "two or more", I Corinthians 13:13 charity vs love, I Timothy 4:1 devils vs demons (OCR illegible), Jeremiah 29:11 "expected end" vs current; 2 image/OCR-index mismatches (Romans 10:4, second I Cor 13:13 scan). **John 11:16 defect found & repaired 2026-07-19** (script 42 repair block): round-1 rare-word swap had deleted "fellow" from TSBC's "fellow-disciples" leaving "his -disciples" — superseded with the TSBC reading restored (residue corroborates); export regenerated (1,707 pages, 3,884 restorations)
  - [x] **DONE 2026-07-20** — Owner ruling applied on `residue_verse_proposals_1.md`/`_2.md` (`scripts/51_apply_residue_proposals.py`, flaw_type `residue_verse_proposal`, 13 verses, SUGGESTED text applied verbatim): Genesis 22:1 "tempt"→"tried" (owner decision, 3 duplicate scans collapsed to one restoration), Matthew 3:12 "garner"/"unquenchable fire", Matthew 28:20 "alway", John 14:6 (owner override — authentic memory), John 15:22 "cloke", Jonah 3:10 "relented...inflict" (owner override — God does not commit/repent of evil), Psalms 119:83 "vessel" (owner override — bottle was a wealthy-only item), Genesis 3:15 "he shall bruise thy head" (owner override — birth/life imagery, thee/thy/thou retained), John 12:24 "grain of corn" (owner-override word order 7/16/26), Mark 1:19 "ship...mending their nets", Isaiah 13:21 "doleful creatures", John 11:16 "fellowdisciples", Romans 8:28 "that"/"who" clause variation. Luke 2:46 "doctors" and Numbers 23:22 "unicorn" were explicitly overridden back to KEEP-CURRENT by the owner (2026-07-19) and are NOT among the 13. **Two same-verse conflicts found and left unresolved for owner ruling** (not applied): John 15:22 "cloke" (applied, KJV.db match) vs. a second, un-ruled AI proposal reading "cloak" (`85_john_15_22_res1.png`); Genesis 3:15 "he shall bruise...thee/thy/thou" (applied, owner override) vs. a second, un-ruled AI proposal reading "it shall bruise...bruise both times" (`221_genesis_3_15.jpg`). Export regenerated (1,720 pages, 3,989 restorations). Still open, out of scope for this pass: Matthew 18:20 "two or three", I Corinthians 13:13 charity/love, I Timothy 4:1 devils/demons, Jeremiah 29:11 "expected end", the 2 image/OCR-index mismatches.
  - [ ] Match TSBC memories to existing `memories` rows by verse ref: matches add independent-rememberer corroboration signals to `memory_signals`; non-matches become new memory-intake candidates for `remembered_verses.md` (owner reviews before they enter the md — memory file stays owner-curated)
  - [ ] Reconcile the 20 conflict verses (TSBC `proposed` vs earlier approved restorations) — owner decision per verse
  - [ ] Regenerate the corroboration report (script 11/12 chain) after import and re-rank the corruption index 


### Phase 5 — results as measured (2026-07-14)

- 23 memories imported from `remembered_verses.md`; report generated at
  `references/corroboration_report.md` (regenerated on every run — the md
  file stays the human-editable source of record; re-run script 11 after
  adding memories).
- Corroboration statuses: **8 corroborated** (artifact + documented public
  memory: bottles, lion & lamb, Lord's Prayer, couch, matrix, emoticons,
  money, on-earth), **7 artifact-supported** (co-located artifacts, no
  external documentation yet: tables, destroyed, capitalization, windows,
  thanksgivings, wizards, strait), **8 unconfirmed** (recorded, not
  restorable yet per the falsifiability anchor: Genesis 1:1, divers, spirit
  of error, charity, eyes-to-see, serpent's head, Philippians 4:13,
  judge-not).
- Signals stored in `memory_signals`: 119 artifact co-locations, 9
  public-memory documentations, 106 advisory witness readings.
- Note: "independent memory agreement" currently proxies through external
  reference links documenting unrelated rememberers; a proper multi-witness
  memory intake is future work if more rememberers contribute.

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
- [x] `scripts/12_corruption_index.py` — score every verse; ranked review queue
- [x] `scripts/13_propose_restorations.py` — generate candidate readings for the top-scored verses, starting with the 11 memory-anchored passages
- [x] Review workflow: walk proposals with the project owner, approve/reject, record rationale — **review session 2026-07-14**: all 13 substitution groups approved (59 rows), Group 6 approved with amendment gate→path ("Straight is the path, narrow is the way"). Decisions are version-controlled in `scripts/15_record_reviews.py` (the db is rebuildable, so the script IS the review record); 3 phrase-level rows remain proposed pending KJV-voice phrasing
- [x] Phrase-level proposals: run the king-james-middle-english-expert agent to phrase the lion & lamb and Lord's Prayer (trespasses) readings in KJV voice — done 2026-07-14; all three phrasings owner-approved (Isaiah 65:25, Isaiah 11:6, Matthew 6:12 "forgive us our trespasses, as we forgive them that trespass against us"). **All 62 restorations now approved.** Phrasings live as data in script 13 (`PHRASED`); approvals in script 15.
- [x] `scripts/14_export_restored.py` — emit the restored text per book (markdown), diffable against the current KJV

### Phase 6 — results as measured (2026-07-14)

- `corruption_index`: all 31,102 verses scored. Top of the review queue is
  wall-to-wall memory-anchored verses (Genesis 49:4, the emoticon verses,
  Isaiah 65:25, the matrix and bottles verses) — the weights behave as
  intended (Decision Log #8).
- `restorations`: **62 proposals**, all status `proposed`, spanning bottles→
  wineskins, matrix→womb, couch→crouch, wizards→sorcerers, thanksgivings→
  thank offerings, tables→tablets, strait→straight, in-earth→on-earth,
  destroyed→perish, money phrase, windows→floodgates/openings, Holy Ghost→
  spirit of god, emoticon-paren removal, plus phrasing-pending rows for
  lion & lamb and the Lord's Prayer.
- `exports/Matthew.md` preview generated with `--include-proposed`: 1,071
  verses, 6 proposals applied and footnoted (1:18, 6:10, 6:32, 7:13, 7:14,
  9:17). Default (approved-only) export currently applies 0 — correct, since
  nothing is owner-approved yet.

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
