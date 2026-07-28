#!/usr/bin/env python3
"""91_build_divine_names.py — recover the LORD / Lord distinction the source
text lost, and store it as a per-occurrence map for the modern edition.

**The problem.** The KJV prints the divine name in small caps — LORD (יהוה,
Yahweh) — against plain Lord (אֲדֹנָי, Adonai) and lowercase lord (a human
master, אָדוֹן). The scrollmapper source this project builds on flattened that
typography: `KJV.db` holds **42** all-caps LORD against **54,009** plain Lord.
The distinction is therefore *not in the string*, and no word-for-word rule in
a settings file can make it — "Lord" → "Yahweh" would rewrite Adonai and every
human master along with it.

**The fix.** `bf_words_en` (BibleForge, parsed into `db/mandela.db` by
`scripts/09_convert_bibleforge.py`) carries a `divine` column — the small-caps
flag — on 6,888 words, and each English word links through `orig_id` to its
Strong's number in `bf_words_orig`. That is the lost typography, recoverable
word by word.

**What this script writes.** Table `divine_names`, one row per Lord/God token
of the **restored** text that should change, addressed by its *position* in
that verse's Lord/God token stream (not by string), so the export layer can
replace the 3rd token of a verse without touching the 1st.

Owner rulings 2026-07-27:

  * `divine=1` (Strong's H3068, the tetragrammaton) -> **Yahweh** — 6,881 in
    the OT plus the 4 NT quotations of Psalm 110:1 ("Yahweh said unto my
    Lord": Matt 22:44, Mark 12:36, Luke 20:42, Acts 2:34). This covers both
    the Lord tokens and the GOD of "Lord GOD" (Adonai YHWH), which is why
    that pair comes out "Adonai Yahweh".
  * Old Testament capital Lord with Strong's **H136** (Adonai) -> **Adonai**.
  * **New Testament** capital Lord (Greek κύριος, G2962) -> **unchanged**.
    Owner ruling: it is not the Hebrew word, and many are addressed to Jesus.
  * Old Testament capital Lord with Strong's **H113 / H4756** (a human
    master or lord) -> **unchanged**.
  * lowercase lord / lords -> **unchanged** — the owner of an estate or
    property, which is the reading the directive explicitly protects.
  * every non-divine God -> **unchanged**.

**Safety.** A verse is mapped only when its Lord/God token stream lines up
with BibleForge's **in both length and word identity** (lord-vs-god at every
position). Verses where the project's own restorations changed that stream —
"Holy Ghost" → "spirit of the Lord", the Genesis 1:26 rewrite, the Hallelujah
edits — are **skipped and reported**, never guessed at. The exporter re-checks
the token count at apply time and skips the verse if it has moved again.

Reads `bf_words_en` / `bf_words_orig` (read-only) and writes only its own
table. Idempotent: the table is dropped and rebuilt each run.

Usage:
    python3 scripts/91_build_divine_names.py
    python3 scripts/91_build_divine_names.py --dry-run
    python3 scripts/91_build_divine_names.py --list-skipped
"""
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"

# Every Lord/God token, however punctuated, plural or possessive.
TOKEN_RE = re.compile(r"\b(?i:lord|god)(?:'s|s)?\b")

YHWH = 3068       # the tetragrammaton — printed LORD / GOD in small caps
ADONAI = 136      # אֲדֹנָי — printed Lord
OT_BOOKS = 39     # book ids 1..39 are the Old Testament

SCHEMA = """
CREATE TABLE divine_names (
    verse_id    INTEGER REFERENCES verses(id),
    book_id     INTEGER,
    chapter     INTEGER,
    verse       INTEGER,
    occ_index   INTEGER,   -- 0-based position in the verse's Lord/God stream
    token_total INTEGER,   -- length of that stream, re-checked at apply time
    source_word TEXT,      -- as it stands in the restored text
    replacement TEXT,
    strongs     INTEGER,
    divine      INTEGER,
    PRIMARY KEY (verse_id, occ_index)
)
"""


def load_restored(con):
    """Restored text (base KJV + approved restorations) with references."""
    text, ref = {}, {}
    for vid, bid, name, ch, vs, t in con.execute(
            "SELECT v.id, v.book_id, b.name, v.chapter, v.verse, v.text "
            "FROM verses v JOIN books b "
            "ON b.id = v.book_id AND b.translation = v.translation "
            "WHERE v.translation='KJV'"):
        text[vid] = t
        ref[vid] = (bid, name, ch, vs)
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "ORDER BY id"):
        text[vid] = t
    return text, ref


def load_bibleforge(con):
    """verseID -> [(word, divine, strongs)] in reading order."""
    strongs = dict(con.execute("SELECT id, strongs FROM bf_words_orig"))
    stream = defaultdict(list)
    for key, word, divine, orig_id in con.execute(
            "SELECT verseID, word, divine, orig_id FROM bf_words_en "
            "ORDER BY verseID, lang_order"):
        core = re.sub(r"[^A-Za-z']", "", word or "")
        if re.fullmatch(r"(?i)(lord|god)('s|s)?", core):
            stream[key].append((core, divine, strongs.get(orig_id)))
    return stream


def decide(word, divine, strongs, book_id):
    """The replacement for one token, or None to leave it alone."""
    stem = re.match(r"(?i)(lord|god)", word).group(0)
    suffix = word[len(stem):]          # "", "s", "'s"
    if divine:
        return "Yahweh" + suffix
    if book_id <= OT_BOOKS and stem[:1].isupper() and strongs == ADONAI:
        return "Adonai" + suffix
    return None


def main():
    dry_run = "--dry-run" in sys.argv
    list_skipped = "--list-skipped" in sys.argv
    con = sqlite3.connect(DB_PATH)
    text, ref = load_restored(con)
    stream = load_bibleforge(con)

    rows = []
    skipped, aligned = [], 0
    counts = Counter()
    for vid, t in text.items():
        bid, name, ch, vs = ref[vid]
        found = TOKEN_RE.findall(t)
        tokens = [m.group(0) for m in TOKEN_RE.finditer(t)]
        bf = stream.get(bid * 1000000 + ch * 1000 + vs, [])
        if not tokens and not bf:
            continue
        if len(tokens) != len(bf) or any(
                a[:1].lower() != b[0][:1].lower() for a, b in zip(tokens, bf)):
            skipped.append((f"{name} {ch}:{vs}", len(tokens), len(bf)))
            continue
        aligned += 1
        for i, (token, (_w, divine, strongs)) in enumerate(zip(tokens, bf)):
            new = decide(token, divine, strongs, bid)
            if new is None or new == token:
                continue
            counts[new.rstrip("'s") if new.endswith("'s") else new] += 1
            rows.append((vid, bid, ch, vs, i, len(tokens), token, new,
                         strongs, divine))

    print(f"aligned verses: {aligned}   skipped (stream differs): "
          f"{len(skipped)}")
    print(f"tokens to replace: {len(rows)}")
    for name, n in counts.most_common():
        print(f"  -> {name}: {n}")
    if skipped:
        print(f"\n{len(skipped)} verses left untouched — the project's own "
              f"restorations changed their Lord/God stream:")
        show = skipped if list_skipped else skipped[:10]
        for r, a, b in show:
            print(f"  {r}: text has {a} token(s), BibleForge has {b}")
        if not list_skipped and len(skipped) > len(show):
            print(f"  … {len(skipped) - len(show)} more (--list-skipped)")

    if dry_run:
        print("\ndry run — nothing written.")
        con.close()
        return

    con.execute("DROP TABLE IF EXISTS divine_names")
    con.execute(SCHEMA)
    con.executemany(
        "INSERT INTO divine_names (verse_id, book_id, chapter, verse, "
        "occ_index, token_total, source_word, replacement, strongs, divine) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()
    print(f"\ndivine_names: {len(rows)} rows written.")


if __name__ == "__main__":
    main()
