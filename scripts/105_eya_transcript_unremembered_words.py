#!/usr/bin/env python3
"""105_eya_transcript_unremembered_words.py — render
references/eya-video-transcripts/unremembered_words.md (owner request
2026-10-04): the Bible words that speakers in the EYA Censored videos say
they do not remember, with the earlier reading where one was stated as the
replacement suggestion.

The word lists below were curated by reading all 64 transcript.md files
(scripts/104); this script only adds each word's KJV.db frequency (each verse
counted once — KJV.db stores every verse 7 times), whether the EYA KJV Word
Index (scripts/97) lists it, and timestamped video links. Reads only; safe
to re-run. Advisory corroboration only (Premise Revision)."""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TDIR = ROOT / "references" / "eya-video-transcripts"
OUT = TDIR / "unremembered_words.md"

from collections import Counter
from functools import lru_cache

DIRS, corpus, TOKENS, index_words = {}, "", Counter(), set()


def load():
    """Read the transcript folders, KJV.db and the EYA index (rendering only)."""
    global DIRS, corpus, TOKENS, index_words
    DIRS = {p.name.split("_", 1)[1]: p.name for p in TDIR.iterdir() if p.is_dir()}

    verses = [t.lower() for (t,) in sqlite3.connect(
        ROOT / "bible_databases/formats/sqlite/KJV.db").execute(
        "SELECT MIN(text) FROM KJV_verses GROUP BY book_id, chapter, verse")]  # KJV.db stores each verse 7x
    corpus = "\n".join(verses)

    index_words = set()
    for line in (ROOT / "references/eya-new-words-list/kjv_word_index.tsv").read_text().splitlines()[1:]:
        for w in line.split("\t")[0].split("/"):
            index_words.add(w.strip().lower())
    TOKENS = Counter(re.findall(r"[a-z]+", corpus))


@lru_cache(maxsize=None)
def kjv_count(term):
    """Occurrences of the word/phrase in KJV.db (case-insensitive, whole words)."""
    total = 0
    for t in term.split("/"):
        t = t.strip().lower()
        if not t:
            continue
        if re.fullmatch(r"[a-z]+", t):
            total += TOKENS[t]
        else:
            total += len(re.findall(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", corpus))
    return total


def secs(ts):
    parts = [int(x) for x in ts.split(":")]
    s = 0
    for p in parts:
        s = s * 60 + p
    return s


def src(refs):
    out = []
    for vid, ts in refs:
        d = DIRS[vid]
        out.append(f"[{d[:10]} @{ts}](https://www.youtube.com/watch?v={vid}&t={secs(ts)}s)")
    return "<br>".join(out)


def cnt(term):
    n = kjv_count(term)
    return f"{n:,}" if n else "**0 — not in KJV.db**"


def idx(term):
    return "✓" if any(t.strip().lower() in index_words for t in term.split("/")) else ""


K, F4, CA, MU, WM, QD, OY, BD, E4, HN, XI, WL, JR, YE, DQ, WE, NL, MO, BQ, VK, YO, RH, IE, NQ, PE, ST, IF, X4 = (
    "kP5ZT-CdnXU", "4IMtSOiS4Wo", "c4OSgNFH2DI", "52_Tz1YDjig", "wm3xUNQWk1Q", "qDkaG7P1jAk",
    "OYWrL4UgDuQ", "bDJmqOTkgf0", "E4Tpveksvhk", "hnLhBFAUj8c", "XicZHOBM3nw", "WlOqoASC6Kg",
    "jRNMZ4K7J3A", "YeyXCfzZYQk", "DQu2csrQC7I", "wet2Nyd3JBw", "NlAK1H2J_2I", "3ySPGJk6mVM",
    "bQG15AsF_Ok", "vKeZ4iU5vt8", "Yox-Y2-CF8M", "RHznJK8lpi0", "ie3OLIfyLYg", "_nqJ6hLMODU",
    "2qKYL5O3ans", "U9oAY-5xTNI", "iEFr8-YYhLs", "4xr3WvIyF0w")

# ---- 1. Words with a remembered prior reading stated in the video ----------
# (KJV word or phrase, verse(s), what the speaker remembers, sources, note)
WITH_PRIOR = [
    ("wolf", "Isaiah 11:6; 65:25", "lion", [(K, "01:33"), (F4, "01:07"), (IE, "46:43"), (YO, "22:20")], ""),
    ("dwell", "Isaiah 11:6", "lie down (\"the lion shall lie down with the lamb\")", [(K, "12:43"), (F4, "01:38")], ""),
    ("expected end", "Jeremiah 29:11", "a future and a hope", [(K, "31:00")], ""),
    ("pounds", "Luke 19:13–25", "talents (\"the parable of the talents\")", [(K, "1:08:07")], ""),
    ("evil", "Joshua 23:15; Micah 1:12; 2 Kings 21:12; 1 Samuel 16:14–15", "hurt / trouble / adversity / harm (the lexicon's other renderings of H7451)", [(K, "1:17:11")], "evil sent *from the LORD*"),
    ("repented", "Exodus 32:14", "— (God does not repent, Num 23:19)", [(K, "1:21:57")], "no replacement named"),
    ("bottle/bottles", "Genesis 21:14–19; 1 Samuel 16:20; Matthew 9:17", "wineskin / wineskins (\"the parable of the wineskins\")", [(F4, "04:42"), (NL, "02:42"), (NQ, "09:57")], "residue claimed in a Bible concordance"),
    ("framed", "Hebrews 11:3", "created", [(F4, "22:34")], ""),
    ("candlesticks", "Revelation 1:13", "lampstands", [(F4, "25:11")], ""),
    ("terrible", "Job 37:22", "awesome (\"terrible majesty\")", [(F4, "33:21")], ""),
    ("sin", "John 1:29", "sins (\"taketh away the sins of the world\")", [(F4, "45:12")], ""),
    ("stuff", "Exodus 36:7", "possessions / belongings / provision", [(F4, "47:20")], ""),
    ("do not the truth", "1 John 1:6", "do not practise the truth / do not love the truth", [(F4, "48:52"), (E4, "03:42")], "speaker unsure which"),
    ("charity", "1 Corinthians 13; 1 Peter 4:8", "love (\"the love chapter\"; \"love covers a multitude of sins\")", [(F4, "49:23")], ""),
    ("devil/devils", "James 2:19 and throughout", "demon / demons", [(MU, "03:36"), (XI, "10:46"), (WE, "04:16")], "demon(s) said to be erased; residue claimed in a concordance"),
    ("Holy Ghost", "throughout", "Holy Spirit", [(MU, "13:20")], ""),
    ("bear record", "Revelation 1:2", "bear witness", [(MU, "10:45")], ""),
    ("saints", "Daniel 7:25", "holy ones (\"wear out the holy ones\")", [(QD, "01:47")], "also: saints should not appear before Acts"),
    ("think to change", "Daniel 7:25", "seek to change (times and laws)", [(QD, "02:19")], ""),
    ("words of the lord", "Amos 8:11", "word of the LORD (singular)", [(QD, "03:20")], ""),
    ("that wicked", "2 Thessalonians 2:8", "the lawless one", [(QD, "04:51")], ""),
    ("spirit of his mouth", "2 Thessalonians 2:8", "breath of his mouth", [(QD, "04:51")], ""),
    ("signs and lying wonders", "2 Thessalonians 2:9", "lying signs and wonders", [(QD, "05:23")], ""),
    ("received not the love of the truth", "2 Thessalonians 2:10", "did not love the truth", [(QD, "05:23")], ""),
    ("for this cause", "2 Thessalonians 2:11", "for this reason … send them *a* strong delusion", [(QD, "05:53")], "article \"a\" said to be missing"),
    ("scoffers", "2 Peter 3:3", "mockers", [(QD, "07:58")], ""),
    ("giants", "Genesis 6:4", "Nephilim", [(WL, "05:46")], ""),
    ("doctors", "Luke 2:46", "Jesus *teaching* the religious leaders (in the synagogue)", [(JR, "06:46"), (X4, "09:53")], ""),
    ("corn", "throughout (e.g. Genesis 41)", "grain", [(OY, "10:53"), (XI, "04:18")], ""),
    ("infants", "Luke 18:15", "children (\"Jesus blessed the children\")", [(F4, "35:26"), (PE, "10:58")], ""),
    ("grinding", "Matthew 24:41; Luke 17:35", "\"two in the field: one taken, the other left\"", [(NQ, "04:47")], "Matthew 24:40 still reads \"in the field\""),
    ("strait", "Matthew 7:13–14; Luke 13:24", "narrow (\"enter the narrow gate\")", [(ST, "03:08")], "also straiten, straiteneth, straitness"),
    ("ship", "Mark 4:38", "boat", [(ST, "08:16")], ""),
    ("master", "Mark 4:38", "teacher", [(ST, "08:48")], ""),
    ("wife", "Genesis 16:3", "concubine / servant (Hagar was never Abraham's wife)", [(K, "1:09:47"), (F4, "15:03"), (BD, "02:38")], ""),
    ("work", "James 1:22", "word (\"doers of the word\")", [(RH, "15:10")], "KJV.db still reads \"doers of the word\""),
    ("debts", "Matthew 6:12", "trespasses (speaker's memory of the KJV)", [(RH, "15:43")], ""),
    ("asia", "Acts (throughout)", "Asia Minor", [(JR, "08:18")], ""),
    # spelling / word-division claims
    ("publick", "Matthew 1:19", "public", [(K, "24:28")], "spelling"),
    ("garlick", "Numbers 11:5", "garlic", [(K, "24:28"), (XI, "04:18")], "spelling"),
    ("musick", "1 Chronicles 15:16 and throughout", "music", [(MU, "05:09"), (VK, "07:59")], "spelling; residue claimed at 1 Chr 15:16"),
    ("alway", "throughout", "always", [(K, "25:22")], "spelling"),
    ("forgat", "throughout", "forgot / forget", [(K, "37:59")], ""),
    ("restingplace/dwellingplace/stumblingblock", "throughout", "two words: resting place, dwelling place, stumbling block", [(K, "36:56")], "word division"),
    ("lookingglasses", "Exodus 38:8", "looking glasses (two words)", [(YE, "00:05")], "word division"),
    ("sycomore", "1 Chronicles 27:28", "sycamore", [(VK, "06:27")], "spelling"),
    ("judgment", "throughout", "judgement (with an e)", [(OY, "17:31")], "spelling"),
]

# ---- 2. The study-Bible appendix shown in OYWrL4UgDuQ -----------------------
# KJV word -> the appendix's modern equivalent, which the presenter treats as
# the reading that used to be there. Pairs garbled past recovery by the
# speech recognition are left out.
APPENDIX = [
    ("alleging", "proving (Acts 17:3)"), ("amazement", "terror"), ("ancient/ancients", "elder / elders"),
    ("anon", "immediately"), ("apothecary", "perfumer"), ("answer", "defence"),
    ("armholes", "elbows"), ("artillery", "weapons"), ("belly", "body"),
    ("betimes", "early"), ("bewitched", "amazed"), ("bishoprick", "office"),
    ("bottles", "wineskins"), ("bowels", "heart / compassion / affection"),
    ("breaking up", "breaking in"), ("brigandines", "coats of mail"),
    ("by and by", "immediately"), ("careful", "anxious (Philippians 4:6)"),
    ("chapiter", "capital"), ("charity", "love"), ("check", "chastisement"),
    ("clean", "completely"), ("coast", "border / boundary / territory"),
    ("cockatrice", "adder"), ("communication", "fellowship / companionship"),
    ("compass", "circle"), ("concluded", "shut up"), ("confection", "spice"),
    ("consumption", "destruction"), ("corn", "grain"), ("cracknels", "cakes"),
    ("crouch", "prostrate"), ("cuckow", "seagull"), ("curse", "devoted thing"),
    ("damnation", "condemnation / judgment"), ("damned", "condemned"),
    ("darling", "dear life"), ("devils", "goat-demons / satyrs"),
    ("doctors", "teachers"), ("dragons", "jackals / sea monsters"), ("duke", "chief"),
    ("eared", "plowed"), ("earing", "plowing"), ("earring", "ring"),
    ("easter", "Passover"), ("emerods", "tumours"), ("fan", "winnowing fork"),
    ("fanners", "winnowers"), ("environ", "encompass"), ("exactors", "taskmasters"),
    ("feller", "hewer"), ("fetched a compass", "made a circuit / turned about"),
    ("fitches", "spelt"), ("flagons", "cakes of raisins"), ("flowers", "impurity"),
    ("folk", "nation"), ("fray", "frighten"), ("froward", "perverse / crooked"),
    ("furnished", "filled"), ("furniture", "saddle"), ("gender", "breed"),
    ("halt", "limped"), ("horseleach", "leech"), ("hough", "hamstring"),
    ("instrument", "weapon"), ("inventions", "doings"), ("jeoparded", "jeopardized"),
    ("jewry", "Judea"), ("judgment", "justice (\"righteousness and justice are the foundation of his throne\")"),
    ("leasing", "lies / falsehood"), ("liquor", "juice"), ("loft", "chamber"),
    ("lunatick", "epileptic"), ("maid", "virgin"), ("maul", "club"),
    ("marred", "ruined"), ("mean man", "common man"), ("meat", "food / meal"),
    ("merchantmen", "merchants"), ("minister", "attendant"), ("minstrels", "flute players"),
    ("naughtiness", "wickedness (James 1:21)"), ("nephews", "grandchildren"),
    ("open", "frequent"), ("organ", "pipe"), ("ouches", "settings"),
    ("overcharged", "overburdened"), ("owls", "ostriches"),
    ("possessed", "formed (Psalm 139:13)"), ("printed", "inscribed"),
    ("privily", "secretly"), ("purtenance", "entrails"), ("quick", "alive"),
    ("record", "witness"), ("reins", "kidneys"), ("secret", "counsel"),
    ("scrip", "bag / pouch"), ("satyr", "wild goat"), ("senators", "elders"),
    ("shamefacedness", "decency"), ("shittah/shittim", "acacia"),
    ("sides", "innermost parts"), ("snuffed up the wind", "panted for air"),
    ("smell", "take delight in"), ("sorrows", "cords"),
    ("suburbs", "pasture lands"), ("stuff", "baggage"), ("syrian", "Aramaic"),
    ("tables", "tablets"), ("tablets", "armlets"), ("take no thought", "be not anxious"),
    ("turtles", "doves"), ("unicorn/unicorns", "wild ox"), ("unperfect", "unformed"),
    ("vagabond", "wanderer"), ("vanity", "falsehood"), ("withs", "fresh cords"),
    ("wounds", "tasty morsels (Proverbs 18:8)"),
]

# ---- 3. Words people do not remember; no prior reading stated --------------
# (theme, word, verse(s) or "", sources)
NO_PRIOR = [
    # Spelling, grammar and odd forms
    ("Odd forms and filler", "filledst/diggedst/plantedst", "Deuteronomy 6:11", [(K, "23:21")]),
    ("Odd forms and filler", "overplus", "", [(K, "36:19")]),
    ("Odd forms and filler", "evilfavouredness", "Deuteronomy 17:1", [(K, "36:19")]),
    ("Odd forms and filler", "holpen", "", [(K, "37:59")]),
    ("Odd forms and filler", "us-ward", "", [(X4, "06:13")]),
    ("Odd forms and filler", "magnifical", "1 Chronicles 22:5", [(X4, "07:16")]),
    ("Odd forms and filler", "unperfect", "Psalm 139:16", [(X4, "05:43")]),
    ("Odd forms and filler", "thereat", "Matthew 7:13", [(ST, "03:38")]),
    ("Odd forms and filler", "betwixt", "Philippians 1:23", [(ST, "04:39")]),
    ("Odd forms and filler", "yea", "Job 34:12", [(PE, "05:16")]),
    ("Odd forms and filler", "hither/thither/notwithstanding/wheresoever/whoso", "", [(PE, "05:16")]),
    ("Odd forms and filler", "bestead", "Isaiah 8:21", [(F4, "41:38")]),
    ("Odd forms and filler", "aileth", "2 Kings 6:28", [(WE, "03:45")]),
    ("Odd forms and filler", "respecteth", "Job 37:24", [(F4, "35:56")]),
    ("Odd forms and filler", "straightway", "Matthew 14:22", [(BQ, "03:09")]),
    ("Odd forms and filler", "selfsame", "Leviticus 23:14", [(VK, "05:52")]),
    ("Odd forms and filler", "world without end", "Isaiah 45:17", [(WL, "03:38")]),
    # About God / Jesus
    ("About God and Jesus", "holy thing", "Luke 1:35", [(K, "1:06:32"), (F4, "20:27"), (HN, "02:03")]),
    ("About God and Jesus", "overshadow", "Luke 1:35", [(F4, "19:49")]),
    ("About God and Jesus", "highest", "Luke 1:35", [(F4, "19:49")]),
    ("About God and Jesus", "hiss", "Isaiah 7:18", [(F4, "17:10"), (HN, "02:03")]),
    ("About God and Jesus", "jealous", "Exodus 34:14", [(HN, "02:03")]),
    ("About God and Jesus", "worm", "Job 25:6", [(K, "1:05:57"), (F4, "30:37")]),
    ("About God and Jesus", "touching", "Job 37:23", [(F4, "34:24")]),
    ("About God and Jesus", "fellow", "Luke 23:2", [(PE, "07:48")]),
    ("About God and Jesus", "pervert/perverted/perverteth/perverting", "Job 8:3; Deuteronomy 27:19; Job 34:12; Luke 23:2", [(PE, "02:09")]),
    ("About God and Jesus", "slay", "Luke 19:27", [(K, "1:08:40"), (BD, "05:20"), (E4, "03:08")]),
    ("About God and Jesus", "paps", "Revelation 1:13", [(F4, "25:41"), (NQ, "05:49")]),
    ("About God and Jesus", "girdle", "Revelation 1:13", [(F4, "25:41")]),
    ("About God and Jesus", "pillow", "Mark 4:38", [(ST, "08:16")]),
    ("About God and Jesus", "hinder", "Mark 4:38", [(ST, "08:16")]),
    # Body, sexual and crude language
    ("Body and crude language", "buttocks", "2 Samuel 10:4", [(F4, "23:37"), (F4, "32:50")]),
    ("Body and crude language", "piss", "2 Kings 18:27", [(F4, "27:19"), (WE, "01:39")]),
    ("Body and crude language", "dung", "2 Kings 18:27", [(F4, "27:19")]),
    ("Body and crude language", "bastards", "", [(F4, "39:30")]),
    ("Body and crude language", "foreskin", "Habakkuk 2:16", [(F4, "20:58")]),
    ("Body and crude language", "spewing", "Habakkuk 2:16", [(F4, "20:58")]),
    ("Body and crude language", "breasts", "Job 21:24", [(F4, "31:42"), (XI, "12:53")]),
    ("Body and crude language", "bowels", "Song of Solomon 5:4; 2 Chronicles 21:19; 2 Corinthians 6:12", [(F4, "37:56"), (JR, "02:04"), (JR, "04:11")]),
    ("Body and crude language", "loins", "Genesis 46:26; 1 Kings 12:10", [(F4, "46:19"), (NL, "04:53")]),
    ("Body and crude language", "virginity", "Judges 11:37–38", [(F4, "43:11")]),
    ("Body and crude language", "bewail/bewailed", "Judges 11:37–38", [(F4, "43:11")]),
    ("Body and crude language", "stripped", "1 Samuel 19:24", [(NL, "02:42")]),
    ("Body and crude language", "naked", "throughout (said to be multiplied)", [(X4, "05:43")]),
    ("Body and crude language", "kissed", "1 Kings 19:18; 1 Samuel 20:41", [(WE, "02:11"), (NQ, "03:46")]),
    ("Body and crude language", "exceeded", "1 Samuel 20:41", [(NQ, "03:46")]),
    ("Body and crude language", "grind", "Judges 16:21; Job 31:10", [(NQ, "05:18")]),
    ("Body and crude language", "gender", "2 Timothy 2:23", [(NQ, "06:50")]),
    ("Body and crude language", "man child", "", [(X4, "07:16")]),
    ("Body and crude language", "whorish/whoring", "", [(WE, "01:39")]),
    ("Body and crude language", "earthy", "1 Corinthians 15:49", [(NL, "03:13")]),
    ("Body and crude language", "liver", "", [(XI, "08:39")]),
    ("Body and crude language", "kidneys", "", [(XI, "09:09")]),
    ("Body and crude language", "fingers", "throughout (said to be multiplied)", [(XI, "08:39")]),
    ("Body and crude language", "backbone", "", [(X4, "06:45")]),
    # Character traits / end-times list
    ("Character words", "incontinent", "2 Timothy 3:3", [(F4, "14:03")]),
    ("Character words", "fierce", "2 Timothy 3:3", [(F4, "14:03")]),
    ("Character words", "traitors", "2 Timothy 3:4", [(F4, "14:03")]),
    ("Character words", "heady", "2 Timothy 3:4", [(F4, "14:03")]),
    ("Character words", "highminded", "2 Timothy 3:4", [(F4, "14:03")]),
    ("Character words", "crafty", "", [(WE, "01:39")]),
    ("Character words", "devilish", "", [(WE, "01:39")]),
    ("Character words", "destitute", "James 2:15", [(WE, "03:45")]),
    ("Character words", "offenders", "1 Kings 1:21", [(NL, "04:22")]),
    ("Character words", "quit you like men", "1 Corinthians 16:13", [(NL, "03:45")]),
    ("Character words", "buffeted", "1 Corinthians 4:11", [(NL, "03:45")]),
    ("Character words", "extortioner", "1 Corinthians 5:11", [(MO, "03:43")]),
    ("Character words", "conspiracy", "2 Kings 12:20", [(JR, "06:15")]),
    ("Character words", "lad", "Genesis 21:19; 1 Samuel 20:41", [(F4, "16:39"), (NQ, "03:46")]),
    # Occult
    ("Occult", "wizards", "Isaiah 8:19; 1 Samuel 28:3, 9", [(F4, "41:02"), (DQ, "02:40")]),
    ("Occult", "peep/mutter", "Isaiah 8:19", [(F4, "41:02")]),
    ("Occult", "familiar spirits", "1 Samuel 28:3, 9", [(DQ, "02:40")]),
    ("Occult", "caldron", "", [(WE, "01:39")]),
    ("Occult", "oracle", "1 Kings 6:19, 31", [(WE, "03:15")]),
    ("Occult", "necromancer", "", [(WE, "01:39")]),
    ("Occult", "matrix", "", [(YE, "03:06"), (XI, "10:13")]),
    # Royalty / fable
    ("Royalty and fable", "castle/castles", "Genesis 25:16; Numbers 31:10", [(DQ, "01:04"), (IF, "01:37")]),
    ("Royalty and fable", "princes", "Genesis 25:16 (said to be multiplied)", [(IF, "01:37"), (XI, "11:50")]),
    ("Royalty and fable", "duke/dukes", "Genesis 36", [(DQ, "01:04"), (OY, "13:05")]),
    ("Royalty and fable", "unicorn/unicorns", "Numbers 23:22", [(DQ, "01:04"), (X4, "05:13")]),
    ("Royalty and fable", "damsels", "1 Samuel 25:42", [(DQ, "02:40"), (X4, "09:23")]),
    ("Royalty and fable", "cockatrice", "Isaiah 59:5", [(DQ, "01:04"), (VK, "06:57")]),
    ("Royalty and fable", "satyr", "", [(DQ, "01:04")]),
    ("Royalty and fable", "dwarf", "", [(DQ, "01:04")]),
    ("Royalty and fable", "carriage", "1 Samuel 17:22", [(DQ, "01:39")]),
    ("Royalty and fable", "saluted/salute", "1 Samuel 17:22; 3 John 1:14", [(DQ, "01:39"), (DQ, "06:27")]),
    ("Royalty and fable", "coat of mail", "1 Samuel 17:5", [(DQ, "02:10")]),
    ("Royalty and fable", "realm", "2 Chronicles 20:30", [(DQ, "02:10")]),
    ("Royalty and fable", "seed royal", "2 Chronicles 22:10", [(DQ, "03:43")]),
    ("Royalty and fable", "god save the king", "2 Chronicles 23:11", [(DQ, "04:18")]),
    ("Royalty and fable", "prosperously", "2 Chronicles 7:11", [(DQ, "04:56")]),
    ("Royalty and fable", "palace", "throughout (81 times)", [(X4, "11:53")]),
    ("Royalty and fable", "greyhound", "", [(XI, "11:50")]),
    ("Royalty and fable", "pransings", "Judges 5:22", [(XI, "10:13")]),
    # Professions / government / military
    ("Professions, government and war", "lawyer/lawyers", "Titus 3:13", [(XI, "06:30"), (WL, "06:18"), (X4, "10:53")]),
    ("Professions, government and war", "physicians", "", [(XI, "06:30"), (X4, "10:53")]),
    ("Professions, government and war", "nurse", "", [(XI, "06:30")]),
    ("Professions, government and war", "townclerk", "Acts 19:35", [(XI, "06:30"), (MO, "02:10")]),
    ("Professions, government and war", "sheriffs", "Daniel 3:2–3", [(MO, "02:10"), (BQ, "02:08"), (X4, "10:53")]),
    ("Professions, government and war", "deputies", "", [(WL, "02:05"), (X4, "10:53")]),
    ("Professions, government and war", "officers", "", [(WL, "02:05")]),
    ("Professions, government and war", "presidents", "Daniel 6:2–3", [(XI, "11:18"), (BQ, "03:41"), (ST, "07:14")]),
    ("Professions, government and war", "senators", "", [(XI, "11:18"), (BQ, "01:06")]),
    ("Professions, government and war", "treasurers/counsellors", "Daniel 3:2", [(BQ, "02:08")]),
    ("Professions, government and war", "government", "2 Peter 2:10", [(WL, "04:08")]),
    ("Professions, government and war", "dignities", "2 Peter 2:10", [(WL, "04:08")]),
    ("Professions, government and war", "liberal", "2 Corinthians 9:13", [(XI, "11:18"), (JR, "04:44")]),
    ("Professions, government and war", "publican", "", [(XI, "11:18")]),
    ("Professions, government and war", "porters", "2 Kings 7:11", [(DQ, "05:56"), (MO, "02:10")]),
    ("Professions, government and war", "chief of the guard", "2 Chronicles 12:10", [(DQ, "04:56")]),
    ("Professions, government and war", "bakers/butlers", "", [(X4, "06:45")]),
    ("Professions, government and war", "pilots", "", [(K, "39:49"), (MO, "02:10"), (X4, "08:19")]),
    ("Professions, government and war", "sailors/shipmaster", "Revelation 18:17", [(MO, "04:45"), (ST, "07:14")]),
    ("Professions, government and war", "navy", "1 Kings 9:26; 10:11, 22", [(BQ, "01:06"), (ST, "05:40")]),
    ("Professions, government and war", "artillery", "", [(BQ, "01:06")]),
    ("Professions, government and war", "munitions", "", [(BQ, "01:06")]),
    ("Professions, government and war", "warfare", "1 Corinthians 9:7", [(BQ, "01:38")]),
    ("Professions, government and war", "protested/protesting", "Jeremiah 11:7", [(BQ, "02:39")]),
    ("Professions, government and war", "constrained", "Matthew 14:22", [(BQ, "03:09")]),
    ("Professions, government and war", "preferred", "Daniel 6:3", [(BQ, "04:11")]),
    ("Professions, government and war", "retire", "Jeremiah 4:6", [(MO, "03:12")]),
    ("Professions, government and war", "chain", "Ezekiel 7:23", [(WL, "06:49")]),
    ("Professions, government and war", "crimes", "Ezekiel 7:23", [(WL, "06:49")]),
    ("Professions, government and war", "aliens", "", [(WL, "02:05")]),
    ("Professions, government and war", "outer darkness", "", [(WL, "02:05")]),
    ("Professions, government and war", "forum", "", [(WL, "02:05")]),
    # Money and trade
    ("Money and trade", "bank", "", [(K, "01:33"), (XI, "07:04"), (MO, "02:10"), (X4, "06:45")]),
    ("Money and trade", "mortgaged", "", [(MO, "02:10")]),
    ("Money and trade", "penny", "", [(MO, "02:10")]),
    ("Money and trade", "wealthy", "", [(MO, "02:10")]),
    ("Money and trade", "bill", "", [(MO, "02:10")]),
    ("Money and trade", "employment", "", [(MO, "02:10")]),
    ("Money and trade", "linen yarn", "1 Kings 10:28", [(MO, "03:12")]),
    ("Money and trade", "traffick", "1 Kings 10:15", [(BQ, "04:11")]),
    ("Money and trade", "pledge", "Job 24:3; Ezekiel 18:7", [(MO, "05:15")]),
    ("Money and trade", "concision", "Philippians 3:2", [(MO, "05:15")]),
    # Education / technology
    ("Education and technology", "college", "2 Kings 22:14; 2 Chronicles 34:22", [(K, "39:49"), (XI, "07:04"), (JR, "03:08"), (YE, "03:06")]),
    ("Education and technology", "school", "", [(XI, "07:04"), (YE, "03:06")]),
    ("Education and technology", "scholar", "1 Chronicles 25:8", [(XI, "07:04"), (YE, "03:06")]),
    ("Education and technology", "instructors", "", [(YE, "03:06")]),
    ("Education and technology", "pen/paper", "", [(YE, "03:06")]),
    ("Education and technology", "theatre", "", [(YE, "03:06")]),
    ("Education and technology", "science", "", [(YE, "03:06"), (VK, "02:13")]),
    ("Education and technology", "experiment", "2 Corinthians 9:13", [(JR, "04:44")]),
    ("Education and technology", "ministration", "2 Corinthians 9:13", [(JR, "04:44")]),
    ("Education and technology", "devices", "", [(XI, "11:50")]),
    ("Education and technology", "witty inventions", "", [(XI, "11:50")]),
    ("Education and technology", "engines", "", [(K, "39:49")]),
    ("Education and technology", "network", "", [(K, "39:49")]),
    ("Education and technology", "channel", "Isaiah 27:12", [(F4, "18:11")]),
    ("Education and technology", "publish", "", [(F4, "18:11")]),
    # Space
    ("Space", "worlds", "Hebrews 1:2; 11:3", [(K, "40:20"), (F4, "22:02")]),
    ("Space", "planets", "", [(K, "40:20"), (F4, "22:02")]),
    ("Space", "mars/jupiter", "", [(K, "40:20"), (F4, "22:02")]),
    ("Space", "gravity", "", [(K, "40:20")]),
    ("Space", "space", "", [(K, "40:20")]),
    # Household, travel
    ("Household and travel", "wardrobe", "2 Kings 22:14; 2 Chronicles 34:22", [(K, "39:49"), (JR, "03:08")]),
    ("Household and travel", "furniture", "Genesis 31:34", [(XI, "08:06"), (X4, "08:50")]),
    ("Household and travel", "parlour", "", [(XI, "08:06")]),
    ("Household and travel", "cottage", "", [(XI, "08:06")]),
    ("Household and travel", "cabins", "Jeremiah 37:16", [(X4, "08:50")]),
    ("Household and travel", "cart", "throughout (9 times)", [(X4, "08:50")]),
    ("Household and travel", "aprons", "Genesis 3:7", [(XI, "07:36"), (IF, "03:39")]),
    ("Household and travel", "hosen", "", [(F4, "26:17")]),
    ("Household and travel", "bonnets", "", [(F4, "26:17"), (XI, "13:25")]),
    ("Household and travel", "needlework", "", [(F4, "26:17")]),
    ("Household and travel", "lintel", "1 Kings 6:31", [(WE, "03:45")]),
    ("Household and travel", "holyday", "", [(XI, "07:36")]),
    ("Household and travel", "ward", "", [(XI, "09:42")]),
    ("Household and travel", "ferry boat", "", [(XI, "12:22")]),
    ("Household and travel", "rails/railing", "", [(K, "39:49")]),
    ("Household and travel", "passengers", "", [(K, "39:49")]),
    ("Household and travel", "sport/sporting", "", [(XI, "11:50")]),
    ("Household and travel", "nursing fathers", "", [(XI, "12:53")]),
    # Food, farming, nature
    ("Food, farming and nature", "fryingpan", "Leviticus 7:9", [(F4, "47:52")]),
    ("Food, farming and nature", "baken", "Leviticus 7:9", [(F4, "47:52")]),
    ("Food, farming and nature", "bakemeats", "", [(X4, "06:45")]),
    ("Food, farming and nature", "salted", "Mark 9:49", [(F4, "48:22")]),
    ("Food, farming and nature", "cheeses", "1 Samuel 17:18", [(MO, "05:15")]),
    ("Food, farming and nature", "melons/cucumbers", "Numbers 11:5", [(XI, "04:18"), (VK, "02:13")]),
    ("Food, farming and nature", "apes/peacocks", "1 Kings 10:22", [(XI, "04:18"), (VK, "01:06"), (ST, "05:40")]),
    ("Food, farming and nature", "couching", "Genesis 49:14", [(F4, "46:50")]),
    ("Food, farming and nature", "slime", "", [(K, "39:49")]),
    ("Food, farming and nature", "gross", "", [(K, "39:49")]),
    ("Food, farming and nature", "pollute/pollution", "", [(XI, "06:00"), (VK, "01:06")]),
    ("Food, farming and nature", "environ", "", [(XI, "06:00"), (VK, "01:06")]),
    ("Food, farming and nature", "nature", "", [(VK, "01:06")]),
    ("Food, farming and nature", "corruption", "", [(VK, "01:06")]),
    ("Food, farming and nature", "ferret", "Leviticus 11:30", [(VK, "01:06")]),
    ("Food, farming and nature", "pygarg", "", [(VK, "01:06")]),
    ("Food, farming and nature", "cuckow", "", [(VK, "01:06")]),
    ("Food, farming and nature", "cloudy", "", [(VK, "01:06")]),
    ("Food, farming and nature", "chesnut", "", [(VK, "02:13")]),
    ("Food, farming and nature", "dainty meats", "", [(VK, "02:13")]),
    ("Food, farming and nature", "glede", "", [(VK, "02:13")]),
    ("Food, farming and nature", "kine", "", [(VK, "02:13")]),
    ("Food, farming and nature", "pulse", "", [(VK, "02:13")]),
    ("Food, farming and nature", "naughty figs", "Jeremiah 24:2", [(VK, "02:13")]),
    ("Food, farming and nature", "shambles", "", [(VK, "02:13")]),
    ("Food, farming and nature", "parched corn", "Leviticus 23:14", [(VK, "02:13"), (VK, "05:52")]),
    ("Food, farming and nature", "oil olive", "Leviticus 24:2", [(VK, "06:57")]),
    ("Food, farming and nature", "badgers", "Exodus 39:34", [(VK, "03:18")]),
    ("Food, farming and nature", "harrows", "1 Chronicles 20:3", [(VK, "04:21")]),
    ("Food, farming and nature", "murrain", "Exodus 9:3", [(VK, "04:51")]),
    ("Food, farming and nature", "beeves", "Leviticus 22:21", [(VK, "03:50")]),
    ("Food, farming and nature", "enflaming", "Isaiah 57:5", [(VK, "05:52")]),
    ("Food, farming and nature", "almug", "1 Kings 10:11", [(BQ, "03:09")]),
    ("Food, farming and nature", "palsy", "", [(JR, "02:36")]),
    ("Food, farming and nature", "snatch", "Isaiah 9:20", [(WE, "03:15")]),
    ("Food, farming and nature", "stretched himself", "1 Kings 17:21", [(E4, "01:34")]),
    ("Food, farming and nature", "smelling", "1 Corinthians 12:17", [(E4, "02:36")]),
    ("Food, farming and nature", "cords of a man", "Hosea 11:4", [(F4, "41:38")]),
]

# ---- 4. Names and titles ----------------------------------------------------
NAMES = [
    ("Sion", "Psalms, Hebrews 12:22, Revelation 14:1", "Zion", [(K, "50:37")]),
    ("Nephthalim", "Revelation 7:6; Matthew 4:13", "Naphtali", [(K, "51:38"), (WL, "02:36")]),
    ("Aser", "Revelation 7:6", "Asher", [(K, "51:38")]),
    ("Manasses", "Revelation 7:6", "Manasseh", [(K, "51:38")]),
    ("Zabulon", "Revelation 7:8", "Zebulun", [(K, "51:38")]),
    ("Joseph (tribe of)", "Revelation 7:8", "Ephraim", [(K, "51:38")]),
    ("Juda", "Revelation 7:5", "Judah", [(K, "51:38")]),
    ("Judas", "Matthew 1:2–3", "Judah (Jesus is of the line of Judah)", [(F4, "24:40")]),
    ("Nebuchadrezzar", "Jeremiah, Ezekiel", "Nebuchadnezzar", [(K, "52:09")]),
    ("Osee", "Romans 9:25", "Hosea", [(K, "52:45")]),
    ("Melchisedec", "Hebrews 5–7", "Melchizedek (one spelling)", [(K, "52:45")]),
    ("John Baptist", "", "John the Baptist", [(K, "53:33")]),
    ("Esaias", "Luke 4:17", "Isaiah", [(K, "55:39")]),
    ("Elias", "Matthew 17:3", "Elijah", [(K, "56:28")]),
    ("Jeremy", "Matthew 27:9", "Jeremiah", [(K, "56:59")]),
    ("Noe", "Matthew 24:37–38; Luke 3:36; 17:26–27", "Noah", [(K, "58:03"), (RH, "16:14")]),
    ("Tertius", "Romans 16:22", "Paul (wrote Romans)", [(K, "55:00")]),
    ("Son of man", "Revelation 1:13", "Son of God", [(NQ, "05:49")]),
    ("Joses", "Mark 6:3", "— (no brother of Jesus by that name)", [(K, "42:28")]),
    ("Aholibamah", "Genesis 36", "—", [(K, "53:33")]),
    ("Barjesus", "Acts 13:6", "—", [(WM, "01:39")]),
    ("Paphos", "Acts 13:6", "— (speaker knows only Patmos)", [(WM, "01:39")]),
    ("Justus", "Acts 18:7; Colossians 4:11", "—", [(WM, "02:41")]),
    ("Zenas", "Titus 3:13", "—", [(WL, "06:18")]),
    ("Gaza", "", "—", [(BD, "04:15"), (BQ, "01:06")]),
    ("Ezion-geber", "1 Kings 9:26", "—", [(ST, "06:43")]),
    ("Tharshish", "1 Kings 10:22", "—", [(ST, "06:10")]),
]
TITLES = [
    ("The Revelation of St. John the Divine", "Revelation / Revelations", [(CA, "01:08"), (MU, "11:45")]),
    ("The Gospel according to St. Mark (and the other gospels)", "Mark", [(MU, "07:43")]),
    ("Ecclesiastes; or, the Preacher", "Ecclesiastes", [(MU, "09:15")]),
    ("The Epistle of Paul the Apostle to the Ephesians", "Ephesians", [(MU, "10:15")]),
    ("Psalm (singular, in some Bibles)", "Psalms", [(MU, "02:34")]),
]

# ---- 5. Remembered words now said to be missing -----------------------------
MISSING = [
    ("demon/demons", "now devil(s)", [(F4, "10:21"), (MU, "03:36"), (VK, "07:59")]),
    ("messiah", "only twice in the OT (Daniel 9), none in the NT", [(K, "51:07"), (F4, "10:52"), (VK, "07:59")]),
    ("discernment", "", [(F4, "10:21"), (VK, "07:59")]),
    ("lawlessness", "", [(F4, "10:21")]),
    ("trials", "", [(F4, "10:21")]),
    ("tribulations", "", [(F4, "10:21")]),
    ("jubilee", "", [(F4, "10:21"), (VK, "07:59")]),
    ("music", "now musick", [(MU, "05:09"), (VK, "07:59")]),
    ("animals", "", [(VK, "07:59")]),
    ("holy of holies", "now \"most holy place\"", [(VK, "07:59")]),
    ("berean/bereans", "Acts 17", [(MU, "04:38"), (ST, "05:10")]),
    ("nephilim", "Genesis 6:4, now giants", [(WL, "05:46")]),
    ("love", "1 Corinthians 13, 1 Peter 4:8 — now charity", [(F4, "49:54")]),
]


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out



def main():
    load()
    lines = [
        "# Words People Do Not Remember — from the EYA Censored Video Transcripts",
        "",
        "Extracted by reading all 64 transcripts in this folder (Videos tab of",
        "<https://www.youtube.com/@eyacensored-biblechanges>; 2021-09 → 2026-05).",
        "Each entry is a word or phrase that a speaker says they do not remember in",
        "the Bible. Where the speaker said what the verse *used to* read, that",
        "remembered reading is given as the replacement suggestion.",
        "",
        "**How to read this list**",
        "",
        "- **Source** links open the video at the moment the word is discussed.",
        "- **KJV** is how often the word appears in the base text",
        "  (`bible_databases/formats/sqlite/KJV.db`, case-insensitive whole words;",
        "  each verse counted once; `/` variants summed). **0** means the claimed word is not in our base",
        "  text at all — usually a modern-Bible reading or a speech-recognition",
        "  mishearing.",
        "- **EYA index** ✓ = the word is also in the EYA KJV Word Index already",
        "  imported at `references/eya-new-words-list/`.",
        "- The transcripts are YouTube auto-captions, so some spellings were",
        "  reconstructed from the verse cited; the timestamp lets you check.",
        "- Advisory corroboration only (Premise Revision): these are testimony",
        "  leads for review, not approved restorations.",
        "",
    ]

    lines += ["## 1. Words with a remembered earlier reading", "",
              "The speaker named what the verse used to say.", ""]
    lines += table(["Word now in the KJV", "Verse(s)", "Remembered reading → suggested replacement", "KJV", "EYA index", "Note", "Source"],
                   [[f"**{w}**", v, p, cnt(w), idx(w), n, src(s)] for w, v, p, s, n in WITH_PRIOR])
    lines.append("")

    lines += ["## 2. The study-Bible word list (Explore Issue rerun, 2016 → 2023)", "",
              "In [this video](https://www.youtube.com/watch?v=OYWrL4UgDuQ) the",
              "presenter reads the \"over 500 archaic and obsolete words\" appendix",
              "from a *Holy Bible, Study Edition (KJV)* and treats each **bold** KJV",
              "word as new and its listed modern equivalent as the reading that used",
              "to be there. The pairs below are the ones the auto-captions let us",
              "reconstruct; several more were too garbled to recover.", ""]
    lines += table(["Word now in the KJV", "Appendix's modern equivalent → suggested replacement", "KJV", "EYA index"],
                   [[f"**{w}**", p, cnt(w), idx(w)] for w, p in APPENDIX])
    lines += ["", f"Source for every row: [{DIRS[OY][:10]}, 05:40–25:54](https://www.youtube.com/watch?v={OY}&t=340s).", ""]

    lines += ["## 3. Words people do not remember — no earlier reading given", ""]
    themes = []
    for t, *_ in NO_PRIOR:
        if t not in themes:
            themes.append(t)
    for t in themes:
        lines += [f"### {t}", ""]
        lines += table(["Word", "Verse(s) cited", "KJV", "EYA index", "Source"],
                       [[f"**{w}**", v, cnt(w), idx(w), src(s)] for th, w, v, s in NO_PRIOR if th == t])
        lines.append("")

    lines += ["## 4. Names and book titles", ""]
    lines += table(["Name now in the KJV", "Verse(s)", "Remembered name → suggested replacement", "KJV", "Source"],
                   [[f"**{w}**", v, p, cnt(w.split(" (")[0]), src(s)] for w, v, p, s in NAMES])
    lines += ["", "**Book titles**", ""]
    lines += table(["Title now printed", "Remembered title", "Source"],
                   [[f"**{w}**", p, src(s)] for w, p, s in TITLES])
    lines.append("")

    lines += ["## 5. Remembered words said to be missing now", "",
              "The reverse case: words the speakers remember *in* the Bible that",
              "they can no longer find. These are the earlier readings themselves.", ""]
    lines += table(["Remembered word", "Note", "KJV", "Source"],
                   [[f"**{w}**", n, cnt(w), src(s)] for w, n, s in MISSING])
    lines += ["", "---", "",
              f"Totals: {len(WITH_PRIOR)} words with a remembered reading, "
              f"{len(APPENDIX)} study-Bible appendix pairs, {len(NO_PRIOR)} words without one, "
              f"{len(NAMES)} names, {len(TITLES)} book titles, {len(MISSING)} missing words.",
              ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT, len(lines), "lines")
    for name, rows, col in (("WITH_PRIOR", WITH_PRIOR, 0), ("NO_PRIOR", NO_PRIOR, 1), ("APPENDIX", APPENDIX, 0)):
        zero = [r[col] for r in rows if kjv_count(r[col]) == 0]
        print(name, "zero-count:", zero)


if __name__ == "__main__":
    main()
