#!/usr/bin/env python3
"""102_import_kjv1611.py — import the 1611 King James Bible, original spelling,
as the advisory witness `KJV1611` (owner request 2026-10-04).

Source: lb42/KJV_1611 — "A TEI-Conformant version of the 1611 text of the
Bible" (Lou Burnard, 2017; https://github.com/lb42/KJV_1611), archived on
Zenodo as record 1285692. Its header says the transcription was downloaded
from www.kingjamesbibleonline.org and converted to TEI XML; the converter
notes it "contains several areas for amelioration", so treat single readings
as a transcription to be checked against the page facsimiles each chapter
file links (`<pb facs=...>`). The repository declares no licence; the 1611
text itself is out of copyright.

Stages (all idempotent):
1. CACHE — the Zenodo zip is stored once at
   references/source_texts/KJV_1611_lb42-1.0.zip. It is a permanent generated
   artifact: never deleted, never re-fetched if present. (Zenodo answers
   403 to browser-style User-Agents, so an honest tool identifier is sent.)
2. PARSE — each chapter file chaps/<Book>_<NN>.xml holds one
   `<ab n="V">` per verse; `<note>` elements inside a verse are the 1611
   marginal notes (alternative renderings, "Heb." literalisms,
   cross-references). Verse text = the `<ab>` with its notes removed,
   whitespace collapsed, `&amp;` unescaped; the spelling (u/v, i/j, þe,
   bracketed psalm titles) is kept exactly as transcribed. Only the 66
   protocanonical books are loaded, matching the KJV base; the Apocrypha
   stays in the cached zip.
3. LOAD — db/mandela.db, the same way `08_import_witnesses.py` loads the
   scrollmapper witnesses (book ids = the KJV's):
     translations / books / verses  rows for translation 'KJV1611'
     kjv1611_notes(book_id, chapter, verse, seq, note)  -- marginal notes
   Both are deleted and re-copied from the cache each run.

Advisory witness only — never a veto (Premise Revision, Decision Log #5).
"""
import html
import re
import sqlite3
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mandela.db"
CACHE = ROOT / "references" / "source_texts" / "KJV_1611_lb42-1.0.zip"
URL = "https://zenodo.org/records/1285692/files/lb42/KJV_1611-1.0.zip?download=1"
CODE = "KJV1611"
TITLE = ("King James Version (1611), original spelling — lb42/KJV_1611 TEI "
         "transcription of kingjamesbibleonline.org (Zenodo 1285692)")
LICENSE = "Public domain text; transcription licence not declared"

AB = re.compile(r'<ab n="(\d+)">(.*?)</ab>', re.S)
NOTE = re.compile(r"<note>(.*?)</note>", re.S)


def fetch():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "mandelabible-import/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    if not zipfile.is_zipfile(__import__("io").BytesIO(data)):
        sys.exit("ERROR: download is not a zip archive; cache not written.")
    CACHE.write_bytes(data)
    print(f"cache: fetched {URL} -> {CACHE.relative_to(ROOT)}")


def clean(s):
    return html.unescape(" ".join(s.split()))


def file_name(kjv_name):
    """scrollmapper KJV book name -> lb42 chapter-file prefix."""
    name = re.sub(r"^III ", "3-", re.sub(r"^II ", "2-", re.sub(r"^I ", "1-", kjv_name)))
    name = name.replace(" ", "-")
    return {"Revelation-of-John": "Revelation"}.get(name, name)


def main():
    if CACHE.exists():
        print(f"cache: {CACHE.relative_to(ROOT)} (not re-fetched)")
    else:
        fetch()
    z = zipfile.ZipFile(CACHE)
    chapters = {}
    for n in z.namelist():
        m = re.search(r"/chaps/(.+)_(\d+)\.xml$", n)
        if m:
            chapters[(m.group(1), int(m.group(2)))] = n

    con = sqlite3.connect(DB_PATH)
    try:
        kjv_books = con.execute(
            "SELECT id, name FROM books WHERE translation='KJV' ORDER BY id").fetchall()
        kjv_chapters = con.execute(
            "SELECT DISTINCT book_id, chapter FROM verses WHERE translation='KJV' "
            "ORDER BY 1, 2").fetchall()
        names = dict(kjv_books)

        verses, notes, missing = [], [], []
        for bid, ch in kjv_chapters:
            member = chapters.get((file_name(names[bid]), ch))
            if member is None:
                missing.append(f"{names[bid]} {ch}")
                continue
            xml = z.read(member).decode("utf-8")
            for vn, body in AB.findall(xml):
                for seq, note in enumerate(NOTE.findall(body), 1):
                    notes.append((bid, ch, int(vn), seq, clean(note)))
                text = clean(NOTE.sub(" ", body))
                if text:
                    verses.append((CODE, bid, ch, int(vn), text))

        con.execute("BEGIN")
        con.execute("""CREATE TABLE IF NOT EXISTS kjv1611_notes (
            book_id INTEGER, chapter INTEGER, verse INTEGER, seq INTEGER,
            note TEXT, PRIMARY KEY (book_id, chapter, verse, seq))""")
        con.execute("DELETE FROM kjv1611_notes")
        con.execute("DELETE FROM verses WHERE translation=?", (CODE,))
        con.execute("DELETE FROM books WHERE translation=?", (CODE,))
        con.execute("DELETE FROM translations WHERE translation=?", (CODE,))
        con.execute("INSERT INTO translations VALUES (?,?,?)", (CODE, TITLE, LICENSE))
        con.executemany("INSERT INTO books (id, translation, name) VALUES (?,?,?)",
                        [(bid, CODE, name) for bid, name in kjv_books])
        dup = len(verses)
        con.executemany(
            "INSERT OR IGNORE INTO verses (translation, book_id, chapter, verse, text) "
            "VALUES (?,?,?,?,?)", verses)
        con.executemany("INSERT OR IGNORE INTO kjv1611_notes VALUES (?,?,?,?,?)", notes)
        con.commit()

        loaded = con.execute(
            "SELECT COUNT(*) FROM verses WHERE translation=?", (CODE,)).fetchone()[0]
        aligned = con.execute(
            "SELECT COUNT(*) FROM verses k JOIN verses o ON o.translation=? "
            "AND o.book_id=k.book_id AND o.chapter=k.chapter AND o.verse=k.verse "
            "WHERE k.translation='KJV'", (CODE,)).fetchone()[0]
        kjv_total = con.execute(
            "SELECT COUNT(*) FROM verses WHERE translation='KJV'").fetchone()[0]
        n_notes = con.execute("SELECT COUNT(*) FROM kjv1611_notes").fetchone()[0]
    finally:
        con.close()

    print(f"{CODE}: {loaded} verses ({dup - loaded} duplicate verse numbers ignored), "
          f"{len(kjv_books)} books, {n_notes} marginal notes")
    print(f"aligned with KJV: {aligned} of {kjv_total} verses; "
          f"{loaded - aligned} 1611 verses with no KJV counterpart")
    if missing:
        print(f"WARNING: {len(missing)} KJV chapters have no 1611 file: {missing[:10]}")


if __name__ == "__main__":
    main()
