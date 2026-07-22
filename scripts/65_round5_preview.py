#!/usr/bin/env python3
"""65_round5_preview.py — build a was/now PREVIEW of the round-5 rare-word
rulings (references/rare_word_round5_review.md), owner rulings 2026-07-22.
NO DATABASE WRITES.

Round 5 reviewed the 100 rarest lemmas over the current output. Rulings are a
mix of WHITELIST-keeps (no text change; protected via the round-5 section of
rare_word_review_no_safe_swap.md) and revise/swap rulings handled here.

Owner-ruling renderings that needed a grammatical judgment (all flagged in the
preview for the owner's eye):
  - hottest (II Sam 11:15): "delete the word" -> "forefront of the battle".
  - shipping (John 6:24): "revise to leave" -> "they also took leave".
  - straitest (Acts 26:5): "update to straight" -> "most straightest"
    (spelling modernization per scripts/50 strait->straight, double
    superlative kept as in the base text).
  - trimmest (Jer 4:30): "revise to adorned" -> "adornest" (thou-form).
  - unblameable + unreproveable (Col 1:22): both ruled "blameless" — collapsed
    to a single "blameless" to avoid "blameless and blameless".
  - assigned: "appointed to" -> "appointed" ("to" kept only where it fits,
    Genesis 47:22).
  - spitted: Luke 18:32 "spitted on" -> "spit on"; Isaiah 50:6 "shame and
    spitting" left unchanged (no sensible "spit" rendering) — flagged.
  - searchings (Judges 5:16): ruled 'revise to divisions' (2026-07-22) —
    applied, but the doubled 'divisions ... divisions of heart' is flagged.

Output: references/rare_word_round5_apply_preview.md (owner reviews wording,
then a scripts/66 apply step writes the DB + blacklist/whitelist + export).
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "rare_word_round5_apply_preview.md"


def load_current(con):
    resto = {}
    for vid, new in con.execute(
            "SELECT verse_id, proposed_text FROM restorations WHERE status='approved' "
            "AND proposed_text IS NOT NULL ORDER BY id"):
        resto[vid] = new
    names = {i: n for i, n in con.execute(
        "SELECT id, name FROM books WHERE translation='KJV'")}
    cur, base = {}, {}
    for vid, bid, ch, vs, text in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses WHERE translation='KJV'"):
        key = (names[bid], ch, vs)
        base[key] = text
        cur[key] = resto.get(vid, text)
    return cur, base


# ---------------------------------------------------------------------------
# EDIT TABLE.  (book, ch, vs): (kind, payload, note)
#   kind 'replace'  payload = [(old, new), ...] literal, in order
#   kind 'set'      payload = "full text"       -> full verse rewrite
# ---------------------------------------------------------------------------
EDITS = {
    # ---- full rewrite (owner text, envyings + banquetings rulings merged) ---
    ("Galatians", 5, 21): ("set",
        "Envying, murders, drunkenness, gluttonous, and such like: of the "
        "which I tell you before, as I have also told you in time past, that "
        "they which do such things shall not inherit the kingdom of God.",
        "owner rewrite: envyings->envying, banquetings->gluttonous; "
        "whitelist glutton/gluttonous/revilings"),

    # ---- single-word / phrase revises ---------------------------------------
    ("Isaiah", 23, 8): ("replace", [("whose chapmen are", "whose nobles are")],
        "chapmen -> nobles"),
    ("Colossians", 2, 1): ("replace", [("great conflict", "great contention")],
        "conflict -> contention"),
    ("I Chronicles", 18, 10): ("replace", [("to congratulate him", "to greet him")],
        "congratulate -> greet"),
    ("II Peter", 1, 16): ("replace", [("cunningly devised", "subtilly devised")],
        "cunningly -> subtilly"),
    ("Acts", 7, 28): ("replace", [("thou diddest", "thou didst")],
        "diddest -> didst (improper inflection)"),
    ("Psalms", 105, 27): ("replace", [("They displayed among", "They shewed among")],
        "displayed -> shewed"),
    ("Proverbs", 23, 20): ("replace",
        [("riotous eaters of flesh", "riotous gluttons of flesh")],
        "eaters -> gluttons"),
    ("Psalms", 106, 1): ("replace",
        [("for to eternity endureth his mercy", "and his love endureth for ever")],
        "owner phrase swap: 'for to eternity endureth his mercy' -> "
        "'and his love endureth for ever'"),
    ("John", 11, 16): ("replace", [("fellowdisciples", "fellow disciples")],
        "fellowdisciples -> fellow disciples"),
    ("Psalms", 114, 5): ("replace", [("that thou fleddest", "that thou didst flee")],
        "fleddest -> didst flee"),
    ("Galatians", 2, 21): ("replace", [("I do not frustrate", "I do not set aside")],
        "frustrate -> set aside"),
    ("Jeremiah", 2, 36): ("replace", [("Why gaddest thou about", "Why goest thou about")],
        "gaddest -> goest"),
    ("II Kings", 4, 35): ("replace", [("the child gaped seven", "the child sneezed seven")],
        "gaped -> sneezed; whitelist sneezed"),
    ("Matthew", 3, 12): ("replace",
        [("into the garner", "into the storehouse"),
         ("with unquenchable fire", "with everlasting fire")],
        "garner -> storehouse; unquenchable -> everlasting (merged rulings)"),
    ("Lamentations", 5, 9): ("replace", [("We gat our bread", "We got our bread")],
        "gat -> got"),
    ("I Kings", 7, 31): ("replace", [("were gravings with", "were engravings with")],
        "gravings -> engravings"),
    ("Colossians", 2, 16): ("replace", [("an holyday", "an holy day")],
        "holyday -> holy day"),
    ("II Samuel", 11, 15): ("replace",
        [("forefront of the hottest battle", "forefront of the battle")],
        "hottest -> deleted (owner: nonsensical, delete the word)"),
    ("Amos", 8, 3): ("replace", [("shall be howlings", "shall be cryings")],
        "howlings -> cryings"),
    ("Colossians", 3, 5): ("replace", [("inordinate affection", "lust")],
        "'inordinate affection' -> lust"),
    ("Colossians", 2, 18): ("replace",
        [("intruding into those things", "looking into those things"),
         ("vainly puffed up", "foolishly puffed up")],
        "intruding -> looking; vainly -> foolishly (merged rulings)"),
    ("James", 1, 5): ("replace",
        [("all men liberally", "all men freely"),
         ("and upbraideth not", "and rebuketh not")],
        "liberally -> freely; upbraideth -> rebuketh (merged rulings); "
        "whitelist rebuketh"),
    ("II Kings", 19, 23): ("replace", [("into the lodgings of", "into the dwellings of")],
        "lodgings -> dwellings"),
    ("Revelation of John", 2, 13): ("replace",
        [("my faithful martyr", "my faithful witness")],
        "martyr -> witness"),
    ("Colossians", 3, 22): ("replace", [("as menpleasers", "as men pleasers")],
        "menpleasers -> men pleasers; whitelist pleasers"),
    ("Hebrews", 11, 36): ("replace", [("cruel mockings", "cruel scoffings")],
        "mockings -> scoffings; whitelist scoffings"),
    ("Romans", 1, 12): ("replace", [("the mutual faith", "the common faith")],
        "mutual -> common"),
    ("Revelation of John", 18, 22): ("replace",
        [("voice of players", "voice of musicians")],
        "players -> musicians; whitelist musicians"),
    ("Genesis", 8, 11): ("replace", [("branch pluckt off", "branch plucked off")],
        "pluckt -> plucked"),
    ("Philippians", 1, 7): ("replace",
        [("defence and proof of the gospel", "defence and truth of the gospel")],
        "proof -> truth"),
    ("Colossians", 3, 16): ("replace", [("in thee richly", "in thee abundantly")],
        "richly -> abundantly"),
    ("Colossians", 2, 8): ("replace",
        [("the rudiments of the world", "the elements of the world")],
        "rudiments -> elements; whitelist elements"),
    ("Judges", 5, 16): ("replace",
        [("For the divisions of Reuben", "For the tribes of Reuben"),
         ("great searchings of heart", "great divisions of heart")],
        "searchings -> divisions; opening 'divisions of Reuben' -> 'tribes of "
        "Reuben' (owner preview edit 2026-07-22)"),
    ("Nehemiah", 13, 20): ("replace", [("merchants and sellers", "merchants and nobles")],
        "sellers -> nobles"),
    ("John", 6, 24): ("replace", [("also took shipping", "also took leave")],
        "shipping -> leave (owner: revise to leave)"),
    ("Isaiah", 48, 13): ("replace", [("hath spanned the heavens", "hath measured the heavens")],
        "spanned -> measured"),
    ("Acts", 26, 5): ("set",
        "Which knew me from the beginning, if they would testify, that after "
        "the most straight sect of our religion, I lived as a Pharisee.",
        "owner preview rewrite: 'most straight sect ... I lived as a Pharisee'"),
    ("Jeremiah", 4, 30): ("replace",
        [("thou trimmest thee with", "thou adorned thee with")],
        "trimmest -> adorned (owner confirmed 'adorned', not 'adornest')"),
    ("Colossians", 1, 22): ("replace",
        [("holy and unblameable and unreproveable", "holy and blameless")],
        "unblameable + unreproveable both ruled 'blameless' — collapsed to one"),
    ("I Timothy", 6, 17): ("replace", [("in uncertain riches", "in strange riches")],
        "uncertain -> strange"),
    ("Psalms", 56, 8): ("replace", [("tellest my wanderings", "tellest my troubles")],
        "wanderings -> troubles"),
    ("Genesis", 49, 6): ("replace",
        [("in their wantonness they digged", "in their selfwill they digged")],
        "wantonness -> selfwill; whitelist selfwill/selfwilled"),
    ("Genesis", 39, 8): ("replace", [("my master wotteth not", "my master knoweth not")],
        "wotteth -> knoweth"),
    ("Psalms", 106, 6): ("replace",
        [("we have done wrongly", "we have sinned")],
        "owner: replace 'done wrongly' with sinned"),

    # ---- 2-verse lemmas ------------------------------------------------------
    ("II Samuel", 13, 18): ("replace", [("virgins apparelled", "virgins arrayed")],
        "apparelled -> arrayed"),
    ("Luke", 7, 25): ("replace", [("gloriously apparelled", "gloriously arrayed")],
        "apparelled -> arrayed"),
    ("Jeremiah", 27, 9): ("replace", [("to your dreamers", "to your magicians")],
        "dreamers -> magicians"),
    ("Jude", 1, 8): ("replace", [("filthy dreamers", "filthy magicians")],
        "dreamers -> magicians"),
    ("II Corinthians", 12, 20): ("replace", [("debates, envyings,", "debates, envying,")],
        "envyings -> envying"),
    ("Psalms", 66, 17): ("replace", [("he was extolled", "he was magnified")],
        "extolled -> magnified"),
    ("Isaiah", 52, 13): ("replace", [("exalted and extolled", "exalted and magnified")],
        "extolled -> magnified"),
    ("II Corinthians", 7, 5): ("replace", [("without were fightings", "without were contentions")],
        "fightings -> contentions"),
    ("James", 4, 1): ("replace", [("wars and fightings", "wars and contentions")],
        "fightings -> contentions"),
    ("Luke", 18, 32): ("replace", [("and spitted on", "and spit on")],
        "spitted -> spit"),
    ("Isaiah", 50, 6): ("replace", [("shame and spitting", "shame and spit")],
        "spitting -> spit (owner confirmed: 'spit is correct')"),
    ("Job", 36, 29): ("replace", [("the spreadings of the clouds", "the measurings of the clouds")],
        "spreadings -> measurings"),
    ("Job", 37, 16): ("replace", [("the spreadings of the clouds", "the measurings of the clouds")],
        "spreadings -> measurings"),
    ("Matthew", 27, 48): ("replace", [("took a spunge", "took a sponge")],
        "spunge -> sponge"),
    ("Mark", 15, 36): ("replace", [("filled a spunge full", "filled a sponge full")],
        "spunge -> sponge"),
    ("Matthew", 27, 39): ("replace", [("wagging their heads", "shaking their heads")],
        "wagging -> shaking"),
    ("Mark", 15, 29): ("replace", [("wagging their heads", "shaking their heads")],
        "wagging -> shaking"),
    ("II Corinthians", 6, 5): ("replace",
        [("in watchings, in fastings", "in nights without rest, in fastings")],
        "watchings -> 'nights without rest'"),
    ("II Corinthians", 11, 27): ("replace",
        [("in watchings often", "in nights without rest often")],
        "watchings -> 'nights without rest' (phrasing flagged for owner)"),

    # ---- 3-verse lemmas ------------------------------------------------------
    ("Romans", 5, 2): ("replace", [("we have access by faith", "we have entrance by faith")],
        "access -> entrance"),
    ("Ephesians", 2, 18): ("replace", [("have access by one Spirit", "have entrance by one Spirit")],
        "access -> entrance"),
    ("Ephesians", 3, 12): ("replace", [("boldness and access with", "boldness and entrance with")],
        "access -> entrance"),
    ("I Corinthians", 10, 11): ("replace", [("for our admonition", "for our reproof")],
        "admonition -> reproof"),
    ("Ephesians", 6, 4): ("replace", [("instruction and admonition", "instruction and reproof")],
        "admonition -> reproof"),
    ("Titus", 3, 10): ("replace", [("second admonition reject", "second reproof reject")],
        "admonition -> reproof"),
    ("I Kings", 3, 1): ("replace", [("made affinity with", "made an agreement with")],
        "affinity -> 'an agreement'"),
    ("II Chronicles", 18, 1): ("replace", [("joined affinity with", "joined an agreement with")],
        "affinity -> 'an agreement'"),
    ("Ezra", 9, 14): ("replace", [("join in affinity with", "join in agreement with")],
        "affinity -> agreement"),
    ("II Samuel", 18, 25): ("replace", [("he came apace", "he came quickly")],
        "apace -> quickly"),
    ("Psalms", 68, 12): ("replace", [("did flee apace", "did flee quickly")],
        "apace -> quickly"),
    ("Jeremiah", 46, 5): ("replace", [("are fled apace", "are fled quickly")],
        "apace -> quickly"),
    ("Numbers", 16, 32): ("replace",
        [("that appertained unto Korah", "that belonged unto Korah")],
        "appertained -> belonged"),
    ("Numbers", 16, 33): ("replace",
        [("all that appertained to them", "all that belonged to them")],
        "appertained -> belonged"),
    ("Nehemiah", 2, 8): ("replace",
        [("which appertained to the house", "which belonged to the house")],
        "appertained -> belonged"),
    ("Acts", 12, 4): ("replace", [("had apprehended him", "had caught him")],
        "apprehended -> caught"),
    ("Philippians", 3, 12): ("replace", [("I am apprehended of", "I am caught of")],
        "apprehended -> caught"),
    ("Philippians", 3, 13): ("replace", [("to have apprehended", "to have caught")],
        "apprehended -> caught"),
    ("Genesis", 47, 22): ("replace",
        [("a portion assigned them", "a portion appointed to them")],
        "assigned -> 'appointed to' (owner wording)"),
    ("Joshua", 20, 8): ("replace", [("they assigned Bezer", "they appointed Bezer")],
        "assigned -> appointed ('to' does not fit here — flagged)"),
    ("II Samuel", 11, 16): ("replace", [("he assigned Uriah", "he appointed Uriah")],
        "assigned -> appointed ('to' does not fit here — flagged)"),
    ("Exodus", 3, 1): ("replace", [("to the backside of", "to the back side of")],
        "backside -> back side"),
    ("Exodus", 26, 12): ("replace", [("over the backside of", "over the back side of")],
        "backside -> back side"),
    ("Revelation of John", 5, 1): ("replace", [("on the backside,", "on the back side,")],
        "backside -> back side"),
    ("Proverbs", 27, 16): ("replace", [("which bewrayeth itself", "which betrayeth itself")],
        "bewrayeth -> betrayeth; whitelist betrayeth"),
    ("Proverbs", 29, 24): ("replace", [("and bewrayeth it not", "and betrayeth it not")],
        "bewrayeth -> betrayeth"),
    ("Matthew", 26, 73): ("replace", [("speech bewrayeth thee", "speech betrayeth thee")],
        "bewrayeth -> betrayeth"),
}

# Owner answers folded in 2026-07-22 (annotated preview preserved at
# references/rare_word_round5_apply_preview_owner_annotated.md):
#   Judges 5:16 tribes/divisions; Isaiah 50:6 spit; Acts 26:5 owner rewrite;
#   Jeremiah 4:30 'adorned'; John 6:24 'took leave' confirmed;
#   Colossians 1:22 single 'blameless' and Psalms 106:6 'sinned' stand.
OPEN_QUESTIONS = []  # all resolved by the owner's annotated preview


def main():
    con = sqlite3.connect(DB)
    cur, base = load_current(con)
    con.close()

    rows, flags = [], 0
    for ref, (kind, payload, note) in EDITS.items():
        was = cur.get(ref)
        if was is None:
            rows.append((ref, "(verse not found)", "", note, "MISSING-VERSE"))
            flags += 1
            continue
        if kind == "set":
            now, flag = payload, ""
        else:
            now, missing = was, []
            for old, new in payload:
                if old not in now:
                    missing.append(old)
                    continue
                now = now.replace(old, new)
            flag = ("NOT-FOUND: " + "; ".join(missing)) if missing else ""
            if missing:
                flags += 1
        rows.append((ref, was, now, note, flag))

    rows.sort(key=lambda r: (str(r[0][0]), r[0][1], r[0][2]))
    changed = [r for r in rows if r[2] and r[1] != r[2]]

    out = [
        "# Round 5 — Rare Word Review: APPLY PREVIEW (not yet applied)",
        "",
        f"*{len(changed)} verses proposed for change from the owner rulings in "
        "`rare_word_round5_review.md` (2026-07-22). Computed against the ACTUAL "
        "current DB text (base KJV + approved restorations). NO DATABASE WRITES "
        "yet. WHITELIST-keep rulings are protected via the round-5 section of "
        "`rare_word_review_no_safe_swap.md` (no text change, not shown here).*",
        "",
        f"**Flags needing attention: {flags}.**",
        "",
        "## Open questions for the owner",
        "",
    ]
    out += [f"- {q}" for q in OPEN_QUESTIONS]
    out.append("")
    for ref, was, now, note, flag in rows:
        if not (now and was != now):
            continue
        b, c, v = ref
        out.append(f"## {b} {c}:{v}")
        out.append(f"- ruling: {note}")
        if flag:
            out.append(f"- ⚠️ **FLAG:** {flag}")
        out.append(f"- was: {was}")
        out.append(f"- now: {now}")
        out.append("")

    problems = [r for r in rows if r[4]]
    if problems:
        out.append("## ⚠️ Flagged (anchor not found — needs a look)")
        out.append("")
        for ref, was, now, note, flag in problems:
            b, c, v = ref
            out.append(f"- **{b} {c}:{v}** — {flag} — ruling: {note}")
        out.append("")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(changed)} changed verses, {flags} flags")


if __name__ == "__main__":
    main()
