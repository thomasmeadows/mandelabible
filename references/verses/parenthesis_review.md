# Parenthesis / Bracket Review — 2026-07-26

Every verse in the **current restored text** (base KJV + all 7,031
`status='approved'` restorations) that still carries a parenthesis `( )` or a
square bracket `[ ]`. Scanned the whole 31,102-verse text; braces `{ }` and
angle brackets `< >` do not occur at all.

**Only two verses remain.** The global parenthesis/emoticon removal (owner
ruling 2026-07-14, scripts 13/15) swept 221 verses; Romans 1:13 leaked back
because a *later* approved pass rebuilt the verse from the base Oxford text
and reintroduced the parentheses, and I John 2:23 was never in scope because
its markers are square brackets, not parentheses.

Proposals below are from the King James agent
(`.claude/agents/king-james-middle-english-expert.md`). Owner-ruling lines are
left blank.

---

## 1. Romans 1:13 — `(but was let hitherto,)`

**Why it is still here:** restoration `id=3338` (`punctuation`, approved)
already removed these parentheses. Restoration `id=9816`
(`kjvrestore_fold`, approved — the you→thee pass) composed *after* it and was
built from the base text, so it carried the parentheses back in. The exporter
takes the highest-id approved row, so 9816 wins.

### Current restored text
> Now I would not have thee ignorant, brethren, that oftentimes I purposed to
> come unto thee, **(but was let hitherto,)** that I might have some fruit
> among thee also, even as among other Gentiles.

### Comparison editions
- **Standard Oxford Edition (1769 Blayney, base `KJV.db`)** — Now I would not
  have you ignorant, brethren, that oftentimes I purposed to come unto you,
  (but was let hitherto,) that I might have some fruit among you also, even as
  among other Gentiles.
- **Geneva 1599** — Now my brethren, I would that ye should not be ignorant,
  how that I haue oftentimes purposed to come vnto you (but haue bene let
  hitherto) that I might haue some fruite also among you, as I haue among the
  other Gentiles.
- **Tyndale** — I wolde that ye shuld knowe brethre how that I have often tymes
  purposed to come vnto you (but have bene let hitherto) to have some frute
  amonge you as I have amonge other of ye Gentyls.
- **Textus Receptus** — ου θελω δε υμας αγνοειν αδελφοι οτι πολλακις
  προεθεμην ελθειν προς υμας και εκωλυθην αχρι του δευρο ινα καρπον τινα σχω
  και εν υμιν καθως και εν τοις λοιποις εθνεσιν

### King James agent — primary proposal
> Now I would not have thee ignorant, brethren, that oftentimes I purposed to
> come unto thee, but was let hitherto, that I might have some fruit among thee
> also, even as among other Gentiles.

A bare comma pair suffices. The parentheses are printer's apparatus around a
clause that is fully grammatical as a plain coordinate clause — nothing in it
is a true aside, and comma-bounding is standard KJV practice for this kind of
interruption. **Nothing is deleted:** the bracketed matter is genuine text
(και εκωλυθην), not spurious.

- **"but" is kept, not changed to "and."** The Greek καὶ ἐκωλύθην would render
  literally as "and was hindered," but Geneva 1599 and Tyndale *independently*
  both read "but" — unanimous English-witness precedent for turning the Greek
  coordination into a felt contrast.
- **"let" (= hindered) stands.** Both Geneva and Tyndale use it; well attested
  pre-1611, no substitution needed.

### Alternates
1. **Semicolon pair** — "…unto thee; but was let hitherto; that I might have
   some fruit…" — 1611 printing does use semicolons for firmer internal breaks;
   acceptable, but heavier than the short clause needs.
2. **Literal-Greek "and"** — "…unto thee, and was let hitherto, that I might
   have some fruit…" — defensible from bare καί, but unattested in any English
   witness and against unanimous Geneva/Tyndale precedent. Not recommended.

### ⚠ Adjacent finding (separate from the parenthesis fix) — number error
The addressee is **"brethren"** (plural), and the Greek pronouns are
ὑμᾶς/ὑμῖν (plural). Geneva and Tyndale both read "you… among you." The current
restored text says **"thee" three times**, which is singular-familiar and
cannot address "brethren." This looks like the thee/thine pass (restoration
9816) applying a blanket singular substitution without checking the addressee's
number. The King James agent recommends "you"/"your" throughout this verse.
This is a *different* layer from the parenthesis removal and needs its own
ruling.

**If the number error is also ruled on, the verse would read:**
> Now I would not have you ignorant, brethren, that oftentimes I purposed to
> come unto you, but was let hitherto, that I might have some fruit among you
> also, even as among other Gentiles.

**OWNER RULING (parentheses):**
Now I would not have thee ignorant, brethren, that oftentimes I purposed to come unto thee, but was let hitherto, that I might have some fruit among thee also, even as among other Gentiles.

---

## 2. I John 2:23 — `[but]`

**Why it is still here:** square brackets, not parentheses — outside the scope
of the 2026-07-14 sweep, which matched `(` and `)` only. This is the *only*
square bracket in the entire restored text.

### Current restored text (identical to Oxford)
> Whosoever denieth the Son, the same hath not the Father: **[but]** he that
> acknowledgeth the Son hath the Father also.

### Comparison editions
- **Standard Oxford Edition (1769 Blayney, base `KJV.db`)** — Whosoever denieth
  the Son, the same hath not the Father: [but] he that acknowledgeth the Son
  hath the Father also.
- **Geneva 1599** — Whosoeuer denyeth the Sonne, the same hath not the Father.
  *(second clause absent entirely)*
- **Tyndale** — *(row empty in the local database — a coverage gap in the
  epistles, not a variant reading; absence of data, not evidence)*
- **Wycliffe 1382** — So ech that denyeth the sone, hath not the fadir; **but**
  he that knowlechith the sone, hath also the fadir.
- **Textus Receptus** — πας ο αρνουμενος τον υιον ουδε τον πατερα εχει ο
  ομολογων τον υιον και τον πατερα εχει

### King James agent — primary proposal
> Whosoever denieth the Son, the same hath not the Father: but he that
> acknowledgeth the Son hath the Father also.

Drop the brackets, keep the word. The bracket surrounds only the supplied
connective "but" — the clause itself is plainly in the Textus Receptus; the
Greek is simply asyndetic (no conjunction between the two clauses), so the 1611
translators supplied one and flagged the supply.

**Not deleted as out of context:** Wycliffe 1382 independently supplies "but"
here, two centuries before the AV, which shows it is the settled English
rendering of this asyndeton and not a 1611 invention. Geneva's omission of the
whole second clause is a translation-base difference, not evidence the clause
is spurious — and the clause is doctrinally load-bearing Johannine parallelism
("he that hath not… he that hath").

### Alternates
1. **Asyndetic, following the Greek exactly** — "Whosoever denieth the Son, the
   same hath not the Father; he that acknowledgeth the Son hath the Father
   also." Closest to the Greek's own asyndeton; drops the only
   English-witness-attested connective.
2. **Italics instead of brackets** — keep "but" but set it in italics, the
   authentic 1611 convention for translator-supplied words. Preserves the
   "this was supplied" information the brackets carried while satisfying the
   no-brackets ruling — only viable if the project wants to introduce an
   italics markup convention, which it currently does not have.

The agent's primary proposal (plain "but," no brackets, no italics) is the
simplest fit with the 2026-07-14 ruling and matches the treatment of the other
221 already-swept verses.

**OWNER RULING:**
Whosoever denieth the Son, the same hath not the Father: but he that acknowledgeth the Son hath the Father also.
---

## Applying a ruling

Both fixes are new approved rows on the existing verses (composition: the
exporter takes the highest-id approved row per verse), written by a new
numbered migration script per the CLAUDE.md revert/migration pattern —
idempotent, checks current state first. Romans 1:13 in particular must compose
*after* restoration 9816, or the you→thee pass will win again.

Then republish, since the text of the Bible changes:

```bash
python3 scripts/17_export_full.py
python3 scripts/81_publish_site_editions.py
```
