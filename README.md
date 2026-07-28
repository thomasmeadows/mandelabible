# The Mandela Bible

**A memory-led restoration of the King James Bible.**

Generations memorized scripture — and what they remember does not match the
text on the page. Wineskins, not bottles. The lion lying down with the lamb.
*Straight* is the path. Forgive us our trespasses. This project treats those
shared memories as witness testimony and restores the King James text
accordingly, using the discipline of textual criticism: memory testimony
first, internal alteration artifacts second, all written texts advisory.

**Why does this project exist?** [The Full Story](./THESTORY.md) ·
**Website**: [mandelabible.com](https://mandelabible.com) ·
**GitHub**: [github.com/thomasmeadows/mandelabible](https://github.com/thomasmeadows/mandelabible)

## Download

Two published editions of the complete 66-book restored text — 7,031
owner-reviewed restorations, every changed verse marked, every original reading
preserved in the Restoration Appendix:

| Edition | Download |
|---|---|
| **Reconstructed KJV** — the restored text in its 1611 Early Modern English | [PDF](./docs/downloads/the-mandela-bible-reconstructed-kjv.pdf) · [Markdown](./docs/downloads/the-mandela-bible-reconstructed-kjv.md) |
| **Reconstructed KJV in Modern English** — the same restorations, modernized | [PDF](./docs/downloads/reconstructed-kjv-in-modern-english.pdf) · [Markdown](./docs/downloads/reconstructed-kjv-in-modern-english.md) |

Both are also on [mandelabible.com](https://mandelabible.com), and both are
generated from committed settings files (`custom/site-original.json`,
`custom/site-modern.json`) by `scripts/81_publish_site_editions.py` — so what
the site publishes can be changed by editing JSON, never by editing a script.
See "Build your own edition" below.

The plain repo export — the restored text with no settings layer at all — stays
at [`exports/MandelaBible-MVP.{pdf,md}`](./exports/), rebuilt by
`scripts/17_export_full.py`. Per-book exports with footnoted changes live in
[`exports/`](./exports/) too.

## Project documentation

| File | What it holds |
|------|---------------|
| [`references/instructions.md`](./references/instructions.md) | The mission, the ten-phase methodology, and the Premise Revision (evidence hierarchy) |
| [`references/roadmap.md`](./references/roadmap.md) | Phased plan, task tracking, and the **Decision Log** — every significant choice, with rationale |
| [`references/evidence/remembered_verses.md`](./references/evidence/remembered_verses.md) | The memory evidence: every remembered reading, with current text and advisory context |
| [`references/evidence/corroboration_report.md`](./references/evidence/corroboration_report.md) | Generated: each memory's corroboration status (artifacts, public documentation, witness readings) |
| [`references/word_reviews/word_review_report.md`](./references/word_reviews/word_review_report.md) | Generated: the era audit's flagged words with advised period alternates |
| [`references/word_lists/uncleared_words.md`](./references/word_lists/uncleared_words.md) | Generated: KJV words unattested in the local pre-1611 corpora |
| [`references/word_reviews/`](./references/word_reviews/) | The raw agent review verdicts (first pass, second opinion, owner rulings) |
| [`references/sources.md`](./references/sources.md) | **Comprehensive source list** — every data set, reference text, and public Mandela-effect-Bible source catalogued so far |
| [`references/evidence/blog_search_references/`](./references/evidence/blog_search_references/) | Raw multi-engine blog/website search results (public memory literature) |
| [`references/evidence/general_references.md`](./references/evidence/general_references.md) | External sources and links |
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

## Build your own edition

You can produce your own variation of the restored text — your wording, your
spelling, your whole-verse readings — without editing a single script. Two
exporters read a JSON settings file and write a complete 66-book edition as
markdown **and** PDF into `exports/custom/`:

```bash
# 1. your edition, in the King James voice (the "original version")
python3 scripts/79_export_custom.py custom/example-original.json

# 2. the same edition, automatically modernized on top of those changes
python3 scripts/80_export_custom_modern.py custom/example-original.json \
                                           custom/example-modern.json
```

Copy `custom/example-original.json` / `custom/example-modern.json`, edit them,
and re-run. Both scripts are idempotent, take an optional `--out-dir`, and
**never write to the database** — they only read it.

The two editions published on mandelabible.com are exactly this mechanism
pointed at committed settings files:

```bash
python3 scripts/81_publish_site_editions.py   # custom/site-*.json → docs/downloads/
```

That one command rebuilds both published editions and refreshes the site's
download buttons. To change what the site publishes, edit
`custom/site-original.json` / `custom/site-modern.json` and re-run it — both
ship with empty rule sets, so the Reconstructed KJV edition is the restored
text exactly as the project produced it.

Both start from the same base: the restored Mandela text, i.e. the KJV with
every owner-approved restoration already applied, so the memories are in your
edition before your own changes are. Script 80 does not re-parse script 79's
output — it re-derives the text and stacks the layers:

```
restored Mandela text
  → your original settings file        (script 79 stops here)
  → built-in modernization rules
  → your modernization settings file   (overrides the built-in rules)
```

### The settings file

```json
{
    "VersionTitle": "Billy Bob's Bible",
    "BookIndex": "yes",
    "BookLinks": "yes",
    "ChangeAppendix": "yes",
    "CustomSettingAppendix": "yes",
    "GlobalReplacements": {
        "thee": "you",
        "thou": "you",
        "thine": "your",
        "ye": "you",
        "trespassed": "betrayed",
        "trespass": "betrayal",
        "backbiters": "backstabbers",
        ";": ",",
        ":": "."
    },
    "VerseReplacements": {
        "revelations": {
            "1": {
                "1": {
                    "replacement": "In the beginning, God created the heaven and the earth.",
                    "comment": "I remember it being heaven"
                }
            }
        }
    }
}
```

| Setting | What it does |
|---|---|
| `VersionTitle` | **Required.** The edition's title, and its file name: `exports/custom/billy-bobs-bible.{md,pdf}` |
| `BookIndex` | `yes` adds a Contents list of all 66 books — with page numbers in the PDF |
| `BookLinks` | `yes` makes the markdown Contents entries clickable and puts an "↑ Contents" link on every book. Needs `BookIndex`; defaults to whatever `BookIndex` is |
| `ChangeAppendix` | `yes` marks every verse your settings changed with `†` and appends a was/now list of them, with your comments |
| `RestorationAppendix` | `yes` marks every project restoration with `*` and appends the was/now list of all 7,031 of them — the same appendix the repo export carries. Turn it off for a slimmer file |
| `CustomSettingAppendix` | `yes` appends the settings themselves — every rule, where it came from, and how many times it fired |
| `DivineNames` | `yes` restores the divine name: **Yahweh** where the KJV printed LORD/GOD in small caps, **Adonai** for the Old Testament's *Lord*. Off unless you ask for it, and only available to the modernizing exporters (scripts 80 and 81). See "The divine names" below |
| `GlobalReplacements` | word/phrase → replacement, applied everywhere |
| `VerseReplacements` | book → chapter → verse → `{ "replacement": "...", "comment": "..." }` (a plain string works too when you don't want a comment) |

Flags accept `yes`/`no` (or `true`/`false`); anything omitted defaults to on.

**How replacements behave**

- **Capitalization is preserved from the text, not the rule.** `"thou": "you"`
  turns *thou* into *you*, *Thou* into *You*, and *THOU* into *YOU*.
- **Whole words only.** `"ye": "you"` will not touch *yea* or *eye*. Keys that
  are punctuation (`";": ","`) are matched literally, and keys may be phrases
  (`"forasmuch as": "since"`).
- **One pass, no cascading.** All rules are applied simultaneously, so
  `"thee": "you"` plus `"you": "ye"` cannot turn *thee* into *ye*. Longer keys
  win over shorter ones.
- **Verse replacements win and are taken verbatim** — global rules in the same
  settings file are not applied to them. (In script 80, a verse you replace in
  the *original* file still gets modernized by the later layer; that is the
  point of stacking.)
- Book names are forgiving: `revelations`, `Revelation`, `1 John`, `I John`,
  `first john`, `song of songs` all resolve. An unknown book is reported as a
  warning and skipped rather than failing the run.
- Swapping punctuation across the whole Bible (`";": ","`) changes tens of
  thousands of verses, so the Change Appendix — and the PDF — get very large.
  Set `ChangeAppendix` to `no` if you don't want that.

### The automatic modernization (script 80)

Script 80 applies a built-in Early Modern → Modern English pass before your
modernization settings:

- pronouns — *thee/thou → you*, *thy/thine → your*, *ye → you*, *thyself →
  yourself*. The **absolute** *thine* — the one that is a pronoun rather than a
  modifier — becomes *yours* instead: *"for thine is the kingdom" → "for yours
  is the kingdom"*, *"not my will, but thine, be done" → "but yours, be done"*.
  This is the one rule that looks at context (59 places in the text), because a
  word-for-word map cannot tell *thine eyes* from *thine is the kingdom*.
  Setting your own `"thine"` rule switches it off along with the built-in.
- auxiliaries and irregulars — *hath → has*, *doth → does*, *art → are*,
  *shalt → shall*, *saith → says*, *spake → spoke*, *wist → knew*
- a curated table of ~260 archaic verb forms, plus an automatic `-eth`/`-est`
  rule for the long tail: *restoreth → restores*, *preparest → prepare*,
  *sitteth → sits*, *crieth → cries*. It only fires when a base form of the
  word is itself a word in the text, which is what keeps *priest*, *harvest*,
  *forest*, *request*, *tempest*, *Nazareth* and *Mephibosheth* intact;
  ordinals (*twentieth*) and superlatives (*greatest*, *highest*) are
  blocklisted on top of that.
- archaic spelling and vocabulary — *shew → show*, *unto → to*, *verily →
  truly*, *betwixt → between*, *peradventure → perhaps*

**Your settings file always wins over a built-in rule.** Put the word in
`GlobalReplacements` with the reading you want — and map a word to *itself*
(`"burneth": "burneth"`, `"thee": "thee"`) to switch a built-in rule off for
that word. Rare forms the automatic rule cannot verify (*aileth*, *availeth*)
are deliberately left alone; add them to `GlobalReplacements` if you want them
changed.

The Custom Setting Appendix in the output lists every rule with its source
(`built-in`, `settings`, or `settings (overrides built-in)`) and how many times
it actually fired — the fastest way to see whether a rule did what you meant.

### The divine names (`"DivineNames": "yes"`)

The King James Bible distinguishes three different words that all look like
"lord" once the typography is gone:

| Printed as | Original | Means |
|---|---|---|
| **LORD** / **GOD** in small caps | יהוה (H3068) | the divine name — Yahweh |
| **Lord** | אֲדֹנָי (H136) | Adonai, a title of God |
| **lord** | אָדוֹן (H113) | a human master — the owner of an estate |

The text this project builds on **lost the small caps**: its source holds 42
all-caps `LORD` against 54,009 plain `Lord`. So no `GlobalReplacements` rule
can separate them — `"Lord": "Yahweh"` would rename Adonai and every human
master too.

`"DivineNames": "yes"` fixes that from the data instead of the string. It uses
the `divine_names` table, which `scripts/91_build_divine_names.py` builds by
aligning every Lord/God token against BibleForge's small-caps flag and Strong's
numbers, addressing each occurrence **by its position in the verse** so the
third "Lord" of a verse can change while the first does not. The result:

- **Yahweh** — 6,870 occurrences, wherever the KJV printed small caps,
  including the GOD of "Lord GOD", which therefore reads *Adonai Yahweh*
- **Adonai** — 436 occurrences, the Old Testament's H136
- **unchanged** — lowercase *lord* (the estate owner), the Old Testament's
  human masters, the New Testament's Greek κύριος, and every non-divine *God*

**The definite article goes with the title.** "the LORD" is English convention
for a *title*; a personal name does not take one, so the article is dropped
along with the word it belonged to: *"the LORD is my shepherd"* → **"Yahweh is
my shepherd"**, *"unto the LORD"* → *"unto Yahweh"*, *"the Lord GOD"* →
*"Adonai Yahweh"*. Leviticus 16:8 comes out with the Hebrew's own parallel
intact: *"one lot for Yahweh, and the other lot for Azazel."*

111 verses are deliberately skipped: the project's own restorations changed
their Lord/God token stream (*"Holy Ghost" → "spirit of the Lord"* and the
like), so the positions no longer address what they were built against. They
keep their existing reading rather than being guessed at — run
`python3 scripts/91_build_divine_names.py --list-skipped` to see them all.

Run script 91 once before using the setting; without the table the export
stops with an explanation rather than publishing a half-converted text. The
published "Reconstructed KJV in Modern English" has this on, paired with two
ordinary `GlobalReplacements` rules — `"Jesus": "Yeshua"`, and *scapegoat* →
**Azazel** in Leviticus 16:8, 10, 26, the reading the Hebrew names and the
Book of Enoch knows. The 1611-voice edition has none of it.

Those two are worth contrasting with the divine names: *Jesus* and *scapegoat*
are ordinary settings rules because the words are still *in the text* — you
could add them to any edition yourself. `DivineNames` needs its own layer only
because the LORD/Lord distinction is not.

### The archaism sweep

`custom/site-modern.json` also carries 39 rules from a review of the published
modern edition by the project's King James agent (full report:
`references/word_reviews/modern_english_archaisms_review.md`), catching what the
built-in pass left behind. Proper names and locations were removed from the
candidate list before the review began, so none could be touched.

The valuable ones are **false friends** — where the text reads plausibly but
wrongly to a modern eye:

| Reads like | Actually means | Rule |
|---|---|---|
| *conversation* | conduct, manner of life | → `conduct` (20) |
| *carriage* | baggage, what you carry | → `baggage` (6) |
| *prevent* | go before, precede | → `precede` (18) |
| *communicate* | share, materially | → `share` |
| *presently* | at once, immediately | → `immediately` |
| *naughty* | wicked — a real moral charge | → `wicked` |

Plus plain archaisms: *wroth* → angry (50), *froward* → perverse (23),
*asunder* → apart (21), *hitherto* → until now (19), *victuals* → provisions
(17), *privily* → secretly (16), and more.

Some archaic words were deliberately **left alone** because one modern word
cannot serve every occurrence: *suffer* (mostly "allow", but "the Son of man
must suffer many things" carries the modern sense), *meat offering* (a
liturgical term of art, 199 times), *quick*, *meet*, *curious*, *abroad*,
*halt*. Those need per-verse handling, which is what `VerseReplacements` is
for.

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
5)  Verify against our [word white-list](https://github.com/thomasmeadows/mandelabible/blob/main/references/word_whitelist.md)</a> and [word black-list](https://github.com/thomasmeadows/mandelabible/blob/main/references/word_blacklist.md) that a word you have used has been guaranteed KJV or guaranteed against KJV
6)  Do not submit your request on the first day (a full 24 hours) of finding a change that should be made.  Meditate on your verse throughout a full day. Meditate on what we have, and what you believe the verse should be.  Before going to bed, pray that the Lord guide you unto the correct wording and make sure you have a writing pencil, pen, or phone to gather the knowledge given to you by the spirit. Then, submit your spirit led verse on github or send on discord.


### Database exports

Two manualdb snapshots the working database (`db/mandela.db`) into
portable SQLite files in [`db/`](./db/), each with a companion
markdown describing its tables:

- **`db/MandelaKJV.db`** — the restored text (base KJV with all approved
  restorations applied) in the exact
  [scrollmapper `bible_databases`](./bible_databases/) format
  (`MandelaKJV_books`, `MandelaKJV_verses`, `translations`), suitable for a
  merge request upstream. Schema: `db/MandelaKJV_schema.md`.
- **`db/MandelaProject.db`** — everything this project produced
  (memories, restorations, anomalies, corruption scores, word-era verdicts,
  residue imports, plus the `verses`/`books`/`translations` reference tables),
  excluding only the bulk BibleForge imports, which are regenerable.
  Schema: `db/MandelaProject_schema.md`.

**To export** (idempotent — each run rebuilds both output files from scratch):

```bash
python3 scripts/69_export_scrollmapper.py   # db/MandelaKJV.db + schema md
python3 scripts/70_export_project_db.py     # db/MandelaProject.db + schema md
```

**To rebuild a working `db/mandela.db` from the db:** yes, this is
possible from `MandelaProject.db` — it contains every project table; the only
tables it omits (`bf_words_en`, `bf_words_orig`, `lexicon_greek`,
`lexicon_hebrew`) are re-parsed from the read-only `bible_forge_db/` dumps by
script 09, which drops and rebuilds exactly those tables:

```bash
mv db/MandelaProject.db db/mandela.db
python3 scripts/09_convert_bibleforge.py    # restores the BibleForge word/lexicon tables
```

(`MandelaKJV.db` alone cannot seed a rebuild — it carries text only, none of
the project's evidence tables.)

### Database

Having the database is not necessary to contribute, you can contribute to white list or with memories and residuals.  However if you intend to use AI for validation or more research, the database is below
[current sqlite db](https://github.com/thomasmeadows/mandelabible/tree/70_export_project_db.py/db)
The current sqlite db is up to date through 70_export_project_db.py.  Any other changes may not be applied yet until I up date the db export.  It is on a second branch so it is not under version control and is very large.  You will need 7-zip or another known method to extract a multi file zip.