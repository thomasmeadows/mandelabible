## Difference between colon and semicolon in Early Modern English (EModE)

The core difference: rhetorical vs. grammatical

Modern punctuation is syntactic — marks signal clause structure. EModE punctuation was rhetorical "pointing" — marks scripted breath-length for reading aloud, on a graded scale:

comma < semicolon < colon < period

None of these were tied to conjunctions, clause completeness, or lists. That's why period pointing looks "wrong" by modern rules: it's answering how long do I pause?, not what is the syntactic relation?

The colon

Today it announces (list, explanation, quotation). In 1611 it was simply the second-longest pause, dropped mid-verse wherever the sense wanted a breath — routinely between two unrelated independent clauses:

- Phil 4:4 — "Rejoice in the Lord alway: and again I say, Rejoice." Nothing is being announced; a modern editor would use a comma or a period.
- Ruth 1:16 — "…for whither thou goest, I will go; and where thou lodgest, I will lodge: thy people shall be my people…" Colons and semicolons alternate between parallel clauses with no grammatical logic distinguishing them.

The semicolon

Calibrated to pause-length, not to "exactly one independent-clause boundary." The modern rule is a strict subset of EModE practice. The big divergence: EModE semicolons sit directly before "and"/"or", which modern style forbids.

- Isa 53:5 — "…was upon him; and with his stripes we are healed." Modern: comma before "and."
- Ps 23:1 — "The LORD is my shepherd; I shall not want." This one happens to match modern usage.

1769 Blayney

KJV.db is the 1769 text, already one step lighter than 1611: Blayney thinned semicolons/colons and nudged pointing toward clause-awareness — though not to modern rules (Phil 4:4's colon survives). Genuine 1611 pointing can't be audited locally; no 1611-orthography source is in the repo. The agent flags that as a gap.

Practical rule for restorations

1. Semicolon directly before "and"/"or" — the single most reliable authenticity tell. A restoration that always uses comma-before-conjunction reads too modern.
2. License colons rhetorically — a long mid-verse pause is enough reason; no list required.
3. Don't fragment into short sentences — chain clauses across the whole verse (Ruth 1:16: four clauses, three internal marks, no period).
4. Match the local chapter's pointing density in KJV.db rather than applying a fixed rule.
5. Flag base-text pointing oddities, don't silently fix them. It noted KJV.db Gen 1:2 reads "without form and void;" — no comma after "form," unlike many modern printings.

## Was only a period used in EModE for line terminators?

the period was the dominant terminal mark, but far from the only one. The agent counted verse-final characters across all 31,102 deduplicated verses in KJV.db:

┌────────────────┬────────┬───────┐
│   final char   │ count  │   %   │
├────────────────┼────────┼───────┤
│ . period       │ 24,032 │ 77.3% │
├────────────────┼────────┼───────┤
│ : colon        │ 2,288  │ 7.4%  │
├────────────────┼────────┼───────┤
│ , comma        │ 1,599  │ 5.1%  │
├────────────────┼────────┼───────┤
│ ? question     │ 1,594  │ 5.1%  │
├────────────────┼────────┼───────┤
│ ; semicolon    │ 1,332  │ 4.3%  │
├────────────────┼────────┼───────┤
│ ! exclamation  │ 139    │ 0.4%  │
├────────────────┼────────┼───────┤
│ ) paren        │ 111    │ 0.4%  │
├────────────────┼────────┼───────┤
│ no punctuation │ 7      │ 0.02% │
└────────────────┴────────┴───────┘

Roughly 23% of verses end on something other than a period.

Both ? and ! were fully in use in 1611 — the "note of interrogation" and the "note of admiration." E.g. Gen 3:9 "Where art thou?"; Gen 17:18 "O that Ishmael might live before thee!"

Colons and semicolons routinely end verses mid-sentence (11.7% combined) — Gen 1:14 ends "...and for days, and years:" with the grammatical sentence completing verses later. Verse-division and sentence-division were independent systems to a 1611 compositor. Seven verses end with no mark at all (e.g. Gen 23:17 "...were made sure", Ps 98:8 "...let the hills be joyful together").

Marks that differ from modern practice:
- Terminal punctuation inside the closing paren — Gen 49:24 "...the stone of Israel:)" where modern style puts it outside. DB-verifiable.
- Pilcrow ¶ — used in the 1611 printing for paragraph divisions; stripped long before 1769, absent from KJV.db. Knowledge, not verifiable here.
- Virgule / and double-hyphen at line-break — typesetting-era conventions invisible in a continuous-string database.
- It flagged the "? doing double duty for exclamations" claim as low confidence — by 1611 English printing had already separated the two marks.

Caveat it repeated: these are 1769 rates. Blayney lightened 1611's heavier pointing, so the true 1611 verse-final colon/semicolon rate was likely higher. Closing that gap needs an external 1611 facsimile the project doesn't hold.