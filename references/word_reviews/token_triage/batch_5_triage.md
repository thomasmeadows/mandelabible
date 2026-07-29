# Token triage — batch 5 of 6

Triage pass (owner request 2026-07-29) over 194 inflection groups (counts 12–21) from
`references/word_lists/token_list_full.md` — the restored text's words that the whitelist
and proper-noun exclusions do not already protect. Verdicts: **178 KEEP**, **14 WHITELIST**,
**2 REPLACE**. All KEEP/WHITELIST rulings are register-and-referent judgments made against
this agent's working knowledge of the Authorized Version corpus; the two REPLACE findings
were confirmed against `KJV.db` and period witnesses via direct SQLite query, and both
turned out to be corruptions left by an earlier restoration/rare-word pass rather than
fresh problems — the most important findings of this batch are the **hem/fringes conflation**
at Numbers 15:38 and Deuteronomy 22:12, and the **"lewdness wickedness" garble** at
Job 31:11. WHITELIST entries are unique-referent nouns (garment, vessel, instrument,
ornament, disease-term, office, animal, or measure) with no good substitute, flagged so a
later pass does not "modernize" them away. Everything else is ordinary, sound Early Modern
English naming something of the biblical world — archaic register is the target, not a defect.

---

## durst — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic preterite of "dare" (cf. Esther 7:5, Numbers 14:44), standard KJV usage throughout; the referents (going up a hill, standing barefoot, imagining a plot) are all ordinary biblical-world actions.

## easy — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary EModE adjective, well attested (Matthew 11:30 "my yoke is easy"); no anachronism in sense.

## equity — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Standard KJV judicial/moral vocabulary (Psalms 98:9, 99:4); abstract legal concept present in the ancient Near Eastern world of judgment and covenant.

## fort — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine KJV word (2 Samuel 5:9 "David dwelt in the fort"); source-era referent (a fortified stronghold) is well attested archaeologically for Iron Age Israel/Judah and Babylon.

## grind — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb naming a real ancient technology (hand-mill/millstone, cf. Matthew 24:41); no era problem on either axis.

## guile — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Core KJV moral vocabulary (Psalms 32:2, 34:13), sound register and sense throughout.

## hem — 12 uses
- verdict: REPLACE
- suggestion: [whitelist] none fits — "fringe(s)" is not on the current whitelist, though this finding recommends adding it; the nearest whitelisted candidate, "hem" itself, is exactly the word that must NOT stand at these two verses because it names the wrong object | [witness] `KJV.db`'s own base reading, Geneva 1599, DRC, and ASV are unanimous on "fringes" at both verses — Geneva 1599 Numbers 15:38: "bid them that they make them fringes vpon the borders of their garments... and put vpon the fringes of the borders a ryband of blewe silke"; Geneva 1599 Deuteronomy 22:12 reads "fringes" identically to KJV | [other] restore "fringes"/"fringe" at these two verses specifically
- reason: This group conflates two distinct KJV words. Exodus 28:33–34 and 39:24–25 genuinely read "hem" in the base text — the ornamented lower edge of the priestly robe — and those four occurrences in the batch are correct. But Numbers 15:38 and Deuteronomy 22:12 read "hems"/"hem" in the *restored* text where `KJV.db` itself reads **"fringes"** — the corner tassels (Hebrew tzitzit) commanded as a distinct religious object, not a garment edge. An earlier pass appears to have globally swapped "fringes" → "hems," collapsing two different referents into one word; this is an Axis 2 problem (the wrong object is named) introduced by that pass, not a fresh anachronism. Flag both occurrences for restoration to "fringes"; the four genuine "hem" verses need no change.

## maintain — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary EModE verb (I Kings 8:45 "maintain their cause"), sound throughout.

## meal — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient staple foodstuff (fine ground grain, Genesis 18:6, Numbers 5:15); no era problem.

## oven — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Real ancient Near Eastern cooking technology (Leviticus 2:4, 7:9); word and referent both sound.

## oversight — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (Numbers 3:32, 4:16), fits both axes.

## poll — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic sense "head" / "to shave the head" (Numbers 1:2 "by their polls," Ezekiel 44:20 "poll their heads"), well attested KJV usage.

## requite — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Standard KJV verb (Genesis 50:15, Deuteronomy 32:6), sound throughout.

## sad — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE sense "sorrowful" (Genesis 40:6-7), matches KJV usage exactly; not a modern-idiom risk.

## servile — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Standard technical phrase "servile work" for holiday labor restriction (Leviticus 23:7-8, 21); genuine cultic-calendar term.

## signet — 12 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific ancient object — a personal seal, often set in a ring (Genesis 38:18, 25; Exodus 28:11) — with no true one-word substitute; protect from future "modernization" swaps.

## similitude — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine KJV theological-vision vocabulary (Numbers 12:8, Deuteronomy 4:12), sound register.

## speed — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Archaic sense "success/prosperity" (Genesis 24:12 "good speed") as well as "haste" (I Samuel 20:38); both senses genuine EModE, no anachronism.

## stiffnecked — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Distinctive KJV compound (Exodus 32:9, 33:3, 5) translating a Hebrew idiom directly; sound on both axes.

## unawares — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary EModE adverb (Genesis 31:20, 26), well attested, no issue.

## wist — 12 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic preterite of "wit" (to know) — Exodus 16:15, 34:29 — a hallmark KJV form, not to be touched.

## ambassador — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Standard period word (attested Geneva/Tyndale/KJV), sound office for the ancient world's diplomatic practice. Note in passing: the Joshua 9:4 occurrence quoted in this batch reads "wine wineskins, old, and rent" — `KJV.db`'s base text reads "wine bottles," so an earlier bottles→wineskins pass left a duplicate "wine" (should read simply "wineskins" or "old wineskins for wine"). This is a corruption of the surrounding verse, not of "ambassador" itself — flag it for repair in whichever pass owns the bottles/wineskins swap (Decision Log #4's canonical example).

## bereave — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Standard KJV verb (Genesis 42:36, Jeremiah 15:7), sound throughout.

## consulted — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound register and sense (I Kings 12:6, 8).

## convert — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine KJV religious-conversion vocabulary (Matthew 23:15, Acts 6:5), fits both axes for the first-century mission context.

## correction — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (Job 37:13, Proverbs 3:11), sound.

## dragon — 13 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific mythic/symbolic creature-type central to apocalyptic imagery (Revelation 12) and OT usage (translating Hebrew tannin); no substitute captures the same referent — protect from future swap attempts.

## edify — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine Pauline vocabulary (Romans 14:19, I Corinthians 14), sound theological register.

## evildoer — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary compound noun (John 18:30, Psalms 37:1), well attested.

## fierceness — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Standard KJV abstract noun (Deuteronomy 13:17, Joshua 7:26), sound.

## footmen — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine military term for infantry (Numbers 11:21, Judges 20:2), matches ancient warfare's foot-soldier/chariot distinction.

## fret — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Multiple genuine EModE senses present and correct — "spread/corrode" (Leviticus 13:55, of a leprous stain) and "vex oneself" (Psalms 37:1); both sound.

## fully — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue.

## intent — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (II Samuel 17:14, Hebrews 4:12), sound.

## mitre — 13 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names the specific priestly headdress of Exodus 28 — a unique liturgical garment with no substitute; protect it as with other priestly-vestment terms.

## necessity — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (Acts 20:34, Romans 12:13), sound.

## network — 13 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names the specific lattice-work bronze grating of the tabernacle altar and temple pillars (Exodus 27:4, I Kings 7:17) — genuinely period (OED attests "net-work" for lattice construction well before 1611) but liable to be mistaken for a modern-anachronism flag ("computer network") by a naive future pass; whitelist to protect it.

## overseer — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary administrative title (Genesis 39:4, Nehemiah 11:9) with a plain modern equivalent ("supervisor"); not a uniquely irreplaceable term, no issue as is.

## plaister — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine period spelling of "plaster" (Leviticus 14:42, Deuteronomy 27:2), matches real ancient building material (lime plaster over stone), sound on both axes.

## safe — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, no issue (I Samuel 12:11, II Samuel 18:29).

## scales — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary anatomical term for fish scales (Leviticus 11:9-12), genuine dietary-law vocabulary.

## sentence — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine legal-judicial term (Deuteronomy 17:9-11), sound for the ancient Israelite court system.

## several — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Archaic sense "separate, distinct" (Numbers 28:13, 21, 29 "a several tenth deal"), genuine KJV usage — not the modern "more than two" sense; sound.

## shower — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary weather noun (Ezekiel 34:26, Deuteronomy 32:2), no issue.

## straitly — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE adverb "strictly" (Genesis 43:3, 7), well attested KJV usage.

## stroke — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun for a blow/legal case-category (Deuteronomy 17:8, 19:5), sound.

## stuff — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic sense "goods, possessions" (Genesis 45:20, Exodus 22:7), matches KJV usage; not the modern vague-filler sense.

## tooth — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary anatomical term ("eye for eye, tooth for tooth," Exodus 21:24), sound legal-formula usage.

## tradition — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine first-century religious vocabulary (Matthew 15:2-3, Galatians 1:14 "traditions of my fathers"), sound on both axes.

## victory — 13 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, sound (II Samuel 19:2, 23:10).

## ago — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary EModE adverb (I Samuel 9:20, 30:13), no issue.

## approve — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine KJV verb, several senses all sound ("test and find worthy," Romans 14:18; "commend," Acts 2:22).

## bag — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun for a real ancient carrying-pouch (Deuteronomy 25:13, I Samuel 17:40 "a shepherd's bag... in a scrip"), sound on both axes.

## behave — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary reflexive verb (Deuteronomy 32:27, I Chronicles 19:13), no issue.

## contain — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound both in the theological sense (I Kings 8:27 "heaven cannot contain thee") and the literal capacity sense (I Kings 7:26 "two thousand baths").

## enchantment — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient Near Eastern/Egyptian magical practice named accurately (Leviticus 19:26, Exodus 7:11); sound on both axes.

## expectation — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (Psalms 9:18, 62:5), no issue.

## falsehood — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (II Samuel 18:13, Job 21:34), sound.

## fit — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective/verb, genuine sense throughout (Genesis 2:20 "helper fit for him"; I Kings 6:35 "fitted upon"), sound.

## furthermore — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary connective adverb, no issue (Exodus 4:6, Deuteronomy 4:21).

## palsy — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient medical condition (paralysis), correctly named across Gospel healing accounts (Matthew 4:24, 8:6, 9:2); sound on both axes.

## plainly — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue (Exodus 21:5, Numbers 12:8).

## plenteous — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE adjective "abundant" (Genesis 41:34, 47; Deuteronomy 26:5), well attested.

## point — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun/verb, several genuine senses (Genesis 25:32 "at the point to die"; Numbers 34:7 "point out"), sound.

## push — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb for a goring ox (Exodus 21:28-32), genuine ancient legal-code vocabulary (cf. the ox-goring statutes of the ancient Near East).

## rear — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE verb "to erect" (Exodus 26:30, 40:17-18, "reared up the tabernacle"), sound throughout.

## scall — 14 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific dermatological condition in the priestly diagnostic law (Leviticus 13:30-32) with no true one-word substitute; protect as a unique technical term.

## sorry — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine sense "grieved, sorrowful" (I Samuel 22:8, Nehemiah 8:10), matches KJV usage exactly.

## state — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine sense "condition/estate" (Genesis 43:7 "our state and kindred"; Esther 1:7 "the state of the king"), sound.

## stoop — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound both physically (I Samuel 24:8) and figuratively (Job 9:13).

## subjection — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (Psalms 106:42, Jeremiah 34:11), no issue.

## swell — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine physiological term used in the trial-by-ordeal ritual (Numbers 5:21-27); sound as the correct ancient legal-ritual referent.

## triumph — 14 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb (II Samuel 1:20, Psalms 25:2, Exodus 15:1 "triumphed gloriously"), sound.

## wreath — 14 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific decorative chain/cord-work motif on priestly and temple ornament (Exodus 28:14, 22, 24; I Kings 7:17) — a unique craft term worth protecting alongside "knop" and "network."

## arches — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary architectural noun in Ezekiel's temple vision (Ezekiel 40:16, 21-22); sound as an ancient Near Eastern gatehouse feature.

## attend — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound both as "wait upon" (Esther 4:5) and "pay heed" (Psalms 17:1).

## banquet — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient feast-vocabulary (Esther 5:4-6, Song of Solomon 2:4 "banqueting house"), sound.

## betwixt — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE preposition "between" (Genesis 17:11, 23:15, 26:28), well attested KJV usage.

## controversy — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary legal-judicial noun (Deuteronomy 17:8, 19:17), sound.

## dash — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary violent verb, genuine ancient-warfare imagery (II Kings 8:12, Psalms 2:9), sound.

## defend — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Judges 10:1, II Kings 19:34).

## derision — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun (Job 30:1, Psalms 2:4), sound.

## difference — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine cultic-legal vocabulary "put difference between holy and unholy" (Leviticus 10:10, 11:47), sound on both axes.

## effect — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun/phrase "of none effect" (Numbers 30:8, Psalms 33:10), sound.

## enjoy — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine sabbatical-year vocabulary "the land shall enjoy her sabbaths" (Leviticus 26:34, 43), sound.

## fade — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, genuine botanical/agricultural imagery (Isaiah 1:30, 40:7, 64:6), sound.

## impute — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine Pauline theological vocabulary (Romans 4:6, 8, 11) as well as ordinary legal sense (Leviticus 7:18, 17:4); sound on both axes.

## mirth — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun for festive joy (Genesis 31:27, Nehemiah 8:12), sound.

## natural — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, sound in both the physical sense (Deuteronomy 34:7 "natural force") and Paul's argument (Romans 1:26-27).

## nether — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE adjective "lower" (Exodus 19:17, Deuteronomy 24:6 "nether or upper millstone"), well attested.

## pattern — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, sound tabernacle-construction vocabulary (Exodus 25:9, 40; Hebrews 9:23).

## plenty — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, sound (Genesis 27:28, 41:29-30).

## raven — 15 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific bird species appearing in creation, dietary-law, and Elijah narratives (Genesis 8:7, Leviticus 11:15, I Kings 17:4-6) — a unique creature name, protect it as with other biblical animal names.

## reconcile — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine cultic and Pauline theological vocabulary (Leviticus 6:30, Romans 5:10), sound on both axes.

## rode — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary past tense of "ride," sound (Genesis 24:61, Judges 10:4).

## saddle — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient riding equipment for camels/asses (Genesis 31:34, II Samuel 19:26), sound on both axes.

## strove — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary past tense of "strive," sound (Genesis 25:22, 26:20-21).

## value — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine vow-redemption/appraisal vocabulary (Leviticus 27:8-16), sound cultic-legal usage.

## visitation — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine KJV theological vocabulary "day of visitation" (Isaiah 10:3, Job 10:12), sound.

## wear — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound (Exodus 18:18, Deuteronomy 22:5, 11).

## withdraw — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (I Samuel 14:19, II Samuel 11:15).

## wondrous — 15 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, sound (I Chronicles 16:9, Job 37:14, 16).

## attain — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Psalms 139:6, Genesis 47:9).

## bloody — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, genuine idiom "a bloody husband art thou to me" tied to the circumcision narrative (Exodus 4:25-26); sound.

## buckler — 16 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific small ancient shield distinct from the larger "shield" (I Chronicles 12:8 pairs the two), a unique military-equipment term worth protecting.

## entice — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound (Exodus 22:16, Deuteronomy 13:6, Judges 14:15).

## entry — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary architectural noun (II Kings 16:18, I Chronicles 9:19, Ezekiel 40:38), sound.

## harm — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, no issue (Genesis 31:52, Leviticus 5:16).

## mire — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun for wet mud/clay, genuine ancient imagery (Job 8:11, 30:19), sound.

## musick — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine period spelling of "music" (I Samuel 18:6, I Chronicles 15:16), matches real ancient instrumental worship practice; sound.

## poverty — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue (Genesis 45:11, Leviticus 25:35).

## privily — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE adverb "secretly" (Judges 9:31, I Samuel 24:4), well attested.

## retain — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Job 2:9, Proverbs 4:4, 11:16).

## sceptre — 16 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names the specific royal staff of rule (Genesis 49:10, Numbers 24:17, Esther 4:11) — a unique regalia term, protect from replacement.

## shot — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound both botanically (Genesis 40:10 "blossoms shot forth") and militarily (Exodus 19:13 "shot through").

## slow — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, no issue (Exodus 4:10, Nehemiah 9:17 "slow to anger").

## soever — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE combining suffix "-soever" (Leviticus 15:9, 17:3, 22:4), well attested legal-formula usage.

## surname — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb/noun, sound (Isaiah 44:5, Matthew 10:3, Mark 3:16-17).

## vexation — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue (Deuteronomy 28:20, Ecclesiastes 1:14).

## zeal — 16 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, sound (II Samuel 21:2, II Kings 10:16, 19:31).

## blast — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, sound both for a trumpet (Joshua 6:5) and figurative divine breath (Exodus 15:8).

## direct — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Genesis 46:28, Psalms 5:3).

## fatness — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE abstract noun (Genesis 27:28, 39; Deuteronomy 32:15), well attested blessing-formula vocabulary.

## freewill — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine compound sacrificial-category term (Leviticus 22:18, 21, 23 "freewill offering"), still transparent English, no substitute needed.

## ignorant — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, no issue (Psalms 73:22, Isaiah 56:10, 63:16).

## integrity — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, sound (Genesis 20:5-6, I Kings 9:4).

## pound — 17 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific unit of weight/currency used inconsistently for both weight of metal (I Kings 10:17, Ezra 2:69) and the Lukan mina-equivalent coin (Luke 19:13-18) — a measure term the standing rule flags for protection regardless of ordinariness of the English word.

## prosperity — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue (Deuteronomy 23:6, I Samuel 25:6).

## purchase — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb/noun, genuine ancient land-transaction vocabulary (Genesis 49:32, 25:10), sound.

## refrain — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Genesis 45:1, Job 7:11, Proverbs 1:15).

## siege — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary military noun, genuine ancient siege-warfare vocabulary (Deuteronomy 20:19, 28:53), sound.

## stature — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, sound (Numbers 13:32, I Samuel 16:7).

## surety — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary legal/idiomatic noun, sound both as "of a surety" (Genesis 15:13) and financial guarantor (Proverbs 22:26).

## threshold — 17 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary architectural noun, genuine Dagon-temple narrative detail (I Samuel 5:4-5), sound.

## agree — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Matthew 5:25, 18:19, 20:2, 13).

## armourbearer — 18 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific ancient military office/role (Judges 9:54, I Samuel 14:7, 12) with no substitute — protect the compound as a unique title.

## consolation — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, sound (Jeremiah 16:7, Luke 2:25).

## dishonour — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun/verb, no issue (Ezra 4:14, Psalms 35:26, 69:19).

## exercise — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, genuine sense "practice/exert" throughout (Psalms 131:1, Matthew 20:25), not the modern physical-fitness sense; sound.

## ignorance — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine cultic-legal vocabulary "sin through ignorance" (Leviticus 4:2, 13, 22), sound.

## imagine — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, genuine sense "to devise/plot" (Esther 7:5, Job 6:26), sound.

## ransom — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine cultic/legal vocabulary (Exodus 21:30, 30:12 "ransom for his soul"), sound.

## revenge — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb/agent-noun, including the real KJV legal title "revenger of blood" (Numbers 35:19, 21, 24) for the ancient kinsman-avenger institution; sound throughout.

## robber — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, no issue (Job 5:5, Proverbs 6:11).

## rush — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun/verb, sound both for the marsh plant (Job 8:11, Isaiah 35:7) and violent motion (Judges 9:44).

## shewbread — 18 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names the specific consecrated bread of the tabernacle table (Exodus 25:30, 35:13) — a unique cultic-object term with no substitute; protect it.

## stablish — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine EModE variant of "establish" (II Samuel 7:13, I Chronicles 17:12), well attested KJV usage.

## tempest — 18 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, no issue (Job 9:17, 27:20, Psalms 11:6).

## convocation — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine cultic-calendar term "holy convocation" (Exodus 12:16, Leviticus 23:2-7), still a live English word (academic convocation), no substitute needed.

## fortress — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, sound (II Samuel 22:2, Psalms 18:2, 31:3).

## hatred — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue (Numbers 35:20, II Samuel 13:15).

## hedge — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient agricultural boundary feature (Job 1:10, Proverbs 15:19), sound on both axes.

## league — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine sense "covenant/treaty" (Joshua 9:6-11), matches KJV usage exactly — not the modern distance-unit or sports sense; sound.

## lewdness — 19 uses
- verdict: REPLACE
- suggestion: [whitelist] none fits — neither "heinous" nor "crime" is currently on the whitelist; this finding recommends adding them once the owner confirms the revert | [witness] `KJV.db`'s own base reading, DRC, and ASV independently agree on "heinous crime" — DRC Job 31:11: "For this is a heinous crime, and a most grievous iniquity"; ASV: "For that were a heinous crime; Yea, it were an iniquity to be punished by the judges" (Geneva 1599 and Wycliffe instead read plain "wickednes"/"wickidnesse," without the "heinous crime" phrase, so they corroborate the general sense of grave wrongdoing without settling the exact wording) | [other] restore "an heinous crime" exactly as `KJV.db` reads
- reason: This flags Job 31:11 only — the word "lewdness" is genuine and correctly used elsewhere in this same group (Judges 20:6, Jeremiah 11:15). But the Job 31:11 occurrence as it now stands reads "For this is an lewdness wickedness; yea, it is an iniquity to be punished by the judges" — ungrammatical (an before a consonant), redundant (two near-synonyms stacked with no conjunction), and it replaces the base KJV's "an heinous crime." This reads as an earlier rare-word pass botching a two-word phrase swap; it needs restoring, not further replacement.

## resist — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Zechariah 3:1, Matthew 5:39).

## sir — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary address term, sound (Genesis 43:20, Matthew 13:27, Acts 16:30).

## skirt — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine sense "the lower part/edge of a garment" used euphemistically (Deuteronomy 22:30, 27:20 "uncovereth his father's skirt") and literally (Ruth 3:9); sound, distinct from the "hem" conflation flagged above.

## spent — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary past participle, no issue (Genesis 21:15, 47:18).

## unjust — 19 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, no issue (Psalms 43:1, Proverbs 11:7, 28:8).

## accursed — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine cultic-legal term "the accursed thing" (herem, Joshua 6:17-18), sound on both axes.

## alas — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary interjection, no issue (Numbers 12:11, 24:23, Joshua 7:7).

## aloud — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue (Genesis 45:2, I Kings 18:27-28).

## bad — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, sound in the idiom "speak good or bad" (Genesis 24:50, 31:24, 29).

## catch — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Exodus 22:6, Judges 21:21).

## censer — 20 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific ritual incense vessel used in tabernacle worship (Leviticus 10:1, 16:12, Numbers 16:6-17) — a unique cultic-object term worth protecting.

## conversation — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine but shifted sense "conduct, manner of life" (Psalms 37:14, II Corinthians 1:12), not modern "talking" — correct KJV usage, no anachronism; worth a glossing note but not a swap.

## courage — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, no issue (Numbers 13:20, Deuteronomy 31:6-7).

## cruel — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, no issue (Genesis 49:7, Exodus 6:9, Deuteronomy 32:33).

## dress — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine archaic sense "to tend/prepare" (Genesis 2:15 "dress it and keep it," of the garden; 18:7-8, of preparing meat) — not the modern clothing sense; sound throughout.

## familiar — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine technical phrase "familiar spirits" for necromantic practice (Leviticus 19:31, 20:6, 27), sound ancient Near Eastern referent.

## garrison — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary military noun, sound (I Samuel 10:5, 13:3-4, II Samuel 8:6).

## ghost — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine idiom "gave up the ghost" = died (Genesis 25:8, 17; 35:29); per Decision Log #6 this is unrelated to the capitalized "Holy Ghost" divine-title question — sound, lowercase idiom throughout the batch.

## imagination — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine theological vocabulary "imagination of the heart" (Genesis 6:5, 8:21), sound.

## knop — 20 uses
- verdict: WHITELIST
- suggestion: -
- reason: Names a specific bud-shaped ornament on the tabernacle candlestick (Exodus 25:31-36) — a unique architectural/craft term with no substitute; protect alongside "wreath" and "network."

## middle — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective/noun, no issue (Exodus 26:28, Joshua 12:2).

## nail — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, genuine both as a tent-peg (Judges 4:21-22, matching the Sisera narrative's ancient nomadic tent technology) and metal fastener (I Chronicles 22:3); sound.

## openly — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue (Genesis 38:21, II Samuel 6:20).

## pardon — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound theological/legal usage throughout (Exodus 23:21, Numbers 14:19-20).

## sigh — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb/noun, no issue (Isaiah 24:7, Lamentations 1:4, 11).

## simple — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine sense "untaught, naive" (Psalms 19:7, 116:6, 119:130), matches KJV usage exactly; sound.

## sole — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary anatomical noun "sole of the foot" (Genesis 8:9, Deuteronomy 28:35, 56), sound.

## treasury — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary noun, no issue (I Chronicles 9:26, Joshua 6:19, 24).

## troop — 20 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary military/collective noun, sound (Genesis 30:11, 49:19, I Samuel 30:8).

## chase — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Leviticus 26:7-8, 36; Deuteronomy 1:44).

## clear — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective/verb, sound both in the oath-release sense (Genesis 24:8, 41) and comparative brightness sense (Lamentations 4:7).

## consent — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, no issue (Genesis 34:15, 22-23; Acts 8:1).

## corruption — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary abstract noun, sound both literally (Job 17:14, "the worm... my mother") and as the place-name "mount of corruption" (II Kings 23:13, the Mount of Olives desecrated by Solomon's high places); no issue.

## earnestly — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue (Numbers 22:37, I Samuel 20:6, 28).

## large — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adjective, no issue (Genesis 34:21, Exodus 3:8 "a good land and a large").

## oracle — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine dual usage — the technical term for the temple's inner sanctuary/Holy of Holies (I Kings 6:5, 16) and "oracles of God" for scripture (Romans 3:2, Hebrews 5:12); both senses sound and still comprehensible in modern English, so no protection needed beyond ordinary care.

## reserve — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary verb, sound both theologically (Jeremiah 3:5, 50:20) and cultically (Numbers 18:9).

## scourge — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine ancient punishment vocabulary (Job 5:21, 9:23, Matthew 27:26 "scourged Jesus"), sound on both axes.

## secretly — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Ordinary adverb, no issue (Genesis 31:27, Deuteronomy 13:6, 27:24).

## twined — 21 uses
- verdict: KEEP
- suggestion: -
- reason: Genuine tabernacle-textile term "fine twined linen" (Exodus 26:1, 31, 36), describing the real ancient technique of twisting individual threads before weaving; sound on both axes.
