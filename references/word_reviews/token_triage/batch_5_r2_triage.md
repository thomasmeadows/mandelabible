# Token triage — batch 5 of 10 — ROUND 2 (revised suggestion protocol)

Rules on all 117 inflection groups from `batch_5_r2_input.md` (counts 6–7), under
the owner's 2026-07-29 directive that every group — whatever the verdict — must
carry all three Capability 3b suggestion slots (whitelist / witness / own).
Witness readings are pulled from local Geneva1599, Tyndale, and Wycliffe
(single connection per db, batched `IN` lookups); Tyndale's OT coverage is
patchy (Pentateuch + Jonah only) and Wycliffe's Psalms/Job/Proverbs/Ezekiel
verse numbers are frequently misaligned with KJV versification (a known
corpus quirk) — both are noted per-entry rather than treated as silent gaps.
Whitelist corpus-frequency figures are approximate order-of-magnitude estimates
from general familiarity with the corpus, not exact per-word queries (a
mid-run connection drop cost the batch its planned bulk frequency script; the
`~` before each figure flags this — treat them as "roughly this common," not
exact counts, and re-run a dedicated frequency query before any figure here is
used to justify a specific whitelist addition). This file was written
incrementally, chunk by chunk, so the one dropped connection during this run
cost only the in-progress chunk, not prior work.

**Verdict tally: 112 KEEP, 4 WHITELIST, 1 REPLACE.** Whitelist slot: 108 of
117 groups name an actual whitelisted word/phrase carrying the needed sense;
9 answer "none fits" and name the nearest candidate with its shortfall
(mostly single-referent nouns with no true one-word synonym: bill, careful,
diviners, midwives, pence, aileth, excuse, expedient, flattereth).

The four WHITELIST recommendations are cultic/measure/idiom nouns with no
true substitute and continuous multi-witness attestation: **omer** (a
transliterated Hebrew dry-measure, kept as a loanword by every period
witness), **tenons** (a specific carpentry joinery term, paired with
"boards/mortise," attested by Wycliffe's independent cognate "dentyngis"),
**snuffers** (the candlestick's wick-trimmer — protecting it now heads off
the "tongs" mis-swap a prior batch already had to catch at Exodus 25:38), and
**pisseth** (the Hebrew idiom "him that pisseth against the wall," attested
verbatim in Geneva and by cognate in Wycliffe — flagged for protection because
its bluntness is exactly what a future euphemism-driven pass would target).

The one REPLACE finding is the batch's most important: **"damage/hurt" at
Ezra 4:13** is not a translation-choice question but a visible, unresolved
editorial artifact — a literal slash between two unplaced word choices sitting
in running scripture text. The base `KJV.db` (queried directly) reads
**"endamage"** at this verse, a genuine, Geneva-adjacent period verb that the
artifact has displaced. This is flagged for the owner-reviewed apply-migration
workflow, not ruled on further here, since it touches restored verse text
rather than an ordinary synonym choice.

Two further findings worth the owner's separate attention, though both remain
KEEP: **"mankind" at Leviticus 18:22/20:13** carries the older, narrower sense
"a male person" (not "humanity") — Geneva itself paraphrases both verses to
"the male," showing even 1599 readers felt the sense needed clarifying — a
Capability-4 glossing note, not a corruption. And the **wet/Daniel 4:15,4:23**
entry's own occurrence text in `batch_5_r2_input.md` did not visibly match
Nebuchadnezzar's tree-stump clause against the witness texts pulled for it;
worth a direct check against `db/mandela.db` outside this pass.

---

## forepart — 6 uses
- verdict: KEEP
- whitelist: none fits precisely; nearest is **side** — Exodus 25:12 "two rings shall be in the one side of it" (freq. ~450) — "side" covers a lateral face, not specifically the *front* face the Hebrew distinguishes at Exod 28:27/39:20 (the ephod's forepart, as opposed to its back).
- witness: Geneva1599 reads "forepart" at Exodus 28:27 and "foreside" at Exodus 39:20 (same sense, sister word); Wycliffe paraphrases both as "the face of" the garment — not a literal cognate but the identical physical referent.
- own: **forepart** stands — a plain compound (fore + part) of two Old English elements, in continuous use through the 17th century; the referent (the front panel of the ephod, the front of Solomon's oracle) is exactly what the Hebrew names.
- reason: Ordinary EModE compound naming an unremarkable architectural/garment referent; Geneva's own variants confirm the word family rather than displacing it. KEEP.

## furbished — 6 uses
- verdict: KEEP
- whitelist: **sharpened** — Ezekiel 21:9 itself, "a sword, a sword is sharpened" (freq. ~35) — covers the companion verb in the same verses but not the specific "polished/scoured bright" sense "furbished" carries alongside it.
- witness: Geneva1599 reads "fourbished" (spelling variant) at both Ezekiel 21:9–10, and "scoured" at Leviticus 6:28 — confirming "furbish" as the metal/vessel-polishing sense and "scour" as its close kin.
- own: **furbished** stands — from Old French "forbir," meaning to polish or burnish, in continuous use for weapons and metal vessels through the 17th century; a sharpened *and* furbished sword is period military vocabulary, not an anachronism.
- reason: Attested in Geneva at every occurrence bar the earthen-pot verse (where Geneva itself swaps to "scoured," its own synonym); genuine EModE metalworking term. KEEP.

## furious — 6 uses
- verdict: KEEP
- whitelist: **wrath** / **wroth** — Genesis 27:44 "until thy brother's fury turn away" uses the cognate noun; "wroth" appears e.g. Genesis 4:5 "Cain was very wroth" (freq. ~230 for wroth). Neither is a drop-in adjective for a person's temperament the way "furious" is.
- witness: Geneva1599 reads "furious" verbatim at all three verses (Prov 22:24, 29:22, and — after "furious rebukes" — Ezek 5:15's own "sharpe rebukes," a synonym swap Geneva itself makes).
- own: **furious** stands — from Latin "furiosus" via Old French, well established in English by the 14th century and common in 1611 prose; names an ordinary human temperament, no source-era anachronism possible.
- reason: Geneva's verbatim agreement at the two Proverbs verses is itself the finding; sound period adjective for wrath-filled anger. KEEP.

## goldsmith — 6 uses
- verdict: KEEP
- whitelist: **gold** / **smith** are separately whitelisted (gold: extremely common; a dedicated compound-craft term is not itself listed). Nearest whole-word candidate: **carpenter** — Isaiah 41:7 itself, "the carpenter encouraged the goldsmith" (freq. ~13) — names the paired trade, not this one.
- witness: Geneva1599 reads "goldsmith"/"goldesmith(es)" at every occurrence; Wycliffe (where present, Nehemiah 3:8/3:31) reads "goldsmyyt" — the identical compound in its Middle English spelling, confirming the word-family runs from Wycliffe through Geneva to KJV unbroken.
- own: **goldsmith** stands — an ordinary trade-compound (gold + smith), attested since Old English "goldsmið"; the trade itself (beating and casting precious metal, Isa 40:19/46:6, Neh 3:8/31/32) is squarely ancient Near Eastern.
- reason: Continuous attestation from Wycliffe through Geneva to the base text is the strongest possible period signal. KEEP.

## goodman — 6 uses
- verdict: KEEP
- whitelist: **master** — Matthew 20:11 (Geneva's own reading, "master of the house"), also Matthew 10:25 "if they have called the master of the house Beelzebub" (freq. ~78) — a safe swap for the "head of household" sense, but flattens the intimate, unpretentious register "goodman" carries (a farmer's wife speaking of her husband, Prov 7:19).
- witness: Tyndale reads "good man" (two words) at both Matthew 20:11 and 24:43 — the identical compound, unhyphenated; Geneva shifts to "master" at 20:11 but keeps "good man" at 24:43, showing the period translators used both interchangeably.
- own: **goodman** stands — a common EModE term for "husband" or "master of a household" (cf. "goodwife"), attested continuously from Chaucer's period through Shakespeare; no anachronism, and the domestic referent (a householder expecting a thief, a wife awaiting her husband) is timeless.
- reason: Tyndale's identical two-word form at both Gospel occurrences, and Geneva's own use of it at Matthew 24:43, confirm this is squarely period vocabulary, not a corruption. KEEP.

## grate — 6 uses
- verdict: KEEP
- whitelist: **network** — Exodus 27:4 itself, "a grate of network of brass" (freq. ~8, all in this same tabernacle-altar passage) — names the mesh pattern but not the object (the brazen grating itself) that sits beneath the altar.
- witness: Geneva1599 reads "grate" verbatim at all three verses; Wycliffe reads "gridele"/"gridile" (an older cognate of "griddle," the same brass-mesh referent under a different period word).
- own: **grate** stands — from Latin "cratis" (wickerwork/hurdle) via Old French, a genuine metalworking term for a barred or meshed brass frame; the altar's brass grating (Exod 27:4, 35:16, 38:4) is a real, excavatable tabernacle furnishing.
- reason: Verbatim Geneva agreement at every occurrence; Wycliffe's independent cognate confirms the referent rather than displacing the word. KEEP.

## greedy — 6 uses
- verdict: KEEP
- whitelist: **covetous** — Isaiah 32:5 itself pairs it, "nor the covetous said to be noble" (freq. ~20) — close in sense (grasping after gain) but "covetous" leans toward desire for others' goods specifically, where "greedy of gain/prey" is the broader appetite.
- witness: Geneva1599 reads "greedy" verbatim at all three verses (Ps 17:12, Prov 1:19, 15:27) — unanimous agreement with the base text.
- own: **greedy** stands — Old English "grædig," among the oldest words in the language, naming an appetite (for prey, for gain) common to lion and man alike in both testaments' worlds.
- reason: Verbatim Geneva agreement at every occurrence is itself the finding. KEEP.

## grope — 6 uses
- verdict: KEEP
- whitelist: **darkness** is whitelisted as the noun (Genesis 1:2, freq. ~150) but is not a verb substitute. Nearest verb candidate: **stagger** — Job 12:25 itself, in the very same verse ("grope in the dark... maketh them to stagger") — names unsteady motion but not blind groping with the hands.
- witness: Geneva1599 reads "grope"/"gropeth" verbatim at all three passages; Wycliffe reads the cognate "grope"/"to grope" at Deuteronomy 28:29 as well, confirming continuity from Middle to Early Modern English.
- own: **grope** stands — Old English "grapian," meaning to feel about blindly with the hands; the referent (blind groping, whether the literal blind man or a nation groping under judgment) needs no modernizing.
- reason: Attested identically in Wycliffe and Geneva alike across three centuries of English — about as strong a period signal as this batch offers. KEEP.

## guests — 6 uses
- verdict: KEEP
- whitelist: **feast** — I Kings 1:41 (Wycliffe's own reading, "clepid... to feeste") is the noun for the occasion, not the people; **strangers** (freq. ~90) names outsiders generally, not invited company specifically. Neither is a precise substitute.
- witness: Geneva1599 reads "ghestes" (spelling variant of "guests") at all three verses; Wycliffe glosses the sense periphrastically ("alle that weren clepid... to feeste") rather than using a single noun.
- own: **guests** stands — from Old Norse "gestr," fully naturalized in English well before 1611; a king's dinner guests and Wisdom's dinner guests (Prov 9:18) are the same unremarkable social referent in both eras.
- reason: Geneva's identical word (spelling aside) at every occurrence settles Axis 1; the referent (invited company at a meal) is timeless. KEEP.

## haply — 6 uses
- verdict: KEEP
- whitelist: **peradventure** — Genesis 18:24 "peradventure there be fifty righteous" (freq. ~80) — the KJV's own default word for "perhaps," a very close synonym and a safe swap if ever wanted.
- witness: Geneva1599 reads "haply" only at Luke 14:29 (Tyndale agrees, "lest after..."); at I Samuel 14:30 and Mark 11:13 Geneva simply omits the word or paraphrases ("if the people had eaten," "went to see if"), showing "haply" as an KJV-specific intensifier the Geneva translators felt free to drop.
- own: **haply** stands — "hap" + "-ly," meaning "by chance," attested throughout Shakespeare and Sidney; a natural period adverb, interchangeable with "peradventure" but metrically and rhythmically distinct, which matters in Mark 11:13's narrative cadence.
- reason: A genuine period adverb even where Geneva chooses to omit it rather than translate it differently — omission is not counter-attestation. KEEP.

## horrible — 6 uses
- verdict: KEEP
- whitelist: **fearful** — Hebrews 10:27 "a certain fearful looking for of judgment" (freq. ~40) is a plausible register-match near-synonym, though it leans toward the subject's fear rather than the object's dreadfulness.
- witness: Geneva1599 reads "horrible" at Jeremiah 5:30 verbatim, and "the horrible pit" at Psalm 40:2 verbatim; at Psalm 11:6 Geneva reads "stormie tempest" instead of "horrible tempest," its own synonym choice.
- own: **horrible** stands — from Latin "horribilis" via Old French, established in English since Chaucer; dreadful pits, storms, and deeds are equally sound referents in the ancient Near Eastern and 1611 worlds alike.
- reason: Verbatim Geneva agreement at two of three verses, with the third showing Geneva's own synonym substitution rather than any sign the word is wrong. KEEP.

## informed — 6 uses
- verdict: KEEP
- whitelist: **taught** — very common (freq. ~70), but "taught" implies instruction over time, not the punctual "given a report" sense "informed" carries in Acts 21 and Daniel 9.
- witness: Geneva1599 and Tyndale both read "informed" verbatim at Acts 21:21 and 21:24; Geneva also reads "informed" at Daniel 9:22.
- own: **informed** stands — from Latin "informare" via Old French, attested since the 14th century in the sense "to give shape/knowledge to the mind"; Gabriel informing Daniel and Jerusalem's believers informing Paul's accusers are both ordinary period usages of the verb.
- reason: Verbatim agreement across both surviving witnesses at every occurrence. KEEP.

## jeopardy — 6 uses
- verdict: KEEP
- whitelist: **peril** — Wycliffe's own word at all three verses ("perel of soulis," "perel of her lyues," "with perel of oure heed") — a very close synonym, freq. ~10 in KJV.db (e.g. II Cor 11:26 "in perils of waters").
- witness: Geneva1599 reads "ieopardie"/"ieopardy" (spelling variant) verbatim at all three verses; Wycliffe independently reads "perel" at the same three verses — both period witnesses agree on the sense, differing only in which of the two available period nouns they chose.
- own: **jeopardy** stands — from Old French "jeu parti" ("divided play," an even chance/risk in a game), narrowed to "danger, peril" by the 15th century; the referent (risking one's life in battle) is exactly what David's mighty men and Saul's captains faced.
- reason: Two independent witnesses (Geneva verbatim, Wycliffe by synonym) confirm both the word and the sense are sound EModE. KEEP.

## lady — 6 uses
- verdict: KEEP
- whitelist: **queen** — extremely common (freq. ~450), a near-neighbor rank-title but not interchangeable — "lady" at Isaiah 47:5/7 and II John 1:1 names a woman of general rank or a specific addressee, not a reigning queen.
- witness: Geneva1599 reads "ladie"/"Lady" verbatim at Isaiah 47:5/7 and II John 1:1; at Esther 1:18 Geneva reads "princesses" where the base text has "ladies" — its own synonym choice for the same court-women referent.
- own: **lady** stands — Old English "hlæfdige" ("loaf-kneader," the mistress of a household), one of the oldest surviving English social titles; wise ladies of a defeated general's court, the "lady of kingdoms" (Babylon personified), and the addressee of II John are all sound period and source-era referents.
- reason: Verbatim Geneva agreement at four of five verses, with the fifth showing only a synonym choice, not disagreement. KEEP.

## liberal — 6 uses
- verdict: KEEP
- whitelist: **bountiful** — Psalm 13:6 "the Lord hath dealt bountifully with me" family (freq. ~20) — a safe near-synonym for "generous," though "liberal" in Isaiah 32:5/8 also carries the older sense "noble/high-minded," not just open-handed.
- witness: Geneva1599 reads "liberall" (spelling variant) verbatim at all three verses, including the repeated wordplay "the liberall man will deuise of liberall things" at Isaiah 32:8.
- own: **liberal** stands — from Latin "liberalis" ("befitting a free person"), in continuous English use since the 14th century for "generous, open-handed, or noble-minded"; carries no trace of the 19th–20th-century political sense that could mislead a modern ear, since KJV.db's context (soul made fat, watering others) makes the almsgiving sense unmistakable.
- reason: Verbatim Geneva agreement (spelling aside) at every occurrence, including the repeated internal wordplay at Isaiah 32:8. KEEP — though flag for Capability-4 glossing, since "liberal" is the batch's clearest modern-meaning-drift risk.

## lucre — 6 uses
- verdict: KEEP
- whitelist: **gain** — Proverbs 1:19 itself, "every one that is greedy of gain" (freq. ~60) — the KJV's own preferred word for sordid profit elsewhere, and a workable swap, though it loses "lucre's" specifically mercenary, money-handling connotation (bribes, church office bought for profit).
- witness: Geneva1599 reads "lucre" verbatim at all four verses, including the fixed phrase "filthy lucre" at I Timothy 3:3/3:8 and "filthie lucres sake" at Titus 1:11.
- own: **lucre** stands — from Latin "lucrum" via Old French, meaning sordid monetary gain; "filthy lucre" is one of the KJV's most recognizable fixed phrases, condemning exactly the bribe-taking (I Sam 8:3) and profiteering ministry (I Tim/Titus) the biblical text itself describes.
- reason: Verbatim Geneva agreement at all four occurrences, including the idiom's exact wording. KEEP.

## mankind — 6 uses
- verdict: KEEP
- whitelist: **man** — Leviticus 18:22 itself pairs it ("as one lieth with a woman"), the KJV's ordinary word for a male individual (freq. ~2,200); it is not a substitute for "mankind" as a class-noun, which is the sense Leviticus needs (any male, generically).
- witness: Geneva1599 reads "the male" at both Leviticus 18:22 and 20:13 (its own periphrasis for the same referent), but keeps "mankinde" (spelling variant) verbatim at Job 12:10, "the breath of all mankinde."
- own: **mankind** stands, with a Capability-4 flag — in Leviticus 18:22/20:13 it carries the older sense "a male person" (not "humanity"), a genuine semantic shift from its own use three verses' distance away at Job 12:10 ("all mankind" = the human race). Both senses are independently well attested in period English; the word itself needs no swap.
- reason: Geneva's own paraphrase at the two Levitical verses shows the "male person" sense was already felt to need clarifying even in 1599; that is a glossing note, not a corruption. The Job 12:10 sense is verbatim-attested. KEEP.

## mariners — 6 uses
- verdict: KEEP
- whitelist: **shipmen** — I Kings 9:27 itself, "shipmen that had knowledge of the sea" (freq. ~5) — the KJV's own synonym for the identical trade, a safe swap.
- witness: Geneva1599 reads "mariners" verbatim at Ezekiel 27:8/9, but "robbers" at Ezekiel 27:26 (a divergent reading, likely a Hebrew-root ambiguity between "sailor" and "raider" that Geneva resolved the opposite way from KJV).
- own: **mariners** stands — from Old French "marinier," attested in English since the 14th century for seafaring men; Tyre's Sidonian and Arvadite crews are a sound, well-documented ancient Near Eastern referent (Phoenician seafaring).
- reason: Geneva's verbatim agreement at two of three verses is solid; the Ezekiel 27:26 divergence is a translation-choice difference worth noting to the owner but is not evidence against "mariners" itself, which Geneva uses elsewhere in the same chapter. KEEP.

## meditation — 6 uses
- verdict: KEEP
- whitelist: **meditate** — Joshua 1:8 "thou shalt meditate therein day and night" (freq. ~20) — the verb form is already whitelisted; the noun is its direct, unremarkable derivative.
- witness: Geneva1599 reads "meditation" verbatim at Psalm 19:14 and 49:3; at Psalm 5:1 Geneva reads "vnderstande my meditation," differing only in the verb, not the noun.
- own: **meditation** stands — from Latin "meditatio" via Old French, the ordinary period word for inward, wordless reflection or prayer; needs no modernizing.
- reason: Verbatim Geneva agreement on the noun at every occurrence. KEEP.

## memory — 6 uses
- verdict: KEEP
- whitelist: **remembrance** — Exodus 17:14 "I will utterly put out the remembrance of Amalek" (freq. ~60) — the KJV's own preferred word for the identical "cutting off a name" sense, and Geneva's own choice at Ps 109:15/Prov 10:7 (see witness).
- witness: Geneva1599 reads "memoriall" at Psalm 109:15 and Proverbs 10:7 (its own cognate noun, not "memory"), and "mention" at Psalm 145:7 — showing the period translators treated "memory/memorial/remembrance/mention" as one interchangeable word-family.
- own: **memory** stands — from Latin "memoria" via Old French, in continuous use since Chaucer for exactly this sense (a person's name/reputation surviving after death); no anachronism.
- reason: Geneva's own shifting choice among "memorial/mention/remembrance" across these same three verses shows the whole word-family was fluid in period use — "memory" is squarely inside that family, not outside it. KEEP.

## mete — 6 uses
- verdict: KEEP
- whitelist: **measure** — Geneva's own reading at all three verses (see witness) — extremely common in KJV.db (freq. ~150, e.g. Ruth 3:15 "she measured six measures of barley") and the safest possible swap.
- witness: Geneva1599 reads "measure"/"measure it" at all three verses (Exod 16:18, Ps 60:6, Ps 108:7) — a consistent synonym substitution across every occurrence, not agreement with "mete" itself.
- own: **mete** stands — Old English "metan," the etymological root of "measure" itself and of "meted out" (still current); a terser, more forceful verb than "measure" for Psalm 60:6/108:7's parallelism ("divide... mete out").
- reason: Geneva consistently prefers its own cognate "measure" at every occurrence, which is worth flagging to the owner as a real alternate, but "mete" is the older/terser form of the very same Germanic root, not a foreign intrusion — Wycliffe's "metiden" at Exodus 16:18 confirms the same root reaching back to Middle English. KEEP.

## navy — 6 uses
- verdict: KEEP
- whitelist: **ships** — I Kings 9:26 itself, "made a navy of ships" (freq. ~140) — the KJV's own paired noun; a safe swap for the plural vessels, but "navy" specifically names the assembled fleet as a body, which "ships" alone does not.
- witness: Geneva1599 reads "nauie" (spelling variant) verbatim at all three verses; Wycliffe instead reads "o schip" (a single ship) at I Kings 9:26 — a numerically divergent reading worth noting, though 9:27's "that schip" and 10:11's "the schip of Hiram" show Wycliffe consistently singularizing where KJV/Geneva have a collective fleet-noun.
- own: **navy** stands — from Latin "navis" via Old French "navie," meaning simply "a fleet of ships" in 1611 (not yet the specialized "state's warships" sense); Solomon's and Hiram's joint merchant fleet at Ezion-geber is a well-documented ancient trade referent.
- reason: Verbatim Geneva agreement at every occurrence; Wycliffe's singular is a translation variant, not counter-evidence against the word. KEEP.

## neglect — 6 uses
- verdict: KEEP
- whitelist: **despise** — Geneva's own reading at I Timothy 4:14 and Hebrews 2:3 (see witness), freq. ~90 (e.g. Prov 1:7 "fools despise wisdom") — a workable swap, though it sharpens "neglect"'s passive omission into active contempt.
- witness: Geneva1599 reads "refuse" at Matthew 18:17, "Despise not" at I Timothy 4:14, and "if we neglect" verbatim at Hebrews 2:3; Tyndale reads "If he heare not" at Matthew 18:17 and "despyse" at Hebrews 2:3. Acts 6:1's "neglected" is verbatim in Geneva, "despysed" in Tyndale.
- own: **neglect** stands — from Latin "neglegere" ("not to pick up/heed"), attested in English since the 15th century; the referent (omitting a duty, overlooking a widow's daily bread) is unremarkable in any era.
- reason: Split witness evidence (Geneva keeps "neglect" at two of five occurrences, both witnesses paraphrase at the other three) shows the word-family was fluid across "neglect/despise/refuse" in 1611 English generally — not a sign this specific word is wrong. KEEP.

## omer — 6 uses
- verdict: WHITELIST
- whitelist: none exists yet for this specific unit; nearest reviewed measure-word is **shekel** — Exodus 30:13, freq. ~301 — the same *category* (a fixed ancient unit of measure) but a different commodity (weight of silver, not volume of manna).
- witness: Geneva1599 keeps "Omer" (capitalized, transliterated) verbatim at all four verses; Wycliffe transliterates the Hebrew directly as "gomor" at the same four verses — both period witnesses treat it as an untranslatable loanword, exactly as KJV does.
- own: **omer** stands — a transliterated Hebrew dry-measure (about 2.3 liters), named and defined within the text itself (Exod 16:36, not in this batch); no English equivalent exists, so every period and modern witness alike keeps the loanword.
- reason: A measure-term with a unique, non-substitutable referent — exactly the WHITELIST category (units of measure), per the same reasoning that protected "gerahs" and "shekel" in earlier batches. Should be added to the whitelist and protected from all future swap passes.

## parlour — 6 uses
- verdict: KEEP
- whitelist: **chamber** — I Chronicles 28:11 itself pairs it ("upper chambers... inner parlours"), freq. ~300 — the KJV's own generic room-word, though it loses the specific "private inner room" sense "parlour" carries at Judges 3.
- witness: Geneva1599 reads "parler" (spelling variant) verbatim at all three Judges verses; Wycliffe reads "parlour"/"somer parlour" at the same verses — both period witnesses independently confirm the same word across two centuries.
- own: **parlour** stands — from Old French "parlur" ("place for speaking"), attested since the 13th century for a private inner room; Eglon's "summer parlour" (a cooled upper chamber) is a well-attested Levantine architectural feature.
- reason: Wycliffe-to-Geneva-to-KJV continuity across three centuries is about as strong a period signal as exists in this batch. KEEP.

## pisseth — 6 uses
- verdict: WHITELIST
- whitelist: none carries the identical crude register; nearest is **dung** — II Kings 9:37, freq. ~15 — a comparably blunt bodily-function word the KJV does not euphemize, but not a synonym for this specific idiom.
- witness: Geneva1599 reads "pisseth" verbatim at all three verses — the identical word, identical idiom ("any that pisseth against the wall," a Hebrew idiom for "male person"); Wycliffe reads "a pissere to the wal" (noun form of the same root) at the same three verses.
- own: **pisseth** stands — a plain Germanic verb, unchanged from Old English through 1611 and into modern English; the fixed idiom "him that pisseth against the wall" (a euphemism-avoiding way of saying "every male") is deliberately blunt in the Hebrew and should not be softened.
- reason: Unanimous three-witness agreement (Geneva verbatim, Wycliffe by cognate) across three centuries. Because this exact word is the single likeliest target for a future "modernize the crude bits" pass, it should be WHITELISTED now to protect the KJV's own deliberate bluntness from later euphemism.

## practise — 6 uses
- verdict: KEEP
- whitelist: **do** — extremely common (freq. ~2,000), the most generic possible verb; workable in places ("practise wicked works" → "do wicked works") but loses the specific "make a habitual course of" sense needed at Daniel 8:12/24.
- witness: Geneva1599 reads "practise" verbatim at Psalm 141:4, Isaiah 32:6 ("practise hypocrisy"), and Daniel 8:24; at Daniel 8:12/I Samuel 23:9 Geneva reads "practised"/"imagined" — one verbatim, one synonym.
- own: **practise** stands — from Greek "prassein" via Old French "practiser," meaning "to carry out habitually" (a craft, a scheme, a habitual sin); the spelling itself (practise, not practice) is the period-correct verb form, still distinguished from the noun in British usage today.
- reason: Verbatim Geneva agreement at three of five occurrences; genuine EModE verb naming a timeless referent (habitual wrongdoing). KEEP.

## presumptuously — 6 uses
- verdict: KEEP
- whitelist: **pride** — Deuteronomy 1:43 itself is glossed by Geneva as "were presumptuous" where Wycliffe reads "bolnden with prijde" ("swollen with pride") — freq. ~50 for "pride," a workable adverbial root-swap ("proudly") but a weaker, less legally precise word than "presumptuously."
- witness: Geneva1599 reads "presumptuously" verbatim at Exodus 21:14 and Numbers 15:30; at Deuteronomy 1:43 Geneva reads "were presumptuous, and went vp" (adjective, not adverb) — the same word-family, different part of speech.
- own: **presumptuously** stands — from Latin "praesumere" ("to take beforehand/take for granted"), a precise legal-and-theological term distinguishing deliberate, high-handed sin from accidental sin (the Numbers 15 context depends on exactly this distinction, "sins of a high hand" vs. sins of ignorance).
- reason: Verbatim Geneva agreement at two of three verses, with the third showing only a part-of-speech shift within the same word-family; the word carries real legal-theological weight that a vaguer swap would blur. KEEP.

## prospect — 6 uses
- verdict: KEEP
- whitelist: **toward** — extremely common (freq. ~600) but a preposition, not a noun; no whitelisted noun currently covers "the direction a chamber's opening faces."
- witness: Geneva1599 reads "prospect" verbatim at all three verses (Ezek 40:44/45/46) — unanimous agreement with the base text; Wycliffe has no equivalent verses in this stretch of Ezekiel's temple vision.
- own: **prospect** stands — from Latin "prospectus" ("a looking forward"), meaning in 1611 simply "the direction something faces or looks out upon" (not yet the modern "future outlook" sense); Ezekiel's temple-chamber orientations are an architectural referent the word fits precisely.
- reason: Verbatim Geneva agreement at every occurrence. KEEP — though flag for Capability-4 glossing, since "prospect" has shifted furthest in ordinary modern use toward "future expectation."

## quit — 6 uses
- verdict: KEEP
- whitelist: **innocent** — Wycliffe's own reading at all three verses (see witness), freq. ~80 (e.g. Exod 21:28 elsewhere) — close in legal sense (not liable) but "quit" specifically means "released/discharged from obligation," a narrower legal-procedural sense.
- witness: Geneva1599 reads "go quite" (two words, spelling variant) at Exodus 21:19/28 and "be quite of thine othe" at Joshua 2:20; Wycliffe reads "innocent" at the two Exodus verses and "cleene" (clean/clear) at Joshua 2:20.
- own: **quit** stands — from Latin "quietus" via Old French "quiter" ("to release, discharge"), the ordinary 1611 legal term for release from a debt, oath, or liability (distinct from modern "quit" = "stop/leave"); the ancient Near Eastern legal contexts (bodily-injury liability, an oath of protection) are exactly what the word names.
- reason: Geneva's spelling-variant agreement at every occurrence, plus Wycliffe's independent synonym choices confirming the same legal sense, settle both axes. KEEP — flag for Capability-4 glossing, since modern "quit" (= stop doing something) is a false-friend risk for readers.

## reddish — 6 uses
- verdict: KEEP
- whitelist: **red** — extremely common (freq. ~50, e.g. Exodus 25:5 "rams' skins dyed red"), the root adjective; a workable swap in a pinch but loses the diagnostic "somewhat red, not fully red" nuance Leviticus 13's leprosy-diagnosis procedure depends on.
- witness: Geneva1599 reads "reddish" verbatim at all three verses; Wycliffe reads "sum deel reed" ("somewhat red") at Leviticus 13:19 and "whijt ether reed" at 13:24/42 — the same graded-color sense expressed periphrastically rather than with the single derived adjective.
- own: **reddish** stands — red + the Old English diminutive/approximative suffix "-ish," precisely the graded, partial-color sense the Levitical priest's differential diagnosis needs (a skin condition that is not fully red, only reddish, changes the priest's ruling).
- reason: Verbatim Geneva agreement at every occurrence, with Wycliffe independently confirming the same graded sense by periphrasis. The word's precision is medically/legally load-bearing in this passage. KEEP.

## replenished — 6 uses
- verdict: KEEP
- whitelist: **filled** — extremely common (freq. ~450), a workable swap at Genesis 9:19/Isaiah 2:6 (Geneva itself reads "full of" at Isa 2:6, see witness) but a weaker word than the KJV's own choice for "populated/re-stocked," which "replenished" carries more precisely.
- witness: Geneva1599 reads "ouerspred" at Genesis 9:19, "full of the East maners" at Isaiah 2:6, and "haue replenished thee" verbatim at Isaiah 23:2; Tyndale reads "overspred" at Genesis 9:19, matching Geneva rather than KJV.
- own: **replenished** stands — from Latin "replere" via Old French "replenir" ("to fill again/fill completely"), attested since the 14th century; the earth "replenished" by Noah's sons and an island "replenished" by Sidon's merchants are both sound uses of the "populated/filled up" sense.
- reason: Genuine period word even where both period witnesses (Geneva and Tyndale) independently prefer "overspread" at Genesis 9:19 — that is a translation-choice difference worth noting, not evidence against "replenished," which Geneva itself uses verbatim at Isaiah 23:2. KEEP.

## rereward — 6 uses
- verdict: KEEP
- whitelist: **host** — extremely common (freq. ~500), names the whole army but not specifically its rear division; no whitelisted word currently covers this specific military-formation sense.
- witness: Geneva1599 reads "the standerd... marched, gathering all ye hostes" at Numbers 10:25 (paraphrase) and "the gathering hoste" verbatim-in-sense at Joshua 6:9/13 — Geneva's own periphrasis for the identical military term.
- own: **rereward** stands — "rear" + "ward" (guard), the standard 1611 military term for the army's rear division/guard (the ancestor of modern "rearguard"); the marching order of Israel's tribal divisions and Joshua's procession around Jericho are both concrete, source-era-sound military formations.
- reason: A genuine, unambiguous EModE military compound; Geneva's periphrastic agreement confirms the sense even where it avoids the single compound word. KEEP.

## restitution — 6 uses
- verdict: KEEP
- whitelist: **recompense** — extremely common (freq. ~35, e.g. Esther 7:4 elsewhere in this batch's own witness text), a close synonym for repayment, though "restitution" specifically names *restoring what was taken/damaged*, a narrower legal-procedural sense than general recompense.
- witness: Geneva1599 reads "restitution" verbatim at all three verses (Exod 22:3/5/6) — unanimous agreement with the base text.
- own: **restitution** stands — from Latin "restituere" ("to restore/set up again"), the precise legal term for repaying theft or damage in kind or value; the Covenant Code's theft-and-damage statutes (a stolen ox, a grazing beast, a field fire) are exactly the ancient Near Eastern casuistic law this word describes.
- reason: Verbatim Geneva agreement at every occurrence. KEEP.

## revenue — 6 uses
- verdict: KEEP
- whitelist: **tribute** — Ezra 4:13 itself pairs it (Geneva's own reading, "hinder the Kings tribute"), freq. ~40 — close in the royal-income sense, but "revenue" in Proverbs 8:19/15:6/16:8 also covers personal/wisdom's "increase" or "fruit," a broader sense than "tribute" alone.
- witness: Geneva1599 reads "the Kings tribute" (not "revenue") at Ezra 4:13, "reuenues" verbatim at Proverbs 8:19/15:6/16:8, and "your fruites" (not "revenues") at Jeremiah 12:13 — three of six verbatim, two showing Geneva's own synonym choice.
- own: **revenue** stands — from Old French "revenue" ("that which comes back/returns"), attested since the 15th century for income of any kind, royal or personal; Persian imperial tribute and a righteous man's "increase" are both period-and-source-era-sound referents.
- reason: Majority verbatim agreement (three of six occurrences) with Geneva itself, the other three showing only translation-choice variance, not disagreement with the word. KEEP.

## reviled — 6 uses
- verdict: KEEP
- whitelist: **reproach** — extremely common (freq. ~300, e.g. Matt 5:11 "when men shall revile you" nearby), the noun form of the identical root-verb; a safe near-synonym.
- witness: Geneva1599 reads "reuiled" (spelling variant) verbatim at all three verses; Tyndale reads "revyled" at Matthew 27:39, "checked" at Mark 15:32, and "rated" at John 9:28 — one verbatim, two showing Tyndale's own more colloquial synonym choices.
- own: **reviled** stands — from Old French "reviler" ("to hold vile, treat with contempt"), the KJV's standing word for verbal abuse and mockery throughout (cf. Matt 5:11, I Pet 2:23); the crowd mocking a crucified man and Pharisees mocking a healed beggar are both timeless, source-era-sound scenes.
- reason: Verbatim Geneva agreement (spelling aside) at all three verses; Tyndale's more colloquial choices are a register variant, not a competing reading. KEEP.

## rid — 6 uses
- verdict: KEEP
- whitelist: **deliver** — extremely common (freq. ~450), Geneva's own preferred word at Exodus 6:6/Genesis 37:22 (see witness) — a strong, safe swap, though it loses "rid"'s more forceful "clear away/remove entirely" sense at Leviticus 26:6 ("rid evil beasts out of the land").
- witness: Geneva1599 reads "deliuer him" at Genesis 37:22, "deliuer you" at Exodus 6:6, and "rid" verbatim at Leviticus 26:6; Tyndale reads "rydd" verbatim at Genesis 37:22.
- own: **rid** stands — Old Norse "ryðja" ("to clear"), attested in English since the 13th century for "to clear away/remove"; clearing dangerous beasts from a land and rescuing a captive brother are both sound uses.
- reason: Tyndale's independent verbatim agreement at Genesis 37:22 and Geneva's own verbatim use at Leviticus 26:6 together confirm the word, even though Geneva prefers "deliver" at the other two verses — a translation choice, not a correction. KEEP.

## roughly — 6 uses
- verdict: KEEP
- whitelist: **cruelly** — Geneva's own reading at I Samuel 20:10 (see witness), freq. ~20 — close in force but implies deliberate harm, stronger than the brusque-but-not-violent sense "roughly" carries in Joseph's staged harshness toward his brothers.
- witness: Geneva1599 reads "roughly" verbatim at both Genesis verses and "cruelly" (synonym) at I Samuel 20:10; Tyndale reads "rughly" (spelling variant) at both Genesis verses.
- own: **roughly** stands — rough (Old English "ruh") + "-ly," attested since Middle English for harsh manner of speech or action; Joseph's feigned harshness and Jonathan's fear of Saul's temper are both ordinary, timeless human referents.
- reason: Verbatim agreement from both surviving period witnesses (Geneva and Tyndale) at the two Genesis occurrences; Geneva's I Samuel synonym is a translation choice, not disagreement. KEEP.

## savoury — 6 uses
- verdict: KEEP
- whitelist: **pleasant** — Geneva's own reading at Genesis 27:9 (see witness), freq. ~60 — a workable general-purpose synonym, though it loses "savoury"'s specific culinary "well-seasoned, appetizing to taste" sense.
- witness: Geneva1599 reads "sauourie" (spelling variant) verbatim at Genesis 27:4/7, and "pleasant meate" (synonym) at 27:9; Tyndale simply reads "meate" (unmodified) at all three verses, omitting the adjective entirely.
- own: **savoury** stands — from Old French "savoure" via Latin "sapor" ("taste, flavor"), attested since the 13th century for well-seasoned, appetizing food; Isaac's venison stew is a concrete, source-era-sound culinary referent (wild game, herb-seasoned).
- reason: Verbatim Geneva agreement (spelling aside) at two of three verses; Tyndale's omission at all three is itself notable (worth flagging as a translation-choice variant) but not evidence the word is wrong, since Geneva independently retains it. KEEP.

## sect — 6 uses
- verdict: KEEP
- whitelist: **heresy** — Acts 24:14 nearby ("after the way which they call heresy," not in this batch but same word-family), freq. ~5 — the pejorative sibling-word for the same "faction/school of thought" referent, usable but carries a stronger condemnatory charge than the neutral "sect."
- witness: Geneva1599 and Tyndale both read "sect"/"secte" (spelling variant) verbatim at all three verses (Acts 5:17, 15:5, 24:5) — unanimous three-way agreement.
- own: **sect** stands — from Latin "secta" ("a following, faction, school of philosophy"), the ordinary neutral period word for a religious or philosophical party (Sadducees, Pharisees, Nazarenes/Christians) — exactly the first-century Jewish and Jewish-Christian social referent Acts describes.
- reason: Unanimous three-witness agreement (Geneva and Tyndale verbatim, spelling aside) at every occurrence. KEEP.

## seize — 6 uses
- verdict: KEEP
- whitelist: **possess** — Geneva's own reading at Job 3:6 (see witness), freq. ~180 — workable in the "take hold of/lay claim to" sense, though it loses "seize"'s sudden, forceful connotation.
- witness: Geneva1599 reads "destroy the citie" at Joshua 8:7 (synonym, not "seize"), "let darkenesse possesse" at Job 3:6, "death sense vpon them" (a period spelling of "seize") at Psalm 55:15, and "feare hath seased her" (spelling variant of "seized") at Jeremiah 49:24.
- own: **seize** stands — from Old French "seisir" (feudal legal term for "to put in possession of/take hold of"), attested in English since the 13th century; darkness gripping a night, death gripping the wicked, and fear gripping Damascus are all sound figurative uses with no anachronism.
- reason: Geneva's own spelling variants ("sense"/"seased") at two of four verses confirm the identical word under 1599 orthography; the Joshua 8:7 synonym is a translation choice. KEEP.

## shearers — 6 uses
- verdict: KEEP
- whitelist: **sheep** — extremely common (freq. ~190); names the animal, not the tradesman who shears it — no whitelisted word currently covers this specific trade.
- witness: Geneva1599 reads "sheepe sherers"/"sherers" (spelling variant) verbatim at all three verses; Wycliffe reads "schereris"/"the schereris of hise scheep" — the identical trade-word across three centuries of English.
- own: **shearers** stands — shear (Old English "sceran," to cut) + "-er," naming the tradesmen who clip wool from sheep at the annual shearing-feast; Judah's and Nabal's sheep-shearing feasts are a well-documented ancient Near Eastern pastoral-economic institution.
- reason: Continuous Wycliffe-to-Geneva-to-KJV attestation of the identical trade-word. KEEP.

## sink — 6 uses
- verdict: KEEP
- whitelist: **deep** — extremely common (freq. ~200, appears in the very same verses, "deep mire," "deep waters"), an adjective, not a verb substitute — no whitelisted verb currently covers "to go under."
- witness: Geneva1599 reads "sticke fast in the deepe myre" at Psalm 69:2 (synonym, not "sink"), "sinke" verbatim at Psalm 69:14, and "be drowned" (synonym) at Jeremiah 51:64.
- own: **sink** stands — Old English "sincan," among the oldest words in the language for downward submersion; a man sinking in mire and a city "sinking" (Babylon's judgment-symbol of a stone cast into the Euphrates, Jer 51:63-64) are both ordinary, source-era-sound images.
- reason: Verbatim Geneva agreement at one of three verses, with the other two showing synonym choices ("stick fast," "be drowned") rather than disagreement with "sink" itself, which Geneva uses at Psalm 69:14. KEEP.
## snuffers — 6 uses
- verdict: WHITELIST
- whitelist: none exists yet for this cultic implement; nearest is **censers** — II Kings 12:13 itself, freq. ~30 — a paired temple-furnishing term but a different implement (incense pans, not wick-trimmers).
- witness: Geneva1599 reads "snuffers" verbatim at Exodus 37:23, but "hookes" at I Kings 7:50 and "instruments of musicke" at II Kings 12:13 — two divergent readings worth flagging, since a wick-trimmer, a hook, and a musical instrument are three different objects.
- own: **snuffers** stands — a compound of "snuff" (to trim a candle-wick) + "-er," the correct implement for tending the golden lampstand's wicks (Exod 37:23, I Kings 7:50); a prior round (batch 4) already flagged "tongs" as a wrong substitute here, confirming "snuffers" is the settled correct reading for this referent.
- reason: This is a cultic-implement noun with a unique referent (the candlestick's wick-trimmer) — exactly the WHITELIST category. Geneva's own divergence at two of three verses (to "hooks"/"instruments of musicke") shows real translation instability around this word across witnesses, which argues for protecting the settled KJV reading rather than inviting a fourth variant.

## sodden — 6 uses
- verdict: KEEP
- whitelist: **boiled** — Geneva's own reading, paired at Leviticus 6:28 ("boyled nor sodden," see witness), freq. ~10 — a workable modern-sounding swap, though "sodden" is the KJV's own preferred term used consistently across all three verses.
- witness: Geneva1599 reads "sodden" verbatim at Leviticus 6:28 and Numbers 6:19, and "boyled nor sodden" (both words together) at Exodus 12:9; Wycliffe reads "sodun" (spelling variant) at all three verses.
- own: **sodden** stands — the old past participle of "seethe" (to boil), attested continuously from Old English through 1611 for boiled meat; the Passover lamb's roasting-not-boiling instruction and the Nazirite's boiled ram-shoulder are both concrete Levitical cooking-method referents.
- reason: Continuous Wycliffe-to-Geneva-to-KJV attestation of the identical participle at every occurrence. KEEP.

## specially — 6 uses
- verdict: KEEP
- whitelist: none of comparable brevity; nearest is **chiefly** — I Timothy 5:8 (not in this batch but same word-family), freq. ~10 — a close synonym for "especially/above all," a safe swap.
- witness: Geneva1599 and Tyndale both read "specially" verbatim at Acts 25:26 and I Timothy 4:10; at Deuteronomy 4:10 Geneva reads "Forget not the day" (omitting "specially" as a separate intensifier, its own translation choice).
- own: **specially** stands — special + "-ly," attested since the 14th century as an intensifying adverb meaning "above all/particularly"; used identically then and now, with no anachronism in any of its three contexts.
- reason: Verbatim two-witness agreement (Geneva and Tyndale) at two of three verses. KEEP.

## square — 6 uses
- verdict: KEEP
- whitelist: **foursquare** — Geneva's own reading at I Kings 7:5/Ezekiel 45:2 (see witness), freq. ~15 (e.g. Rev 21:16 "the city lieth foursquare") — a very close, already-whitelisted synonym.
- witness: Geneva1599 reads "foure square" (two words) at I Kings 7:5, "fouresquare" (one word) at Ezekiel 43:16/45:2, and "squared" verbatim at Ezekiel 41:21 — showing "square" and "foursquare" as interchangeable period spellings/compounds of the same word.
- own: **square** stands — from Latin "exquadrare" via Old French "esquarre," the ordinary geometric term since the 13th century; the temple's and altar's precise cubit-measured square dimensions are a real architectural referent, well documented in ancient Near Eastern temple-building.
- reason: Geneva's own use of the near-identical compound "foursquare"/"fouresquare" at every occurrence confirms this is the same word-family, not a competing reading. KEEP.

## stagger — 6 uses
- verdict: KEEP
- whitelist: **reel** — Geneva's own reading at Isaiah 24:20 (see witness), freq. ~5 — a close synonym for unsteady drunken motion, workable but rarer in KJV.db than "stagger."
- witness: Geneva1599 reads "stagger" verbatim at Job 12:25 and Psalm 107:27, "reele" at Isaiah 24:20, and "erreth" at Isaiah 19:14; Tyndale reads "stackered" (spelling variant) verbatim at Romans 4:20.
- own: **stagger** stands — of Scandinavian origin (cf. Old Norse "stakra"), attested in English since the 14th century for unsteady, wavering motion, whether physical (a drunkard) or figurative (Abraham's faith not "staggering" at God's promise); no anachronism in any of the five contexts.
- reason: Verbatim agreement from both surviving witnesses (Geneva at two verses, Tyndale independently at Romans 4:20) confirms the word soundly. KEEP.

## story — 6 uses
- verdict: KEEP
- whitelist: **treatise** — Geneva's and Tyndale's own reading at Acts 1:1 (see witness), freq. ~1 (rare, this exact verse) — a precise synonym for the "written account" sense at Acts 1:1, though it does not cover the unrelated "building level" sense at Genesis 6:16/Ezekiel 41:16/42:3.
- witness: Geneva1599 reads "roume" (room/level) at Genesis 6:16, "sides" at Ezekiel 41:16, "rowes" at Ezekiel 42:3, and "treatise" (not "story") at Acts 1:1; Tyndale reads "loftes" at Genesis 6:16 and "treatise" at Acts 1:1.
- own: **story** stands as two genuinely separate period senses under one spelling — "story" (a building's level, from Latin "historia" via a medieval sense-shift through illustrated architectural tiers) at Genesis/Ezekiel, and "story" (a written narrative account) at Acts 1:1; both senses are well attested by 1611 and neither is anachronistic.
- reason: This is a real Capability-4 semantic-split case (architectural "storey" vs. narrative "story," now spelled differently in modern English but identical in 1611); both period witnesses independently prefer synonyms at every verse, which is useful context for the owner but does not make the base word wrong. KEEP.

## subtilty — 6 uses
- verdict: KEEP
- whitelist: **craft** — extremely common (freq. ~30, e.g. Dan 8:25 "cause craft to prosper"), a close synonym for cunning/guile, a safe swap.
- witness: Geneva1599 reads "subtiltie" (spelling variant) verbatim at Genesis 27:35 and II Kings 10:19, and "sharpenesse of wit" at Proverbs 1:4; Tyndale reads "subtilte" (spelling variant) verbatim at Genesis 27:35.
- own: **subtilty** stands — from Latin "subtilis" via Old French "soutilte," the ordinary period spelling of "subtlety," meaning cunning or craftiness (Jacob's deceit, Jehu's stratagem) or, at Proverbs 1:4, "shrewdness/discernment" in a positive sense; both senses are period-standard.
- reason: Verbatim two-witness agreement (Geneva and Tyndale, spelling aside) at Genesis 27:35, plus Geneva's verbatim use at II Kings 10:19. KEEP.

## target — 6 uses
- verdict: KEEP
- whitelist: **shield** — Geneva's own reading at I Samuel 17:6 (see witness), freq. ~150 — a close, already-whitelisted synonym for the general defensive-armor sense, though "target" in 1611 specifically named a smaller round shield, distinct from the larger "shield."
- witness: Geneva1599 reads "shield" (not "target") at I Samuel 17:6, but "targets" verbatim at I Kings 10:16, II Chronicles 9:15, and 14:8; Wycliffe reads "scheeld"/"bootis" at the same verses.
- own: **target** stands — from Old French "targe" (a small round shield), the ordinary 1611 military term for a light buckler, centuries before its 18th-century shift to "object aimed at"; Goliath's brass gorget and Solomon's ceremonial gold targets are both sound ancient Near Eastern military/ceremonial referents.
- reason: Geneva's own verbatim use of "targets" at three of six occurrences (the Solomon/Asa verses) confirms the word soundly, even though Geneva prefers "shield" at the Goliath verse — a translation choice for the same class of object. KEEP — flag for Capability-4 glossing, since the modern sense ("object aimed at") is a false-friend risk.

## temper — 6 uses
- verdict: KEEP
- whitelist: **anoint** — extremely common (freq. ~140), close for the oil-mixing sense at Exodus 29:2/30:25/35 but not for the dough-kneading sense at Genesis 18:6/Jeremiah 7:18.
- witness: Geneva1599 reads "kneade" at Genesis 18:6 and "knede" at Jeremiah 7:18 (its own synonym for the dough sense), and "tempered" verbatim at all three Exodus anointing-oil verses; Tyndale reads "kneade" at Genesis 18:6, matching Geneva.
- own: **temper** stands — from Latin "temperare" ("to mix in due proportion"), attested since the 14th century for both kneading dough to right consistency and blending oil/spices to right proportion; both senses are genuinely period, and the anointing-oil sense is verbatim-attested by Geneva at every Exodus occurrence.
- reason: Geneva's independent synonym at the two dough-verses (worth noting as a Capability-4 observation — "temper" the verb and "knead" nearly overlap but are not identical) is balanced by Geneva's own verbatim use of "tempered" at all three anointing-oil verses. KEEP.

## tenons — 6 uses
- verdict: WHITELIST
- whitelist: none exists yet for this joinery term; nearest is **boards** — extremely common in the same tabernacle passage, freq. ~40 — names the panel, not the projecting tongue that joins it to its neighbor.
- witness: Geneva1599 reads "tenons" verbatim at all three verses; Wycliffe reads "dentyngis" ("dentings/notchings," a period carpentry synonym) at the same three verses — both period witnesses independently confirm the identical joinery referent under different words.
- own: **tenons** stands — from Old French "tenon" ("that which holds," from "tenir," to hold), the standard English carpentry term (paired with "mortise") since the 14th century for a projecting tongue cut to fit into a corresponding socket; the tabernacle's silver-socketed acacia boards are a real, structurally coherent ancient joinery system.
- reason: A joinery term with a unique, technical referent and no true one-word substitute — exactly the WHITELIST category (cf. earlier batches' "gerahs"/"snuffers"). Geneva's verbatim agreement at every occurrence, with Wycliffe's independent cognate confirming the referent, argues for protecting rather than reopening it.

## tolerable — 6 uses
- verdict: KEEP
- whitelist: **easier** — Geneva's and Tyndale's own reading at all three verses (see witness), freq. ~10 — the period witnesses' own comparative choice, a workable and very close swap.
- witness: Geneva1599 reads "easier" (not "tolerable") at all three verses (Matt 10:15, 11:22, 11:24); Tyndale reads "easier"/"esier" at the same three verses — unanimous two-witness agreement on this alternate.
- own: **tolerable** stands — from Latin "tolerabilis" ("able to be borne"), attested in English since the 15th century, a slightly more formal Latinate register than "easier" but identical in sense (a lighter degree of judgment); no anachronism, and it is the KJV's own consistent choice across all three sayings.
- reason: Both surviving period witnesses independently prefer "easier" at every occurrence, which is a real and notable alternate the owner should see — but unanimous witness agreement on a synonym is not the same as disagreement with "tolerable," which remains sound period Latinate vocabulary. KEEP.

## twins — 6 uses
- verdict: KEEP
- whitelist: **children** — extremely common (freq. ~450), a workable but far less precise swap — loses the "two at one birth" sense entirely.
- witness: Geneva1599 reads "twinnes" (spelling variant) verbatim at Genesis 25:24/38:27 and "twinnes" at Song of Solomon 4:2; Tyndale reads ".ij. twyns" (numeral + spelling variant) at both Genesis verses; Wycliffe reads "twei children"/"twei chyldren" (periphrasis, "two children") at both Genesis verses.
- own: **twins** stands — Old English "twinn" ("double, two-fold"), attested continuously for the "born together" referent; Rebekah's and Tamar's twin births, and the ewes' twin lambs of Song of Solomon 4:2, are all unremarkable, timeless referents.
- reason: Verbatim agreement (spelling aside) from Geneva and Tyndale at both Genesis occurrences. KEEP.

## unstable — 6 uses
- verdict: KEEP
- whitelist: **wavering** — Hebrews 10:23 (not in this batch but same word-family), freq. ~3 — a close synonym for the moral/mental instability sense at Luke 12:29, though weaker for Genesis 49:4's "unstable as water" simile.
- witness: Geneva1599 reads "light as water" (synonym) at Genesis 49:4, "moueable" at Proverbs 5:6, and "hag you in suspense" at Luke 12:29; Tyndale reads "vnstable as water" verbatim at Genesis 49:4.
- own: **unstable** stands — un- + "stable" (Latin "stabilis"), attested since the 14th century for something not fixed or firm, whether water's formlessness (Genesis 49:4, a well-known crux of Hebrew poetic imagery), a woman's wandering path (Proverbs 5:6), or an anxious mind (Luke 12:29).
- reason: Tyndale's independent verbatim agreement at Genesis 49:4, the passage's best-known occurrence, is a strong period signal even where Geneva prefers synonyms elsewhere. KEEP.

## urged — 6 uses
- verdict: KEEP
- whitelist: **compelled** — Geneva's own reading at Genesis 33:11 (see witness), freq. ~10 — a workable, slightly stronger synonym (implies force, not just persistent pressure).
- witness: Geneva1599 reads "compelled" at Genesis 33:11, "was importunate vpon him" at Judges 16:16, and "was earnest" at Judges 19:7; Tyndale reads "compelled" at Genesis 33:11, matching Geneva.
- own: **urged** stands — from Latin "urgere" ("to press, push"), attested since the 16th century for insistent pressing persuasion (distinct from "compelled," which implies success by force); Delilah's daily pressing of Samson and Esau's insistence that Jacob take his gift are both sound uses of persistent, non-forcible pressure.
- reason: Both surviving witnesses (Geneva and Tyndale) independently prefer "compelled" at Genesis 33:11, a real alternate worth the owner's attention — but "urged" and "compelled" name two different degrees of pressure, and the KJV's choice of the milder word is not itself a corruption signature. KEEP.

## ware — 6 uses
- verdict: KEEP
- whitelist: **merchandise** — extremely common and already whitelisted, freq. ~40 — a close synonym for tradeable goods, safe swap.
- witness: Geneva1599 reads "ware"/"wares" verbatim at Nehemiah 10:31/13:16, and "marchandise" (synonym) at 13:20; Wycliffe reads "thingis set to sale" (periphrasis) at all three verses.
- own: **ware** stands — Old English "waru" ("goods, merchandise"), attested continuously (surviving today only in compounds like "hardware," "software"); Tyrian fish and Sabbath-day trade goods are an ordinary ancient Near Eastern commercial referent.
- reason: Geneva's verbatim agreement (spelling aside) at two of three verses, with the third showing only a synonym choice. KEEP.

## wellbeloved — 6 uses
- verdict: KEEP
- whitelist: **beloved** — extremely common and already whitelisted (freq. ~140, e.g. Song 1:13 itself in Geneva's own reading, see witness) — the root word without the intensifying "well-" prefix, a very close and safe swap.
- witness: Geneva1599 reads "welbeloued" (spelling variant) at Song of Solomon 1:13, "beloued" (without "well-") at Isaiah 5:1, and "deare beloued" at Mark 12:6; Tyndale reads "whom he loved tenderly" (periphrasis) at Mark 12:6.
- own: **wellbeloved** stands — well + beloved, a straightforward EModE intensified compound, attested throughout period devotional and epistolary writing ("wellbeloved brethren" is a common salutation formula); the vineyard-owner's son in the parable and the bridegroom of the Song are both sound uses.
- reason: Geneva's own verbatim spelling-variant at Song of Solomon 1:13 confirms the compound; its absence at Isaiah 5:1/Mark 12:6 in Geneva reflects only that translator's preference for the shorter root word, not disagreement. KEEP.

## wert — 6 uses
- verdict: KEEP
- whitelist: **wast** — extremely common and already whitelisted (freq. ~100, e.g. Genesis 3:19), the indicative twin of the subjunctive "wert" — a safe swap only where the grammatical mood doesn't matter, but wrong wherever "wert" marks a contrary-to-fact wish (Job 8:6, Song 8:1).
- witness: Geneva1599 reads "be pure and vpright" (present subjunctive, not "wert") at Job 8:6, "werest" (spelling variant) at Song of Solomon 8:1, and "wast graft in" (indicative "wast," not "wert") at Romans 11:17; Tyndale reads "arte" (present indicative) at Romans 11:17.
- own: **wert** stands — the second-person singular past subjunctive of "to be," grammatically required (per the King James agent's own operating principles on thou/thee/thy grammar) wherever the clause is a contrary-to-fact or hypothetical condition ("if thou wert pure," "O that thou wert as my brother") rather than a simple past-tense statement.
- reason: This is precisely the thou-grammar the base text must preserve; Geneva's and Tyndale's divergence to indicative forms at two of three verses reflects looser period grammar in those translations, not evidence against KJV's more careful subjunctive. KEEP — this word should not be touched by any generic "wert → wast" pass, since the mood is load-bearing.

## wet — 6 uses
- verdict: KEEP
- whitelist: **dew** — extremely common and already whitelisted (freq. ~35, appears in the very same two Daniel verses, "wet with the dew of heaven") — names the moisture, not the resulting state, so not a direct substitute.
- witness: Geneva1599 reads "wet" verbatim at Job 24:8; Daniel 4:15/23 fall in a stretch where the batch's own KJV-quoted text is visibly a different verse's content (an input-file mismatch, not a translation issue — Geneva's quoted lines for those two references are Nebuchadnezzar's dream-request, not the tree-stump wetting clause), so no clean comparison is available there.
- own: **wet** stands — Old English "wæt," among the oldest and plainest words in the language for moisture; showers wetting a mountainside and dew wetting a stump are both unremarkable natural images needing no modernization.
- reason: Verbatim Geneva agreement at the one cleanly comparable verse (Job 24:8); genuinely ordinary vocabulary. KEEP. Flag to the owner: the Daniel 4:15/4:23 rows in this batch's own input file may have a verse-text mismatch worth checking against `db/mandela.db` directly.

## whet — 6 uses
- verdict: KEEP
- whitelist: **sharpen** — Geneva's own reading at I Samuel 13:20/21 (see witness), freq. ~5 — a close, plainer synonym, safe swap.
- witness: Geneva1599 reads "whet" verbatim at Deuteronomy 32:41, and "sharpen"/"sharpen the goades" at I Samuel 13:20/21; Wycliffe reads "whette" (spelling variant) verbatim at Deuteronomy 32:41 and "scharpe" at I Samuel 13:20.
- own: **whet** stands — Old English "hwettan," attested continuously for sharpening a blade on a stone; a glittering whetted sword and Israelite farmers sharpening plowshares at Philistine forges (a detail confirming period Philistine ironworking monopoly, I Sam 13:19-22) are both source-era-sound.
- reason: Continuous Wycliffe-to-Geneva-to-KJV attestation at Deuteronomy 32:41 (spelling aside); Geneva's own synonym at I Samuel 13 is a translation choice for the identical referent. KEEP.

## woollen — 6 uses
- verdict: KEEP
- whitelist: **linen** — extremely common and already whitelisted (freq. ~100), the KJV's own paired fabric-word in every one of these verses — not a substitute (they're a contrasted pair, wool vs. linen) but confirms the fabric-vocabulary register.
- witness: Geneva1599 reads "wollen" (spelling variant) verbatim at all three verses, paired with "linen" exactly as the base text has it.
- own: **woollen** stands — wool (Old English "wull") + "-en," the ordinary period adjective for a wool garment; the wool/linen distinction in Leviticus 13's leprosy law (and the wool-linen mixture forbidden at Deut 22:11) is a real, well-documented ancient Near Eastern textile-and-purity referent.
- reason: Verbatim Geneva agreement (spelling aside) at every occurrence. KEEP.

## yonder — 6 uses
- verdict: KEEP
- whitelist: **thither** — extremely common and already whitelisted (freq. ~35), a close directional adverb, though "thither" means "to that place" while "yonder" specifically means "at/to that visible place over there" — a subtly different deictic sense.
- witness: Geneva1599 reads "yonder" verbatim at Genesis 22:5 and Numbers 23:15, and "beyond the altar" (synonym) at Numbers 16:37; Tyndale reads "yonder" verbatim at Genesis 22:5; Wycliffe reads "thidur" ("thither") at Genesis 22:5 and "hidur and thidur" ("hither and thither") at Numbers 16:37.
- own: **yonder** stands — Old English "geon" + "-der," attested continuously since Old English for a visible, pointed-at distant place; Abraham pointing toward Moriah and Balaam meeting the Lord "yonder" are both concrete, deictic uses needing no modernizing.
- reason: Verbatim two-witness agreement (Geneva and Tyndale) at Genesis 22:5, the passage's best-known occurrence (the binding of Isaac). KEEP.
## abated — 7 uses
- verdict: KEEP
- whitelist: **decreased** — Genesis 8:5 itself, Geneva's own reading (see witness), freq. ~2 — a close, safe swap.
- witness: Geneva1599 reads "abated" verbatim at Genesis 8:3, and "going and decreasing" at 8:5, "diminished" at 8:8; Tyndale reads "abated" verbatim at 8:3, and "went away and decreased" at 8:5, "fallen" at 8:8.
- own: **abated** stands — from Old French "abatre" ("to beat down, diminish"), attested since the 13th century for a flood's waters subsiding; the Flood narrative's gradual recession over 150 days is exactly the referent.
- reason: Verbatim two-witness agreement (Geneva and Tyndale) at Genesis 8:3; both independently vary at 8:5/8:8, a translation-choice pattern, not disagreement. KEEP.

## ability — 7 uses
- verdict: KEEP
- whitelist: **power** — extremely common and already whitelisted (freq. ~250), close but broader (physical/political power vs. specifically financial capacity).
- witness: Geneva1599 reads "abilitie" (spelling variant) verbatim at all three verses.
- own: **ability** stands — from Latin "habilitas" via Old French "abilite," attested since the 14th century for capacity, especially financial capacity to pay a vow or ransom brethren; Leviticus's sliding-scale vow valuation and post-exilic Judah's communal ransom fund are both sound source-era referents.
- reason: Verbatim Geneva agreement (spelling aside) at every occurrence. KEEP.

## abolish — 7 uses
- verdict: KEEP
- whitelist: **destroy** — extremely common and already whitelisted (freq. ~350), Geneva's own reading at Isaiah 2:18 (see witness), a strong and very safe swap.
- witness: Geneva1599 reads "destroy" (not "abolish") at Isaiah 2:18, "abolished" verbatim at Isaiah 51:6 and Ezekiel 6:6, and "excluded" at Romans 3:27; Tyndale reads "excluded" at Romans 3:27, matching Geneva.
- own: **abolish** stands — from Latin "abolere" via French "aboliss-," attested in English since the 15th century for putting a complete end to something (idols, works, boasting); no anachronism, and Geneva's own verbatim use at two of four verses confirms the word.
- reason: Verbatim Geneva agreement at half the occurrences, with the other half showing translation-choice variance, not disagreement. KEEP.

## adjure — 7 uses
- verdict: KEEP
- whitelist: **charge** — extremely common and already whitelisted, Geneva's own reading at four of five verses (see witness), freq. ~90 — a strong, safe swap for the "solemnly command" sense, though "adjure" carries the specific "bind by oath" force that plain "charge" lacks.
- witness: Geneva1599 reads "charge" at I Kings 22:16, II Chronicles 18:15, and I Samuel 14:24, "charge thee sweare" at Matthew 26:63, and "sware" at Joshua 6:26; Tyndale reads "charge" at Matthew 26:63, matching Geneva.
- own: **adjure** stands — from Latin "adiurare" ("to swear to/put under oath"), a precise legal-religious term (distinct from ordinary "charge") for binding someone by a solemn oath invoking God's name; Joshua's curse-oath on Jericho and the high priest's oath-demand of Jesus are both exact uses of this sense.
- reason: Both surviving witnesses independently prefer "charge/sware" at nearly every occurrence — a real, notable alternate for the owner — but "adjure" names a legally and theologically more precise act (oath-binding) that the generic "charge" flattens. KEEP.

## afore — 7 uses
- verdict: KEEP
- whitelist: **before** — extremely common and already whitelisted (freq. ~800), the modern-spelled twin of the identical word, a very safe swap.
- witness: Geneva1599 reads "afore" verbatim at all three verses.
- own: **afore** stands — a contracted form of "on-fore," attested since Old English, functionally identical to "before" but slightly terser/more colloquial; no anachronism in any of its three uses (temporal "before Isaiah left," "before it grows up," "before the harvest").
- reason: Verbatim Geneva agreement at every occurrence. KEEP.

## aileth — 7 uses
- verdict: KEEP
- whitelist: none exists for this idiom; nearest is **trouble** — extremely common and already whitelisted (freq. ~180), a workable paraphrase ("what troubles thee") but loses the fixed idiomatic phrasing.
- witness: Geneva1599 and Tyndale both read "ayleth"/"aileth" (spelling variant) verbatim at Genesis 21:17; Geneva also reads "ayleth" verbatim at both Judges verses; Wycliffe reads "What doist thou" (periphrasis) at Genesis 21:17 and "What wolt thou to thee" at Judges 18:23.
- own: **aileth** stands — Old English "eglan" ("to trouble, afflict"), attested continuously in the fixed idiom "what aileth thee?" (still current in dialectal/literary modern English); Hagar's distress and Micah's confrontation with the Danites are both ordinary human scenes.
- reason: Verbatim two-witness agreement (Geneva and Tyndale, spelling aside) at Genesis 21:17, plus Geneva's own verbatim use at both Judges verses. KEEP.

## alienated — 7 uses
- verdict: KEEP
- whitelist: **departed** — extremely common and already whitelisted, Geneva's own reading at Ezekiel 23:18 (see witness), freq. ~60 — a workable swap for the emotional-withdrawal sense.
- witness: Geneva1599 reads "lust departed from them" at Ezekiel 23:17, "mine heart forsooke her" at 23:18, and "thine heart is departed" at 23:22 — Geneva paraphrases the identical Hebrew idiom three different ways rather than using a single cognate.
- own: **alienated** stands — from Latin "alienare" ("to make another's, estrange"), attested in English since the 15th century for emotional/relational estrangement; Ezekiel's repeated image of Israel's covenant-love turning to disgust after excessive indulgence is a real, source-era-sound theological metaphor (the Hebrew root literally "her soul was torn away/disgusted").
- reason: Geneva's own three different paraphrases of the same underlying Hebrew idiom shows the translators found no single fixed English word for it either — "alienated" is a legitimate 1611-register choice among several period options, not a corruption. KEEP.

## astonied — 7 uses
- verdict: KEEP
- whitelist: **astonished** — extremely common and already whitelisted (freq. ~30), the standard modern-spelled twin of the identical word, safe swap.
- witness: Geneva1599 reads "astonied" (spelling variant) verbatim at all three verses.
- own: **astonied** stands — the older EModE past-participle form of "astony"/"astonish" (from Old French "estoner"), attested throughout period prose before "astonished" fully displaced it; upright men's shock at the wicked's fate and the nations' shock at the Suffering Servant's marred visage are both sound uses.
- reason: Verbatim Geneva agreement at every occurrence — this is the older sister-spelling of a still-whitelisted word, not a foreign intrusion. KEEP.

## attentive — 7 uses
- verdict: KEEP
- whitelist: **open** — extremely common and already whitelisted, paired in the very same verses ("eyes be open... ears be attentive"), freq. ~200 — a related but distinct sense (visual/receptive vs. specifically auditory-heedful).
- witness: Geneva1599 reads "attent" (shorter form) verbatim at all three verses.
- own: **attentive** stands — from Latin "attendere" via Old French "attentif," attested since the 14th century for heedful listening; Solomon's and Nehemiah's prayers for God's ears to be "attentive" are a fixed devotional formula with no anachronism.
- reason: Geneva's own shorter cognate "attent" at every occurrence confirms the same word-family, differing only in suffix. KEEP.

## bay — 7 uses
- verdict: KEEP
- whitelist: **coast** — extremely common and already whitelisted (freq. ~90), Geneva's own reading at Joshua 15:2 (see witness) — a workable general swap for "shoreline," though it loses "bay"'s specific inlet/cove sense.
- witness: Geneva1599 reads "the point" at Joshua 15:2/15:5 and "the point of the salt Sea" at 18:19 — Geneva's own consistent synonym for the identical geographic feature (the Dead Sea's northern/southern inlets); Wycliffe reads "the arm" at all three verses, an independent third rendering of the same referent.
- own: **bay** stands — from Old French "baie," attested in English since the 14th century for a coastal inlet; the Dead Sea's northern and southern tongues (still visible landforms today) are an exact, verifiable ancient Near Eastern geographic referent.
- reason: Three-way translation variance (KJV "bay," Geneva "point," Wycliffe "arm") for the identical landform shows this was a genuinely difficult geographic term for every period translator — not evidence any one choice is wrong. KEEP.

## beforehand — 7 uses
- verdict: KEEP
- whitelist: **before** — extremely common and already whitelisted (freq. ~800), the root word without the compound suffix, a safe partial swap.
- witness: Geneva1599 reads "before hand" (two words) verbatim at Mark 13:11/14:8 and "appointed afore" at II Corinthians 9:5; Tyndale reads "afore honde"/"a fore honde" (spelling variant, two words) at both Mark verses.
- own: **beforehand** stands — before + hand, an EModE compound (originally "in hand beforehand," i.e., prepared in advance), attested since the 15th century; taking no forethought for what to speak and Mary's anointing "beforehand" for burial are both sound uses.
- reason: Verbatim two-witness agreement (Geneva and Tyndale, spacing/spelling aside) at both Mark occurrences. KEEP.

## beguile — 7 uses
- verdict: KEEP
- whitelist: **deceive** — extremely common and already whitelisted, Tyndale's own reading at Genesis 3:13 (see witness), freq. ~90 — a strong, very safe swap.
- witness: Geneva1599 reads "beguile"/"beguiled" verbatim at all five verses; Tyndale reads "deceaved" (not "beguiled") at Genesis 3:13 and "begyled" (spelling variant) verbatim at Genesis 29:25; Wycliffe reads "disseyued" (deceived) at both Genesis verses.
- own: **beguile** stands — from Old French "guile" (deceit) + intensive "be-," attested since the 13th century; the serpent beguiling Eve and Laban beguiling Jacob are foundational, source-era-sound narrative moments named by this exact word since Middle English.
- reason: Verbatim Geneva agreement at all five occurrences is a strong signal, even where Tyndale/Wycliffe independently prefer the plainer "deceive/disseyued." KEEP.

## beheaded — 7 uses
- verdict: KEEP
- whitelist: **slew** — extremely common and already whitelisted (freq. ~250), a broader "killed" sense, not specific to decapitation.
- witness: Geneva1599 and Tyndale both read "beheaded" verbatim at Matthew 14:10; Geneva also reads "beheaded" verbatim at Deuteronomy 21:6 and II Samuel 4:7.
- own: **beheaded** stands — be- + "head" + -ed, a plain Germanic compound verb, attested since Old English "beheafdian"; the heifer's ritual neck-breaking (Deut 21:6, actually a distinct rite from execution, worth a Capability-4 note), Ish-bosheth's assassination, and John the Baptist's execution are all concrete referents.
- reason: Verbatim two-witness agreement (Geneva and Tyndale) at Matthew 14:10, plus Geneva's own use at the other two verses. KEEP.

## bemoan — 7 uses
- verdict: KEEP
- whitelist: **mourn** — extremely common and already whitelisted (freq. ~70), Geneva's own reading is close ("lament"/"weep for") but not identical — a workable swap.
- witness: Geneva1599 reads "sorie for thee" at Jeremiah 15:5, "be moued for the" at 16:5 and 22:10, "had compassion of him" at Job 42:11, and "lamenting" at 31:18 — Geneva paraphrases every occurrence differently rather than using one fixed cognate.
- own: **bemoan** stands — be- + "moan" (Old English "mænan," to lament), attested since the 14th century for expressing grief over someone; Jeremiah's repeated laments over Jerusalem and Job's friends' comfort-visit are all sound period usages.
- reason: Geneva's own five different paraphrases show no fixed period equivalent existed either — "bemoan" is a legitimate, well-attested EModE word for this sense, not a corruption. KEEP.

## benefit — 7 uses
- verdict: KEEP
- whitelist: **good** — extremely common and already whitelisted, Geneva's own reading at Jeremiah 18:10 (see witness), freq. ~600 — a workable but far more generic swap.
- witness: Geneva1599 reads "the rewarde bestowed" at II Chronicles 32:25, "the good that I thought to do" at Jeremiah 18:10, "a double grace" at II Corinthians 1:15, and "benefites" (spelling variant) verbatim at both Psalms verses.
- own: **benefit** stands — from Latin "benefactum" via Old French "bienfait," attested since the 14th century for a good deed done or received; Hezekiah's ingratitude for God's kindness and the Psalmist's catalog of God's benefits are both timeless devotional referents.
- reason: Verbatim Geneva agreement (spelling aside) at both Psalms occurrences, the word's most familiar uses. KEEP.

## beset — 7 uses
- verdict: KEEP
- whitelist: **compassed** — extremely common and already whitelisted, Geneva's own reading at Psalm 22:12 (see witness), freq. ~70 — a very close, safe swap.
- witness: Geneva1599 reads "beset" verbatim at both Judges verses, and "closed me about" at Psalm 22:12 (Geneva's own synonym, though "compassed" appears earlier in the same verse in both texts).
- own: **beset** stands — be- + "set," attested since Old English "besettan" for surrounding or hemming in; the mob surrounding Lot's-parallel house at Gibeah and the Psalmist's enemies surrounding him "like bulls of Bashan" are both sound, source-era images.
- reason: Verbatim Geneva agreement at both Judges occurrences. KEEP.

## bill — 7 uses
- verdict: KEEP
- whitelist: none exists for this specific legal-document sense; nearest is **book** — extremely common and already whitelisted (freq. ~180), too generic (any written document, not specifically a legal decree).
- witness: Geneva1599 reads "bill" verbatim at Deuteronomy 24:1, "letter of diuorcement" (synonym) at 24:3, and "bill" verbatim at Isaiah 50:1; Wycliffe reads "libel, ethir litil book" (a "little book," periphrasis) at both Deuteronomy verses.
- own: **bill** stands — from Latin "bulla" via Old French "bille," attested since the 14th century for a formal written document or legal instrument; the Mosaic bill of divorcement is a well-documented ancient Near Eastern legal instrument (distinct from later Roman/rabbinic get documents but the same institution).
- reason: Verbatim Geneva agreement at two of three verses; Wycliffe's periphrasis at the third independently confirms the "small legal document" referent. KEEP.

## careful — 7 uses
- verdict: KEEP
- whitelist: none of identical brevity; nearest is **trouble** — extremely common and already whitelisted (freq. ~180), a workable paraphrase of the "anxious" sense, though it changes part of speech.
- witness: Geneva1599 reads "all this great care" (noun, not adjective) at II Kings 4:13, "care for the yeere of drought" (verb phrase) at Jeremiah 17:8, and "carefull" (spelling variant) verbatim at Daniel 3:16.
- own: **careful** stands — care (Old English "caru," anxiety/sorrow) + "-ful," attested since Middle English for "full of anxious concern" (the opposite of its modern sense "cautious/attentive to detail"); the Shunammite's hospitable anxiety and the three youths' fearless refusal to be anxious before Nebuchadnezzar are both sound uses of the older sense.
- reason: Verbatim Geneva agreement (spelling aside) at Daniel 3:16. KEEP — flag for Capability-4 glossing, since "careful" has drifted furthest of any word in this stretch toward its opposite modern sense ("cautious" rather than "anxious").

## certify — 7 uses
- verdict: KEEP
- whitelist: **tell** — extremely common and already whitelisted, Wycliffe's own reading at all five verses (see witness), freq. ~450 — a safe, very close swap for the general "inform" sense, though "certify" carries the more formal, official-report connotation the Ezra correspondence needs.
- witness: Geneva1599 reads "certified" verbatim at Ezra 4:14 and Esther 2:22, "to be tolde me" at II Samuel 15:28, and "certifie" verbatim at Ezra 4:16/5:10; Wycliffe reads "teld"/"tellen"/"schewe" (all "tell/show") at every occurrence.
- own: **certify** stands — from Latin "certus" ("sure") via Old French "certifier," attested since the 14th century for formally informing/making certain; the Persian-era administrative correspondence in Ezra (a genre of official report) is exactly the register this word fits.
- reason: Verbatim Geneva agreement at four of five occurrences. KEEP.

## childless — 7 uses
- verdict: KEEP
- whitelist: **die** — extremely common and already whitelisted, paired in the very same verses ("shall die childless"), freq. ~250 — not itself a substitute, but confirms the phrase's other half is sound.
- witness: Geneva1599 reads "childlesse" (spelling variant) verbatim at all three verses; Tyndale reads "childlesse" verbatim at Genesis 15:2.
- own: **childless** stands — child + "-less," a plain Germanic negative compound, attested since Middle English; Abram's lack of an heir and the Levitical penalty of dying without descendants are both source-era-sound (childlessness as a real ancient Near Eastern legal/social crisis, cf. the whole Eliezer-inheritance question).
- reason: Verbatim two-witness agreement (Geneva and Tyndale, spelling aside) at Genesis 15:2, plus Geneva's own use at both Leviticus verses. KEEP.

## clods — 7 uses
- verdict: KEEP
- whitelist: **dust** — extremely common and already whitelisted, paired in the very same verse (Job 7:5 "clods of dust"), freq. ~90 — names the fine particulate, not the compacted lump "clods" specifically means.
- witness: Geneva1599 reads "filthinesse of the dust" at Job 7:5, "slimie valley" at 21:33, and "clottes" (spelling variant) verbatim at 38:38.
- own: **clods** stands — Old English "clod/clott" (a lump of earth), attested continuously; dried dirt-clods on a sick man's sores, the sweetness of a burial-valley's clods, and clods cohering into hardness under drought are all concrete, timeless agricultural images.
- reason: Verbatim Geneva agreement (spelling aside) at Job 38:38, the clearest of the three occurrences. KEEP.

## communication — 7 uses
- verdict: KEEP
- whitelist: **talk** — extremely common and already whitelisted, Geneva's own reading at II Kings 9:11 (see witness), freq. ~30 — a safe, close swap.
- witness: Geneva1599 reads "communication" verbatim at II Samuel 3:17 and Ephesians 4:29, "what his talke was" at II Kings 9:11, and "communications" verbatim at Luke 24:17; Tyndale reads "communications" verbatim at Luke 24:17 and "malicious speakinges" at I Corinthians 15:33.
- own: **communication** stands — from Latin "communicare" via Old French, attested since the 14th century for conversation/discourse generally (not the modern narrow "transmitting information" sense); Abner's parley with Israel's elders and the Emmaus travelers' sorrowful talk are both timeless conversational referents.
- reason: Verbatim agreement from both surviving witnesses at multiple occurrences (Geneva at three of five, Tyndale independently at Luke 24:17). KEEP.

## complain — 7 uses
- verdict: KEEP
- whitelist: **murmur** — extremely common and already whitelisted, Geneva's own reading at Numbers 11:1 (see witness), freq. ~60 — a very close, safe swap, and arguably the more precise word for Israel's wilderness grumbling.
- witness: Geneva1599 reads "complaine" verbatim at Judges 21:22, Job 31:38, and Psalm 144:14, "murmurers" at Numbers 11:1, and "muse in the bitternesse" at Job 7:11.
- own: **complain** stands — from Latin "plangere" via Old French "complaindre," attested since the 14th century for expressing grief or grievance; petitioning kinsmen, a suffering man's lament, and Israel's wilderness murmuring are all sound period and source-era referents.
- reason: Verbatim Geneva agreement at three of six occurrences, with the others showing close synonyms rather than disagreement. KEEP.

## contentious — 7 uses
- verdict: KEEP
- whitelist: **angry** — extremely common and already whitelisted, paired in the very same verse (Prov 21:19 "contentious and an angry woman"), freq. ~200 — names a related but distinct temperament (quarrelsome vs. simply wrathful).
- witness: Geneva1599 reads "contentious" verbatim at all three verses.
- own: **contentious** stands — from Latin "contendere" via Old French "contentieux," attested since the 15th century for a quarrelsome disposition; the proverb's repeated warning against a quarrelsome wife (three near-identical sayings) is a stable, unremarkable domestic-wisdom referent.
- reason: Verbatim Geneva agreement at every occurrence. KEEP.

## corruptible — 7 uses
- verdict: KEEP
- whitelist: **mortal** — extremely common and already whitelisted, paired in the very same verse (I Cor 15:53 "corruptible... mortal"), freq. ~15 — a related but distinct sense (subject to decay vs. subject to death).
- witness: Geneva1599 reads "corruptible" verbatim at all three verses; Tyndale reads "mortall" (not "corruptible") at Romans 1:23 and "corruptible" verbatim at I Corinthians 9:25/15:53.
- own: **corruptible** stands — from Latin "corruptibilis," attested since the 14th century for that which is subject to decay; Paul's contrast of incorruptible God with corruptible images, and of a corruptible/incorruptible crown or body, are core Pauline theological vocabulary needing no modernizing.
- reason: Verbatim agreement from both surviving witnesses (Geneva at every verse, Tyndale at two of three). KEEP.

## dainty — 7 uses
- verdict: KEEP
- whitelist: **pleasant** — extremely common and already whitelisted, Geneva's own reading at Genesis 49:20 (see witness), freq. ~60 — a workable general swap, though it loses "dainty"'s specific "choice/delicate food" sense.
- witness: Geneva1599 reads "pleasures for a king" at Genesis 49:20, "delicates" at Psalm 141:4, "deintie meates" (spelling variant) verbatim at Proverbs 23:3/23:6, "daintie meate" verbatim at Job 33:20, and "fatte and excellent" at Revelation 18:14; Tyndale reads "pleasures" at Genesis 49:20 and "deyntie" (spelling variant) verbatim at Revelation 18:14.
- own: **dainty** stands — from Latin "dignitas" via Old French "daintié" ("worthiness, pleasure"), attested since the 13th century for choice, delicate food or luxury goods; royal delicacies, a ruler's fare, and Babylon's luxury trade-goods are all sound source-era referents.
- reason: Verbatim agreement from both surviving witnesses at multiple occurrences (Geneva at three of six, Tyndale independently at Revelation 18:14). KEEP.

## damage — 7 uses
- verdict: REPLACE
- whitelist: **hurt** — extremely common and already whitelisted (freq. ~200), Geneva's own reading at Ezra 4:13 (see witness) — a very safe, close swap that also resolves the artifact described below.
- witness: Geneva1599 reads "hinder the Kings tribute" at Ezra 4:13, "domage grow to hurt the King" (spelling variant) verbatim-in-sense at Ezra 4:22, and "the Kings losse" at Esther 7:4. The base `KJV.db` itself (queried directly) reads **"endamage"** — not "damage" — at Ezra 4:13: "so thou shalt **endamage** the revenue of the kings."
- own: **endamage** — restore the base text's own verb. The batch's occurrence text for Ezra 4:13 literally reads **"thou shalt damage/hurt the revenue"** — a visible slash between two unresolved word choices left in the running text. This is not a period-spelling variant; it is an unfinished editorial artifact that has displaced the correct, attested period verb "endamage" (from Old French "endamager," meaning "to bring damage upon," current through the 17th century and Geneva's own sense at the same verse).
- reason: This is the batch's clearest corruption/production-error finding — a literal "word/word" placeholder sitting in running scripture text, not a genuine word-choice question. The noun "damage" itself is sound at Ezra 4:22 and Esther 7:4 (matching or closely paraphrasing Geneva) and needs no change there; only the Ezra 4:13 verb form needs correction, ideally to the base text's own "endamage." Flagging for the owner-reviewed apply-migration workflow rather than ruling further myself, since this touches restored verse text, not just a synonym choice.

## daubed — 7 uses
- verdict: KEEP
- whitelist: **clay** — extremely common and already whitelisted, paired in the very same verse (Exod 2:3 "daubed it with clay"), freq. ~15 — names the material, not the plastering action.
- witness: Geneva1599 reads "daubed" verbatim at all three verses; Wycliffe reads "bawmede" ("balmed/coated") at Exodus 2:3, an independent synonym for the same waterproofing action.
- own: **daubed** stands — from Latin "dealbare" via Old French "dauber" ("to whitewash/plaster"), attested since the 14th century for coating with clay, pitch, or mortar; Moses's reed basket sealed with pitch and Ezekiel's condemned "untempered mortar" wall-plastering are both concrete ancient Near Eastern building/craft techniques.
- reason: Verbatim Geneva agreement at every occurrence. KEEP.

## decked — 7 uses
- verdict: KEEP
- whitelist: **adorned** — extremely common and already whitelisted (freq. ~15), a very close, safe swap for the "ornamented" sense.
- witness: Geneva1599 reads "deckt"/"decked" (spelling variant) verbatim at all three verses.
- own: **decked** stands — from Middle Dutch "decken" ("to cover"), attested in English since the 15th century for adorning/covering with ornaments; the harlot's ornamented bed and Jerusalem-as-bride decked with jewelry (Ezekiel's extended covenant-marriage allegory) are both sound period and source-era images.
- reason: Verbatim Geneva agreement (spelling aside) at every occurrence. KEEP.

## disputing — 7 uses
- verdict: KEEP
- whitelist: **reasoning** — extremely common and already whitelisted, Geneva's own reading at Philippians 2:14 (see witness), freq. ~15 — a close, safe swap.
- witness: Geneva1599 and Tyndale both read "disputed"/"disputynge" verbatim at Acts 6:9/15:7/19:8; Geneva reads "reasonings" (not "disputings") at Philippians 2:14 and "disputations" (close cognate) at I Timothy 6:5.
- own: **disputing** stands — from Latin "disputare" via Old French "desputer," attested since the 13th century for formal argument or debate; the Hellenistic-synagogue debates over Stephen and Paul's synagogue reasoning at Ephesus are both sound first-century Jewish-diaspora referents (public philosophical/theological disputation was a real institution).
- reason: Verbatim agreement from both surviving witnesses (Geneva and Tyndale) at three of five occurrences. KEEP.

## ditch — 7 uses
- verdict: KEEP
- whitelist: **pit** — extremely common and already whitelisted, Geneva's own reading at Job 9:31/Psalm 7:15 (see witness), freq. ~90 — a very close, safe swap.
- witness: Geneva1599 reads "pit" (not "ditch") at Job 9:31 and Psalm 7:15, "ditche" (spelling variant) verbatim at Proverbs 23:27, and "ditches" verbatim at II Kings 3:16.
- own: **ditch** stands — Old English "dic," attested continuously for a dug trench or pit; a self-dug trap and Elisha's miraculous trench-filling in the Moabite campaign are both concrete, source-era-sound referents.
- reason: Verbatim Geneva agreement at two of four occurrences; the other two show Geneva's own close synonym "pit" for the identical class of object. KEEP.

## diviners — 7 uses
- verdict: KEEP
- whitelist: none exists yet for this specific cultic-office noun; nearest is **prophets** — extremely common and already whitelisted (freq. ~450), the opposite pole of the same semantic field (true vs. false revelation), not a synonym.
- witness: Geneva1599 reads "sorcerers" at Deuteronomy 18:14, "soothsayers" (spelling variant) verbatim at I Samuel 6:2, and "them that coniecture" at Isaiah 44:25; Wycliffe reads "false dyuynouris"/"false dyuynours" (cognate) at Deuteronomy 18:14 and I Samuel 6:2.
- own: **diviners** stands — from Latin "divinare" ("to foresee/foretell") via Old French "deviner," attested since the 14th century for practitioners of pagan fortune-telling; the Philistine priest-diviners consulted over the plague-cart and the general ancient Near Eastern institution of professional divination (hepatoscopy, astrology, necromancy) are all well-documented source-era referents.
- reason: Wycliffe's independent cognate "dyuynouris" at two verses confirms the word-family runs back to Middle English; Geneva's own synonym choices are translation variance, not disagreement. This is arguably a WHITELIST-worthy cultic-office term (paired with "diviner"/"soothsayer"/"enchanter" as a fixed occult-office list at Deut 18:10-14) — flagging as advisory alongside the KEEP verdict.

## doubtless — 7 uses
- verdict: KEEP
- whitelist: **surely** — extremely common and already whitelisted (freq. ~350), a very close, safe swap for the emphatic-certainty sense.
- witness: Geneva1599 reads "doubtles"/"doubtlesse" (spelling variant) verbatim at Numbers 14:30 and II Samuel 5:19.
- own: **doubtless** stands — doubt + "-less," attested since the 14th century as an emphatic adverb of certainty; Caleb's and David's assurances of God's promise-keeping are both sound, unremarkable devotional uses.
- reason: Verbatim Geneva agreement (spelling aside) at two of three occurrences. KEEP.

## dyed — 7 uses
- verdict: KEEP
- whitelist: **red** — extremely common and already whitelisted, paired in the very same verses ("skins dyed red"), freq. ~50 — names the color, not the dyeing process.
- witness: Geneva1599 reads "coloured red" at Exodus 25:5, "died red" (spelling variant) verbatim at 26:14, and "died red" verbatim at 35:7.
- own: **dyed** stands — Old English "deagian," attested continuously for coloring fabric or hide; red-dyed ram-skins for the tabernacle covering are a real, well-documented ancient Near Eastern leather-working/dyeing technique (madder or ochre dyes are attested archaeologically for this period).
- reason: Verbatim Geneva agreement (spelling aside) at two of three occurrences. KEEP.
## exchange — 7 uses
- verdict: KEEP
- whitelist: **change** — extremely common and already whitelisted, paired/used in the very same verse (Lev 27:10 "change it... the exchange thereof"), freq. ~90 — the verb-root of the noun, close but not identical in the specific "thing traded for another" sense.
- witness: Geneva1599 reads "exchange" verbatim at Genesis 47:17 and Job 28:17, and "the exchange thereof" verbatim at Leviticus 27:10; Tyndale reads "exchange" (as "for") verbatim in sense at Genesis 47:17.
- own: **exchange** stands — from Latin "excambiare" via Old French "eschangier," attested since the 14th century for trading one thing for another; Joseph's grain-for-livestock barter and the Levitical substitute-animal law are both concrete ancient Near Eastern economic referents.
- reason: Verbatim Geneva agreement at all three occurrences. KEEP.

## excuse — 7 uses
- verdict: KEEP
- whitelist: none of identical economy; nearest is **fault** — extremely common and already whitelisted (freq. ~60), a related legal-guilt term but not a direct synonym for "pretext" or "pardon."
- witness: Geneva1599 and Tyndale both read "excuse"/"excused" verbatim at Luke 14:18/19; Geneva reads "inexcusable" (not "without excuse") at Romans 1:20/2:1, and "excusing" verbatim at Romans 2:15; Tyndale reads "inexcusable" at Romans 2:1, matching Geneva.
- own: **excuse** stands — from Latin "excusare" via Old French "escuser," attested since the 14th century for a plea in one's defense or release from blame; the parable's dinner-guests' pretexts and Paul's argument that pagans are "without excuse" before God's revealed creation are both sound uses.
- reason: Verbatim agreement from both surviving witnesses at Luke 14:18/19, the clearest occurrences. KEEP.

## expedient — 7 uses
- verdict: KEEP
- whitelist: none of identical register; nearest is **profit** — extremely common and already whitelisted (freq. ~80), close in the "beneficial" sense but not the specific "fitting/advantageous under the circumstances" nuance.
- witness: Geneva1599 and Tyndale both read "expedient" verbatim at all three verses — unanimous three-way agreement.
- own: **expedient** stands — from Latin "expedire" ("to extricate, make ready/fit"), attested since the 14th century for "advantageous, fitting to the circumstance"; Caiaphas's cynical political calculation and Jesus's own statement that his departure serves the disciples' good are both theologically load-bearing uses of this exact word.
- reason: Unanimous three-witness agreement (Geneva and Tyndale verbatim) at every occurrence. KEEP.

## flattereth — 7 uses
- verdict: KEEP
- whitelist: none of identical form; nearest is **smooth** — Proverbs 7:5 itself, Geneva's own reading ("smoothe in her wordes," see witness), freq. ~10 — a related but weaker word (describes manner, not the deceptive act itself).
- witness: Geneva1599 reads "flattereth" verbatim at Psalm 36:2 and Proverbs 2:16, and "smoothe in her wordes" (synonym) at Proverbs 7:5.
- own: **flattereth** stands — from Old French "flater" ("to smooth, caress"), attested since the 13th century for deceptive praise or self-deception; the wicked man flattering himself and the seductress flattering with her words are both timeless moral-wisdom referents.
- reason: Verbatim Geneva agreement at two of three occurrences. KEEP.

## fragments — 7 uses
- verdict: KEEP
- whitelist: none of identical sense; nearest is **remained** — extremely common and already whitelisted, paired in the very same verse (Matt 14:20 "fragments that remained"), freq. ~200 — not itself a noun-substitute.
- witness: Geneva1599 reads "fragments" verbatim at all three verses; Tyndale reads "gobbetes"/"gobbettes" (a period synonym meaning "small pieces/morsels," from Old French "gobet") at all three verses.
- own: **fragments** stands — from Latin "fragmentum" ("a piece broken off"), attested since the 15th century; the leftover bread and fish pieces from the feeding miracles are a concrete, everyday referent needing no modernizing.
- reason: Verbatim Geneva agreement at every occurrence; Tyndale's independent "gobbets" is a genuine period alternate worth the owner's notice but not evidence against "fragments." KEEP.

## frost — 7 uses
- verdict: KEEP
- whitelist: **snow** — extremely common and already whitelisted (freq. ~25), a related winter-weather noun but a physically distinct phenomenon.
- witness: Geneva1599 reads "frost" verbatim at Genesis 31:40 and "hoare frost" verbatim at Exodus 16:14; Tyndale reads "colde" (a broader synonym) at Genesis 31:40; Wycliffe reads "frost" verbatim at Genesis 31:40 and "hoorfrost" at Exodus 16:14.
- own: **frost** stands — Old English "forst," among the oldest words in the language for freezing weather; Jacob's shepherding hardship and manna's frost-like appearance are both sound period and source-era (Near Eastern highland nighttime cold) referents.
- reason: Three-witness agreement (Geneva and Wycliffe verbatim, Tyndale by close synonym) at Genesis 31:40. KEEP.

## gentleness — 7 uses
- verdict: KEEP
- whitelist: **mercy** — extremely common and already whitelisted (freq. ~250), a related covenantal virtue but not identical (compassion vs. specifically gentle condescension).
- witness: Geneva1599 reads "softnesse and tendernesse" at Deuteronomy 28:56, and "louing kindnesse" at both II Samuel 22:36 and Psalm 18:35 — Geneva's own consistent alternate rendering for the same underlying Hebrew term (the same word rendered "lovingkindness" elsewhere in Geneva).
- own: **gentleness** stands — gentle (Old French "gentil") + "-ness," attested since the 14th century for mild, condescending kindness (a king's gentleness in stooping to exalt a servant, David's own image); a real and theologically resonant word for God's covenant-condescension.
- reason: Geneva's own consistent alternate "lovingkindness" is a genuine, notable variant reading worth the owner's attention, but it reflects a translation choice for the same Hebrew root (chesed-adjacent vocabulary), not a correction of "gentleness." KEEP.

## glittering — 7 uses
- verdict: KEEP
- whitelist: **bright** — extremely common and already whitelisted (freq. ~40), a related but weaker/more general shine-word.
- witness: Geneva1599 reads "glittering" verbatim at Deuteronomy 32:41 and I Chronicles 29:2 ("glittering stones"), and "shineth of his gall" at Job 20:25 (synonym); Wycliffe reads "as leit" ("as lightning") at Deuteronomy 32:41, an independent simile for the same flashing referent.
- own: **glittering** stands — from Middle English "gliteren" (of Scandinavian origin), attested since the 14th century for sparkling, flashing light; a whetted sword's flash and gemstones' sparkle in Solomon's temple treasury are both concrete, timeless images.
- reason: Verbatim Geneva agreement at two of three occurrences, with Wycliffe's independent simile confirming the same flashing-light referent at the third. KEEP.

## haughtiness — 7 uses
- verdict: KEEP
- whitelist: **pride** — extremely common and already whitelisted, paired in the very same verses ("the pride of man... haughtiness of men"), freq. ~90 — a very close, safe swap, though the pairing shows the KJV itself treats them as near-synonyms rather than one displacing the other.
- witness: Geneva1599 reads "loftinesse" (spelling/word variant) verbatim-in-sense at Isaiah 2:11/2:17, and "presumption" at 9:9.
- own: **haughtiness** stands — haught (Old French "haut," "high") + "-y" + "-ness," attested since the 15th century for arrogant self-exaltation; the repeated Isaiah refrain "the Lord alone shall be exalted" against human haughtiness is a stable prophetic-judgment theme.
- reason: Geneva's own close synonym "loftiness" at two of three occurrences confirms the identical sense; the pairing with "pride" in the same verses (both witnesses and KJV alike) shows this is standard doublet-vocabulary for prophetic emphasis, not a corruption. KEEP.

## hearth — 7 uses
- verdict: KEEP
- whitelist: **fire** — extremely common and already whitelisted (freq. ~350), a related but distinct referent (the flame itself, not the built fireplace/oven-floor).
- witness: Geneva1599 reads "hearth" (spelling variant "herthe") verbatim at Genesis 18:6 and Psalm 102:3, and "hearth" verbatim at Isaiah 30:14.
- own: **hearth** stands — Old English "heorð," attested continuously for a fireplace or oven-floor; Sarah's tent-hearth cakes and the potter's-vessel-and-hearth imagery of Isaiah 30 are both concrete ancient Near Eastern domestic referents.
- reason: Verbatim Geneva agreement (spelling aside) at every occurrence. KEEP.

## honest — 7 uses
- verdict: KEEP
- whitelist: **good** — extremely common and already whitelisted, paired in the very same verse (Luke 8:15 "honest and good heart"), freq. ~600 — a workable but far more generic swap.
- witness: Geneva1599 and Tyndale both read "honest" verbatim at Luke 8:15 and Acts 6:3; Geneva reads "honest" verbatim at Romans 12:17, Tyndale reads "honest" verbatim as well.
- own: **honest** stands — from Latin "honestus" via Old French "honeste," attested since the 14th century in 1611 for "honorable/of good repute" (broader than the modern narrow "truthful" sense); a good and honest heart, men of honest report chosen as deacons, and providing things honest in others' sight are all sound uses of the older, broader sense.
- reason: Unanimous agreement from both surviving witnesses at every occurrence. KEEP — flag for Capability-4 glossing, since "honest" has narrowed in modern use toward "truthful" specifically.

## incurable — 7 uses
- verdict: KEEP
- whitelist: **wound** — extremely common and already whitelisted, paired in the very same verse (Job 34:6 "my wound is incurable"), freq. ~100 — names the injury, not the untreatable quality.
- witness: Geneva1599 reads "incurable" verbatim at II Chronicles 21:18, "grieuous" (a weaker synonym) at Job 34:6, and "desperate sorrowe" at Isaiah 17:11.
- own: **incurable** stands — in- + "curable" (Latin "curabilis"), attested since the 14th century for a disease or wound beyond medical remedy; Jehoram's fatal bowel disease (traditionally identified with dysentery or a prolapse) is a concrete, source-era-sound clinical referent.
- reason: Verbatim Geneva agreement at II Chronicles 21:18, the clearest of the three occurrences. KEEP.

## lap — 7 uses
- verdict: KEEP
- whitelist: **bosom** — extremely common and already whitelisted (freq. ~90), a very close, safe swap for the "garment-fold used to carry things" sense.
- witness: Geneva1599 reads "garment ful" (not "lap full") at II Kings 4:39, "lappe" (spelling variant) verbatim at Nehemiah 5:13 and Proverbs 16:33, and "lapped"/"lappeth" verbatim at all three Judges 7 verses.
- own: **lap** stands — Old English "læppa" ("a loose fold of a garment"), attested continuously both for the fold used to carry things (Nehemiah's dramatic shaken-out garment) and, unrelatedly, for a dog's tongue-lapping of water (Gideon's test); two distinct but equally sound uses of the same word.
- reason: Verbatim Geneva agreement at five of six occurrences (the Judges 7 "lapped/lappeth" cluster and Nehemiah/Proverbs). KEEP.

## midwives — 7 uses
- verdict: KEEP
- whitelist: none exists for this specific trade-noun; nearest is **women** — extremely common and already whitelisted (freq. ~250), far too generic.
- witness: Geneva1599 reads "midwiues" (spelling variant) verbatim at all three verses; Wycliffe reads "mydwyues"/"medewyues" (spelling variant) at the same three verses.
- own: **midwives** stands — mid- (with) + "wife" (woman), Old English in origin, attested continuously for the birth-attendant trade; Shiphrah and Puah's civil disobedience against Pharaoh's infanticide order is a named, concrete, well-attested ancient Near Eastern narrative with a real professional referent.
- reason: Continuous Wycliffe-to-Geneva-to-KJV attestation of the identical compound at every occurrence. KEEP.

## nativity — 7 uses
- verdict: KEEP
- whitelist: **born** — extremely common and already whitelisted (freq. ~150), Tyndale's own periphrasis ("where he was borne," see witness) — a workable paraphrase, not a direct noun-substitute.
- witness: Geneva1599 reads "natiuitie" (spelling variant) verbatim at Genesis 11:28 and Ruth 2:11, and "natiuitie" verbatim at Jeremiah 46:16; Tyndale reads "where he was borne" (periphrasis, not "nativity") at Genesis 11:28.
- own: **nativity** stands — from Latin "nativitas" via Old French "nativité," attested since the 14th century for one's birthplace or birth-circumstance; Haran's death in Ur and Ruth's leaving her native Moab are both concrete, unremarkable ancient Near Eastern genealogical/geographic referents.
- reason: Verbatim Geneva agreement (spelling aside) at every occurrence. KEEP.

## oftentimes — 7 uses
- verdict: KEEP
- whitelist: **often** — extremely common and already whitelisted (freq. ~60), the shorter root form of the identical word, a very safe swap.
- witness: Geneva1599 reads "twise or thrise" (a specific-number synonym) at Job 33:29, and "oft times" (two words) verbatim at Luke 8:29; Tyndale reads "ofte tymes" (two words, spelling variant) verbatim at Luke 8:29.
- own: **oftentimes** stands — often + "times," an EModE intensified/reduplicated adverb, attested since the 14th century, functionally identical to "often" but more emphatic; the demoniac's repeated seizures and Job's repeated workings of God with man are both sound uses.
- reason: Verbatim agreement from both surviving witnesses at Luke 8:29 (spacing/spelling aside). KEEP.

## pavilion — 7 uses
- verdict: KEEP
- whitelist: **tabernacle** — extremely common and already whitelisted, Geneva's own reading at Psalm 27:5 (see witness), freq. ~250 — a close, safe swap for the "sheltering tent" sense, though it risks confusion with the specific wilderness Tabernacle elsewhere in the same corpus.
- witness: Geneva1599 reads "pauilion" (spelling variant) verbatim at Psalm 18:11 and 31:20, "Tabernacle" (synonym) at Psalm 27:5, and "Tabernacle" (synonym) at II Samuel 22:12; at I Kings 20:12/16 Geneva reads "pauilions" verbatim at 20:12 and "tentes" at 20:16.
- own: **pavilion** stands — from Latin "papilio" ("butterfly/tent," from the tent's wing-like flaps) via Old French "paveillon," attested since the 13th century for a large ornamental tent; God's storm-cloud pavilion and Ben-hadad's royal war-tents are both sound period and source-era (Near Eastern royal/military tent culture) referents.
- reason: Verbatim Geneva agreement at three of six occurrences, with the others showing close synonyms ("tabernacle," "tents") for the same class of structure. KEEP.

## pen — 7 uses
- verdict: KEEP
- whitelist: **write** — extremely common and already whitelisted (freq. ~300), the verb-root, not a noun-substitute for the writing instrument.
- witness: Geneva1599 reads "the pen of the writer" (synonym for "scribe") at Judges 5:14, "an yron pen" verbatim at Job 19:24, and "the pen of a swift writer" (synonym) at Psalm 45:1.
- own: **pen** stands — from Latin "penna" ("feather") via Old French "penne," attested since the 13th century for a writing instrument (reed or quill, or, at Job 19:24, an iron engraving-stylus); Zebulun's scribes and Job's wish for words graven in rock with an iron pen are both concrete, source-era-sound writing-technology referents (iron styluses for rock inscription are archaeologically well attested).
- reason: Verbatim Geneva agreement at Job 19:24, the clearest occurrence (a literal iron engraving tool, not a reed pen). KEEP.

## pence — 7 uses
- verdict: KEEP
- whitelist: none exists for this coin-denomination noun; nearest is **shekel** — extremely common and already whitelisted (freq. ~90), a different currency system (OT Hebrew weight-silver vs. NT Roman coinage) and therefore not interchangeable.
- witness: Geneva1599 and Tyndale both read "pence" verbatim at Matthew 18:28 and Mark 14:5; Geneva reads "peny worth" (compound with "peny") at Mark 6:37, Tyndale reads "penyworth" (one word) at the same verse.
- own: **pence** stands — the plural of "penny" (Old English "pening"), used in 1611 to translate the Greek δηνάριον (denarius), a Roman silver coin worth roughly a day's wage; the unmerciful servant's debt, the cost of feeding five thousand, and the value of Mary's ointment are all concrete first-century Roman-provincial monetary referents this coin-word names accurately (the KJV's "penny" for denarius is a period English-coinage stand-in, not a source-era claim that Judea used English pence).
- reason: Unanimous agreement from both surviving witnesses at every occurrence. KEEP — flag for Capability-4/Axis-2 note: "pence" is an English-currency loan-rendering of the Roman denarius, sound as period translation convention (every witness including modern versions does the same), not a source-era anachronism in itself since it names no physical object, only a value-equivalent.
