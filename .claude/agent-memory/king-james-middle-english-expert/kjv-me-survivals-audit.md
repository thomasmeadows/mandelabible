---
name: kjv-me-survivals-audit
description: Genuine Middle English word-form survivals found sitting in the current KJV text (as opposed to homographs/spelling coincidences), with corpus evidence
metadata:
  type: project
---

- **2026-07-20 audit** (owner question: does the KJV itself contain true Middle
  English holdovers, distinct from the 203-form Wycliffe→KJV mapping in
  `references/middle_english_to_early_modern.md`, which only found coincidental
  homographs). Method: a word only counts as a genuine ME survival if it is (a)
  the KJV's actual word at that verse, (b) Wycliffe's dominant/live word for the
  concept (not a one-off), and (c) absent from BOTH Tyndale.db and Geneva1599.db
  everywhere in their corpora — presence in either witness, even at a different
  verse, proves the word was still live c. 1526/1599 and disqualifies it.
- **Strongest finding: "leasing" (Psalm 4:2, Psalm 5:6, only 2 KJV occurrences).**
  Continues Wycliffe's "leesyng/leesing" (609 occurrences total in Wycliffe.db —
  Wycliffe's ordinary word for "lie/falsehood," from OE lēasung). The Middle
  English Reader glossary itself lists it as an OE-derived ME headword (line
  37624 of `references/Understand Middle English - A middle English Reader.txt`).
  Zero occurrences anywhere in Tyndale.db or Geneva1599.db. Decisive: Geneva 1599
  translates the identical Hebrew (kazab) at these exact two verses as "lyes,"
  not "leasing" — proof the Geneva translators, the KJV's own primary working
  text, had already moved past this word. Proposed EModE replacement: "lies"
  (204 KJV occurrences, well-attested, matches Geneva's actual reading at both
  verses). Not found in King James's own Essayes (weak evidence, short corpus).
- **Borderline, considered but NOT flagged** (checked, insufficient/contrary
  evidence): "champaign" (Deut 11:30 — attested contemporary EModE via
  Shakespeare's King Lear c.1605, Geneva's different word "plaine" is a
  translation-preference not an era gap; Tyndale blank there is a known
  coverage gap not evidence); "tabering" (Nahum 2:7 — no Wycliffe cognate found
  to compare against, Geneva paraphrases around it, Tyndale doesn't cover Nahum
  — a true "missing check," not a ruling); "neesings" (Job 41:18 — Wycliffe's
  parallel-passage word is "fnesynge" from OE fnēosan, a genuinely DIFFERENT
  native word from neese/neeze < ON hnjósa that KJV's "neesings" derives from —
  not the same lexical item carried over, so this is EModE dialectal choice, not
  a ME holdover).
- **Cleared as genuine EModE** (found attested in Tyndale.db and/or
  Geneva1599.db somewhere in their corpus, therefore NOT Middle English
  holdovers regardless of how archaic-sounding): gat, trow, occupied, sith,
  afore, clouted, chapmen, wimples, listeth, ensample.
- Full write-up delivered to `/home/t/.claude/jobs/f8f1876a/tmp/kjv_me_survivals.txt`
  (2026-07-20) — re-run the Tyndale/Geneva/Wycliffe regex checks before reusing
  any of these rulings; they depend on the read-only sub-repo files staying as
  they are.
