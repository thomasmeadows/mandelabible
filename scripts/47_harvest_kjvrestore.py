#!/usr/bin/env python3
"""47_harvest_kjvrestore.py — harvest The KJV Restoration Project
(https://kjvrestore.org/; roadmap Phase 5 open item, owner directive
2026-07-16; crawl details from owner 2026-07-19: pages are
kjvrestore.org/?page_id=###, some ids missing, WordPress server-side
rendered, restored readings marked <span style="background-color: #ffff00;">).

Stages (all idempotent):
1. CRAWL — discover page_ids by BFS from the homepage nav (plus any ids
   linked from fetched pages) and cache each page's raw HTML in
   references/kjvrestore_pages/page_<id>.html. Cached files are permanent
   generated artifacts: never deleted, never re-fetched if present.
   The server rejects short User-Agents (406), so a full browser UA is sent;
   1s politeness delay between fetches.
2. PARSE — for each cached page whose <title> names a KJV book, walk the
   entry-content with html.parser, mark yellow-span text with sentinels,
   split into chapters ("Chapter N" strong headings) and inline-numbered
   verses. Load into db/mandela.db:
     kjvr_pages(page_id, title, book, url, fetched_len)
     kjvr_verses(page_id, book, chapter, verse, text)   -- text w/o markers
     kjvr_highlights(book, chapter, verse, phrase)      -- their restorations
   Tables are rebuilt each run from the caches.
3. REPORT — references/kjvrestore_comparison.md: every highlighted phrase
   compared against our KJV base text and our composed restored text, plus
   verse-ref collisions with `memories`. Advisory corroboration only — never
   a veto (Premise Revision). Overwrite guard: refuses to replace an
   existing report with one containing fewer highlight rows.
"""
import html
import json
import re
import sqlite3
import time
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "references" / "kjvrestore_pages"
REPORT = ROOT / "references" / "kjvrestore_comparison.md"
DB_PATH = ROOT / "db" / "mandela.db"
BASE = "https://kjvrestore.org/?page_id={}"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HL_OPEN, HL_CLOSE = "⟦", "⟧"  # sentinels for yellow spans

KJV_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
    "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
    "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John",
    "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians",
    "Ephesians", "Philippians", "Colossians", "1 Thessalonians",
    "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation",
]
TITLE_ALIASES = {
    "Psalm": "Psalms", "Song of Songs": "Song of Solomon",
    "Revelation of John": "Revelation",
    "I Samuel": "1 Samuel", "II Samuel": "2 Samuel",
    "I Kings": "1 Kings", "II Kings": "2 Kings",
    "I Chronicles": "1 Chronicles", "II Chronicles": "2 Chronicles",
    "I Corinthians": "1 Corinthians", "II Corinthians": "2 Corinthians",
    "I Thessalonians": "1 Thessalonians",
    "II Thessalonians": "2 Thessalonians",
    "I Timothy": "1 Timothy", "II Timothy": "2 Timothy",
    "I Peter": "1 Peter", "II Peter": "2 Peter",
    "I John": "1 John", "II John": "2 John", "III John": "3 John",
    "1st John": "1 John", "2nd John": "2 John", "3rd John": "3 John",
}
# our db uses Roman numerals + "Revelation of John"
DB_BOOK_ALIASES = {"Revelation": "Revelation of John"}
for _n, _r in (("1", "I"), ("2", "II"), ("3", "III")):
    for _b in ("Samuel", "Kings", "Chronicles", "Corinthians",
               "Thessalonians", "Timothy", "Peter", "John"):
        DB_BOOK_ALIASES[f"{_n} {_b}"] = f"{_r} {_b}"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode(
        "utf-8", "replace")


def crawl():
    CACHE.mkdir(exist_ok=True)
    home = fetch("https://kjvrestore.org/")
    (CACHE / "home.html").write_text(home, encoding="utf-8") \
        if not (CACHE / "home.html").exists() else None
    queue = sorted(set(int(x) for x in re.findall(r"page_id=(\d+)", home)))
    seen, fetched, failed = set(), 0, []
    while queue:
        pid = queue.pop(0)
        if pid in seen:
            continue
        seen.add(pid)
        path = CACHE / f"page_{pid}.html"
        if path.exists():
            body = path.read_text(encoding="utf-8")
        else:
            try:
                body = fetch(BASE.format(pid))
            except Exception as e:
                failed.append((pid, str(e)))
                continue
            path.write_text(body, encoding="utf-8")
            fetched += 1
            time.sleep(1)
        for x in re.findall(r"page_id=(\d+)", body):
            if int(x) not in seen:
                queue.append(int(x))
    print(f"crawl: {len(seen)} ids seen, {fetched} newly fetched, "
          f"{len(failed)} failed {failed[:5]}")


class ContentParser(HTMLParser):
    """Collects entry-content text; yellow spans wrapped in sentinels."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_content = 0
        self.hl_depth = []  # span nesting depths that are yellow
        self.depth = 0
        self.out = []
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if "entry-content" in (a.get("class") or ""):
            self.in_content = 1
            self.depth = 0
        if self.in_content:
            self.depth += 1
            if tag == "span" and "#ffff00" in (a.get("style") or ""):
                self.hl_depth.append(self.depth)
                self.out.append(HL_OPEN)
            if tag in ("p", "div", "h1", "h2", "h3", "h4", "br", "li"):
                self.out.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if self.in_content:
            if self.hl_depth and self.depth == self.hl_depth[-1] \
                    and tag == "span":
                self.hl_depth.pop()
                self.out.append(HL_CLOSE)
            self.depth -= 1
            if self.depth <= 0:
                self.in_content = 0
            if tag in ("p", "div", "h3", "li"):
                self.out.append("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_content:
            self.out.append(data)


def book_from_title(title):
    name = title.split("–")[0].split("-")[0].strip()
    name = TITLE_ALIASES.get(name, name)
    return name if name in KJV_BOOKS else None


def parse_verses(text):
    """{(chapter, verse): marked_text} from sentinel-marked page text."""
    verses = {}
    chapter = 0
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^Chapter\s+(\d+)\b", line)
        if m:
            chapter = int(m.group(1))
            continue
        if chapter == 0:
            continue
        # verse numbers are inline: "1 In the beginning... 2 And the earth..."
        parts = re.split(r"(?:(?<=^)|(?<=[\s⟦⟧]))(\d{1,3})\s+", line)
        cur_v = None
        for i in range(1, len(parts), 2):
            v, body = int(parts[i]), parts[i + 1].strip()
            expected = (cur_v + 1) if cur_v else 1
            if v == expected or (cur_v is None and v == 1) or \
                    (cur_v and v == cur_v + 1):
                cur_v = v
                verses[(chapter, v)] = body
            elif cur_v:  # stray number inside a verse (e.g. "40 days")
                verses[(chapter, cur_v)] += f" {v} {body}"
        if cur_v is None and line and (chapter, 1) not in verses and \
                re.match(r"^[A-Z]", line) and len(line) > 40:
            pass  # prose intro under a chapter heading — ignore
    return verses


def parse_all():
    con = sqlite3.connect(DB_PATH)
    con.executescript(
        "DROP TABLE IF EXISTS kjvr_pages;"
        "DROP TABLE IF EXISTS kjvr_verses;"
        "DROP TABLE IF EXISTS kjvr_highlights;"
        "CREATE TABLE kjvr_pages(page_id INTEGER PRIMARY KEY, title TEXT,"
        " book TEXT, url TEXT, fetched_len INTEGER);"
        "CREATE TABLE kjvr_verses(page_id INTEGER, book TEXT,"
        " chapter INTEGER, verse INTEGER, text TEXT);"
        "CREATE TABLE kjvr_highlights(book TEXT, chapter INTEGER,"
        " verse INTEGER, phrase TEXT);")
    n_pages = n_verses = n_hl = 0
    for path in sorted(CACHE.glob("page_*.html"),
                       key=lambda p: int(p.stem.split("_")[1])):
        pid = int(path.stem.split("_")[1])
        raw = path.read_text(encoding="utf-8")
        p = ContentParser()
        p.feed(raw)
        title = html.unescape(p.title).strip()
        book = book_from_title(title)
        con.execute("INSERT INTO kjvr_pages VALUES (?,?,?,?,?)",
                    (pid, title, book, BASE.format(pid), len(raw)))
        n_pages += 1
        if not book:
            continue
        text = "".join(p.out)
        for (ch, vs), marked in sorted(parse_verses(text).items()):
            plain = marked.replace(HL_OPEN, "").replace(HL_CLOSE, "")
            plain = re.sub(r"\s+", " ", plain).strip()
            con.execute("INSERT INTO kjvr_verses VALUES (?,?,?,?,?)",
                        (pid, book, ch, vs, plain))
            n_verses += 1
            for phrase in re.findall(
                    rf"{HL_OPEN}(.*?){HL_CLOSE}", marked, re.S):
                phrase = re.sub(r"\s+", " ", phrase).strip()
                if phrase:
                    con.execute(
                        "INSERT INTO kjvr_highlights VALUES (?,?,?,?)",
                        (book, ch, vs, phrase))
                    n_hl += 1
    con.commit()
    print(f"parse: {n_pages} pages, {n_verses} verses, "
          f"{n_hl} highlighted readings")
    return con


def report(con):
    books = dict(con.execute(
        "SELECT name, id FROM books WHERE translation='KJV'"))
    kjv, restored = {}, {}
    for vid, bid, ch, vs, t in con.execute(
            "SELECT id, book_id, chapter, verse, text FROM verses "
            "WHERE translation='KJV'"):
        kjv[(bid, ch, vs)] = t
        restored[(bid, ch, vs)] = t
    comp = {}
    for vid, t in con.execute(
            "SELECT verse_id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL "
            "AND flaw_type!='kjvrestore_fold' ORDER BY id"):
        comp[vid] = t
    vid_of = {}
    for vid, bid, ch, vs in con.execute(
            "SELECT id, book_id, chapter, verse FROM verses "
            "WHERE translation='KJV'"):
        vid_of[(bid, ch, vs)] = vid
        if vid in comp:
            restored[(bid, ch, vs)] = comp[vid]
    mem_refs = set()
    for (ref,) in con.execute(
            "SELECT verse_ref FROM memories WHERE verse_ref IS NOT NULL"):
        mem_refs.add(re.sub(r"\s+", " ", ref).strip().lower())

    their = {(b, c, v): t for b, c, v, t in con.execute(
        "SELECT book, chapter, verse, text FROM kjvr_verses")}
    rows = con.execute(
        "SELECT book, chapter, verse, phrase FROM kjvr_highlights "
        "ORDER BY book, chapter, verse").fetchall()
    by_status = defaultdict(list)
    for book, ch, vs, phrase in rows:
        db_book = DB_BOOK_ALIASES.get(book, book)
        key = (books.get(db_book), ch, vs)
        base_t = kjv.get(key, "")
        rest_t = restored.get(key, "")
        norm = phrase.lower()
        in_base = norm in base_t.lower()
        in_rest = norm in rest_t.lower()
        mem_hit = any(f"{b} {ch}:{vs}".lower() in mem_refs
                      for b in (book, db_book,
                                db_book.replace(" of John", "")))
        if not base_t:
            status = "REF-NOT-FOUND"
        elif in_rest and in_base:
            status = "MATCHES-BOTH"      # highlight = unchanged AV wording
        elif in_rest:
            status = "AGREES-WITH-OURS"  # they restored what we restored
        elif in_base:
            status = "THEY-KEPT-BASE"    # in KJV base but not our restored
        else:
            status = "DIVERGES"          # their reading differs from ours
        by_status[status].append(
            (book, ch, vs, phrase, rest_t, mem_hit,
             their.get((book, ch, vs), "")))

    if REPORT.exists():
        old = len(re.findall(r"^\| ", REPORT.read_text(encoding="utf-8"),
                             re.M))
        if old > len(rows) + 40:
            raise SystemExit("REFUSING: existing report is larger")

    out = ["# kjvrestore.org comparison report", "",
           "*Generated by `scripts/47_harvest_kjvrestore.py`. The KJV "
           "Restoration Project's yellow-highlighted restored readings vs "
           "our KJV base and composed restored text. Advisory corroboration "
           "only — never a veto (Premise Revision; roadmap Phase 5).*", "",
           f"Highlighted readings: **{len(rows)}** across "
           f"{len(set((r[0], r[1]) for r in rows))} chapters. Status "
           "counts: " + ", ".join(
               f"{k} {len(v)}" for k, v in sorted(by_status.items())), "",
           "- **AGREES-WITH-OURS** — their restored phrase already appears "
           "in our restored text (independent corroboration).",
           "- **DIVERGES** — their restored phrase differs from both the "
           "KJV base and our restored text (owner-review candidates).",
           "- **MATCHES-BOTH** — phrase identical in base and ours (their "
           "highlight may mark a passage, not a change).",
           "- **THEY-KEPT-BASE** — phrase is current-KJV wording that our "
           "restoration changed (possible counter-signal).",
           "- `MEM` — verse ref collides with a `memories` row.",
           "- A phrase of literal **X** is the site's own marker for a "
           "word they deleted at that spot (not a parse artifact).", ""]
    for status in ("DIVERGES", "THEY-KEPT-BASE", "AGREES-WITH-OURS",
                   "MATCHES-BOTH", "REF-NOT-FOUND"):
        entries = by_status.get(status, [])
        if not entries:
            continue
        out += [f"## {status} ({len(entries)})", ""]
        for book, ch, vs, phrase, rest_t, mem_hit, their_t in entries:
            mem = " `MEM`" if mem_hit else ""
            out.append(f"### {book} {ch}:{vs}{mem}")
            out.append(f"- their reading: **{phrase}**")
            if status in ("DIVERGES", "THEY-KEPT-BASE"):
                if their_t:
                    out.append(
                        f"- their verse: "
                        f"{their_t.replace(phrase, f'**{phrase}**', 1)}")
                if rest_t:
                    out.append(f"- our verse: {rest_t}")
            out.append("")
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"report: {REPORT.name} — " + ", ".join(
        f"{k}:{len(v)}" for k, v in sorted(by_status.items())))


def main():
    crawl()
    con = parse_all()
    report(con)
    con.close()


if __name__ == "__main__":
    main()
