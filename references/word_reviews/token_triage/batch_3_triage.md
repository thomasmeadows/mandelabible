# Token triage — batch 3 of 6

Triage ruling on all 194 inflection groups (5–7 uses) in `references/word_reviews/token_triage/batch_3_input.md`, per the owner's 2026-07-29 triage-pass request. **Tallies: 186 KEEP, 8 WHITELIST, 0 REPLACE.** This batch skews toward common, well-worn Early Modern English vocabulary — sound register, nothing manufactured into a problem for being merely archaic. Attestation was checked by full-text search across Geneva1599.db, Tyndale.db, and Wycliffe.db for every headword (batch query, logged below per entry); the handful of flagged items below carry deeper individual verification (Geneva/Wycliffe quotes, KJV.db comparison, and — where the batch file's own quoted verse looked wrong — a direct check against `db/mandela.db`).

**Data-quality caveat (read before using this file for a full review round):** three of this batch's quoted-verse citations in `batch_3_input.md` do not match the live restored text in `db/mandela.db` — they appear to be cross-contaminated with other translations/word-groups by whatever indexed the token list:
- **"revenue"/"damage" at Ezra 4:13** — the input file quotes "thou shalt **damage/hurt** the revenue of the kings," a garbled slash-notation that is not real prose. `db/mandela.db` (and `KJV.db`) actually read "thou shalt **endamage** the revenue of the kings" — a single genuine EModE verb. The words "damage" and "revenue" are unaffected (their other citations are clean); "endamage" itself is untouched, correct, and outside this batch's scope.
- **"extortioners" at Luke 18:11 and "neglect" at Matthew 18:17** — both quotes end "...or even as this **tax collector**" / "...as an heathen man and a **tax collector**." The live restored text reads **publican** at both verses (confirmed against `db/mandela.db`'s `KJV_restored` row) — "tax collector" is a modern-English witness row (ASV-style) that leaked into the quote.
- **"transformed" at Matthew 17:2 and Mark 9:2** — the input file lists these as occurrences of "transformed," but both verses actually read **transfigured** in the restored text; `word_counts` appears to have indexed "transfigured" and "transformed" together. The real occurrences of "transformed" are Romans 12:2 and II Corinthians 11:14–15, which are genuine and unaffected.

None of these three represent actual corruption of the restored text — they are artifacts of the batch-generation tooling. Flagging so a regeneration pass can fix the source before this data feeds a full Rare-Word Review round.

## preferred — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary EModE verb ("preferred her... unto the best place," "preferred above the presidents"), attested Geneva 1599 (Esther 2:9 uses "preferred" itself). No anachronism; advancement/promotion existed in every era named.

## presently — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Means "immediately/at once" in all three citations (1 Sam 2:16, Prov 12:16, Matt 21:19) — the older EModE sense, not the modern "soon" sense. Genuine period usage, no drift risk in context.

## presidents — 5 uses
- verdict: WHITELIST
- suggestion: -
- reason: Unique administrative-office term (Daniel's Persian-empire "presidents," Aramaic סָרְכִין sarekin — chief ministers over the satraps). Geneva reads "rulers" and Wycliffe "princes" at Dan 6:2 — genuine translation divergence, not corruption — but there is no better single English word for this specific rank; protect it from a future swap pass rather than risk flattening a distinct office into "rulers"/"princes"/"governors," which the text already uses for other ranks.

## print — 5 uses (forms: print, printed)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 ("print any marks" sense, Lev 19:28). Axis 2 note worth recording: Job 19:23 "printed in a book" could misread as the printing press (post-dates Job's world entirely) — but the parallel v.24 "graven with an iron pen... in the rock" shows the intended sense is "impressed/engraved," the older and broader meaning of "print" (Old French preinte, "pressed"), which the ancient world did have (seals, stelae, cuneiform). Not source-anachronistic once read correctly; not a corruption signature.

## process — 5 uses
- verdict: KEEP
- suggestion: -
- reason: "In process of time" is a standing EModE idiom (Gen 4:3, 38:12, Exod 2:23), not a modern-sounding coinage; "process" is Middle English via Old French/Latin. Referent (elapsed time) is era-neutral.

## pureness — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun from "pure," genuine EModE formation, no substitute needed.

## rate — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Means "portion/allotted amount" (manna gathered "a certain rate," a "daily rate" of provisions) — the older sense, not modern "percentage/speed." Genuine, referent (a fixed daily allowance) existed in both OT settings cited.

## remedy — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, unremarkable, both medical (Prov 17:22) and general ("no remedy," 2 Chr 36:16) senses attested since Middle English.

## reputation — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "esteem/standing" throughout (Eccl 10:1, Acts 5:34, Gal 2:2) — genuine period sense, no drift.

## riot — 5 uses (forms: riot, rioting)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "dissipation/debauchery" (Greek ἀσωτία), the older sense — not "civil disorder." A false-friend for modern ears but not a corruption; genuinely the KJV's own word.

## rot — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Plain word, no issue.

## rottenness — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, unremarkable in all three citations.

## rump — 5 uses
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599. Unique Levitical sacrificial term for the fat tail of the ram/sheep (the alyah, a delicacy fat-tail portion specifically reserved for the altar) — no ordinary English synonym names this cut precisely; protect from a "delicacy" pass that might soften it to a vaguer word and lose the technical sense.

## sanctification — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Standard Pauline theological term, genuine period vocabulary (the Reformation-era doctrinal debates make this word extremely well-worn by 1611).

## sanctifieth — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Regular -eth inflection, no issue.

## scrape — 5 uses (forms: scrape, scraped)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary verb; both the leprous-house ritual (Lev 14) and Job's potsherd are period-plausible actions.

## scum — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word for cooking-pot residue (Ezek 24, the boiling-pot allegory) — ancient bronze-cauldron cookery is exactly the referent; no anachronism.

## simplicity — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, both the negative sense (2 Sam 15:11, "simplicity"=naivety) and positive (Rom 12:8) are genuine period usage.

## skull — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Plain anatomical word; Golgotha ("place of a skull") is the Gospel's own etymology, both axes clean.

## spue — 5 uses (forms: spue, spued)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Archaic spelling of "spew," genuine, no substitute needed.

## steep — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word for a precipitous slope; the swine-into-the-sea account (Matt 8:32) describes real Gerasene-district terrain. No issue.

## straitness — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstraction from "strait" (narrow/distressing), genuine, describes siege hardship (Deut 28) accurately for the ANE.

## succour — 5 uses (forms: succour, succoured)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary "help/aid" verb, genuine EModE, no anachronism (military and personal aid both existed).

## sweetness — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue in any of the three citations.

## tendeth — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Regular -eth inflection of "tend," ordinary.

## testifieth — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Regular inflection, ordinary.

## title — 5 uses (forms: title, titles)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Notably accurate at John 19:19–20: the Greek τίτλος is itself a loanword from Latin titulus, the placard Rome affixed above a crucified man's head — "title" is precisely the right word both linguistically and historically. Job 32/2 Kings senses ("flattering titles," an inscription) are equally ordinary.

## tongs — 5 uses
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599. Unique tabernacle/temple-lampstand implement (wick tongs, paired with snuffers and trimming dishes) — a specific cultic tool with no good one-word substitute; protect from a future "obscure object" pass.

## trance — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE word (Old French transir) for the state Balaam and Peter experience; the referent (visionary/ecstatic state) is well attested in both the OT prophetic and NT apostolic worlds.

## transformed — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Genuine occurrences are Romans 12:2 and II Corinthians 11:14–15 (Greek μεταμορφοῦσθε / μετασχηματίζεται) — see the header caveat: this batch's Matt 17:2/Mark 9:2 citations are a data-quality error, those verses actually read "transfigured" and are untouched.

## trap — 5 uses (forms: trap, traps)
- verdict: KEEP
- suggestion: -
- reason: Attested Wycliffe. Ordinary hunting/snare vocabulary, genuine to the ANE pastoral-hunting world in every citation.

## treason — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word for political betrayal/conspiracy against a king — a concept well attested in every ANE monarchy (1 Kings 16, Athaliah's overthrow).

## trieth — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Regular -eth inflection of "try" (test/examine), genuine theological usage.

## unsearchable — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary theological compound, no issue.

## warfare — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine word for military service/campaign in every citation; warfare plainly existed in both the OT and Pauline-era worlds.

## whit — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. "Every whit" is a standing EModE idiom (a small amount/bit), genuine and common.

## wonderfully — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary adverb, no issue.

## wrest — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Legal-idiom verb ("wrest judgment" = pervert justice), genuine and specific to the Mosaic law-court context in which it appears.

## wrung — 5 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary past tense of "wring," genuine sacrificial-procedure and pastoral (Gideon's fleece) usage.

## abstain — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine to the Jerusalem Council's decree (Acts 15) and Pauline exhortation; no substitute needed.

## abuse — 6 uses (forms: abuse, abused, abusing)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 (in the "abused"/"abuse" sense). Covers both "mistreat/violate" (Judg 19:25) and "misuse" (1 Cor 9:18) senses, both genuinely period.

## advantage — 6 uses (forms: advantage, advantaged, advantageth)
- verdict: KEEP
- suggestion: -
- reason: Ordinary word (profit/gain), including the archaic verb forms "advantaged"/"advantageth" — genuine EModE morphology, no substitute needed.

## affirm — 6 uses (forms: affirm, affirmed)
- verdict: KEEP
- suggestion: -
- reason: Attested Tyndale (affirmed). Ordinary word, no issue.

## appease — 6 uses (forms: appease, appeased, appeaseth)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word for calming wrath, genuine to every context cited.

## apt — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. "Apt for war" = fit/suited for war, genuine period military idiom.

## assay — 6 uses (forms: assay, assayed, assaying)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine EModE verb "to attempt/try" (cognate with "essay"), no substitute needed.

## assurance — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "certainty/confidence" throughout, genuine period sense (not modern financial "assurance").

## banner — 6 uses (forms: banner, banners)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Military/tribal standard, a well-attested ANE practice (Numbers' tribal standards, Song of Solomon's imagery).

## bishop — 6 uses
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599. Unique NT ecclesiastical office (Greek ἐπίσκοπος, "overseer"), the KJV's and every period witness's standing rendering; genuine to the earliest church's organizational vocabulary (1 Tim 3, Acts). No better one-word substitute exists without either modernizing ("overseer," losing the office-title force) or anachronizing further ("pastor").

## bolster — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word for a head-cushion/pillow, genuine ANE bedding item (goats'-hair pillow, 1 Sam 19).

## bountifully — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue.

## breeches — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Specific priestly linen undergarment (Exod 28:42) — an accurate, attested piece of Levitical vestment, both axes clean.

## calm — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine in every citation (the Jonah storm narrative, a maritime referent well within the ANE Mediterranean world).

## careless — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Means "unguarded/without care/secure" (Judg 18:7, "dwelt careless... quiet and secure") — the older sense, genuine, not the modern "sloppy" sense. No drift risk in context.

## carriage — 6 uses (forms: carriage, carriages)
- verdict: KEEP
- suggestion: -
- reason: Means "baggage/that which is carried," the standard EModE sense (Judg 18:21, 1 Sam 17:22, Isa 10:28/46:1, Acts 21:15) — not a vehicle. Genuine period word, referent (pack-baggage) existed throughout.

## chastisement — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary theological/disciplinary term, genuine.

## cloudy — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Tyndale. Ordinary adjective describing the pillar of cloud (Exod 33, Neh 9), genuine to the wilderness-wandering narrative.

## communicate — 6 uses (forms: communicate, communicated)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "share/give" (Gal 6:6, Phil 4:14–15) — the older sense, genuine, not the modern "converse" sense.

## conceit — 6 uses (forms: conceit, conceits)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "opinion/estimation" (esp. "in his own conceit" = self-opinion) — genuine EModE sense, not "vanity" or "witty remark."

## conferred — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary verb, covers both "discussed with" (1 Kings 1:7) and "pondered" (Luke 2:19) senses, both genuine period usage.

## constrained — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "compelled/urged," genuine, no issue.

## continuance — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary abstract noun ("duration"), no issue.

## dare — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Plain word, no issue.

## debate — 6 uses (forms: debate, debates)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Means "strife/contention" throughout — genuine older sense, not modern "formal argument."

## delicate — 6 uses (forms: delicate, delicates)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE adjective/noun (tender, pampered; also "delicacies" as food), no issue.

## desirous — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Plain word, no issue.

## dignity — 6 uses (forms: dignities, dignity)
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun for rank/honor, genuine in every citation (patriarchal blessing, royal honor, angelic "dignities").

## discouraged — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Plain word, no issue.

## disquieted — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE word (troubled/agitated), well-attested psalmic vocabulary.

## doted — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "lusted after/became infatuated" (Ezek 23) — genuine older sense, not modern "adored fondly."

## drams — 6 uses
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599. Renders Hebrew אֲדַרְכֹּנִים (adarkonim, Persian daric gold coins) at 1 Chr 29:7/Ezra 2:69/8:27 — all post-exilic, Persian-period contexts, so the referent (a specific historical coin) is source-era correct. "Dram" is a fixed weight/coinage term with no substitute that doesn't lose precision; protect it.

## effectual — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary Pauline theological adjective, no issue.

## election — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Standard Pauline/Reformation theological term (God's choosing), extremely well-worn by 1611 given the era's predestination debates.

## enlightened — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word ("his eyes were enlightened" = brightened/revived; Job 33's spiritual sense) — genuine period usage in both senses.

## ensample — 6 uses (forms: ensample, ensamples)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine EModE doublet of "example," standard KJV vocabulary, no substitute needed.

## expert — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. "Expert in war" = skilled/practiced, genuine military idiom for the tribal musters described.

## expounded — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Ordinary word for explaining/interpreting (a riddle, scripture), genuine to both the Judges narrative and the Emmaus road account.

## expressed — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "named/designated by name" (a census-list sense) — genuine older meaning, not modern "voiced an opinion."

## extortioner — 6 uses (forms: extortioner, extortioners)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary term for one who extorts, genuine in every citation. Note the header caveat: Luke 18:11's quoted verse in this batch has a "tax collector" contamination from a modern witness row — the live text correctly reads "publican," and "extortioners" itself at that verse is untouched.

## flint — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine ANE material (flint tool-making and flint outcrops in the wilderness are well documented), no anachronism.

## forepart — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary architectural compound ("front part"), genuine in tabernacle/temple description.

## furbished — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE verb (sharpened/polished, of a sword and a cooking vessel), no substitute needed.

## furious — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Plain word, no issue.

## goldsmith — 6 uses (forms: goldsmith, goldsmith's, goldsmiths)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Goldsmithing is a well-documented ANE and Second Temple-era trade (idol casting in Isaiah, temple-wall repair guilds in Nehemiah), both axes clean.

## goodman — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE term for "master of the house/husband," well attested; no issue.

## grate — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Bronze altar grating (Exod 27, 35, 38), an accurate tabernacle-construction component; still ordinary modern English for a grating, no substitute needed.

## greedy — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Plain word, no issue.

## grope — 6 uses (forms: grope, gropeth)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Genuine word for blind groping, no issue.

## guests — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine in every citation.

## haply — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Tyndale. Genuine EModE adverb ("by chance/perhaps"), standard KJV vocabulary.

## horrible — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Plain word, no issue.

## informed — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Ordinary word, no issue.

## jeopardy — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE word (from Old French "jeu parti"), well established by 1611, no substitute needed.

## lady — 6 uses (forms: ladies, lady)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary title word (not a proper name here — "the lady of kingdoms," "elect lady"), genuine in every citation.

## liberal — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Wycliffe. Means "generous," the standard older sense, genuine in every citation (not modern political "liberal").

## lucre — 6 uses (forms: lucre, lucre's)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. "Filthy lucre" is a standing EModE idiom for dishonest gain, genuine.

## mankind — 6 uses
- verdict: KEEP
- suggestion: -
- reason: The KJV uses "mankind" in two genuine period senses — "humanity" (Job 12:10) and "a male person" (Lev 18:22, 20:13, from Hebrew זָכָר zakar) — both attested EModE usages of the compound. A modern reader may misread the Leviticus sense as "humanity," but that is a readability risk inherited from the base text's own accurate period usage, not a corruption; no swap needed.

## mariners — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Tyre's seafaring trade (Ezek 27) is well-documented Phoenician maritime history — both axes clean.

## meditation — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary devotional-psalmic term, no issue.

## memory — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, no issue.

## mete — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Genuine EModE verb "to measure out," standard, no substitute needed.

## navy — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Means "fleet of ships" in 1611 usage (not a national military branch) — genuine sense, and Solomon's Red Sea trading fleet at Ezion-geber (1 Kings 9:26) is well-attested ANE maritime history.

## neglect — 6 uses (forms: neglect, neglected, neglecting)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word throughout. Note the header caveat: Matthew 18:17's quoted verse in this batch has a "tax collector" contamination — the live text correctly reads "publican," and "neglect" itself is untouched.

## omer — 6 uses (forms: omer, omers)
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. A transliterated Hebrew dry-measure unit (עֹמֶר), used to describe the manna ration — untranslatable without losing precision; protect from a "measures" swap pass.

## parlour — 6 uses (forms: parlour, parlours)
- verdict: KEEP
- suggestion: -
- reason: Attested Tyndale and Wycliffe. Ehud's "summer parlour" (Judg 3) — a cool upper/inner chamber, a genuine ANE domestic-architecture feature; "parlour" (from OFr parler, "to speak," i.e. a private room) is the period English term for it.

## pisseth — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Crude but wholly genuine KJV idiom ("him that pisseth against the wall" = every male), an authentic Hebrew idiom rendered literally — not a defect of register.

## practise — 6 uses (forms: practise, practised)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine period spelling of the verb (practice), no issue.

## presumptuously — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary legal/moral adverb (Mosaic law's distinction between presumptuous and unwitting sin), genuine to the source era.

## prospect — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "outlook/direction faced" (Ezekiel's temple chambers) — genuine architectural sense, not modern "future outlook."

## quit — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Tyndale. Means "acquitted/released from liability" — genuine older legal sense (Exod 21, Josh 2), not modern "stopped/gave up."

## reddish — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary color-descriptor for the Levitical skin-disease diagnostics, no issue.

## replenished — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "filled/populated" (Gen 9:19 "the whole earth replenished") — genuine older sense, not modern "restocked."

## rereward — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic spelling of "rearward" (rear guard of an army/procession), standard EModE military vocabulary, no substitute needed.

## restitution — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary Mosaic-law legal term, genuine to the source era's restitution statutes (Exod 22).

## revenue — 6 uses (forms: revenue, revenues)
- verdict: KEEP
- suggestion: -
- reason: Ordinary economic term; royal/agricultural revenue existed in every era cited. Note the header caveat on Ezra 4:13's quoted verse — see above; "revenue" itself is unaffected.

## reviled — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine to the Passion narratives (Matt 27, Mark 15) and John 9.

## rid — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "deliver/remove" (Gen 37:22, Exod 6:6, Lev 26:6) — genuine older transitive sense, not modern "get rid of."

## roughly — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary adverb, no issue.

## savoury — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word for well-seasoned food (Isaac's venison, Gen 27), no issue.

## sect — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Renders Greek αἵρεσις (hairesis, "faction/school of thought") — the Pharisees, Sadducees, and Nazarenes were genuinely called "sects" by contemporaries (cf. Josephus); both axes clean.

## seize — 6 uses (forms: seize, seized)
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine in every citation (military capture, personification of death/fear seizing).

## shearers — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Sheep-shearing is a core ANE pastoral-economy trade (Judah's shearers at Timnath, Nabal's shearers at Carmel), both axes clean.

## sink — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## snuffers — 6 uses
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599. Unique tabernacle/temple-lampstand implement (wick-trimmer, paired with tongs) — a specific cultic tool with no better one-word substitute; protect from a future swap.

## sodden — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine archaic past participle of "seethe" (boiled), standard EModE, referring to ordinary ANE boiling/cooking of meat.

## specially — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Ordinary adverb, no issue.

## square — 6 uses (forms: square, squared, squares)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Ordinary architectural/geometric term, genuine to Ezekiel's temple description and Solomon's temple.

## stagger — 6 uses (forms: stagger, staggered, staggereth)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word (to reel like a drunken man), genuine in every citation, including Romans 4:20's figurative "staggered not at the promise."

## story — 6 uses (forms: stories, story)
- verdict: KEEP
- suggestion: -
- reason: Attested Wycliffe ("stories"). Two genuine period senses, both correct in context: "narrative/account" (Acts 1:1, Greek λόγος) and "building level/floor" (Gen 6:16, Ezek 41–42) — no anachronism in either.

## subtilty — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic spelling of "subtlety" (craftiness/guile), standard EModE, no substitute needed.

## target — 6 uses (forms: target, targets)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 ("two hundreth targets of beaten golde," 1 Kings 10:16, matching the KJV exactly) alongside Geneva's own use of "shield" at 1 Sam 17:6 and 2 Chr 14:8 — the two words denote genuinely distinct period military items (target = a smaller round shield/buckler; shield = the larger kind), and the KJV/Geneva both use both words for that reason, sometimes in the same verse (2 Chr 14:8). A modern reader may mistake "target" for the goal/objective sense, but that is ordinary semantic drift, not a defect — the word is period-attested and the referent (a decorative gold shield, Solomon's ceremonial armory) is historically documented. Not manufacturing a REPLACE for mere archaism here.

## temper — 6 uses (forms: temper, tempered)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "mix/blend" (dough, ointment, oil) — genuine older sense, not modern "mood." Referent (kneading, blending spices/oil) existed throughout.

## tenons — 6 uses
- verdict: WHITELIST
- suggestion: -
- reason: Attested Geneva 1599. Specific tabernacle-construction woodworking joint term (Exod 26, 36) — no substitute preserves the technical carpentry sense; protect from a future swap.

## tolerable — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine to the Gospel judgment sayings, no issue.

## twins — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## unstable — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## urged — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## ware — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine EModE noun for "merchandise/goods" (Nehemiah's sabbath-trading passages), no substitute needed.

## wellbeloved — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE compound term of endearment, standard, no substitute needed.

## wert — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Pure Early Modern English second-person singular past-tense grammar ("thou wert"), not a vocabulary choice at all — this is the King James grammar itself.

## wet — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Plain word, no issue.

## whet — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE verb "to sharpen," standard, no substitute needed.

## woollen — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary textile term, genuine to Levitical fabric law (wool vs. linen, both ANE textiles).

## yonder — 6 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine EModE demonstrative adverb, still dialectally alive, no substitute needed.

## abated — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Ordinary word, genuine to the Flood narrative (receding waters).

## ability — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, no issue.

## abolish — 7 uses (forms: abolish, abolished)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, no issue.

## adjure — 7 uses (forms: adjure, adjured)
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE legal/religious verb (to charge solemnly under oath), well-attested by 1611 (Latin adiurare via Old French); referent (solemn oath-charging) is well documented in both OT and NT settings (1 Kings 22, Matt 26:63).

## afore — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Genuine archaic form of "before," standard, no issue.

## aileth — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE idiom ("what aileth thee"), still colloquially alive today, no issue.

## alienated — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word (estranged), genuine to Ezekiel's marital-allegory vocabulary.

## astonied — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine archaic form of "astonished," standard EModE, no substitute needed.

## attentive — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, genuine to the temple-dedication prayers (2 Chr, Neh), no issue.

## bay — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "inlet/gulf of the sea" (Joshua's border descriptions), the same sense the word carries today — genuine, no drift.

## beforehand — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## beguile — 7 uses (forms: beguile, beguiled)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE verb (deceive/entice), standard from Genesis 3 onward, no substitute needed.

## beheaded — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word; decapitation as judicial/military punishment is well documented in both the Mosaic-law world (Deut 21) and Herodian Judea (Matt 14, John the Baptist).

## bemoan — 7 uses (forms: bemoan, bemoaned, bemoaning)
- verdict: KEEP
- suggestion: -
- reason: Ordinary word for lamenting, genuine to Jeremiah's mourning vocabulary, no issue.

## benefit — 7 uses (forms: benefit, benefits)
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## beset — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine EModE verb (surrounded/besieged), standard, no issue.

## bill — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. "Bill of divorce" (Hebrew סֵפֶר כְּרִיתֻת sefer keritut) is a genuine, historically attested legal-document term for the Mosaic-law divorce certificate — both axes clean.

## careful — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "full of care/anxious" (2 Kings 4:13, Dan 3:16 "we are not careful to answer thee") — genuine older sense, not modern "cautious." No drift risk in context.

## certify — 7 uses (forms: certified, certify)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine EModE legal/administrative verb ("inform officially"), used correctly throughout (Ezra's Persian-court correspondence, Esther).

## childless — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## clods — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary agricultural term (clumps of earth), genuine to the ANE farming imagery of Job.

## communication — 7 uses (forms: communication, communications)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Means "conversation/talk" (2 Sam 3:17, Luke 24:17) — genuine older sense, not modern "transmission of information." No drift risk in context.

## complain — 7 uses (forms: complain, complained, complaining)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, no issue.

## contentious — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word (quarrelsome), genuine to Proverbs' wisdom-sayings register.

## corruptible — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Genuine Pauline philosophical/theological term (Greek φθαρτός), well within both the Hellenistic-philosophical and Reformation-doctrinal vocabulary current by 1611.

## dainty — 7 uses (forms: dainties, dainty)
- verdict: KEEP
- suggestion: -
- reason: Ordinary word for a delicacy/fine food, genuine in every citation including Revelation's merchant-lament passage.

## damage — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary economic/legal term, genuine to the Ezra correspondence and Esther. Note the header caveat: this batch's Ezra 4:13 citation is a garbled "damage/hurt" artifact from conflation with "endamage" — see above; "damage" itself is correctly attested at Ezra 4:22 and Esther 7:4 unaffected.

## daubed — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Genuine word for plastering/coating (Moses' basket with pitch, Ezekiel's whitewashed wall), no issue.

## decked — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Genuine word for adorning/decorating, no issue.

## disputing — 7 uses (forms: disputing, disputings)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, genuine to the Acts synagogue-debate accounts.

## ditch — 7 uses (forms: ditch, ditches)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word (a pit/trench), genuine in every citation, including the military water-trenches of 2 Kings 3.

## diviners — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary term for a well-documented ANE and Philistine religious practice (Deut 18's condemnation of it, the Philistine priests consulting diviners over the ark) — both axes clean.

## doubtless — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary word, no issue.

## dyed — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Ram-skin dyeing (red-dyed leather for the tabernacle covering) is an attested ANE tanning/dyeing craft — both axes clean.

## exchange — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary trade/barter term, genuine to the ANE and Second Temple economies described.

## excuse — 7 uses (forms: excuse, excused, excusing)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Ordinary word, no issue.

## expedient — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Tyndale. Ordinary word (Latin-derived, established since Middle English), genuine to the Johannine passages cited.

## flattereth — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Regular -eth inflection, ordinary, no issue.

## fragments — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, genuine to the feeding-miracle accounts.

## frost — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Ordinary weather term, genuine to the ANE climate described (Job, the manna-and-hoarfrost simile in Exodus).

## gentleness — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue.

## glittering — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary adjective for polished metal/gems, genuine in every citation.

## haughtiness — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue.

## hearth — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary domestic-architecture feature, genuine to ANE tent/house cooking (Abraham's hearth-cakes, Gen 18).

## honest — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599, Tyndale, and Wycliffe. Means "honorable/upright" in these citations (Luke 8:15, Acts 6:3, Rom 12:17) — the broader older sense, genuine, not narrowed to "truthful."

## incurable — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599 and Wycliffe. Ordinary medical/figurative term, no issue.

## lap — 7 uses (forms: lap, lapped, lappeth)
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary word, both the anatomical sense (a garment-fold used as a pocket, Neh 5:13) and the drinking sense (Gideon's men lapping water, Judg 7) are genuine period usage.

## midwives — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Midwifery is a well-documented ANE profession (the named Hebrew midwives Shiphrah and Puah, Exod 1) — both axes clean, ordinary occupational noun.

## nativity — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Means "birthplace/one's birth" (land of one's nativity) throughout — the broader older sense (from Latin nativitas), genuine, not narrowed to the Christmas Nativity. No drift risk in context.

## oftentimes — 7 uses
- verdict: KEEP
- suggestion: -
- reason: Attested Geneva 1599. Ordinary adverb, no issue.
