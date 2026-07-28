# Modern-Edition Archaism Review — King James agent, 2026-07-27

*Owner directive 2026-07-27: "Have the king james agent review the modern KJV
output file and find any archaic words that can be modernized (through the
settings file) in the custom folder... Make sure proper names and locations are
not touched."*

Reviewed by the `king-james-middle-english-expert` agent against
`docs/downloads/reconstructed-kjv-in-modern-english.md` (body only; the
Restoration Appendix quotes the 1611-voice readings and is out of scope).
Candidate set: the edition's own 6,640 word types with the 3,602 `word_era`
proper nouns and 1,192 always-capitalized words removed first, so no name or
location could be proposed.

**The agent's report is reproduced verbatim below.** What was actually applied
differs in seven places — every difference is recorded in the roadmap's
Decision Log #23, and the shipped rules live in `custom/site-modern.json`.
In short: `communicated` was dropped as a blanket rule (Gal 2:2 is already
idiomatic modern English), `thenceforth` became *thereafter* rather than
*from then on*, and six phrase keys were added to stop real breakages
(`from thenceforth`, `put asunder`, `communicate unto him`,
`communicated with me`, `give subtilty to the simple`, `naughty figs`).
Three inflections the review missed were added: `afore`, `preventest`,
`subtilly`.

---

# Modernization Review — Reconstructed KJV in Modern English

Reviewed: `docs/downloads/reconstructed-kjv-in-modern-english.md` (body only; Restoration Appendix `- was:`/`- now:` lines ignored per instructions). Candidate set: `modern_vocab.txt` (6,640 word types, proper nouns and always-capitalized words pre-removed).

**Counts:** 22 accepted rules (17 high-confidence, 5 medium-confidence going into the JSON block) · 12 words examined and flagged as **FALSE FRIENDS** (5 with a safe accepted swap already counted above and re-listed here for visibility; 7 with **no safe global swap** because a colliding modern-looking sense also occurs) · 19 words considered and rejected.

---

## 1. Proposed rules

| Archaic word | Modern replacement | Count | POS | Proof verse | Confidence |
|---|---|---|---|---|---|
| beguile | deceive | 2 | v. | 1 Cor 3:18 "Let no man beguile you of your reward…" | high |
| beguiled | deceived | 5 | v. | Gen 3:13 "The serpent beguiled me, and I did eat." | high |
| wroth | angry | 50 | adj. | Gen 4:5-6 "Cain was very wroth… Why are you wroth?" | high |
| affrighted | frightened | 9 | v./adj. | Deut 7:21 "You shall not be affrighted at them…" | high |
| sodden | boiled | 6 | v./adj. | Exod 12:9 "Eat not of it raw, nor sodden at all with water…" | high |
| ensample | example | 3 | n. | 1 Cor 10:11 "these things happened to them for ensamples" (see ensamples) | high |
| ensamples | examples | 3 | n. | Phil 3:17 "you have us for an ensample" / 1 Cor 10:11 | high |
| subtilty | craftiness | 6 | n. | Gen 27:35 "your brother came with subtilty"; 2 Kings 10:19 "Jehu did it in subtilty" | high |
| froward | perverse | 23 | adj. | Ps 18:26 "with the froward you will show yourself contrary"; Prov 6:12 | high |
| mete | measure | 6 | v. | Exod 16:18 "when they did mete it with an omer" | high |
| meted | measured | 3 | v. | Isa 18:2 "a nation meted out and trodden down" | high |
| privily | secretly | 16 | adv. | 1 Sam 24:4 "David... cut off the skirt of Saul's robe privily" | high |
| naughty | wicked | 3 | adj. | 1 Sam 17:28 "the naughtiness of your heart" (see naughtiness); Prov 6:12 "a naughty tongue" | high |
| naughtiness | wickedness | 3 | n. | Ps 7:9 (context of iniquity, "transgressors shall be taken in their own naughtiness") | high |
| carriage | baggage | 3 | n. | 1 Sam 17:22 "David left his carriage in the hand of the keeper of the carriage" | high |
| carriages | baggage | 3 | n. | Isa 46:1 "your carriages were heavily burdened; they are a burden to the weary beast" | high |
| communicate | share | 4 | v. | Gal 6:6 "Let him that is taught... communicate to him that teaches in all good things" | high |
| communicated | shared | 2 | v. | Phil 4:15 "no church communicated with me as concerning giving and receiving" | high |
| presently | immediately | 5 | adv. | Prov 12:16 "A fool's wrath is presently known"; Matt 21:19 "presently the fig tree withered away" | high |
| conversation | conduct | 20 | n. | Ps 50:23 "orders his conversation aright"; Phil 3:20 "our conversation is in heaven" | high |
| aforetime | formerly | 8 | adv. | Neh 13:5 "where aforetime they laid the meat offerings…" | medium |
| heretofore | previously | 8 | adv. | Exod 5:8 "as heretofore: let them go and gather straw for themselves" | medium |
| asunder | apart | 21 | adv. | Ps 2:3 "Let us break their bands asunder"; Matt 19:6 "let not man put asunder" | medium |
| subtil | crafty | 3 | adj. | Gen 3:1 "the serpent was more subtil than any beast of the field" | medium |
| victual | food | 5 | n. | Exod 12:39 "could not stay, neither had they prepared for themselves any victual" | medium |
| victuals | provisions | 17 | n. | Josh 1:11 "Prepare you victuals; for within three days you shall pass over…" | medium |
| hitherto | until now | 19 | adv. | Exod 7:16 "hitherto you would not hear" | medium |
| thenceforth | from then on | 4 | adv. | 2 Chr 32:23 "he was magnified in the sight of all nations from thenceforth" | medium |
| prevent | precede | 8 | v. | Ps 21:3 "you prevent him with the blessings of goodness" | medium |
| prevented | preceded | 9 | v. | Ps 88:13 "the snares of death prevented me" | medium |
| espoused | betrothed | 5 | v./adj. | Matt 1:18 "his mother Mary was espoused to Joseph, before they came together" | medium |

**Note on `prevent`/`prevented`:** one occurrence (2 Sam? — actually 1 Thess 4:15 "shall not prevent them which are asleep") lands in a doctrinally-adjacent verse (the "not precede those who have died" clause about the Lord's return). "Precede"/"preceded" preserves the sense in every occurrence checked; flagging so the owner can spot-check that one.

**Note on `espoused`:** the word covers two degrees of relationship in this corpus — Matt 1:18 is a true betrothal (not yet married), but 2 Sam 3:14 ("my wife Michal, which I espoused to me for an hundred foreskins") describes a bride-price marriage already consummated. "Betrothed" fits the Matthew sense exactly and is close enough in the Samuel sense (the act of taking to wife by pledge) that meaning is not lost, but it is not a perfect one-word fit in both places — medium confidence for that reason.

**Note on `asunder`:** works cleanly as an intensifier after verbs of division/breaking (cut, broken, cleave, part, pluck) in every occurrence checked, including the famous Matt 19:6 "let not man put asunder." A couple of instances read slightly flat ("the ground clung asunder" → "clung apart") but none become ungrammatical or wrong.

---

## 2. FALSE FRIENDS

Words where the *current modern-English reading is plausible but wrong* — the owner's highest-value fix. Split into two groups.

### 2a. False friends with a safe global swap (already in §1 and the JSON block)
- **conversation** = conduct/manner of life, not "talk." Ps 50:23, Phil 3:20, 1 Pet 2:12, etc. — 20 occurrences, all one sense. → `conduct`.
- **communicate/communicated** = share (materially/financially), not "convey information." Gal 6:6, Phil 4:14-15. → `share`/`shared`.
- **presently** = immediately/at once, not "currently, at this time." Prov 12:16, Matt 21:19, Luke 24:53(ish). → `immediately`.
- **carriage/carriages** = baggage/load, not "a wheeled vehicle." 1 Sam 17:22, Isa 10:28, Isa 46:1, Acts 21:15. → `baggage`.
- **prevent/prevented** = go before, precede, not "stop from happening." Ps 21:3, Ps 88:13, Job 3:12, 1 Thess 4:15. → `precede`/`preceded`.
- **naughty/naughtiness** = wicked/wickedness, a serious moral judgment — not "mildly mischievous," the trivializing sense modern readers reach for first. 1 Sam 17:28, Prov 17:4. → `wicked`/`wickedness`.

### 2b. False friends with **NO safe global swap** — flagged for the owner, left untouched
These have a genuine misleading-modern-reading problem, but a second, colliding sense of the *same spelling* also occurs in the body, so a blind find-and-replace would corrupt the verses carrying the other sense. Recommend per-verse handling only (outside the scope of a `GlobalReplacements` rule).

- **suffer** (213 occurrences) — mostly "allow/permit" (Matt 19:14 "Suffer the little children to come to me"; Exod 22:18 "You shall not suffer a sorceress to live") — but a large and doctrinally central minority is the *modern* sense "endure pain," e.g. every Passion prediction: "the Son of man must **suffer** many things… and be slain" (Matt 16:21, Mark 8:31, Luke 24:26). A global swap to "allow" would corrupt the Passion narrative into nonsense. **Do not touch.**
- **quick** (10 occurrences) — mostly "living" (the traditional "quick and the dead," Lev 13:10 "quick raw flesh," Ps 55:15 "go down quick into hell") but Isa 11:3 "make him of **quick** understanding" uses quick in its ordinary modern sense (keen-witted) — replacing that instance would break it. **Do not touch.**
- **meet / meetest** (adj., "fitting/suitable") — Gen 2:18 "an help meet for him," Judg 9:2 "the best and meetest of your master's sons." Both words are heavy homographs of the ordinary verb *to meet* ("the king of Sodom went out to meet him"; "you meetest him that rejoices"), which accounts for the overwhelming majority of the 132/2 occurrences. No regex-safe way to hit only the adjective sense. Also note "help meet" is itself the well-known source of the modern word "helpmeet," which argues for leaving it as a recognizable idiom regardless. **Do not touch.**
- **curious** (12 occurrences) — two unrelated senses: "skillfully made" (Exod 28:8 "the curious apron of the ephod," 8 occurrences, garment/craft context) vs. "meddling, prying" (1 Tim 5:13, 2 Thess 3:11, 1 Pet 4:15 "curious in other men's matters," 4 occurrences) — the opposite of modern "curious" = inquisitive-in-a-good-sense. No single swap serves both. **Do not touch.**
- **abroad** (80 occurrences) — mostly "outward/openly/far and wide" (Gen 11:4 "scattered abroad upon the face of the whole earth," Lev 13:12 "leprosy break out abroad in the skin") rather than modern "in a foreign country." Genuine false-friend risk, but the semantic range needed (widely/far vs. outside/openly vs. in public) varies by verse enough that one replacement word reads wrong somewhere in nearly every batch tried ("outside," "widely," "openly" each fail on different occurrences). **Do not touch**, flagging for owner awareness only.
- **stones** — polysemous between literal rock and the euphemism for testicles (Deut 23:1 "he that is wounded in the stones... shall not enter into the congregation"). No safe global swap (and the literal sense is overwhelmingly dominant at 182 occurrences). **Do not touch.**
- **halt** — polysemous between "waver/hesitate" (1 Kings 18:21 "How long halt you between two opinions?") and "limp" (Ps 38:17 "I am ready to halt"), neither of which is today's dominant sense ("stop"). Only 6 occurrences and two different needed replacements — no single swap. **Do not touch.**
- **meat/meats** — "meat" = food generally (Gen 1:29-30, not necessarily animal flesh) is a real false-friend risk, BUT the phrase **"meat offering"** (the grain/cereal offering, as distinct from the "burnt offering") occurs **199 times** in the body — a fixed liturgical term of art. A blind "meat"→"food" swap would turn "meat offering" into "food offering," erasing a specific technical distinction the text elsewhere carefully keeps (grain vs. animal sacrifice). **Do not touch** without a phrase-level exception for "meat offering(s)," which the owner may want to consider separately as a two-word key.

---

## 3. CONSIDERED AND REJECTED (already modern enough, or structural risk)

- **wealth** — checked all senses in context (Gen 34:29, Deut 8:17, Ruth 2:1, 2 Kings 15:20, 1 Kings 3:11-12): every occurrence found is the literal "riches/goods" sense that matches modern English exactly. The classic false-friend sense ("well-being," as in Ps 73:12) was not found dominating this corpus's samples — no correction needed.
- **let** — 1,508 occurrences, virtually all the ordinary permissive/causative sense ("Let there be light," "Let us..."). The archaic "hinder" sense (Num 22:16 "Let nothing... hinder you") does occur but is rare and already reads with its own word "hinder" nearby; no global rule is safe given the volume of the dominant sense.
- **whereof / whereby / wherein / whereupon / wherewith / wherewithal** and **thereof / thereby / therein / thereupon / therewith** — formal but still current modern English (contracts, official prose); "thereof" alone occurs 907 times. A one-word replacement forces awkward restructuring ("the name thereof" → "the name of it," which is not a whole-word swap and changes the clause). Left as formal register, not archaism.
- **grievous / grievously** — still current modern usage ("grievous bodily harm," "grievous error"); meaning matches directly. Not archaic.
- **exceeding / exceedingly** — dated-sounding intensifier but still understood by any modern reader; leaving alone avoids diluting the King James cadence for no comprehension gain.
- **nevertheless / notwithstanding** — both standard modern English words. Not archaic.
- **marvel / marvelled / marvellous** — "marvelled"/"marvellous" are simply the British spelling of "marveled"/"marvelous" (a spelling variant, not an archaism); "marvel" itself is a live modern word. Not touched.
- **wondrous** — still a recognized (if literary) modern word. Not touched.
- **amazed** — meaning identical to modern usage. Not touched.
- **unclean / uncleanness** — perfectly transparent to a modern reader and arguably borders on ritual/legal terminology (Levitical purity law) worth preserving as-is; not archaic vocabulary in any case.
- **lewd / lewdness** — modern sense (sexual indecency) already matches the KJV usage checked (Ezek 16:27, 23:44); not a false friend here.
- **maimed / stricken (adjective sense, e.g. "stricken in years," "stricken with grief")** — both still current, unambiguous modern words in their adjectival use. (Note: one occurrence, Matt 26:67 "they did spit in his face, and **stricken** him," uses stricken as a finite past-tense verb, which no longer works grammatically in modern English regardless of vocabulary — this is a grammar fossil, not a vocabulary one, and out of scope for a word-swap rule.)
- **issue** — polysemous between "offspring" (a usage still current in modern legal English, "died without issue") and "discharge" (Lev 15, "issue of blood," also still a modern medical-technical word). Both senses remain valid modern English on their own; no correction needed.
- **sore** (adverb, "sore afraid," "pressed sore") — the archaic intensifier sense collides with the very common adjective "sore" (painful, Lev 13 "a sore red spot"). No safe single-word global rule; flagged only as a caution, not proposed.

---

```json
{
  "aforetime": "formerly",
  "affrighted": "frightened",
  "asunder": "apart",
  "beguile": "deceive",
  "beguiled": "deceived",
  "carriage": "baggage",
  "carriages": "baggage",
  "communicate": "share",
  "communicated": "shared",
  "conversation": "conduct",
  "ensample": "example",
  "ensamples": "examples",
  "espoused": "betrothed",
  "froward": "perverse",
  "heretofore": "previously",
  "hitherto": "until now",
  "mete": "measure",
  "meted": "measured",
  "naughtiness": "wickedness",
  "naughty": "wicked",
  "prevent": "precede",
  "prevented": "preceded",
  "presently": "immediately",
  "privily": "secretly",
  "sodden": "boiled",
  "subtil": "crafty",
  "subtilty": "craftiness",
  "thenceforth": "from then on",
  "victual": "food",
  "victuals": "provisions",
  "wroth": "angry"
}
```
