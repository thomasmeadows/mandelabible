# Bible Versions and History

What Bible texts this project holds, where each came from, how each was made,
and how the 1611 King James Bible differs from the 1769 Standard Oxford Edition
that is the project's base text.

> **Evidence status.** The history below is the conventional published record.
> Under the Premise Revision (`references/instructions.md`, Decision Log #5)
> every written text — including every edition described here — is
> **advisory**: memory testimony (`references/evidence/remembered_verses.md`)
> leads, and no text or history can veto a memory. Facts marked
> *(observed)* were checked against `db/mandela.db` on 2026-10-04; the rest
> is standard historical background, not verifiable inside this repository.

---

## 1. Versions loaded in `db/mandela.db` (14)

Thirteen were copied from the read-only scrollmapper corpus
(`bible_databases/formats/sqlite/<code>.db`) into the `verses` table by
`scripts/08_import_witnesses.py`; **KJV1611** was added on 2026-10-04 by
`scripts/102_import_kjv1611.py` from a separate source (below). Titles and
licences are as recorded in the `translations` table; verse and book counts
are *(observed)*.

| Code | Title in DB | Date | Language | Made from | Verses / books | Role here |
|---|---|---|---|---|---|---|
| **KJV** | King James Version (1769) with Strongs Numbers and Morphology and CatchWords | 1611 / 1769 text | Early Modern English | Hebrew, Greek (TR), with the Bishops' Bible as base | 31,102 / 66 | **The base text** every restoration is applied to |
| **KJV1611** | King James Version (1611), original spelling — lb42/KJV_1611 TEI transcription | 1611 | Early Modern English (original spelling) | The 1611 first printing, via a web transcription | 31,102 / 66 | The 1611 text itself; 10,192 marginal notes in `kjv1611_notes` |
| KJVPCE | King James Version: Pure Cambridge Edition | c. 1900 | Early Modern English | The KJV via the Cambridge printing line | 31,098 / 66 | Second KJV-family witness |
| Geneva1599 | Geneva Bible (1599) | 1560 / 1599 | Early Modern English (original spelling) | Hebrew and Greek | 31,064 / 66 | Period witness, the main Bible before the KJV; one of the two editions shown for comparison in rare-word reviews |
| Tyndale | William Tyndale Bible (1525/1530) | 1525–1534 | Early Modern English (early Tudor) | Greek (Erasmus) and Hebrew | 7,888 / **10** | Period witness: Genesis plus 9 NT books only |
| Wycliffe | John Wycliffe Bible (c.1395) | c. 1382–1395 | Middle English | Latin Vulgate | 31,378 / 66 | Oldest English witness |
| DRC | Douay-Rheims Bible, Challoner Revision | 1582–1610 / 1749–52 | English (Catholic) | Latin Vulgate | 31,432 / 66 | Catholic line, independent of the KJV |
| Webster | Webster Bible | 1833 | English | The KJV, lightly revised | 31,102 / 66 | KJV-lineage witness |
| YLT | Young's Literal Translation (1898) | 1862 / 1898 | English (literal) | Hebrew and Greek | 31,102 / 66 | Word-for-word witness |
| AKJV | American King James Version | 1999 | Modern English | The KJV, modernized | 31,102 / 66 | KJV-lineage witness |
| UKJV | Updated King James Version | early 2000s | Modern English | The KJV, modernized | 31,102 / 66 | KJV-lineage witness |
| RNKJV | Restored Name King James Version | modern | English | The KJV with divine names restored | 31,102 / 66 | Divine-name witness |
| TR | Textus Receptus (1550/1894) | 1516–1894 | Koine Greek | Greek manuscripts | 7,957 / 27 (NT) | The Greek NT behind the KJV |
| WLC | Westminster Leningrad Codex | c. 1008 ms. / digital | Biblical Hebrew (with vowel points and accents) | Leningrad Codex | 23,213 / 39 (OT) | The Hebrew OT behind modern study |

Notes on the loaded texts *(observed)*:

- **KJV.db is a flattened digital text.** It carries the 1769 wording, but
  the scrollmapper source dropped the small capitals that distinguish LORD
  from Lord (42 `LORD` vs 54,009 `Lord`; see CLAUDE.md → DivineNames), and it
  writes the æ ligature as plain *e* (*Cesar*, *Judea* where printed
  editions have *Cæsar*, *Judæa*).
- **Tyndale covers only Genesis, Matthew, Mark, Luke, John, Acts, Romans,
  1 Corinthians, Hebrews and Revelation.** His other translated books
  (rest of the Pentateuch, Jonah, the rest of the NT) are not in this file.
- **Wycliffe and DRC follow Latin (Vulgate) psalm numbering.** Their
  "Psalm 23" is the KJV's Psalm 24; compare by content, not by number.
- **Geneva1599 rows are duplicated** in the source; deduplicate on
  `(book_id, chapter, verse)` (CLAUDE.md → Rare-Word Review List Protocol).
- **KJVPCE is missing verse 1 of four chapters** (Joshua 15, Job 7, Hosea 8,
  Romans 8), and some book-final verses carry trailing "THE END" style
  markers from the source. These are source-file artifacts, not edition
  differences.
- **KJV1611 is a third-party transcription.** Source: lb42/KJV_1611
  (Lou Burnard, 2017; GitHub `lb42/KJV_1611`, archived as Zenodo record
  1285692; cached at `references/source_texts/KJV_1611_lb42-1.0.zip`),
  converted from the transcription on kingjamesbibleonline.org. Its
  converter notes it "contains several areas for amelioration", and the
  repository declares no licence (the 1611 text itself is out of
  copyright). Spelling is kept exactly as transcribed (*vnto*, *Iesus*,
  *þe*); psalm titles sit in brackets at the start of verse 1 ("[A Psalme
  of Dauid.]"); the marginal notes are split out into `kjv1611_notes`. It
  follows the **first ("He") issue** — Ruth 3:15 "and **he** went into the
  citie". It has no small capitals either ("The Lord is my shepheard"). The
  Apocrypha is in the cached zip but not loaded, matching the 66-book base.
  Check any single reading you rely on against the page facsimiles each
  chapter file links.
- **RNKJV writes the divine name in Hebrew letters**: "יהוה is my
  shepherd" (Psalm 23:1), "For יהוה so loved the world" (John 3:16).

Sample — John 3:16 in the loaded texts *(observed)*:

| Code | Text |
|---|---|
| KJV1611 | ¶ For God so loued þe world, that he gaue his only begotten Sonne: that whosoeuer beleeueth in him, should not perish, but haue euerlasting life. |
| Wycliffe | For God louede so the world, that he yaf his oon bigetun sone, that ech man that bileueth in him perische not, but haue euerlastynge lijf. |
| Tyndale | For God so loveth the worlde yt he hath geven his only sonne that none that beleve in him shuld perisshe: but shuld have everlastinge lyfe. |
| Geneva1599 | For God so loued the worlde, that hee hath giuen his onely begotten Sonne, that whosoeuer beleeueth in him, should not perish, but haue euerlasting life. |
| KJV (1769) | For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life. |
| DRC | For God so loved the world, as to give his only begotten Son: that whosoever believeth in him may not perish, but may have life everlasting. |
| YLT | for God did so love the world, that His Son--the only begotten--He gave, that every one who is believing in him may not perish, but may have life age-during. |
| AKJV | For God so loved the world, that he gave his only begotten Son, that whoever believes in him should not perish, but have everlasting life. |

---

## 2. Other texts in the repository (not loaded into `verses`)

- **The rest of the scrollmapper corpus** — `bible_databases/formats/sqlite/`
  holds 140 translation files (read-only). Scripts and the King James agent
  query them directly when a review needs another witness. English texts
  used most often: **ASV** (American Standard Version, 1901), **Darby**
  (1889), **BSB** (Berean Standard Bible), **LEB** (Lexham English Bible),
  **MKJV** and **LITV** (Jay P. Green's Modern KJV and Literal Translation),
  **KJVA** (the same 1769 KJV *with* the Apocrypha), **RWebster** (Revised
  Webster), **Rotherham** (Emphasised Bible), **JPS** (Jewish Publication
  Society OT), **Noyes** (1869), **Twenty** (Twentieth Century NT), and the
  **NHEB** family. Ancient-language texts include **Byz** (Byzantine Greek
  NT, 2013), **StatResGNT**, **MapM** (Miqra according to the Masorah),
  **SP** (Samaritan Pentateuch), **Peshitta** (Syriac), **Wulfila**
  (Gothic), and five Latin Vulgate editions (**Vulgate**, **VulgClementine**,
  **VulgSistine**, **VulgConte**, **VulgHetzenauer**) — the Vulgate being
  the source Wycliffe and Douay-Rheims translated. The remainder are
  non-English translations.
- **BibleForge** (`bible_forge_db/`, read-only) — a word-level KJV with
  Strong's numbers, Hebrew/Greek word tables, and lexicons, parsed into
  `bf_words_en`, `bf_words_orig`, `lexicon_greek`, `lexicon_hebrew`. Its
  word-level KJV preserves which *Lord*/*God* tokens were small capitals,
  which is how `divine_names` is built.
- **Matthew's Bible** — `references/source_texts/The October Testament -
  Matthews Bible.pdf` (1537; see the timeline).

---

## 3. Timeline of the English Bible

| Year | Event |
|---|---|
| c. 250 BC – AD 68 | **Dead Sea Scrolls** copied — the oldest surviving manuscripts of the Hebrew Bible (found 1947–1956; see §6). |
| c. 382–405 | **Jerome's Latin Vulgate** — the Bible of the Western church for a thousand years; the source of Wycliffe and Douay-Rheims. |
| c. 1008–1009 | **Leningrad Codex** copied in Cairo — the oldest complete Hebrew Bible manuscript in the Masoretic (ben Asher) tradition; basis of the WLC. |
| c. 1382 | **Wycliffe Bible, Early Version** — the first complete Bible in English, translated from the Vulgate by followers of John Wycliffe (d. 1384), word-for-word from the Latin. |
| c. 1388–1395 | **Wycliffe Bible, Later Version** — a more idiomatic revision, often credited to John Purvey; the "c.1395" text in this database. |
| 1407–1409 | **Constitutions of Oxford** (Archbishop Arundel) forbid unlicensed English translation; Wycliffite Bibles circulate in manuscript only. |
| 1516 | **Erasmus's Greek New Testament** — the first published printed Greek NT; the root of the Textus Receptus. |
| 1525–1526 | **Tyndale's New Testament** — printing begins at Cologne (1525, interrupted); the complete NT is printed at Worms (1526): the first English NT translated from Greek and the first printed. |
| 1530–1531 | **Tyndale's Pentateuch** (Antwerp, 1530) and **Jonah** (1531), from the Hebrew. |
| 1534 | Tyndale's **revised New Testament**. |
| 1535 | **Coverdale Bible** — the first complete *printed* English Bible (Myles Coverdale, partly from Tyndale, partly from Latin and German). |
| 1536 | Tyndale is executed at Vilvoorde near Brussels. |
| 1537 | **Matthew's Bible** (John Rogers as "Thomas Matthew") — completes Tyndale's work with his unpublished OT books plus Coverdale. |
| 1539 | **Great Bible** — the first English Bible authorized for reading in churches. |
| 1550 | **Stephanus's Greek NT** (*Editio Regia*) — a principal Textus Receptus edition. |
| 1557–1560 | **Geneva Bible** — NT 1557, complete Bible 1560, by English Protestant exiles in Geneva (William Whittingham and others) under Mary I; the first English Bible with verse numbers throughout, roman type, and extensive marginal notes. |
| 1568 | **Bishops' Bible** — the Church of England's answer to Geneva; the official base text for the KJV. |
| 1576 | **Laurence Tomson's** revision of the Geneva NT. |
| 1582 | **Rheims New Testament** — Catholic English NT from the Vulgate (English College, Rheims). |
| 1599 | **Geneva Bible, 1599 printing** — Tomson NT with Franciscus Junius's notes on Revelation; the Geneva text in this database. |
| 1604 | **Hampton Court Conference** — King James I approves John Rainolds's proposal for a new translation. |
| 1609–1610 | **Douay Old Testament** completes the Douay-Rheims Bible. |
| 1611 | **King James Version** first printed by Robert Barker, the King's Printer. |
| 1629, 1638 | **Cambridge revisions** of the KJV correct misprints and expand the italics. |
| 1633 | The Elzevir edition's preface gives the Greek text its name — the *textum … receptum*, "received text". |
| 1749–1752 | **Challoner's revision** of the Douay-Rheims — the DRC text in this database. |
| 1762 | **Cambridge edition** of the KJV (F. S. Parris) — modernizes spelling and italics. |
| 1769 | **Oxford edition** of the KJV (Benjamin Blayney) — the **Standard Oxford Edition**; the base text of this project. |
| 1833 | **Webster's revision** of the KJV (Noah Webster). |
| 1862 / 1898 | **Young's Literal Translation** (Robert Young) — first edition 1862; the revised 1898 third edition is in this database. |
| 1873 | **Cambridge Paragraph Bible** (F. H. A. Scrivener) — a critical KJV edition. |
| 1881–1885 | **English Revised Version** — the first official revision of the KJV. |
| 1894 | **Scrivener's Greek NT** — reconstructs the Greek text underlying the KJV; the "1894" half of the TR label. |
| c. 1900 | The Cambridge KJV text later named the **Pure Cambridge Edition** settles into its final form. |
| 1901 | **American Standard Version**. |
| 1947–1956 | **Dead Sea Scrolls discovered** in eleven caves near Qumran — about 1,000 years older than the Leningrad Codex. |
| 1999 – 2000s | **AKJV**, **UKJV**, **RNKJV** — public-domain KJV updates and sacred-name editions in digital circulation. |

---

## 4. How each loaded version was written

### Wycliffe Bible (c. 1382–1395)
Produced by John Wycliffe's circle at Oxford, it was translated from the Latin
Vulgate, not from Hebrew or Greek. The Early Version follows Latin word
order so closely that it is often hard to read; the Later Version (c. 1395,
the text here) rewrites it into natural Middle English. It was copied by
hand. After 1409, making or owning an unlicensed English Bible could bring a
heresy charge, yet more than 250 manuscripts survive. Its spelling and
grammar are Middle English: *louede*, *yaf* ("gave"), *bileueth*, *lijf*.

### Tyndale (1525–1534)
William Tyndale translated the NT directly from Erasmus's Greek and then
began the OT from the Hebrew. Because translation was illegal in England, he
worked in Germany and the Low Countries, and his NTs were smuggled into
England. His phrasing — "Let there be light", "the powers that be", "the
salt of the earth" — runs through every later Protestant English Bible, and
the KJV's New Testament is substantially his wording. He was arrested in
Antwerp and executed in 1536 before finishing the OT.

### Geneva Bible (1560; 1599 printing)
Translated by Protestant exiles in Geneva during Mary I's persecution, it
worked from the Hebrew and Greek and drew heavily on Tyndale. It was a
portable, affordable study Bible: roman type, numbered verses, maps, and
Calvinist marginal notes. It was the Bible of Shakespeare, of the Pilgrims,
and of most English households until the mid-1600s. Its notes, which
questioned the obedience owed to kings, are part of why James I wanted a
new translation.

### King James Version (1611)
At the Hampton Court Conference (1604), James I approved a new translation
without marginal commentary. About 47 scholars (the figure usually cited)
worked in six companies, two each at Westminster, Oxford and Cambridge, under
rules issued by Bishop Richard Bancroft: follow the Bishops' Bible, consult
Tyndale, Matthew's, Coverdale's, the Great Bible and Geneva where they read
better, and keep marginal notes to word explanations and cross-references.
Drafts were reviewed by a general committee, and Robert Barker printed the
result in 1611. It was a revision of the existing English tradition, not a
fresh start, which is why so much Tyndale and Geneva wording survives in it.

### Douay-Rheims, Challoner Revision (1582–1610; 1749–52)
English Catholic exiles at the English College (Rheims, later Douai)
translated the Vulgate, keeping many Latinate words (*supersubstantial*,
*chalice*, *penance*) and adding notes against Protestant readings. Bishop
Richard Challoner revised it thoroughly in 1749–52, modernizing its language
and, in places, moving it toward KJV phrasing. The Challoner text is what
English-speaking Catholics used until the 20th century, and is the DRC here.

### Webster Bible (1833)
Noah Webster, the American lexicographer, lightly revised the KJV: he
replaced words he judged obsolete or indelicate, corrected grammar, and
updated some forms (e.g. *my* for *mine* before consonants — Exodus 23:23
"For my Angel" vs the KJV's "For mine Angel" *(observed)*). The wording is
otherwise the KJV's.

### Young's Literal Translation (1862; 1898)
Robert Young, compiler of *Young's Analytical Concordance*, translated with
extreme literalness, reproducing Hebrew and Greek tense and word order
("may have life age-during"). It is a study tool rather than a reading Bible.

### American King James Version (1999)
Prepared by Michael Peter (Stone) Engelbrite: a word-for-word update of the
KJV that replaces archaic forms (*believeth* → *believes*, *whosoever* →
*whoever*) without changing the underlying text. Its DB licence reads
"Copyrighted; Free non-commercial distribution".

### Updated King James Version (early 2000s)
A public-domain update of the KJV in the same spirit as the AKJV:
modernized pronouns and verb endings, some archaic words replaced (Psalm
23:1 "I shall not lack").

### Restored Name King James Version
A "sacred name" edition of the KJV: the text is the KJV, but the divine name
is written as the Hebrew Tetragrammaton יהוה where the KJV prints LORD/GOD
(and in places for *God*, e.g. John 3:16 *(observed)*). Its origin and date
are not recorded in the database.

### Textus Receptus (1516–1894)
The Greek NT printed from late Byzantine manuscripts, beginning with Erasmus
(1516) and running through Stephanus (1550), Beza, and the Elzevirs (who
named it in 1633). The KJV translators worked chiefly from Beza and
Stephanus. In 1894 F. H. A. Scrivener produced a Greek text matching the
readings the KJV actually followed; the "1550/1894" in the label refers to
Stephanus and Scrivener.

### Westminster Leningrad Codex
A digital edition of the Leningrad Codex (copied c. 1008–1009 CE in Cairo,
now in the National Library of Russia), the oldest complete manuscript of the
Hebrew Bible in the Masoretic tradition, with vowel points and cantillation
marks. The digital text is maintained by the J. Alan Groves Center
(Westminster Theological Seminary). The KJV translators did not use this
manuscript itself — they used printed Hebrew Bibles of the Masoretic
tradition (e.g. the Bomberg Rabbinic Bibles) — but it is the same text
family.

### KJV — Pure Cambridge Edition (c. 1900)
"Pure Cambridge Edition" is a name given by its modern proponents to the
Cambridge University Press KJV text as it stood around 1900–1910. It
descends from the Cambridge printing line (1629, 1638, 1762, 1873) and
differs from the Oxford text mainly in spelling (see §5).

---

## 5. The original 1611 King James vs the Standard Oxford Edition (1769)

**The short answer:** the words people read as "the King James Bible" today
are almost never the 1611 printing. They are the **1769 Oxford edition**
edited by **Dr. Benjamin Blayney** (called the *Standard Oxford Edition* in
this project), or a Cambridge text that closely follows it. Blayney did not
retranslate anything. He standardized a text that had drifted through 158
years of reprints: spelling, punctuation, italics, cross-references, and
misprints. In the commonly cited count, the result differs from 1611 in
about 24,000 places (`references/language/Inflection_English_vs_Early_Modern_English.md`),
almost all spelling and punctuation.

### Why a standard edition was needed
Every printing of the KJV after 1611 was reset by hand, and each one
introduced its own errors and "corrections": the 1631 "Wicked Bible" omitted
*not* from "Thou shalt not commit adultery"; even the two 1611 issues differ
(the "He Bible" and "She Bible", named for Ruth 3:15). Cambridge revised the
text in 1629 and 1638 and again in 1762 (F. S. Parris). In 1769, Oxford,
prompted by Archbishop Secker's complaint of "scandalous inaccuracies",
published Blayney's thorough revision, which became the standard.

### What changed between 1611 and 1769

| Area | 1611 printing | 1769 Standard Oxford Edition |
|---|---|---|
| **Typeface** | Black-letter (Gothic) type; words the translators supplied for English sense were set in small roman type | Roman type throughout; supplied words in *italics* |
| **Spelling** | Unstandardized Jacobean spelling: *u*/*v* by position (*loued*, *vnto*), *i* for *j* (*Iesus*), long *ſ*, final *-e* and doubled letters (*sonne*, *shepheard*, *beleeue*) | Standardized 18th-century spelling: *loved*, *unto*, *Jesus*, *son*, *shepherd*, *believe* |
| **Grammar and wording** | As translated | Essentially unchanged; a small number of words corrected or normalized (e.g. some *-eth*/*-s* forms, pronouns, names) |
| **Punctuation** | Heavier: more colons and semicolons, paragraph marks (¶) | Lighter and more regular, though still not modern (see `colon_versus_semicolon.md`) |
| **Italics** | Fewer, inconsistently applied | Greatly expanded and regularized |
| **Marginal notes** | Alternative renderings and literal Hebrew/Greek meanings; cross-references | Notes retained; cross-references greatly expanded |
| **Proper names** | Varied spellings | Normalized |
| **Front matter** | Dedication to King James, *The Translators to the Reader*, calendars, genealogies, map | Simplified |
| **Apocrypha** | Included between the Testaments | Still included (later printings usually drop it; the scrollmapper **KJVA** keeps it) |
| **Errors** | Misprints from hand-set type | Most 1611-era errors corrected, though the 1769 edition introduced some of its own (over 100 commonly cited), later corrected |

**What did not change:** the translation itself — the choice of words, the
sentence structure, and the Early Modern English grammar (*thee*/*thou*,
*-eth*/*-est*, *ye*/*you*). Read with modern spelling, 1611 and 1769 say the
same thing in almost every verse.

### The two editions side by side
The 1611 text is loaded as `KJV1611` *(observed)*:

> **KJV1611, John 3:16** — ¶ For God so loued þe world, that he gaue his only
> begotten Sonne: that whosoeuer beleeueth in him, should not perish, but haue
> euerlasting life.
>
> **KJV.db (1769), John 3:16** — For God so loved the world, that he gave his
> only begotten Son, that whosoever believeth in him should not perish, but
> have everlasting life.

> **KJV1611, Psalm 23:1** — [A Psalme of Dauid.] The Lord is my shepheard, I
> shall not want.
>
> **KJV.db (1769), Psalm 23:1** — The Lord is my shepherd; I shall not want.

> **KJV1611, Ruth 3:15** — Also he said, Bring the vaile that thou hast vpon
> thee, and holde it. And when she helde it, he measured sixe measures of
> barley, and laide it on her: and **he** went into the citie.
>
> **KJV.db (1769), Ruth 3:15** — Also he said, Bring the vail that thou hast
> upon thee, and hold it. And when she held it, he measured six measures of
> barley, and laid it on her: and **she** went into the city.

The same words, the same grammar, different spelling and pointing (John
3:16's colon after *Sonne* and comma before *should*; Psalm 23:1's comma
where 1769 has a semicolon). Ruth 3:15 is the "He/She Bible" verse: the
first 1611 issue reads "*he* went into the city" (Boaz); the second issue
reads "*she*" (Ruth). The loaded 1611 transcription follows the first
issue; the 1769 text reads **she**.

### Oxford vs Cambridge today — measured in this database
Comparing KJV.db (1769 Oxford line) with KJVPCE (Cambridge line) word by
word, ignoring punctuation, **254 of 31,098 verses differ** *(observed)*;
about 15 of those are the source artifacts noted in §1. Nearly all the rest
are spelling:

| KJV.db (Oxford, 1769) | KJVPCE (Cambridge) | Verses |
|---|---|---|
| enquire / enquired | inquire / inquired | 84 |
| counsellor(s) | counseller(s) | 35 |
| Cesar, Cesarea, Judea *(flattened æ)* | Cæsar, Cæsarea, Judæa | ~90 |
| razor | rasor | 7 |

The few wording differences include **Joshua 19:2** — KJV.db "Beer–sheba,
Sheba, and Moladah" vs KJVPCE "Beer-sheba, **or** Sheba, and Moladah" —
and **Exodus 23:23** — KJV.db "the Canaanites, the Hivites" vs KJVPCE "the
Canaanites, **and** the Hivites".

### What this means for the project
- The base text (`KJV.db`) and both published editions are built on the
  **1769 spelling and punctuation**, not 1611's. The "original voice"
  edition is 1611 in *grammar and vocabulary*, with 1769 spelling.
- **1611 spelling and punctuation can now be checked locally** against
  `KJV1611` (added 2026-10-04; this closes the gap noted in
  `colon_versus_semicolon.md`). It is a transcription, so for a reading
  that matters, confirm it against the 1611 page facsimile linked from the
  chapter file.
- Differences between 1611 and 1769 are standardization, not translation
  changes. Under the Premise Revision both editions are advisory
  witnesses, and neither outranks memory testimony.

---

## 6. The Dead Sea Scrolls

**Video:** HISTORY — [*Secrets of the Bible | The UnXplained (S2, E7) | Full
Episode*](https://www.youtube.com/watch?v=zz6NVtRfmJo) (posted 2026-10-03,
42 min, hosted by William Shatner). Added on owner request 2026-10-04.

### What they are
The Dead Sea Scrolls are about **900–1,000 manuscripts**, surviving as
roughly 15,000 fragments, found between **1947 and 1956** in eleven caves
near **Qumran**, on the north-west shore of the Dead Sea. The first cave was
found by Bedouin shepherds in the winter of 1946–47. Related finds came from
other desert sites (Wadi Murabba'at, Nahal Hever, Masada).

- **Date:** copied between about **250 BC and AD 68**, when the Romans
  destroyed the Qumran settlement during the Jewish revolt.
- **Languages:** mostly Hebrew, some Aramaic, a few Greek.
- **Writing material:** mostly parchment (animal skin), some papyrus; one
  scroll — the **Copper Scroll** — is engraved on metal.
- **Who wrote them:** most scholars link them to a Jewish sect living at
  Qumran, usually identified with the **Essenes**; others think the scrolls
  were brought from Jerusalem and hidden. This is still debated.

### What is in them
- **Biblical books (about a quarter of the manuscripts).** Every book of
  the Hebrew Bible (the Protestant Old Testament) is represented except
  **Esther**. The most-copied books are **Psalms, Deuteronomy and Isaiah**.
- **Other religious writings** — books later left out of the Hebrew canon,
  such as *1 Enoch*, *Jubilees*, *Tobit* and *Sirach* (Ecclesiasticus).
- **The community's own texts** — the *Community Rule*, the *War Scroll*,
  the *Damascus Document*, the *Temple Scroll*, and commentaries
  (*pesharim*) applying prophecy to their own day.

### Why they matter for the Bible's text
Before 1947, the oldest complete Hebrew Bible was the **Leningrad Codex**
(c. 1008; the WLC in this database). The scrolls are **about 1,000 years
older**.

- **The Great Isaiah Scroll** (1QIsaᵃ, c. 125 BC) contains all 66 chapters
  of Isaiah. It largely agrees with the medieval Hebrew text, with many
  small differences in spelling and wording. It is on display at the
  Shrine of the Book, Israel Museum, Jerusalem.
- **Several text forms existed side by side.** Most biblical scrolls are
  close to the later Hebrew (Masoretic) text, but some agree with the Greek
  Septuagint and others with the Samaritan Pentateuch. For example, a
  Jeremiah scroll matches the Septuagint's shorter Jeremiah.
- **Readings modern translations have adopted**, for example:
  - **Deuteronomy 32:8** — a scroll reads "sons of **God**" where the
    medieval Hebrew text (and the KJV) reads "children of **Israel**".
  - **1 Samuel 10–11** — a Samuel scroll has an extra paragraph about
    Nahash the Ammonite, missing from the medieval Hebrew and the KJV,
    which some modern Bibles (e.g. the NRSV) now include.
- **The King James translators never saw them.** The scrolls were found
  336 years after 1611; the KJV Old Testament was translated from printed
  Hebrew Bibles of the medieval (Masoretic) tradition.

### Publication and access
For decades a small team controlled access and publication was slow. In
1991 the Huntington Library opened its photographs to all scholars, and the
official series (*Discoveries in the Judaean Desert*) was largely completed
in the 2000s. High-resolution images are now free online through the
**Leon Levy Dead Sea Scrolls Digital Library** (Israel Antiquities
Authority) and the Israel Museum's **Digital Dead Sea Scrolls**. In 2021 new
fragments of a Greek Minor Prophets scroll were announced from the "Cave of
Horror" (Nahal Hever). Fragments sold on the antiquities market since 2002
have proved to include forgeries — the Museum of the Bible found that all 16
of its fragments were fake.

### For this project
- **No Dead Sea Scrolls text is in the repository.** `instructions.md`
  lists them as part of the ideal restoration corpus. An open transcription
  exists: **ETCBC/dss** (https://github.com/ETCBC/dss), based on Martin
  Abegg's data; licence not declared on the repository.
- Under the Premise Revision the scrolls are a written text like any other,
  so they are **advisory**: they can inform the Hebrew behind a verse but
  cannot veto a memory.

---

## 7. Different Bibles in different churches (canons)

The same HISTORY episode (§6) also compares the Bibles of different
churches. The difference is mostly **which books are included** — a church's
list of books is its *canon*. The New Testament's 27 books are shared by
almost every church; the Old Testament is where they part ways.

| Tradition | Books | Old Testament | What it adds |
|---|---|---|---|
| **Jewish (Tanakh)** | 24 | Same content as the Protestant 39, counted and ordered differently (Torah, Prophets, Writings) | — (no New Testament) |
| **Protestant** | 66 | 39 | — the baseline; the KJV's 66 books |
| **Roman Catholic** | 73 | 46 | 7 *deuterocanonical* books plus additions to Esther and Daniel |
| **Eastern Orthodox** | about 76–79 (varies by church) | about 49–52 | The Catholic additions, plus more books from the Greek Septuagint |
| **Ethiopian Orthodox Tewahedo** | 81 (the largest) | 46 + | Books no other major church keeps, including *Enoch* and *Jubilees* |

### Catholic Bible (73 books)
The Catholic Old Testament follows the books found in the Greek
**Septuagint** and the Latin **Vulgate**. It adds seven books — **Tobit,
Judith, Wisdom, Sirach** (Ecclesiasticus), **Baruch** (with the *Letter of
Jeremiah*), **1 and 2 Maccabees** — plus Greek additions to **Esther** and
**Daniel** (the *Prayer of Azariah* and *Song of the Three Young Men*,
*Susanna*, and *Bel and the Dragon*). Catholics call these
*deuterocanonical* ("second canon"); Protestants call them the
*Apocrypha*. The **Council of Trent (1546)** fixed the list formally.

### Protestant Bible (66 books)
During the Reformation, Martin Luther moved these books into a separate
section between the Testaments (1534), and later Protestant confessions
excluded them from Scripture. **The 1611 King James Bible still printed the
Apocrypha** between the Testaments, as did the 1769 edition; British Bible
societies stopped including it in the 1820s, which is why most KJVs today
have only 66 books.

### Eastern Orthodox Bible
The Orthodox Old Testament is based on the Greek Septuagint. It keeps the
Catholic additions plus books such as **1 Esdras, 3 Maccabees, the Prayer
of Manasseh, and Psalm 151** (with 4 Maccabees often in an appendix). The
exact list differs slightly between national churches (Greek, Russian,
Serbian, and others).

### Ethiopian Orthodox Tewahedo Bible (81 books)
The Ethiopian Church — one of the oldest Christian churches, dating to the
4th century — has the largest Bible of any major church, traditionally
counted as **81 books**, written in the ancient language **Ge'ez**.
Besides the Catholic and Orthodox additions it includes:
- **1 Enoch** — visions of the patriarch Enoch, the fallen angels
  (Watchers), and the Nephilim. It is quoted in the New Testament
  (**Jude 14–15**), but survives complete **only in Ge'ez**.
- **Jubilees** — a retelling of Genesis and early Exodus dated by 49-year
  "jubilee" periods; also complete only in Ge'ez.
- **1–3 Meqabyan** — three books unique to Ethiopia, different from the
  Maccabees books despite the similar name.
- Others, such as **4 Baruch** (Paralipomena of Jeremiah), and in the
  church's broader canon, books of church order (*Sinodos*, *Didascalia*).

**Link to the Dead Sea Scrolls:** Aramaic fragments of **Enoch** and Hebrew
fragments of **Jubilees** were found at Qumran (§6), showing both books
were read by Jews before Jesus' time — centuries before they dropped out of
every canon but Ethiopia's.

### Other churches
- **Syriac churches** use the **Peshitta**, whose original New Testament
  lacked 2 Peter, 2 and 3 John, Jude and Revelation (in the scrollmapper
  corpus as `Peshitta`).
- **The Armenian and Coptic churches** have their own canons, close to the
  Orthodox list.

### What this repository holds
*(observed)*
- **Catholic deuterocanon:** the scrollmapper `DRC`, `Vulgate` and `CPDV`
  files include Tobit, Judith, Wisdom, Sirach, Baruch and 1–2 Maccabees
  (plus an appendix with the Prayer of Manasseh, 1–2 Esdras, Psalm 151 and
  the *Epistle to the Laodiceans*). Only their 66 shared books were loaded
  into `db/mandela.db`.
- **KJV Apocrypha:** scrollmapper `KJVA` (the 1769 text) has all 14
  Apocrypha books, and the cached 1611 archive
  (`references/source_texts/KJV_1611_lb42-1.0.zip`) has the 1611
  Apocrypha in original spelling. Neither is loaded.
- **Ethiopian books:** no Ge'ez text, Enoch, Jubilees, or Meqabyan is in
  the repository.
