#!/usr/bin/env python3
"""custom_export.py — shared engine for the custom-edition exporters.

Used by:
  scripts/79_export_custom.py         — a custom edition of the restored text
  scripts/80_export_custom_modern.py  — an automatic modernization stacked
                                        on top of that custom edition

This is an importable module rather than a numbered task script (same role as
`scripts/residuals.py`). It only *reads* `db/mandela.db` — it never writes to
it — and emits markdown + PDF into `exports/custom/`.

A custom edition is built in layers:

  1. the restored Mandela text  (base KJV verses + every `status='approved'`
     restoration, exactly the text `17_export_full.py` exports)
  2. one or more settings layers, applied in order, each of which is a JSON
     file of global word/phrase replacements and whole-verse replacements
  3. (script 80 only) a built-in Early Modern → Modern English rule layer

The last layer supplies the edition's title and its BookIndex / BookLinks /
ChangeAppendix / CustomSettingAppendix flags.

The PDF writer is the same minimal pure-stdlib writer used by
`17_export_full.py` (Decision Log #10 — no PDF library in this environment and
pip dependencies require a logged decision). Layout: US Letter, 1in margins,
Times-Roman 10pt body.
"""

import json
import re
import sqlite3
import unicodedata
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
CUSTOM_DIR = REPO_ROOT / "custom"
OUT_DIR = REPO_ROOT / "exports" / "custom"

PAGE_W, PAGE_H = 612, 792
MARGIN = 72
BODY_SIZE, HEAD_SIZE, TITLE_SIZE = 10, 14, 26
LEADING = 13.5
# rough Times-Roman average char width factor for wrapping
CHARW = 0.48

KNOWN_SETTING_KEYS = {
    "VersionTitle", "BookIndex", "BookLinks", "ChangeAppendix",
    "RestorationAppendix", "CustomSettingAppendix", "GlobalReplacements",
    "VerseReplacements",
}

# Verse markers in the body text
MARK_RESTORED = "*"    # differs from the base KJV: a project restoration
MARK_CUSTOM = "†"      # differs from the restored text: this edition's settings

# --------------------------------------------------------------------------
# Built-in modernization rules (script 80)
#
# Early Modern English → Modern English. Curated on purpose: a blanket
# `-eth`/`-est` suffix regex wrecks priest, rest, lest, teeth, harvest, west,
# forest, manifest, greatest, highest, best, request, twentieth and Nazareth,
# so only attested verb forms are listed. Every entry here can be overridden
# or removed by the modernization settings file's GlobalReplacements.
# --------------------------------------------------------------------------
# Context-sensitive rules, tried BEFORE the literal word keys below.
#
# "thine" is two different words. Attributive, it modifies a noun and
# modernizes to "your" (thine eyes → your eyes). Absolute, it is a pronoun in
# its own right and modernizes to "yours" ("for thine is the kingdom" → "for
# yours is the kingdom"; "not my will, but thine, be done" → "but yours").
# A word-for-word map cannot tell them apart, so the absolute case gets a
# pattern: "thine" followed by no word at all (punctuation or end of verse), or
# by one of the verbs/function words that can only follow a pronoun. Verified
# against the restored text: 59 absolute instances, 43 of the first shape and
# 16 of the second — Gen 31:32, Num 18:9, Deut 15:3, Deut 30:4, II Sam 16:4,
# I Chr 12:18, I Chr 21:24, I Chr 29:11, Jer 32:7, Matt 6:13, Matt 20:14,
# Luke 6:20, Luke 11:4, John 15:20, John 17:6, John 17:10.
#
# A settings file that sets its own "thine" rule switches this off, the same
# way it can override any other built-in (see modernization_layer).
ABSOLUTE_THINE_FOLLOWERS = ("is", "are", "was", "were", "be", "with", "for",
                            "to", "they", "of", "also")
CONTEXT_RULES = [(
    "absolute_thine",
    r"thine\b(?:(?!\s+[A-Za-z])|(?=\s+(?:"
    + "|".join(ABSOLUTE_THINE_FOLLOWERS) + r")\b))",
    "yours",
)]

MODERN_RULES = {
    # pronouns and possessives
    "thee": "you", "thou": "you", "thy": "your", "thine": "your",
    "ye": "you", "thyself": "yourself",
    # irregular / auxiliary verbs
    "art": "are", "wast": "were", "wert": "were", "hast": "have",
    "hath": "has", "doth": "does", "dost": "do", "doeth": "does",
    "shalt": "shall", "wilt": "will", "canst": "can", "couldest": "could",
    "shouldest": "should", "wouldest": "would", "mayest": "may",
    "mightest": "might", "didst": "did", "hadst": "had", "haddest": "had",
    "knowest": "know", "knewest": "knew", "sayest": "say", "saidst": "said",
    "seest": "see", "sawest": "saw", "goest": "go", "wentest": "went",
    "comest": "come", "camest": "came", "makest": "make", "madest": "made",
    "gavest": "gave", "givest": "give", "takest": "take", "tookest": "took",
    "hearest": "hear", "heardest": "heard", "speakest": "speak",
    "spakest": "spoke", "lovest": "love", "livest": "live",
    "dwellest": "dwell", "walkest": "walk", "believest": "believe",
    "receivest": "receive", "keepest": "keep", "callest": "call",
    "eatest": "eat", "drinkest": "drink", "judgest": "judge",
    "seekest": "seek", "findest": "find", "bringest": "bring",
    "sendest": "send", "settest": "set", "puttest": "put",
    "castest": "cast", "askest": "ask", "answerest": "answer",
    "beholdest": "behold", "sittest": "sit", "standest": "stand",
    "sufferest": "suffer", "regardest": "regard", "rememberest": "remember",
    "requirest": "require", "teachest": "teach", "tellest": "tell",
    "thinkest": "think", "trustest": "trust", "turnest": "turn",
    "workest": "work", "writest": "write", "fearest": "fear",
    "followest": "follow", "forsakest": "forsake", "hidest": "hide",
    "holdest": "hold", "leadest": "lead", "liest": "lie",
    # third person -eth
    "cometh": "comes", "goeth": "goes", "maketh": "makes",
    "giveth": "gives", "knoweth": "knows", "liveth": "lives",
    "bringeth": "brings", "taketh": "takes", "speaketh": "speaks",
    "loveth": "loves", "lieth": "lies", "endureth": "endures",
    "dwelleth": "dwells", "seeth": "sees", "eateth": "eats",
    "heareth": "hears", "keepeth": "keeps", "believeth": "believes",
    "seeketh": "seeks", "sitteth": "sits", "walketh": "walks",
    "turneth": "turns", "toucheth": "touches", "passeth": "passes",
    "worketh": "works", "remaineth": "remains", "receiveth": "receives",
    "looketh": "looks", "causeth": "causes", "standeth": "stands",
    "putteth": "puts", "hateth": "hates", "dieth": "dies",
    "calleth": "calls", "abideth": "abides", "falleth": "falls",
    "findeth": "finds", "covereth": "covers", "beareth": "bears",
    "setteth": "sets", "killeth": "kills", "sinneth": "sins",
    "belongeth": "belongs", "sheweth": "shows", "showeth": "shows",
    "openeth": "opens", "feareth": "fears", "entereth": "enters",
    "despiseth": "despises", "faileth": "fails", "judgeth": "judges",
    "sendeth": "sends", "leadeth": "leads", "followeth": "follows",
    "hangeth": "hangs", "healeth": "heals", "helpeth": "helps",
    "holdeth": "holds", "hideth": "hides", "increaseth": "increases",
    "layeth": "lays", "letteth": "lets", "lifteth": "lifts",
    "lodgeth": "lodges", "loseth": "loses", "meeteth": "meets",
    "needeth": "needs", "offereth": "offers", "payeth": "pays",
    "perisheth": "perishes", "prayeth": "prays", "raiseth": "raises",
    "readeth": "reads", "reigneth": "reigns", "rejoiceth": "rejoices",
    "remembereth": "remembers", "returneth": "returns", "riseth": "rises",
    "ruleth": "rules", "runneth": "runs", "saveth": "saves",
    "sayeth": "says", "saith": "says", "serveth": "serves",
    "sheddeth": "sheds", "shineth": "shines", "sleepeth": "sleeps",
    "speedeth": "speeds", "spreadeth": "spreads", "striveth": "strives",
    "suffereth": "suffers", "teacheth": "teaches", "telleth": "tells",
    "thinketh": "thinks", "trusteth": "trusts", "understandeth":
    "understands", "waiteth": "waits", "wanteth": "wants",
    "watcheth": "watches", "weareth": "wears", "weepeth": "weeps",
    "willeth": "wills", "worshippeth": "worships", "writeth": "writes",
    "yieldeth": "yields", "asketh": "asks", "answereth": "answers",
    "beholdeth": "beholds", "blesseth": "blesses", "breaketh": "breaks",
    "buildeth": "builds", "buyeth": "buys", "carrieth": "carries",
    "casteth": "casts", "chooseth": "chooses", "cleanseth": "cleanses",
    "commandeth": "commands", "confesseth": "confesses",
    "considereth": "considers", "createth": "creates", "crieth": "cries",
    "cutteth": "cuts", "delivereth": "delivers", "departeth": "departs",
    "destroyeth": "destroys", "doubteth": "doubts", "draweth": "draws",
    "drinketh": "drinks", "driveth": "drives", "dwelt": "dwelt",
    "escheweth": "shuns", "exalteth": "exalts", "feedeth": "feeds",
    "fighteth": "fights", "filleth": "fills", "flieth": "flies",
    "forgetteth": "forgets", "forsaketh": "forsakes", "gathereth":
    "gathers", "getteth": "gets", "groweth": "grows", "guideth": "guides",
    # archaic verb spellings and vocabulary
    "spake": "spoke", "brake": "broke", "sware": "swore", "clave": "clung",
    "durst": "dared", "wist": "knew", "wot": "knows", "holpen": "helped",
    "shew": "show", "shewed": "showed", "shewing": "showing",
    "shewest": "show", "shewn": "shown",
    "unto": "to", "verily": "truly", "hearken": "listen",
    "yea": "yes", "nay": "no", "twain": "two", "betwixt": "between",
    "ere": "before", "oft": "often", "peradventure": "perhaps",
    "howbeit": "however", "straightway": "immediately",
    "whence": "where", "whither": "where", "hither": "here",
    "thither": "there", "naught": "nothing", "nigh": "near",
    "forasmuch as": "since", "insomuch that": "so that",
    "save that": "except that",
}

# --------------------------------------------------------------------------
# Automatic -eth / -est verb rule (script 80)
#
# The curated table above cannot list every archaic verb form (the text holds
# 569 distinct -eth and 269 distinct -est words). The rest are handled by a
# guarded rule: a word is only rewritten when a plausible base form is itself
# a word in the text ("restoreth" → "restore" → "restores"), which by itself
# already protects the noun/name cases (priest, harvest, request, tempest,
# Nazareth, Mephibosheth, Elizabeth — no base of theirs is a word). The
# blocklists below cover the survivors: ordinals, and the -est superlatives
# whose base IS a word (greatest → great).
# --------------------------------------------------------------------------
# The {2,} counts the letters BEFORE the suffix; the real guard is the base
# check in `make_archaic_verb_rule` (len(base) >= 3 and base is a word).
ARCHAIC_VERB_PATTERN = r"[A-Za-z]{2,}(?:eth|est)\b"

_ORDINALS = {
    "twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth",
    "seventieth", "eightieth", "ninetieth", "hundredth", "thousandth",
}
ETH_BLOCKLIST = _ORDINALS | {
    "teeth", "beneath", "nazareth", "japheth", "elizabeth", "mephibosheth",
    "ashtoreth", "azmaveth", "chinnereth", "harosheth", "alemeth", "bosheth",
}
EST_BLOCKLIST = {
    # superlatives whose base is also a word in the text
    "greatest", "highest", "youngest", "lowest", "smallest", "fairest",
    "finest", "choicest", "basest", "valiantest", "poorest", "vilest",
    "strongest", "fewest", "meetest", "chiefest", "wisest", "oldest",
    "longest", "largest", "nearest", "deepest", "sweetest", "hardest",
    "richest", "purest", "safest", "latest", "loudest", "worst",
    # nouns / adjectives that survive the base-word guard
    "forest", "dishonest", "honest", "earnest", "modest", "harvest",
    "priest", "manifest", "request", "tempest", "protest", "conquest",
    "interest", "arrest", "invest", "digest",
}


def _verb_bases(word: str):
    """Plausible base forms for an archaic `-eth` / `-est` verb."""
    stem3, stem2 = word[:-3], word[:-2]
    bases = [stem2, stem3]
    if stem3.endswith("i"):                       # crieth  → cry
        bases.append(stem3[:-1] + "y")
    if len(stem3) > 2 and stem3[-1] == stem3[-2] and stem3[-1] not in "aeiou":
        bases.append(stem3[:-1])                  # sitteth → sit
    return bases


def _third_person(base: str) -> str:
    if re.search(r"(s|x|z|ch|sh|o)$", base):
        return base + "es"
    if re.search(r"[^aeiou]y$", base):
        return base[:-1] + "ies"
    return base + "s"


def make_archaic_verb_rule(vocab):
    """Handler for words the curated table does not list. None = leave it."""

    def handler(word: str):
        low = word.lower()
        if low.endswith("eth"):
            if low in ETH_BLOCKLIST:
                return None
            for base in _verb_bases(low):
                if len(base) >= 3 and base in vocab:
                    return _third_person(base)
        elif low.endswith("est"):
            if low in EST_BLOCKLIST:
                return None
            for base in _verb_bases(low):
                if len(base) >= 3 and base in vocab:
                    return base          # "thou knowest" → "you know"
        return None

    return handler


# Book-name aliases people are likely to type in a settings file. Keys and
# values are normalized names (see `_norm`).
BOOK_ALIASES = {
    "revelation": "revelation of john",
    "revelations": "revelation of john",
    "the revelation": "revelation of john",
    "revelation of jesus christ": "revelation of john",
    "apocalypse": "revelation of john",
    "psalm": "psalms",
    "song of songs": "song of solomon",
    "canticles": "song of solomon",
    "acts of the apostles": "acts",
    "the acts": "acts",
    "ecclesiastes the preacher": "ecclesiastes",
    "solomons song": "song of solomon",
}

_NUMERALS = {
    "1": "i", "1st": "i", "first": "i", "i": "i",
    "2": "ii", "2nd": "ii", "second": "ii", "ii": "ii",
    "3": "iii", "3rd": "iii", "third": "iii", "iii": "iii",
}


# --------------------------------------------------------------------------
# settings
# --------------------------------------------------------------------------
class SettingsError(Exception):
    """Raised for a settings file that cannot be used as written."""


class Settings:
    """One custom-edition settings JSON file."""

    def __init__(self, path, data):
        self.path = Path(path)
        if not isinstance(data, dict):
            raise SettingsError(f"{path}: top level must be a JSON object")
        self.warnings = []
        for key in data:
            if key not in KNOWN_SETTING_KEYS:
                self.warnings.append(
                    f"{self.path.name}: unknown setting '{key}' ignored")

        title = data.get("VersionTitle")
        if not title or not str(title).strip():
            raise SettingsError(f"{path}: 'VersionTitle' is required")
        self.title = str(title).strip()

        self.book_index = _flag(data.get("BookIndex"), True)
        # BookLinks follows BookIndex unless it is set explicitly
        self.book_links = _flag(data.get("BookLinks"), self.book_index)
        links_explicit = "BookLinks" in data
        self.change_appendix = _flag(data.get("ChangeAppendix"), True)
        self.restoration_appendix = _flag(data.get("RestorationAppendix"), True)
        self.custom_setting_appendix = _flag(
            data.get("CustomSettingAppendix"), True)

        glob = data.get("GlobalReplacements") or {}
        if not isinstance(glob, dict):
            raise SettingsError(f"{path}: 'GlobalReplacements' must be an object")
        self.global_replacements = {str(k): str(v) for k, v in glob.items()}

        verses = data.get("VerseReplacements") or {}
        if not isinstance(verses, dict):
            raise SettingsError(f"{path}: 'VerseReplacements' must be an object")
        self.verse_replacements = verses

        if self.book_links and not self.book_index:
            if links_explicit:
                self.warnings.append(
                    f"{self.path.name}: 'BookLinks' needs 'BookIndex' — no "
                    "index to link to, so book links are omitted")
            self.book_links = False


def _flag(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("yes", "y", "true", "1", "on")


def load_settings(path) -> Settings:
    path = Path(path)
    if not path.exists():
        raise SettingsError(f"settings file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SettingsError(f"{path}: invalid JSON — {exc}") from exc
    return Settings(path, data)


# --------------------------------------------------------------------------
# replacement engine
# --------------------------------------------------------------------------
def match_case(src: str, repl: str) -> str:
    """Give `repl` the capitalization of the text it replaces."""
    if not repl:
        return repl
    letters = [c for c in src if c.isalpha()]
    if not letters:
        return repl
    if len(letters) > 1 and all(c.isupper() for c in letters):
        return repl.upper()
    if letters[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def compile_replacements(mapping, generic=None, context=None):
    """Build one case-insensitive regex over every key.

    A single alternation means replacements are applied in ONE pass, so they
    cannot cascade into each other (thee→you followed by you→ye would
    otherwise turn "thee" into "ye"). Longest keys are tried first, and
    word-ish keys get \\b boundaries while punctuation keys stay literal.

    `context` is an optional list of (name, pattern, replacement) tried FIRST,
    for rules a word-for-word map cannot express because they depend on what
    surrounds the word (the absolute "thine" → "yours"). They are prepended so
    they win over the literal key for the same word; each carries a named group
    so `apply_replacements` can tell which one fired.

    `generic` is an optional pattern appended LAST, so an explicit key always
    wins over it — that is what lets a settings file override (or switch off,
    by mapping a word to itself) the automatic -eth/-est rule.
    """
    entries = {}
    for key, val in mapping.items():
        key = str(key)
        if not key.strip():
            continue
        entries[key.lower()] = str(val)
    context = list(context or [])
    if not entries and not generic and not context:
        return None, {}, {}
    parts = []
    ctx = {}
    for name, pattern, replacement in context:
        ctx[name] = replacement
        parts.append(f"(?P<{name}>{pattern})")
    for key in sorted(entries, key=len, reverse=True):
        pat = re.escape(key)
        if re.match(r"^[0-9A-Za-z]", key):
            pat = r"\b" + pat
        if re.search(r"[0-9A-Za-z]$", key):
            pat = pat + r"\b"
        parts.append(pat)
    if generic:
        parts.append(r"\b" + generic)
    return re.compile("|".join(parts), re.IGNORECASE), entries, ctx


def apply_replacements(text, compiled, counts=None, handler=None):
    rx, entries, ctx = compiled
    if rx is None:
        return text

    def _sub(m):
        src = m.group(0)
        if m.lastgroup in ctx:                 # matched a context rule
            repl, key = ctx[m.lastgroup], f"({m.lastgroup} rule)"
        else:
            repl = entries.get(src.lower())
            if repl is None:                   # matched the generic pattern
                if handler is None:
                    return src
                repl = handler(src)
                if repl is None:
                    return src
                key = GENERIC_COUNT_KEY
            else:
                key = src.lower()
        if counts is not None:
            counts[key] = counts.get(key, 0) + 1
        return match_case(src, repl)

    return rx.sub(_sub, text)


GENERIC_COUNT_KEY = "(automatic -eth/-est verb rule)"


# --------------------------------------------------------------------------
# book-name resolution
# --------------------------------------------------------------------------
def _norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    m = re.match(r"^(1st|2nd|3rd|first|second|third|iii|ii|i|1|2|3)\s+(.+)$", s)
    if m:
        s = f"{_NUMERALS[m.group(1)]} {m.group(2)}"
    return s


def resolve_book(name, books):
    """Resolve a settings-file book name to a (book_id, canonical name)."""
    by_norm = {_norm(bname): (bid, bname) for bid, bname in books}
    key = _norm(name)
    for candidate in (key, BOOK_ALIASES.get(key, ""),
                      key[:-1] if key.endswith("s") else key + "s"):
        if candidate and candidate in by_norm:
            return by_norm[candidate]
    hits = [v for k, v in by_norm.items() if k.startswith(key)]
    if len(hits) == 1:
        return hits[0]
    return None


# --------------------------------------------------------------------------
# layers
# --------------------------------------------------------------------------
class Layer:
    """One stacked transformation: global replacements + verse replacements."""

    def __init__(self, label, mapping, verse_replacements=None, settings=None,
                 sources=None, context=None):
        self.label = label
        self.settings = settings
        self.mapping = dict(mapping)
        # optional provenance for a merged mapping: lowercased key -> origin
        self.sources = dict(sources or {})
        # context-sensitive rules (see CONTEXT_RULES); only script 80's layer
        self.context = list(context or [])
        self.compiled = compile_replacements(self.mapping, context=self.context)
        self.raw_verses = verse_replacements or {}
        self.verses = {}       # (book_id, chapter, verse) -> (text, comment)
        self.counts = {}       # lowercased key -> times replaced
        self.warnings = []
        self.verb_rule = None  # set by enable_verb_rule() on script 80's layer
        self.wants_verb_rule = False

    def enable_verb_rule(self, vocab):
        """Turn on the automatic -eth/-est rule, guarded by `vocab`."""
        self.verb_rule = make_archaic_verb_rule(vocab)
        self.compiled = compile_replacements(
            self.mapping, ARCHAIC_VERB_PATTERN, context=self.context)

    def resolve(self, books):
        self.verses = {}
        for book_name, chapters in self.raw_verses.items():
            found = resolve_book(book_name, books)
            if not found:
                self.warnings.append(
                    f"{self.label}: unknown book '{book_name}' — skipped")
                continue
            bid, canonical = found
            if not isinstance(chapters, dict):
                self.warnings.append(
                    f"{self.label}: '{book_name}' must map chapters to verses")
                continue
            for ch, verses in chapters.items():
                if not isinstance(verses, dict):
                    self.warnings.append(
                        f"{self.label}: {canonical} {ch} must map verses to "
                        "replacements")
                    continue
                for vs, entry in verses.items():
                    try:
                        ch_i, vs_i = int(str(ch).strip()), int(str(vs).strip())
                    except ValueError:
                        self.warnings.append(
                            f"{self.label}: {canonical} {ch}:{vs} — chapter and "
                            "verse must be numbers")
                        continue
                    if isinstance(entry, str):
                        text, comment = entry, ""
                    elif isinstance(entry, dict):
                        text = entry.get("replacement")
                        comment = str(entry.get("comment") or "")
                    else:
                        text, comment = None, ""
                    if not text or not str(text).strip():
                        self.warnings.append(
                            f"{self.label}: {canonical} {ch_i}:{vs_i} — missing "
                            "'replacement' text, skipped")
                        continue
                    self.verses[(bid, ch_i, vs_i)] = (str(text).strip(), comment)

    def apply(self, key, text):
        """Verse replacements win and are taken verbatim; else replacements."""
        if key in self.verses:
            return self.verses[key][0], "verse"
        new = apply_replacements(text, self.compiled, self.counts, self.verb_rule)
        return new, ("global" if new != text else None)


def modernization_layer(settings=None):
    """The built-in modernization rules, with a settings file layered in.

    The user's GlobalReplacements are merged INTO the built-in map rather than
    applied as a later layer, so a settings file can genuinely override a
    built-in rule (a later layer never could: the built-in pass would already
    have consumed the word). Verse replacements from the same settings file
    ride along on this layer and, as always, win over the word rules.
    """
    mapping = dict(MODERN_RULES)
    sources = {k.lower(): "built-in" for k in mapping}
    label = "built-in modernization"
    verses = None
    overridden = set()
    if settings:
        for key, val in settings.global_replacements.items():
            sources[key.lower()] = (
                "settings (overrides built-in)" if key.lower() in sources
                else "settings")
            mapping[key] = val
            overridden.add(key.lower())
        verses = settings.verse_replacements
        label = f"modernization (built-in rules + {settings.path.name})"
    # A settings file that states its own "thine" rule switches the
    # context-sensitive absolute-possessive rule off, the same way it can
    # override any other built-in.
    context = [] if "thine" in overridden else CONTEXT_RULES
    layer = Layer(label, mapping, verses, settings, sources, context)
    layer.wants_verb_rule = True
    return layer


# --------------------------------------------------------------------------
# PDF writer (same minimal stdlib writer as 17_export_full.py)
# --------------------------------------------------------------------------
def esc(s: str) -> bytes:
    b = s.replace("’", "\x92").replace("‘", "\x91").replace("–", "\x96") \
         .replace("—", "\x97").replace("“", "\x93").replace("”", "\x94")
    b = b.encode("cp1252", errors="replace")
    return b.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def wrap(text: str, size: float, width: float):
    maxc = max(10, int(width / (size * CHARW)))
    out, line = [], ""
    for word in text.split():
        cand = f"{line} {word}".strip()
        if len(cand) <= maxc:
            line = cand
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out


class Pdf:
    def __init__(self):
        self.pages = []
        self.buf = []
        self.y = PAGE_H - MARGIN
        self.pageno = 0

    def newpage(self):
        if self.buf:
            self.flush()
        self.pageno += 1
        self.buf = []
        self.y = PAGE_H - MARGIN

    def flush(self):
        footer = (f"BT /F1 8 Tf {PAGE_W/2-12:.0f} {MARGIN-30} Td "
                  f"({self.pageno}) Tj ET")
        self.pages.append("\n".join(self.buf + [footer]))

    def need(self, h):
        if self.y - h < MARGIN:
            self.newpage()

    def text(self, s, size=BODY_SIZE, font="F1", indent=0, dy=None):
        self.need(size + 4)
        self.y -= dy if dy is not None else LEADING * (size / BODY_SIZE)
        self.buf.append(f"BT /{font} {size} Tf {MARGIN + indent} {self.y:.1f} Td "
                        f"({esc(s).decode('latin-1')}) Tj ET")

    def para(self, s, size=BODY_SIZE, font="F1", indent=0):
        for ln in wrap(s, size, PAGE_W - 2 * MARGIN - indent):
            self.text(ln, size, font, indent)

    def space(self, h):
        self.y -= h

    def build(self) -> bytes:
        if self.buf:
            self.flush()
        objs = []
        n_pages = len(self.pages)
        kids = " ".join(f"{6 + 2*i} 0 R" for i in range(n_pages))
        objs.append((1, b"<< /Type /Catalog /Pages 2 0 R >>"))
        objs.append((2, f"<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>".encode()))
        for num, base in [(3, "Times-Roman"), (4, "Times-Bold"),
                          (5, "Helvetica-Bold")]:
            objs.append((num, (f"<< /Type /Font /Subtype /Type1 /BaseFont /{base} "
                               "/Encoding /WinAnsiEncoding >>").encode()))
        for i, content in enumerate(self.pages):
            pnum, cnum = 6 + 2 * i, 7 + 2 * i
            objs.append((pnum, (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} "
                                f"{PAGE_H}] /Resources << /Font << /F1 3 0 R /F2 4 0 R "
                                f"/F3 5 0 R >> >> /Contents {cnum} 0 R >>").encode()))
            data = zlib.compress(content.encode("latin-1"))
            objs.append((cnum, b"<< /Length " + str(len(data)).encode()
                         + b" /Filter /FlateDecode >>\nstream\n" + data + b"\nendstream"))

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}
        for num, body in sorted(objs):
            offsets[num] = len(out)
            out += f"{num} 0 obj\n".encode() + body + b"\nendobj\n"
        xref_at = len(out)
        maxn = max(offsets) + 1
        out += f"xref\n0 {maxn}\n0000000000 65535 f \n".encode()
        for n in range(1, maxn):
            out += f"{offsets[n]:010d} 00000 n \n".encode()
        out += (f"trailer\n<< /Size {maxn} /Root 1 0 R >>\nstartxref\n"
                f"{xref_at}\n%%EOF\n").encode()
        return bytes(out)


# --------------------------------------------------------------------------
# text assembly
# --------------------------------------------------------------------------
def load_restored_text(con):
    """Base KJV with every approved restoration applied (as 17_export_full)."""
    resto = {}
    for vid, _rid, new in con.execute(
            "SELECT verse_id, id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):  # rows compose; the last (highest id) is complete
        resto[vid] = new
    books = con.execute(
        "SELECT id, name FROM books WHERE translation='KJV' ORDER BY id").fetchall()
    verses = []
    for bid, name in books:
        for vid, ch, vs, text in con.execute(
                "SELECT id, chapter, verse, text FROM verses WHERE translation='KJV' "
                "AND book_id=? ORDER BY chapter, verse", (bid,)):
            verses.append((bid, name, ch, vs, resto.get(vid, text), vid in resto))
    return books, verses, len(resto)


def load_restorations(con):
    """The approved restorations, for the Restoration Appendix (as script 17)."""
    return con.execute(
        """SELECT r.id, b.name, v.chapter, v.verse, r.current_text, r.proposed_text
           FROM restorations r
           JOIN verses v ON v.id=r.verse_id
           JOIN books b ON b.translation='KJV' AND b.id=v.book_id
           WHERE r.status='approved' AND r.proposed_text IS NOT NULL
           ORDER BY b.id, v.chapter, v.verse""").fetchall()


def slugify(title: str) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "custom-edition"


def anchor(name: str) -> str:
    """GitHub-style markdown anchor for a `## <name>` heading."""
    s = name.lower()
    s = re.sub(r"[^a-z0-9 -]+", "", s)
    return s.replace(" ", "-")


def build_edition(layers, out_dir=OUT_DIR, db_path=DB_PATH):
    """Apply every layer to the restored text and write markdown + PDF."""
    if not layers:
        raise SettingsError("at least one settings layer is required")
    edition = next(l for l in reversed(layers) if l.settings)
    cfg = edition.settings

    con = sqlite3.connect(db_path)
    books, verses, n_resto = load_restored_text(con)
    restorations = load_restorations(con) if cfg.restoration_appendix else []
    con.close()

    warnings = []
    vocab = None
    for layer in layers:
        if layer.settings:
            warnings.extend(layer.settings.warnings)
        layer.resolve(books)
        warnings.extend(layer.warnings)
        if layer.wants_verb_rule:
            if vocab is None:
                vocab = {w for _b, _n, _c, _v, text, _r in verses
                         for w in re.findall(r"[A-Za-z]+", text.lower())}
            layer.enable_verb_rule(vocab)

    rendered = []   # (book_id, book, chapter, verse, text, changed, restored)
    changes = []    # (book, chapter, verse, base, final, kinds, comments)
    for bid, name, ch, vs, base, restored in verses:
        text, kinds, comments = base, [], []
        for layer in layers:
            text, kind = layer.apply((bid, ch, vs), text)
            if kind:
                kinds.append(f"{layer.label}: {kind}")
            if kind == "verse":
                comment = layer.verses[(bid, ch, vs)][1]
                if comment:
                    comments.append(comment)
        changed = text != base
        rendered.append((bid, name, ch, vs, text, changed, restored))
        if changed:
            changes.append((name, ch, vs, base, text, kinds, comments))

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = slugify(cfg.title)
    md_path = out_dir / f"{stem}.md"
    pdf_path = out_dir / f"{stem}.pdf"

    md_path.write_text(
        _markdown(cfg, layers, books, rendered, changes, n_resto, restorations),
        encoding="utf-8")
    pdf = _pdf(cfg, layers, books, rendered, changes, n_resto, restorations)
    pdf_path.write_bytes(pdf.build())

    return {
        "title": cfg.title,
        "md": md_path,
        "pdf": pdf_path,
        "pages": pdf.pageno,
        "restorations": n_resto,
        "changes": len(changes),
        "warnings": warnings,
        "layers": layers,
    }


def _intro(cfg, layers, n_resto, n_changes):
    names = " → ".join(l.label for l in layers)
    text = (f"A custom edition of The Mandela Bible. Base text: the restored "
            f"King James Bible with {n_resto} owner-approved restorations "
            f"applied. Layers on top of it: {names}. "
            f"{n_changes} verses differ from the restored text"
            + (" — every one is listed in the Change Appendix."
               if cfg.change_appendix else "."))
    marks = []
    if cfg.restoration_appendix:
        marks.append(f"{MARK_RESTORED} marks a verse restored from the base "
                     "King James text (Restoration Appendix)")
    if cfg.change_appendix:
        marks.append(f"{MARK_CUSTOM} marks a verse changed by this edition's "
                     "settings (Change Appendix)")
    if marks:
        text += " " + "; ".join(marks) + "."
    return text


def _marks(cfg, changed, restored):
    return ((MARK_RESTORED if restored and cfg.restoration_appendix else "")
            + (MARK_CUSTOM if changed and cfg.change_appendix else ""))


def _markdown(cfg, layers, books, rendered, changes, n_resto, restorations):
    md = [f"# {cfg.title}", "", f"*{_intro(cfg, layers, n_resto, len(changes))}*", ""]
    if cfg.book_index:
        md += ["## Contents", ""]
        for _bid, name in books:
            md.append(f"- [{name}](#{anchor(name)})" if cfg.book_links
                      else f"- {name}")
        md.append("")

    cur_book, cur_ch = None, None
    for _bid, name, ch, vs, text, changed, restored in rendered:
        if name != cur_book:
            md += ["", f"## {name}", ""]
            if cfg.book_links:
                md += ["[↑ Contents](#contents)", ""]
            cur_book, cur_ch = name, None
        if ch != cur_ch:
            md += [f"### Chapter {ch}", ""]
            cur_ch = ch
        md.append(f"**{vs}**{_marks(cfg, changed, restored)} {text}")

    if cfg.change_appendix:
        md += ["", "## Change Appendix", "",
               f"Every verse marked with {MARK_CUSTOM} differs from the "
               "restored Mandela text. The reading it replaced is preserved "
               "here.", ""]
        for name, ch, vs, base, final, kinds, comments in changes:
            md.append(f"- **{name} {ch}:{vs}** ({'; '.join(kinds)})")
            md.append(f"  - was: {base}")
            md.append(f"  - now: {final}")
            for comment in comments:
                md.append(f"  - comment: {comment}")

    if cfg.restoration_appendix:
        md += ["", "## Restoration Appendix", "",
               f"Every verse marked with {MARK_RESTORED} differs from the base "
               "King James text. These are the project's owner-approved, "
               "memory-led restorations; the original readings are preserved "
               "here and the full rationale lives in the project's "
               "restorations database.", ""]
        for rid, name, ch, vs, cur, new in restorations:
            md += [f"- **{name} {ch}:{vs}** (#{rid})",
                   f"  - was: {cur}", f"  - now: {new}"]

    if cfg.custom_setting_appendix:
        md += ["", "## Custom Setting Appendix", "",
               "The settings this edition was built from.", ""]
        for layer in layers:
            md += [f"### {layer.label}", ""]
            if layer.settings:
                s = layer.settings
                md += [f"- Settings file: `{s.path.name}`",
                       f"- VersionTitle: {s.title}",
                       f"- BookIndex: {'yes' if s.book_index else 'no'}",
                       f"- BookLinks: {'yes' if s.book_links else 'no'}",
                       f"- ChangeAppendix: {'yes' if s.change_appendix else 'no'}",
                       "- CustomSettingAppendix: "
                       f"{'yes' if s.custom_setting_appendix else 'no'}", ""]
            if layer.mapping:
                head = "| from | to | times applied |"
                rule = "|---|---|---|"
                if layer.sources:
                    head, rule = head + " source |", rule + "---|"
                md += [f"**Global replacements ({len(layer.mapping)})**", "",
                       head, rule]
                for key in sorted(layer.mapping, key=str.lower):
                    row = (f"| `{key}` | `{layer.mapping[key]}` | "
                           f"{layer.counts.get(key.lower(), 0)} |")
                    if layer.sources:
                        row += f" {layer.sources.get(key.lower(), '')} |"
                    md.append(row)
                md.append("")
            if layer.verb_rule:
                md += ["**Automatic -eth/-est verb rule**: "
                       f"{layer.counts.get(GENERIC_COUNT_KEY, 0)} further "
                       "archaic verb forms modernized (any word the table "
                       "above does not list, when a base form of it is itself "
                       "a word in the text).", ""]
            if layer.verses:
                md += [f"**Verse replacements ({len(layer.verses)})**", ""]
                by_book = {bid: name for bid, name in books}
                for (bid, ch, vs), (_text, comment) in sorted(layer.verses.items()):
                    md.append(f"- {by_book[bid]} {ch}:{vs}"
                              + (f" — {comment}" if comment else ""))
                md.append("")
    return "\n".join(md) + "\n"


def _pdf(cfg, layers, books, rendered, changes, n_resto, restorations):
    """Render the PDF; twice when a contents page needs real page numbers."""
    pages = {}
    for _pass in range(2 if cfg.book_index else 1):
        pdf, pages = _pdf_pass(cfg, layers, books, rendered, changes, n_resto,
                               restorations, pages)
    return pdf


def _pdf_pass(cfg, layers, books, rendered, changes, n_resto, restorations,
              known_pages):
    pdf = Pdf()
    pdf.newpage()
    pdf.space(180)
    pdf.text(cfg.title, TITLE_SIZE, "F3")
    pdf.space(10)
    pdf.para("A custom edition of The Mandela Bible", 12, "F2")
    pdf.space(30)
    pdf.para(_intro(cfg, layers, n_resto, len(changes)), 10)
    pdf.space(14)
    pdf.text("mandelabible.com", 10)

    if cfg.book_index:
        pdf.newpage()
        pdf.space(20)
        pdf.text("Contents", 20, "F3")
        pdf.space(8)
        for _bid, name in books:
            page = known_pages.get(name)
            pdf.text(f"{name}" + (f" — page {page}" if page else ""), 10)

    book_pages = {}
    cur_book, cur_ch = None, None
    for _bid, name, ch, vs, text, changed, restored in rendered:
        if name != cur_book:
            pdf.newpage()
            book_pages[name] = pdf.pageno
            pdf.space(30)
            pdf.text(name, 20, "F3")
            pdf.space(8)
            cur_book, cur_ch = name, None
        if ch != cur_ch:
            pdf.space(6)
            pdf.text(f"Chapter {ch}", HEAD_SIZE, "F2")
            pdf.space(3)
            cur_ch = ch
        pdf.para(f"{vs}{_marks(cfg, changed, restored)}  {text}")

    if cfg.change_appendix:
        pdf.newpage()
        pdf.space(20)
        pdf.text("Change Appendix", 20, "F3")
        pdf.space(6)
        pdf.para(f"Every verse marked with {MARK_CUSTOM} differs from the "
                 "restored Mandela text. The reading it replaced is preserved "
                 "below.", 9)
        for name, ch, vs, base, final, kinds, comments in changes:
            pdf.space(5)
            pdf.para(f"{name} {ch}:{vs}  ({'; '.join(kinds)})", 9, "F2")
            pdf.para(f"was: {base}", 8, indent=12)
            pdf.para(f"now: {final}", 8, indent=12)
            for comment in comments:
                pdf.para(f"comment: {comment}", 8, indent=12)

    if cfg.restoration_appendix:
        pdf.newpage()
        pdf.space(20)
        pdf.text("Restoration Appendix", 20, "F3")
        pdf.space(6)
        pdf.para(f"Every verse marked with {MARK_RESTORED} differs from the "
                 "base King James text. These are the project's owner-approved, "
                 "memory-led restorations; the original readings are preserved "
                 "below and the full rationale lives in the project's "
                 "restorations database.", 9)
        for rid, name, ch, vs, cur, new in restorations:
            pdf.space(5)
            pdf.para(f"{name} {ch}:{vs}  (restoration #{rid})", 9, "F2")
            pdf.para(f"was: {cur}", 8, indent=12)
            pdf.para(f"now: {new}", 8, indent=12)

    if cfg.custom_setting_appendix:
        pdf.newpage()
        pdf.space(20)
        pdf.text("Custom Setting Appendix", 20, "F3")
        pdf.space(6)
        pdf.para("The settings this edition was built from.", 9)
        by_book = {bid: name for bid, name in books}
        for layer in layers:
            pdf.space(8)
            pdf.para(layer.label, 12, "F2")
            if layer.settings:
                s = layer.settings
                pdf.para(f"settings file: {s.path.name}", 9, indent=12)
                pdf.para(
                    f"BookIndex: {'yes' if s.book_index else 'no'};  "
                    f"BookLinks: {'yes' if s.book_links else 'no'};  "
                    f"ChangeAppendix: {'yes' if s.change_appendix else 'no'};  "
                    "CustomSettingAppendix: "
                    f"{'yes' if s.custom_setting_appendix else 'no'}",
                    9, indent=12)
            if layer.mapping:
                pdf.space(4)
                pdf.para(f"Global replacements ({len(layer.mapping)})", 9, "F2",
                         indent=12)
                for key in sorted(layer.mapping, key=str.lower):
                    origin = layer.sources.get(key.lower(), "")
                    pdf.para(f"{key} -> {layer.mapping[key]}  "
                             f"({layer.counts.get(key.lower(), 0)})"
                             + (f"  [{origin}]" if origin else ""), 8, indent=24)
            if layer.verb_rule:
                pdf.space(4)
                pdf.para("Automatic -eth/-est verb rule: "
                         f"{layer.counts.get(GENERIC_COUNT_KEY, 0)} further "
                         "archaic verb forms modernized", 9, indent=12)
            if layer.verses:
                pdf.space(4)
                pdf.para(f"Verse replacements ({len(layer.verses)})", 9, "F2",
                         indent=12)
                for (bid, ch, vs), (_text, comment) in sorted(layer.verses.items()):
                    pdf.para(f"{by_book[bid]} {ch}:{vs}"
                             + (f" — {comment}" if comment else ""), 8, indent=24)

    return pdf, book_pages


def _display_path(path: Path) -> str:
    """Repo-relative when it is inside the repo, absolute otherwise."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def report(result):
    """Print the standard run summary."""
    for warning in result["warnings"]:
        print(f"WARNING  {warning}")
    rel_md = _display_path(result["md"])
    rel_pdf = _display_path(result["pdf"])
    size = result["pdf"].stat().st_size
    print(f"Edition: {result['title']}")
    print(f"  base:    restored Mandela text ({result['restorations']} "
          "restorations applied)")
    for layer in result["layers"]:
        applied = sum(layer.counts.values())
        auto = layer.counts.get(GENERIC_COUNT_KEY, 0)
        print(f"  layer:   {layer.label} — {len(layer.mapping)} global rules "
              f"({applied - auto} replacements), {len(layer.verses)} verse "
              "replacements"
              + (f", automatic -eth/-est rule ({auto})" if layer.verb_rule
                 else ""))
    print(f"  changed: {result['changes']} verses differ from the restored text")
    print(f"  MD:      {rel_md}")
    print(f"  PDF:     {rel_pdf} ({size/1e6:.1f} MB, {result['pages']} pages)")
