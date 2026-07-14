---
name: corpus-quirks
description: Spelling variants and schema gotchas across KJV.db/Geneva1599.db/Tyndale.db/Wycliffe.db that cause false negatives in naive LIKE searches
metadata:
  type: project
---

- **Book naming uses Roman numerals with a space**, in all four sqlite dbs' `<T>_books.name` column: "I Samuel", "II Samuel", "I Corinthians", "II Corinthians", "I John", "II John", "III John" — NOT "1 Samuel"/"1 Corinthians"/"1 John". A `WHERE name = '1 John'` lookup returns nothing; use "I John".
- **v/u spelling swap in Geneva1599/Wycliffe**: search both forms or you get false negatives.
  - "divers/diverse" → Geneva1599 and Wycliffe spell it "diuers/diuerse". `LIKE '%divers%'` gave 0 hits on both; `LIKE '%diuers%'` gave 44 (Geneva) and 10 (Wycliffe).
  - "heaven" → Geneva1599 spells "heauen".
- **bottle-family spelling**: KJV = "bottle(s)"; Geneva1599 = "bottel(s)"; Wycliffe = "botel(is)"/"botelis". A `LIKE '%bottle%'` search undercounts Geneva (1 vs actual 22) and misses Wycliffe entirely (0 vs actual 20). Search `%bottl%` OR `%bottel%` OR `%botel%` together.
- **Tyndale.db has incomplete OT coverage.** Tyndale's translation project covered the Pentateuch, Jonah, and the NT, but not most of the historical/prophetic/wisdom books. Verse lookups for e.g. Job, Isaiah, Hosea, Amos, 1 Samuel, Jeremiah return an empty string `''` (row exists but text is blank) rather than a missing row — check for blank string, not just "not found."
- Wycliffe's Matthew 6:13 genuinely lacks the Lord's Prayer doxology ("For thine is the kingdom...") — this is NOT an OCR/data gap, it reflects Wycliffe's Vulgate/Latin source text, which follows the Alexandrian-type Greek tradition lacking the doxology, vs. the Byzantine tradition (Tyndale/Geneva/KJV source) which has it. Don't treat a Wycliffe omission as evidence of a missing KJV phrase without checking the specific textual-tradition reason first.
