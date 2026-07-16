# Comprehensive Source List

Every source used or catalogued by the project so far. Compiled 2026-07-15.
Sections I–III are the project's working data and evidence; IV–VIII catalogue
the public Mandela-effect-Bible literature gathered by the multi-engine blog
sweep in `references/blog_search_references/` (chatgpt, chatgpt-wayback,
claude, grok, leo). Inclusion documents public memory testimony and research
leads — it does not endorse a source's theology or conclusions.

## I. Primary data (in-repo, read-only sub-repos)

- **scrollmapper `bible_databases`** — https://github.com/scrollmapper/bible_databases — 140 SQLite translations. Base text `KJV.db`; witnesses in use: Geneva1599, Tyndale, Wycliffe, KJVPCE, AKJV, Webster, RNKJV, UKJV, YLT, DRC; original languages TR (Greek NT), WLC (Hebrew OT); cross-reference extras.
- **BibleForge `BibleForgeDB`** — https://github.com/bibleforge/BibleForgeDB — word-level KJV (`divine`/`red`/`implied` markers, original-word linkage), Strong's-tagged Hebrew/Greek, Greek & Hebrew lexicons.

## II. Period-language reference texts (in `references/`)

- *The Canterbury Tales* — Chaucer (Middle English)
- *The Book of Quinte Essence or the Fifth Being* (Middle English)
- *The Wright's Chaste Wife* (Middle English)
- *Understand Middle English — A Middle English Reader*
- *The Essayes of a Prentise in the Divine Art of Poesie* — King James VI/I (1585), the King's own writing sample
- *Interlinear Greek-English Septuagint Old Testament* (PDF; not yet machine-readable — backlog)
- Project Gutenberg — https://www.gutenberg.org/ebooks/17400

## III. Core memory-evidence documents (in `references/`)

- `remembered_verses.md` — the project's memory testimony (owner + documented public memories)
- *Rather Exhaustive List of Mandela Effect Affected Scriptures* — Truth Farmer (PDF) and online: https://truthfarmer.com/2016/08/05/rather-exhaustive-list-of-mandela-effect-affected-scriptures/
- Truth Farmer earlier list — https://truthfarmer.com/2016/06/27/list-of-mandela-effectquantum-effect-scriptures/ (crowd-sourced, "over a hundred" claimed changes)
- Christian Observer — Lord's Prayer trespasses: https://christianobserver.net/the-lords-prayer-trespasses-another-example-of-the-mandela-effect/
- maxthedork (LiveJournal) — emoticons in the KJV: https://maxthedork.livejournal.com/126279.html
- historyoasis — history of the glass bottle: https://www.historyoasis.com/post/history-glass-bottle

## IV. Dedicated Bible-change websites & ministries (blog sweep)

- **AlteredBible.com** (John Kirwin / WakeUpOrElse ministry) — https://alteredbible.com — the largest dedicated written resource: books (*The Mandela Effect: Supernatural Bible Changes*, *The Doctrine of the Preservation of Scripture*), pastor resources, surveys, testimonies; research guide (2026-07-13): https://alteredbible.com/2026/07/13/supernatural-bible-change-research-a-reference-guide-to-the-prophetic-shaking/
- **The KJV Restoration Project (kjvrestore.org)** — https://kjvrestore.org/ — added 2026-07-16 as a fellow *recreation/restoration* project to cross-reference (the closest kin to this repo's mission: it doesn't just catalogue claimed changes, it works book-by-book across all 66 books toward a restored text). Active since October 2020; full navigable KJV organized by testament/book, per-change articles (e.g. "Lion and the Lamb"), "residue evidence from books and Bibles of the past", materials preserved via encrypted-image backups; companion site Amos8.org; frames the changes via Daniel 7:25 / Amos 8:11-12. Use: compare its claimed-change list and restored readings against `remembered_verses.md` and our restoration proposals — advisory corroboration only, never a veto, per the Premise Revision.
- **Bible-Changes.com** — https://bible-changes.com — extensive claimed-change lists, testimonies, books; cross-linked with the EYA YouTube channel
- **TSBC Scribe search database (search.thesupernaturalbiblechanges.com)** — https://search.thesupernaturalbiblechanges.com/changes — added 2026-07-16 as a memory-extraction source: a structured, searchable KJV change database ("A King James Version database recording the supernatural changes in your Bible"). Live metrics (2026-07-16): **355 changes, 398 memories, 249 residual images** of the claimed original text before the changes. Machine-readable JSON API at same origin, POST `/v1/...`: `GetDBMetrics`, `Search`, `GetChangesByVerse`, `GetChangeByID`, `GetMemoriesOfChange`, `GetMemoriesOfChangeWithResidue`, `GetResidueOfMemory`, `GetChapterTextWithChanges`, `GetBookNamesAsList`, `GetChaptersOfBook`, `GetChapterVerses`, `GetVerseText`. Records carry verse refs, change-type flags (isMissing/isMeaningChange/isDoctrineChange/hasFlipflops, capitalization/punctuation/grammar flags), memory `restoredText` + notes + memoryDate, and residue-image links. Harvest task in roadmap Phase 5.
- **TheSupernaturalBibleChanges.com** — https://thesupernaturalbiblechanges.com — incl. "God Foretold of the Mandela Effect in Scripture" and "Study (a Mandela Affected Bible)..."; older WordPress mirror: https://thesupernaturalbiblechanges.wordpress.com/2019/09/10/bible-changes-and-prophecy-the-mandela-effect-33/
- **MandelaBibleChanges.com** — http://mandelabiblechanges.com/index.php/2019/10/18/how-the-bible-changes-are-lying-signs-and-wonders/ — the "signs and lying wonders" word-order change
- **LivingEndTimes** — https://www.livingendtimes.com/mandela-deception — first-person testimony
- **Jazweeh** — https://jazweeh.com/mandela-effect-and-bible-changes-are-two-different-phenomena/
- **Father's Words** — https://www.fatherswords.com/whymadelaeffect/ — distinguishes "surface" vs doctrinal changes
- **Theatre of the Gods** — https://theatreofthegods.com/king-james-version-bible-changes-mandela-effect-vs-strong-delusion/

## V. Blogs & articles (blog sweep)

- world-mysteries blog — https://blog.world-mysteries.com/guest_authors/mandela-effect-changing-the-bible-magically/ (Exodus 20, ark of bulrushes, horned Moses)
- GeekInsider — https://geekinsider.com/the-mandela-effect-the-bible-bad-changes-to-the-good-book/ (Isaiah 11:6, Lord's Prayer, Exodus 34:14)
- Medium, The Deconverted Man — https://medium.com/@TheDeconvertedMan/the-mandela-effect-and-the-bible-62ec67dacbdf
- Medium, L.K. Summer (Bouncin' and Behavin' Blogs) — "The Mandela Effect and The Bible"
- Bill Prickett (Brain Bubbles) — https://www.billprickett.com/brain-bubbles/mandela-effect-and-bible ("collective religious misremembering": Eve's apple, three wise men)
- The Bible Teaches This — https://thebibleteachesthis.com/mandela-effect-bible-verses-changed/ (engages the claims; catalogues Isaiah 11:6, Exodus 34:14, Matthew 18:20, 1 Timothy 6:10)
- Artesian Ministries — https://www.artesianministries.org/faith/the-mandela-effect-and-the-bible/ (validates the experience, attributes to memory)
- No Longer Lukewarm — https://nolongerlukewarm.com/2019/09/08/the-mandela-effect-and-the-character-of-god/ (responds to the believer community)

## VI. Forums & communities (blog sweep)

- Christian Forums — "The Mandela Effect KJV Bible": https://www.christianforums.com/threads/the-mandela-effect-kjv-bible.8047865/ (cites Luke 12:24, 17:31, 19:23; John 8:32; Revelation 5, 10)
- Christian Forums — "The KJV Mandela Effect Conundrum": https://www.christianforums.com/threads/the-kjv-mandela-effect-conundrum-kjv-only-folks.7995609/ (tables, trespasses/debts, sword/division)
- Reddit essays: r/MandelaEffectSociety end-times essays (https://www.reddit.com/r/MandelaEffectSociety/comments/1qubesb/ , /1qwtx97/), r/Retconned "Missing Signs of the End" (https://www.reddit.com/r/Retconned/comments/1lqg3q0/), r/Mandela_Effect "GOD, The truth, did the changes" (18ib2t9), r/MandelaEffect threads ut2m3a, f036ar
- r/biblechanges — https://www.reddit.com/r/biblechanges/ (dedicated subreddit)
- Archived communities (Wayback targets): r/Retconned, r/Mandela_Effect, r/MandelaEffects, r/MandelaEffectSociety, Glitch-in-the-Matrix threads, AboveTopSecret, GodLikeProductions, Unexplained Mysteries, SurvivalistBoards, Christian Forums archives

## VII. Historical / archival research targets (Wayback Machine)

- MandelaEffect.com (Fiona Broome, 2009–2023) + comment archives; WordPress mirror https://mandelaeffectsite.wordpress.com
- AlteredBible.com yearly captures 2017–2025; pre-rebrand WakeUpOrElse pages
- Bible-Changes.com captures; EYA companion pages
- Defunct Blogspot/WordPress blogs (2016–2019) — search recipes and phrase list in `blog_search_references/chatgptwaybackmachine.md` §V–VIII

## VIII. Video channels (from `general_references.md`)

- EYA (censored) — Bible changes: https://www.youtube.com/@eyacensored-biblechanges
- EYA matrix news: https://www.youtube.com/@eya-matrix-news
- JFCG: https://www.youtube.com/@JFCG
- Lion & lamb evidence video: https://www.youtube.com/watch?v=NxjjGVKNXE0

## IX. General references & tooling

- Britannica — history of the English language: https://www.britannica.com/topic/English-language/Historical-background
- Merriam-Webster (first-use dating): couch, matrix, diver, error entries
- get.bible datasets: https://get.bible/bible-data-sets/
- qBible Brenton Septuagint: http://qbible.com/brenton-septuagint/
- Wikipedia — James VI and I: https://en.wikipedia.org/wiki/James_VI_and_I
- The KJV Store — story of the KJB: https://www.thekjvstore.com/articles/the-story-behind-the-king-james-bible/
- Bible authorship background: https://www.biblestudytools.com/bible-study/topical-studies/how-many-books-are-in-the-bible-and-how-did-they-get-there.html , https://www.gotquestions.org/Bible-authors.html

## X. Noted but excluded (debunking-focused, retained for awareness)

GotQuestions "What is the Mandela Effect?", LetterPile, Messianic Evangelicals,
Now the End Begins (CERN piece), Christianity Beliefs, lovefastliveslow.com —
listed in `blog_search_references/claudeblogsearch.md` and
`leoblogsearch.md`; excluded from evidence use per the sweep's criteria.
