#!/usr/bin/env python3
"""71_round6_preview.py — build a was/now PREVIEW of the round-6 rare-word
rulings (references/rounds/round6/rare_word_round6_review.md), owner rulings 2026-07-26.
NO DATABASE WRITES.

Round 6 reviewed the 100 rarest lemmas over the current output. Rulings are a
mix of WHITELIST-keeps (no text change; not touched here — protect via a
future round-6 section of rare_word_review_no_safe_swap.md) and revise/swap
rulings handled here. 38 words were ruled WHITELIST and skipped: bittern,
blessedness, blush, bushel, buttocks, carrieth, cassia, champion, chancellor,
clapped, clovenfooted, coffer, coffin, copulation, crumbs, dagger, drieth,
dulcimer, dwellers, eighty, embalmed, expressly, fare, fearfulness, flagons,
flatteries, forbare, foremost, forgettest, fourfooted, fray, freewoman,
handmaidens, harmless, hen, heresies, houghed, hundredth.

Owner-ruling renderings that needed a grammatical judgment (flagged in notes
for the owner's eye, applied literally to the owner's own wording):
  - disannulled: mixed forms (disannulled/disannulleth/disannulling) rendered
    "broken"/"breaketh"/"breaking" to fit each verse's own inflection, per
    owner's "broken or hath broken" latitude.
  - dismissed / disorderly: "departed"/"astray" produce awkward transitive
    readings at II Chronicles 23:8, II Thessalonians 3:7 — applied literally,
    flagged.
  - dissension (Acts 15:2): "dissension and contention" -> "contention and
    contention" reads as a doubled word — applied literally, flagged.
  - dissembled: owner ruling "defiled god" applied literally at all three
    occurrences though the resulting sense is unusual — flagged for owner
    review.
  - dromedaries (Esther 8:10): "young dromedaries" -> "young fast camels"
    reads oddly — applied literally, flagged.
  - errand / II Kings 9:5: "an errand" -> "a message" (article fixed);
    Genesis 24:33 "mine errand" -> "my message" (article fixed).
  - govern: owner's "ruleth" is a 3rd-person -eth form; applied literally at
    all three verses even where the subject is "thou" or an implied 2nd
    person ("Dost thou now ruleth", "and ruleth the nations") — flagged.
  - glorieth: owner's "gives"/"gives glory" applied to the headword only,
    producing "him that gives glory, let him glory in the Lord" — kept
    Paul's own second "glory" untouched per the owner's wording.
  - haunt (I Samuel 30:31): "wont to haunt" -> "wont to dwells" is a
    subject-verb mismatch — applied literally, flagged.
  - hay: Proverbs 27:25 and Isaiah 15:6 already contain "grass" elsewhere in
    the verse; swapping "hay"->"grass" doubles the word — applied literally,
    flagged.
  - eloquent / enchanter (Isaiah 3:3): both entries name the same verse and
    the same owner rewrite text; merged into one "set" edit.

Output: references/rounds/round6/rare_word_round6_apply_preview.md (owner reviews wording,
then a future apply step writes the DB + blacklist/whitelist + export).
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mandela.db"
OUT = ROOT / "references" / "rounds" / "round6" / "rare_word_round6_apply_preview.md"


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
    # ---- birthday: revise to birth day -------------------------------------
    ("Genesis", 40, 20): ("replace", [("Pharaoh’s birthday", "Pharaoh’s birth day")],
        "birthday -> birth day"),
    ("Matthew", 14, 6): ("replace", [("Herod’s birthday", "Herod’s birth day")],
        "birthday -> birth day"),
    ("Mark", 6, 21): ("replace", [("on his birthday", "on his birth day")],
        "birthday -> birth day"),

    # ---- bountiful: revise to noble -----------------------------------------
    ("Proverbs", 22, 9): ("replace", [("a bountiful eye", "a noble eye")],
        "bountiful -> noble"),
    ("Isaiah", 32, 5): ("replace", [("to be bountiful", "to be noble")],
        "bountiful -> noble"),
    ("Luke", 22, 25): ("replace", [("are called bountiful", "are called noble")],
        "bountiful -> noble"),

    # ---- brickkiln: revise to "brick furnaces" -------------------------------
    ("II Samuel", 12, 31): ("replace",
        [("through the brickkiln", "through the brick furnaces")],
        "brickkiln -> brick furnaces"),
    ("Jeremiah", 43, 9): ("replace",
        [("in the brickkiln", "in the brick furnaces")],
        "brickkiln -> brick furnaces"),
    ("Nahum", 3, 14): ("replace",
        [("make strong the brickkiln", "make strong the brick furnaces")],
        "brickkiln -> brick furnaces"),

    # ---- buffeted: replace with stricken -------------------------------------
    ("Matthew", 26, 67): ("replace", [("and buffeted him", "and stricken him")],
        "buffeted -> stricken"),
    ("I Corinthians", 4, 11): ("replace", [("and are buffeted", "and are stricken")],
        "buffeted -> stricken"),
    ("I Peter", 2, 20): ("replace", [("ye be buffeted", "ye be stricken")],
        "buffeted -> stricken"),

    # ---- bunches: revise to heaps ---------------------------------------------
    ("II Samuel", 16, 1): ("replace",
        [("an hundred bunches of raisins", "an hundred heaps of raisins")],
        "bunches -> heaps"),
    ("I Chronicles", 12, 40): ("replace",
        [("bunches of raisins", "heaps of raisins")],
        "bunches -> heaps"),
    ("Isaiah", 30, 6): ("replace",
        [("the bunches of camels", "the heaps of camels")],
        "bunches -> heaps"),

    # ---- carelessly: revise to without fear ------------------------------------
    ("Isaiah", 47, 8): ("replace",
        [("that dwellest carelessly", "that dwellest without fear")],
        "carelessly -> without fear"),
    ("Ezekiel", 39, 6): ("replace",
        [("dwell carelessly", "dwell without fear")],
        "carelessly -> without fear"),
    ("Zephaniah", 2, 15): ("replace",
        [("that dwelt carelessly", "that dwelt without fear")],
        "carelessly -> without fear"),

    # ---- celebrate: revise to keep ----------------------------------------------
    ("Leviticus", 23, 32): ("replace",
        [("shall ye celebrate your sabbath", "shall ye keep your sabbath")],
        "celebrate -> keep"),
    ("Leviticus", 23, 41): ("replace",
        [("ye shall celebrate it", "ye shall keep it")],
        "celebrate -> keep"),
    ("Isaiah", 38, 18): ("replace",
        [("death can not celebrate thee", "death can not keep thee")],
        "celebrate -> keep"),

    # ---- cheerful: revise to joyful ----------------------------------------------
    ("Proverbs", 15, 13): ("replace",
        [("a cheerful countenance", "a joyful countenance")],
        "cheerful -> joyful"),
    ("Zechariah", 8, 19): ("replace",
        [("and cheerful feasts", "and joyful feasts")],
        "cheerful -> joyful"),
    ("Zechariah", 9, 17): ("replace",
        [("the young men cheerful", "the young men joyful")],
        "cheerful -> joyful"),

    # ---- chiefly: replace with especially -----------------------------------------
    ("Romans", 3, 2): ("replace",
        [("chiefly, because", "especially, because")],
        "chiefly -> especially"),
    ("Philippians", 4, 22): ("replace",
        [("chiefly they that are", "especially they that are")],
        "chiefly -> especially"),
    ("II Peter", 2, 10): ("replace",
        [("But chiefly them that walk", "But especially them that walk")],
        "chiefly -> especially"),

    # ---- collection: revise to gathering -------------------------------------------
    ("II Chronicles", 24, 6): ("replace",
        [("out of Jerusalem the collection,", "out of Jerusalem the gathering,")],
        "collection -> gathering"),
    ("II Chronicles", 24, 9): ("replace",
        [("the collection that Moses", "the gathering that Moses")],
        "collection -> gathering"),
    ("I Corinthians", 16, 1): ("replace",
        [("concerning the collection for the saints", "concerning the gathering for the saints")],
        "collection -> gathering"),

    # ---- complete: irregular per-verse ------------------------------------------------
    ("Leviticus", 23, 15): ("replace",
        [("seven sabbaths shall be complete", "seven sabbaths shall be perfect")],
        "complete -> perfect (owner ruling)"),
    ("Colossians", 2, 10): ("replace",
        [("And ye are complete in him", "And ye are made whole in him")],
        "complete -> made whole (owner ruling)"),
    ("Colossians", 4, 12): ("set",
        "Epaphras, who is one of you, a servant of Christ, greeteth you, "
        "always labouring earnestly for you in prayers, that ye may stand "
        "perfect in the will of God.",
        "owner full rewrite of Colossians 4:12 (complete ruling)"),

    # ---- comprehended: revise to understood ------------------------------------------
    ("Isaiah", 40, 12): ("replace",
        [("and comprehended the dust", "and understood the dust")],
        "comprehended -> understood"),
    ("John", 1, 5): ("replace",
        [("the darkness comprehended it not", "the darkness understood it not")],
        "comprehended -> understood"),
    ("Romans", 13, 9): ("replace",
        [("it is wholly comprehended in this saying", "it is wholly understood in this saying")],
        "comprehended -> understood"),

    # ---- conception: revise to birth pain --------------------------------------------
    ("Genesis", 3, 16): ("replace",
        [("thy sorrow and thy conception", "thy sorrow and thy birth pain")],
        "conception -> birth pain"),
    ("Ruth", 4, 13): ("replace",
        [("the Lord gave her conception", "the Lord gave her birth pain")],
        "conception -> birth pain"),
    ("Hosea", 9, 11): ("replace",
        [("and from the conception", "and from the birth pain")],
        "conception -> birth pain"),

    # ---- concupiscence: revise to covetous desire ------------------------------------
    ("Romans", 7, 8): ("replace",
        [("all manner of concupiscence", "all manner of covetous desire")],
        "concupiscence -> covetous desire"),
    ("Colossians", 3, 5): ("replace",
        [("evil concupiscence", "evil covetous desire")],
        "concupiscence -> covetous desire"),
    ("I Thessalonians", 4, 5): ("replace",
        [("the lust of concupiscence", "the lust of covetous desire")],
        "concupiscence -> covetous desire"),

    # ---- confederacy: revise to conspiracy -------------------------------------------
    ("Isaiah", 8, 12): ("replace",
        [("Say ye not, A confederacy, to all them to whom this people shall say, A confederacy;",
          "Say ye not, A conspiracy, to all them to whom this people shall say, A conspiracy;")],
        "confederacy -> conspiracy (both instances)"),
    ("Obadiah", 1, 7): ("replace",
        [("All the men of thy confederacy", "All the men of thy conspiracy")],
        "confederacy -> conspiracy"),

    # ---- confederate: revise to "in conspiracy" --------------------------------------
    ("Genesis", 14, 13): ("replace",
        [("these were confederate with Abram", "these were in conspiracy with Abram")],
        "confederate -> in conspiracy"),
    ("Psalms", 83, 5): ("replace",
        [("they are confederate against thee", "they are in conspiracy against thee")],
        "confederate -> in conspiracy"),
    ("Isaiah", 7, 2): ("replace",
        [("Syria is confederate with Ephraim", "Syria is in conspiracy with Ephraim")],
        "confederate -> in conspiracy"),

    # ---- constantly: revise to continually -------------------------------------------
    ("Proverbs", 21, 28): ("replace",
        [("speaketh constantly", "speaketh continually")],
        "constantly -> continually"),
    ("Acts", 12, 15): ("replace",
        [("she constantly affirmed", "she continually affirmed")],
        "constantly -> continually"),
    ("Titus", 3, 8): ("replace",
        [("thou affirm constantly", "thou affirm continually")],
        "constantly -> continually"),

    # ---- contrariwise: revise to otherwise -------------------------------------------
    ("II Corinthians", 2, 7): ("replace",
        [("So that contrariwise ye ought", "So that otherwise ye ought")],
        "contrariwise -> otherwise"),
    ("Galatians", 2, 7): ("replace",
        [("But contrariwise, when they saw", "But otherwise, when they saw")],
        "contrariwise -> otherwise"),
    ("I Peter", 3, 9): ("replace",
        [("but contrariwise blessing", "but otherwise blessing")],
        "contrariwise -> otherwise"),

    # ---- crib: revise to "feeding trough" --------------------------------------------
    ("Job", 39, 9): ("replace",
        [("abide by thy crib", "abide by thy feeding trough")],
        "crib -> feeding trough"),
    ("Proverbs", 14, 4): ("replace",
        [("the crib is clean", "the feeding trough is clean")],
        "crib -> feeding trough"),
    ("Isaiah", 1, 3): ("replace",
        [("his master’s crib", "his master’s feeding trough")],
        "crib -> feeding trough"),

    # ---- damned: revise to condemned ------------------------------------------------
    ("Mark", 16, 16): ("replace",
        [("shall be damned", "shall be condemned")],
        "damned -> condemned"),
    ("Romans", 14, 23): ("replace",
        [("is damned if he eat", "is condemned if he eat")],
        "damned -> condemned"),
    ("II Thessalonians", 2, 12): ("replace",
        [("That they all might be damned", "That they all might be condemned")],
        "damned -> condemned"),

    # ---- deacons: revise to servants, Philippians 1:1 full rewrite ------------------
    ("Philippians", 1, 1): ("set",
        "Paul and Timothy, the servants of Jesus Christ, to all the saints "
        "in Christ Jesus which are at Philippi,",
        "owner full rewrite (deacons ruling): drops 'with the bishops and deacons'"),
    ("I Timothy", 3, 8): ("replace",
        [("Likewise must the deacons be grave", "Likewise must the servants be grave")],
        "deacons -> servants"),
    ("I Timothy", 3, 12): ("replace",
        [("Let the deacons be the husbands", "Let the servants be the husbands")],
        "deacons -> servants"),

    # ---- decayeth: revise to departeth -----------------------------------------------
    ("Job", 14, 11): ("replace",
        [("the flood decayeth and drieth up", "the flood departeth and drieth up")],
        "decayeth -> departeth"),
    ("Ecclesiastes", 10, 18): ("replace",
        [("the building decayeth", "the building departeth")],
        "decayeth -> departeth"),
    ("Hebrews", 8, 13): ("replace",
        [("that which decayeth and waxeth old", "that which departeth and waxeth old")],
        "decayeth -> departeth"),

    # ---- deeply: revise to greatly ---------------------------------------------------
    ("Isaiah", 31, 6): ("replace",
        [("have deeply revolted", "have greatly revolted")],
        "deeply -> greatly"),
    ("Hosea", 9, 9): ("replace",
        [("have deeply corrupted themselves", "have greatly corrupted themselves")],
        "deeply -> greatly"),
    ("Mark", 8, 12): ("replace",
        [("he sighed deeply in his spirit", "he sighed greatly in his spirit")],
        "deeply -> greatly"),

    # ---- deprived: revise to denied ---------------------------------------------------
    ("Genesis", 27, 45): ("replace",
        [("why should I be deprived also", "why should I be denied also")],
        "deprived -> denied"),
    ("Job", 39, 17): ("replace",
        [("God hath deprived her of wisdom", "God hath denied her of wisdom")],
        "deprived -> denied"),
    ("Isaiah", 38, 10): ("replace",
        [("I am deprived of the residue", "I am denied of the residue")],
        "deprived -> denied"),

    # ---- descent: irregular per-verse --------------------------------------------------
    ("Hebrews", 7, 3): ("replace",
        [("without descent,", "without children,")],
        "descent -> children (owner ruling; grammar as given)"),
    ("Hebrews", 7, 6): ("replace",
        [("whose descent is not counted", "whose children is not counted")],
        "descent -> children (owner ruling; 'is' left as printed, grammar flagged)"),
    ("Luke", 19, 37): ("replace",
        [("at the descent of the mount of Olives", "at the path down the mount of Olives")],
        "descent of -> path down, following 'of' removed (owner ruling)"),

    # ---- despiteful: revise to wicked ---------------------------------------------------
    ("Ezekiel", 25, 15): ("replace",
        [("with a despiteful heart", "with a wicked heart")],
        "despiteful -> wicked"),
    ("Ezekiel", 36, 5): ("replace",
        [("with despiteful minds", "with wicked minds")],
        "despiteful -> wicked"),
    ("Romans", 1, 30): ("replace",
        [("despiteful, proud", "wicked, proud")],
        "despiteful -> wicked"),

    # ---- dirt: replace with dust ----------------------------------------------------------
    ("Judges", 3, 22): ("replace",
        [("and the dirt came out", "and the dust came out")],
        "dirt -> dust (more common in KJV)"),
    ("Psalms", 18, 42): ("replace",
        [("as the dirt in the streets", "as the dust in the streets")],
        "dirt -> dust"),
    ("Isaiah", 57, 20): ("replace",
        [("cast up mire and dirt", "cast up mire and dust")],
        "dirt -> dust"),

    # ---- disannul: replace with break -------------------------------------------------------
    ("Job", 40, 8): ("replace",
        [("Wilt thou also disannul my judgment", "Wilt thou also break my judgment")],
        "disannul -> break"),
    ("Isaiah", 14, 27): ("replace",
        [("who shall disannul it", "who shall break it")],
        "disannul -> break"),
    ("Galatians", 3, 17): ("replace",
        [("years after, cannot disannul,", "years after, cannot break,")],
        "disannul -> break"),

    # ---- disannulled: replace with broken/breaketh/breaking per inflection -----------------
    ("Isaiah", 28, 18): ("replace",
        [("shall be disannulled", "shall be broken")],
        "disannulled -> broken"),
    ("Galatians", 3, 15): ("replace",
        [("no man disannulleth,", "no man breaketh,")],
        "disannulleth -> breaketh (present-tense inflection kept to fit; owner "
        "offered 'broken or hath broken')"),
    ("Hebrews", 7, 18): ("replace",
        [("a disannulling of the commandment", "a breaking of the commandment")],
        "disannulling -> breaking"),

    # ---- discreet: replace with temperate ----------------------------------------------------
    ("Genesis", 41, 33): ("replace",
        [("a man discreet and wise", "a man temperate and wise")],
        "discreet -> temperate"),
    ("Genesis", 41, 39): ("replace",
        [("none so discreet and wise", "none so temperate and wise")],
        "discreet -> temperate"),
    ("Titus", 2, 5): ("replace",
        [("To be discreet, chaste", "To be temperate, chaste")],
        "discreet -> temperate"),

    # ---- dismissed: replace with departed ----------------------------------------------------
    ("II Chronicles", 23, 8): ("replace",
        [("Jehoiada the priest dismissed not the courses", "Jehoiada the priest departed not the courses")],
        "dismissed -> departed (owner ruling; transitive reading awkward, flagged)"),
    ("Acts", 15, 30): ("replace",
        [("So when they were dismissed", "So when they were departed")],
        "dismissed -> departed"),
    ("Acts", 19, 41): ("replace",
        [("he dismissed the assembly", "he departed the assembly")],
        "dismissed -> departed (owner ruling; transitive reading awkward, flagged)"),

    # ---- disorderly: replace with astray -----------------------------------------------------
    ("II Thessalonians", 3, 6): ("replace",
        [("that walketh disorderly", "that walketh astray")],
        "disorderly -> astray"),
    ("II Thessalonians", 3, 7): ("replace",
        [("we behaved not ourselves disorderly", "we behaved not ourselves astray")],
        "disorderly -> astray (owner ruling; reading awkward, flagged)"),
    ("II Thessalonians", 3, 11): ("replace",
        [("which walk among you disorderly", "which walk among you astray")],
        "disorderly -> astray"),

    # ---- dissembled: Revise to "defiled god" (owner ruling, applied literally) --------------
    ("Joshua", 7, 11): ("replace",
        [("and dissembled also,", "and defiled god also,")],
        "dissembled -> defiled god (owner ruling; sense unusual, flagged for owner review)"),
    ("Jeremiah", 42, 20): ("replace",
        [("For ye dissembled in your hearts", "For ye defiled god in your hearts")],
        "dissembled -> defiled god (owner ruling; sense unusual, flagged for owner review)"),
    ("Galatians", 2, 13): ("replace",
        [("the other Jews dissembled likewise", "the other Jews defiled god likewise")],
        "dissembled -> defiled god (owner ruling; sense unusual, flagged for owner review)"),

    # ---- dissension: replace with contention --------------------------------------------------
    ("Acts", 15, 2): ("replace",
        [("no small dissension and contention with them", "no small contention and contention with them")],
        "dissension -> contention (owner ruling; verse already reads 'contention', "
        "resulting doubled word flagged for owner review)"),
    ("Acts", 23, 7): ("replace",
        [("there arose a dissension between", "there arose a contention between")],
        "dissension -> contention"),
    ("Acts", 23, 10): ("replace",
        [("there arose a great dissension", "there arose a great contention")],
        "dissension -> contention"),

    # ---- diversities: replace "diversities of" with "diverse" --------------------------------
    ("I Corinthians", 12, 4): ("replace",
        [("there are diversities of gifts", "there are diverse gifts")],
        "'diversities of' -> diverse"),
    ("I Corinthians", 12, 6): ("replace",
        [("there are diversities of operations", "there are diverse operations")],
        "'diversities of' -> diverse"),
    ("I Corinthians", 12, 28): ("replace",
        [("diversities of tongues", "diverse tongues")],
        "'diversities of' -> diverse"),

    # ---- drawers: revise to porters -------------------------------------------------------------
    ("Joshua", 9, 21): ("replace",
        [("and drawers of water unto all the congregation", "and porters of water unto all the congregation")],
        "drawers -> porters"),
    ("Joshua", 9, 23): ("replace",
        [("and drawers of water for the house", "and porters of water for the house")],
        "drawers -> porters"),
    ("Joshua", 9, 27): ("replace",
        [("and drawers of water for the congregation", "and porters of water for the congregation")],
        "drawers -> porters"),

    # ---- dregs: replace with last ------------------------------------------------------------------
    ("Psalms", 75, 8): ("replace",
        [("but the dregs thereof", "but the last thereof")],
        "dregs -> last"),
    ("Isaiah", 51, 17): ("replace",
        [("thou hast drunken the dregs of the cup", "thou hast drunken the last of the cup")],
        "dregs -> last"),
    ("Isaiah", 51, 22): ("replace",
        [("even the dregs of the cup of my fury", "even the last of the cup of my fury")],
        "dregs -> last"),

    # ---- dromedaries: replace with fast camels ------------------------------------------------------
    ("I Kings", 4, 28): ("replace",
        [("for the horses and dromedaries", "for the horses and fast camels")],
        "dromedaries -> fast camels"),
    ("Esther", 8, 10): ("replace",
        [("camels, and young dromedaries", "camels, and young fast camels")],
        "dromedaries -> fast camels (owner ruling; 'young fast camels' reads "
        "oddly, flagged)"),
    ("Isaiah", 60, 6): ("replace",
        [("the dromedaries of Midian", "the fast camels of Midian")],
        "dromedaries -> fast camels"),

    # ---- eloquent + enchanter: Isaiah 3:3 shared full rewrite; other verses ---------------------
    ("Exodus", 4, 10): ("replace",
        [("I am not eloquent,", "I am not noble,")],
        "eloquent -> noble"),
    ("Isaiah", 3, 3): ("set",
        "The captain of fifty, and the honourable man, and the counsellor, "
        "and the cunning workman, and the noble sorcerer.",
        "owner full rewrite of Isaiah 3:3 — shared ruling from both the "
        "'eloquent' and 'enchanter' entries (same verse, same owner text)"),
    ("Acts", 18, 24): ("replace",
        [("an eloquent man", "a noble man")],
        "eloquent -> noble; article 'an' -> 'a' per owner ruling"),
    ("Daniel", 2, 10): ("set",
        "The Chaldeans answered before the king, and said, There is not a "
        "man upon the earth that can shew the king's matter: therefore "
        "there is no king, lord, nor ruler, that asked such things at any "
        "sorcerer, or soothsayer, or Chaldean.",
        "owner full rewrite of Daniel 2:10 (enchanter ruling)"),

    # ---- enjoined: replace with joined -----------------------------------------------------------------
    ("Esther", 9, 31): ("replace",
        [("Esther the queen had enjoined them", "Esther the queen had joined them")],
        "enjoined -> joined"),
    ("Job", 36, 23): ("replace",
        [("Who hath enjoined him his way", "Who hath joined him his way")],
        "enjoined -> joined"),
    ("Hebrews", 9, 20): ("replace",
        [("which God hath enjoined unto you", "which God hath joined unto you")],
        "enjoined -> joined"),

    # ---- errand: replace with message ------------------------------------------------------------------
    ("Genesis", 24, 33): ("replace",
        [("until I have told mine errand", "until I have told my message")],
        "errand -> message; article 'mine' -> 'my' per period usage"),
    ("Judges", 3, 19): ("replace",
        [("I have a secret errand unto thee", "I have a secret message unto thee")],
        "errand -> message"),
    ("II Kings", 9, 5): ("replace",
        [("I have an errand to thee", "I have a message to thee")],
        "errand -> message; article 'an' -> 'a'"),

    # ---- event: revise to affair -----------------------------------------------------------------------
    ("Ecclesiastes", 2, 14): ("replace",
        [("that one event happeneth to them all", "that one affair happeneth to them all")],
        "event -> affair"),
    ("Ecclesiastes", 9, 2): ("replace",
        [("there is one event to the righteous", "there is one affair to the righteous")],
        "event -> affair"),
    ("Ecclesiastes", 9, 3): ("replace",
        [("that there is one event unto all", "that there is one affair unto all")],
        "event -> affair"),

    # ---- exchangers: revise to "money changers" -----------------------------------------------------------
    ("Luke", 19, 23): ("replace",
        [("my money to the exchangers", "my money to the money changers")],
        "exchangers -> money changers"),
    ("John", 2, 14): ("replace",
        [("the exchangers of money sitting", "the money changers sitting")],
        "'exchangers of money' -> money changers"),
    ("John", 2, 15): ("replace",
        [("poured out the exchangers' money", "poured out the money changers' money")],
        "exchangers' -> money changers'"),

    # ---- fallow: irregular ----------------------------------------------------------------------------------
    ("Deuteronomy", 14, 5): ("set",
        "The red deer, and the roe buck, and the spotted deer, and the wild "
        "goat, and the white tail deer, and the wild ox, and the mountain goat.",
        "owner full rewrite of Deuteronomy 14:5 (fallow ruling)"),
    ("Jeremiah", 4, 3): ("replace",
        [("Break up your fallow ground", "Break up your ground")],
        "fallow ground -> ground (owner ruling)"),
    ("Hosea", 10, 12): ("replace",
        [("break up your fallow ground", "break up your ground")],
        "fallow ground -> ground (owner ruling)"),

    # ---- fords: Replace with passages ------------------------------------------------------------------------
    ("Joshua", 2, 7): ("replace",
        [("the way to Jordan unto the fords", "the way to Jordan unto the passages")],
        "fords -> passages"),
    ("Judges", 3, 28): ("replace",
        [("took the fords of Jordan", "took the passages of Jordan")],
        "fords -> passages"),
    ("Isaiah", 16, 2): ("replace",
        [("at the fords of Arnon", "at the passages of Arnon")],
        "fords -> passages"),

    # ---- friendly: revise to kindly ---------------------------------------------------------------------------
    ("Judges", 19, 3): ("replace",
        [("to speak friendly unto her", "to speak kindly unto her")],
        "friendly -> kindly"),
    ("Ruth", 2, 13): ("replace",
        [("spoken friendly unto thine handmaid", "spoken kindly unto thine handmaid")],
        "friendly -> kindly"),
    ("Proverbs", 18, 24): ("replace",
        [("must shew himself friendly", "must shew himself kindly")],
        "friendly -> kindly"),

    # ---- frontlets: revise to foreheads -------------------------------------------------------------------------
    ("Exodus", 13, 16): ("replace",
        [("and for frontlets between thine eyes", "and for foreheads between thine eyes")],
        "frontlets -> foreheads"),
    ("Deuteronomy", 6, 8): ("replace",
        [("they shall be as frontlets between thine eyes", "they shall be as foreheads between thine eyes")],
        "frontlets -> foreheads"),
    ("Deuteronomy", 11, 18): ("replace",
        [("that they may be as frontlets between your eyes", "that they may be as foreheads between your eyes")],
        "frontlets -> foreheads"),

    # ---- frowardness: revise to perverseness ----------------------------------------------------------------------
    ("Proverbs", 2, 14): ("replace",
        [("delight in the frowardness of the wicked", "delight in the perverseness of the wicked")],
        "frowardness -> perverseness"),
    ("Proverbs", 6, 14): ("replace",
        [("Frowardness is in his heart", "Perverseness is in his heart")],
        "frowardness -> perverseness"),
    ("Proverbs", 10, 32): ("replace",
        [("the wicked speaketh frowardness", "the wicked speaketh perverseness")],
        "frowardness -> perverseness"),

    # ---- glorieth: irregular per owner (Jer: gives; Corinthians: gives glory) ----------------------------------------
    ("Jeremiah", 9, 24): ("replace",
        [("let him that glorieth glory in this", "let him that gives glory in this")],
        "glorieth -> gives (owner ruling)"),
    ("I Corinthians", 1, 31): ("replace",
        [("He that glorieth, let him glory in the Lord.", "He that gives glory, let him glory in the Lord.")],
        "glorieth -> gives glory (owner ruling)"),
    ("II Corinthians", 10, 17): ("replace",
        [("But he that glorieth, let him glory in the Lord.", "But he that gives glory, let him glory in the Lord.")],
        "glorieth -> gives glory (owner ruling)"),

    # ---- govern: revise to ruleth (owner's inflection, applied literally) ----------------------------------------------
    ("I Kings", 21, 7): ("replace",
        [("Dost thou now govern the kingdom of Israel", "Dost thou now ruleth the kingdom of Israel")],
        "govern -> ruleth (owner ruling; 2nd-person 'Dost thou...ruleth' mismatch, flagged)"),
    ("Job", 34, 17): ("replace",
        [("he that hateth right govern?", "he that hateth right ruleth?")],
        "govern -> ruleth"),
    ("Psalms", 67, 4): ("replace",
        [("and govern the nations upon earth", "and ruleth the nations upon earth")],
        "govern -> ruleth (owner ruling; 2nd-person mismatch with 'shalt...ruleth', flagged)"),

    # ---- gravel: irregular per-verse wording ---------------------------------------------------------------------------
    ("Proverbs", 20, 17): ("replace",
        [("his mouth shall be filled with gravel", "his mouth shall be filled with small stones")],
        "gravel -> small stones"),
    ("Isaiah", 48, 19): ("replace",
        [("like the gravel thereof", "like the small stones thereof")],
        "gravel -> small stones"),
    ("Lamentations", 3, 16): ("replace",
        [("with gravel stones", "with small stones")],
        "gravel -> small (owner said 'small'; rendered 'small stones' to preserve sense)"),

    # ---- grayheaded: revise to gray headed --------------------------------------------------------------------------------
    ("I Samuel", 12, 2): ("replace",
        [("I am old and grayheaded", "I am old and gray headed")],
        "grayheaded -> gray headed"),
    ("Job", 15, 10): ("replace",
        [("both the grayheaded and very aged men", "both the gray headed and very aged men")],
        "grayheaded -> gray headed"),
    ("Psalms", 71, 18): ("replace",
        [("when I am old and grayheaded", "when I am old and gray headed")],
        "grayheaded -> gray headed"),

    # ---- handbreadth: revise to "hand's measure"; fix article an->a -----------------------------------------------------------
    ("Exodus", 37, 12): ("replace",
        [("a border of an handbreadth", "a border of a hand's measure")],
        "handbreadth -> hand's measure; article 'an' -> 'a'"),
    ("II Chronicles", 4, 5): ("replace",
        [("was an handbreadth", "was a hand's measure")],
        "handbreadth -> hand's measure; article 'an' -> 'a'"),
    ("Psalms", 39, 5): ("replace",
        [("my days as an handbreadth", "my days as a hand's measure")],
        "handbreadth -> hand's measure; article 'an' -> 'a'"),

    # ---- haunt: irregular per-verse ------------------------------------------------------------------------------------------
    ("I Samuel", 23, 22): ("replace",
        [("where his haunt is", "where his dwelling is")],
        "haunt -> dwelling"),
    ("I Samuel", 30, 31): ("replace",
        [("were wont to haunt", "were wont to dwells")],
        "haunt -> dwells (owner ruling; subject-verb mismatch with 'wont to', flagged)"),
    ("Ezekiel", 26, 17): ("replace",
        [("which cause their terror to be on all that haunt it", "which cause their terror to be on all that dwells in it")],
        "haunt it -> dwells in it"),

    # ---- hay: revise to grass -----------------------------------------------------------------------------------------------------
    ("Proverbs", 27, 25): ("replace",
        [("The hay appeareth,", "The grass appeareth,")],
        "hay -> grass (owner ruling; verse already reads 'the tender grass "
        "sheweth itself' later, resulting doubled 'grass' flagged)"),
    ("Isaiah", 15, 6): ("replace",
        [("for the hay is withered away", "for the grass is withered away")],
        "hay -> grass (owner ruling; verse already reads 'the grass faileth' "
        "later, resulting doubled 'grass' flagged)"),
    ("I Corinthians", 3, 12): ("replace",
        [("wood, hay, stubble", "wood, grass, stubble")],
        "hay -> grass"),

    # ---- headlong: revise to hastily --------------------------------------------------------------------------------------------
    ("Job", 5, 13): ("replace",
        [("is carried headlong", "is carried hastily")],
        "headlong -> hastily"),
    ("Luke", 4, 29): ("replace",
        [("cast him down headlong", "cast him down hastily")],
        "headlong -> hastily"),
    ("Acts", 1, 18): ("replace",
        [("and falling headlong,", "and falling hastily,")],
        "headlong -> hastily"),

    # ---- highminded: revise to proud --------------------------------------------------------------------------------------------
    ("Romans", 11, 20): ("replace",
        [("Be not highminded, but fear", "Be not proud, but fear")],
        "highminded -> proud"),
    ("I Timothy", 6, 17): ("replace",
        [("that they be not highminded", "that they be not proud")],
        "highminded -> proud"),
    ("II Timothy", 3, 4): ("replace",
        [("fierce, highminded, lovers of pleasures", "fierce, proud, lovers of pleasures")],
        "highminded -> proud"),

    # ---- hindmost: revise to back ------------------------------------------------------------------------------------------------
    ("Numbers", 2, 31): ("replace",
        [("They shall go hindmost with their standards", "They shall go back with their standards")],
        "hindmost -> back"),
    ("Deuteronomy", 25, 18): ("replace",
        [("smote the hindmost of thee", "smote the back of thee")],
        "hindmost -> back"),
    ("Joshua", 10, 19): ("replace",
        [("smite the hindmost of them", "smite the back of them")],
        "hindmost -> back"),

    # ---- hurtful: revise with wicked; I Timothy 6:9 sink -> swallows -----------------------------------------------------------
    ("Ezra", 4, 15): ("replace",
        [("hurtful unto kings and provinces", "wicked unto kings and provinces")],
        "hurtful -> wicked"),
    ("Psalms", 144, 10): ("replace",
        [("from the hurtful sword", "from the wicked sword")],
        "hurtful -> wicked"),
    ("I Timothy", 6, 9): ("replace",
        [("many foolish and hurtful lusts, which sink men in destruction",
          "many foolish and wicked lusts, which swallows men in destruction")],
        "hurtful -> wicked; sink -> swallows (owner ruling)"),

    # ---- ice: revise to hailstones -----------------------------------------------------------------------------------------------
    ("Job", 6, 16): ("replace",
        [("black by reason of the ice", "black by reason of the hailstones")],
        "ice -> hailstones"),
    ("Job", 38, 29): ("replace",
        [("came the ice?", "came the hailstones?")],
        "ice -> hailstones"),
    ("Psalms", 147, 17): ("replace",
        [("He casteth forth his ice like morsels", "He casteth forth his hailstones like morsels")],
        "ice -> hailstones"),

    # ---- impoverished: revise to lacking -----------------------------------------------------------------------------------------
    ("Judges", 6, 6): ("replace",
        [("Israel was greatly impoverished", "Israel was greatly lacking")],
        "impoverished -> lacking"),
    ("Isaiah", 40, 20): ("replace",
        [("He that is so impoverished", "He that is so lacking")],
        "impoverished -> lacking"),
    ("Malachi", 1, 4): ("replace",
        [("We are impoverished,", "We are lacking,")],
        "impoverished -> lacking"),
}

OPEN_QUESTIONS = [
    "Several owner rulings were applied literally though they read awkwardly "
    "in context (dissembled -> 'defiled god'; dismissed/disorderly -> "
    "'departed'/'astray' at a few transitive spots; govern -> 'ruleth' at "
    "2nd-person verses; haunt -> 'dwells' at I Samuel 30:31; hay -> 'grass' "
    "doubling an existing 'grass' at two verses; dissension -> 'contention' "
    "doubling an existing 'contention' at Acts 15:2; dromedaries -> 'fast "
    "camels' doubling 'camels' at Esther 8:10). Flagged in each entry's note "
    "for the owner's eye before an apply step runs.",
]


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
        "# Round 6 — Rare Word Review: APPLY PREVIEW (not yet applied)",
        "",
        f"*{len(changed)} verses proposed for change from the owner rulings in "
        "`rare_word_round6_review.md` (2026-07-26). Computed against the ACTUAL "
        "current DB text (base KJV + approved restorations through round 5). "
        "NO DATABASE WRITES yet. 38 WHITELIST-ruled words are skipped entirely "
        "(no text change, not shown here; a future step should protect them via "
        "a round-6 section of `rare_word_review_no_safe_swap.md`).*",
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
