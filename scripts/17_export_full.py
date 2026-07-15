#!/usr/bin/env python3
"""17_export_full.py — export the full restored Bible (MVP) as PDF + markdown.

Applies all APPROVED restorations to the base KJV text and emits:
  exports/MandelaBible-MVP.pdf  — full 66-book text, front matter, and a
                                  restoration appendix (every change listed)
  exports/MandelaBible-MVP.md   — same content as markdown

PDF is generated with a minimal pure-stdlib writer (Decision Log #10: no
PDF library exists in this environment and pip dependencies require a
logged decision — a small internal writer using the built-in Times/
Helvetica fonts, WinAnsi encoding, and Flate compression keeps the
stdlib-first rule). Layout: US Letter, 1in margins, Times-Roman 10pt body.

Idempotent: regenerates both files each run.
"""

import sqlite3
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
EXPORT_DIR = REPO_ROOT / "exports"

PAGE_W, PAGE_H = 612, 792
MARGIN = 72
BODY_SIZE, HEAD_SIZE, TITLE_SIZE = 10, 14, 26
LEADING = 13.5
# rough Times-Roman average char width factor for wrapping
CHARW = 0.48

TITLE = "The Mandela Bible"
SUBTITLE = "A Memory-Led Restoration of the King James Bible — MVP Edition"


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
        self.outline = []  # (title, page index)

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

    def mark(self, title):
        self.outline.append((title, self.pageno))

    def build(self) -> bytes:
        if self.buf:
            self.flush()
        objs = []  # (num, bytes)
        n_pages = len(self.pages)
        # 1 catalog, 2 pages-tree, 3 F1 (Times), 4 F2 (Times-Bold),
        # 5 F3 (Helvetica-Bold); pages start at 6
        kids = " ".join(f"{6 + 2*i} 0 R" for i in range(n_pages))
        objs.append((1, b"<< /Type /Catalog /Pages 2 0 R >>"))
        objs.append((2, f"<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>".encode()))
        for i, (num, base) in enumerate(
                [(3, "Times-Roman"), (4, "Times-Bold"), (5, "Helvetica-Bold")]):
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


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    resto = {}
    for vid, rid, new in con.execute(
            "SELECT verse_id, id, proposed_text FROM restorations "
            "WHERE status='approved' AND proposed_text IS NOT NULL"):
        resto[vid] = (rid, new)

    books = con.execute(
        "SELECT id, name FROM books WHERE translation='KJV' ORDER BY id").fetchall()
    n_resto = len(resto)

    pdf = Pdf()
    md = [f"# {TITLE}", "", f"*{SUBTITLE}*", ""]

    # title page
    pdf.newpage()
    pdf.space(180)
    pdf.text(TITLE, TITLE_SIZE, "F3")
    pdf.space(10)
    pdf.para(SUBTITLE, 12, "F2")
    pdf.space(30)
    for ln in [
            "Restored from the corrupted base text by memory-led textual criticism:",
            "memory testimony first, internal alteration artifacts second,",
            "all written witnesses advisory (Premise Revision, 2026-07-14).",
            "",
            f"{n_resto} owner-approved restorations are applied in this edition.",
            "Every change is documented in the Restoration Appendix.",
            "",
            "mandelabible.com"]:
        pdf.text(ln, 10)
    intro = ("Restored from the corrupted base text by memory-led textual "
             "criticism. Memory testimony first; internal alteration artifacts "
             f"second; all written witnesses advisory. {n_resto} owner-approved "
             "restorations applied — every change is listed in the appendix.")
    md += [intro, ""]

    for bid, name in books:
        pdf.newpage()
        pdf.mark(name)
        pdf.space(30)
        pdf.text(name, 20, "F3")
        pdf.space(8)
        md += [f"\n## {name}", ""]
        ch_cur = None
        changed = []
        for vid, ch, vs, text in con.execute(
                "SELECT id, chapter, verse, text FROM verses WHERE translation='KJV' "
                "AND book_id=? ORDER BY chapter, verse", (bid,)):
            if vid in resto:
                rid, text2 = resto[vid]
                changed.append((ch, vs, text, text2, rid))
                text = text2
            if ch != ch_cur:
                pdf.space(6)
                pdf.text(f"Chapter {ch}", HEAD_SIZE, "F2")
                pdf.space(3)
                md += [f"\n### Chapter {ch}", ""]
                ch_cur = ch
            mark = "*" if vid in resto else ""
            pdf.para(f"{vs}{mark}  {text}")
            md.append(f"**{vs}**{mark} {text}")
        con.execute("DROP TABLE IF EXISTS _tmp")  # no-op keeps con busy-free

    # appendix
    pdf.newpage()
    pdf.mark("Restoration Appendix")
    pdf.space(20)
    pdf.text("Restoration Appendix", 20, "F3")
    pdf.space(6)
    pdf.para("Every verse marked with * differs from the base text. Original "
             "readings are preserved below; full rationale and evidence live in "
             "the project's restorations database.", 9)
    md += ["\n## Restoration Appendix",
           "", "Every verse marked with * differs from the base text.", ""]
    for rid, name, ch, vs, cur, new in con.execute(
            """SELECT r.id, b.name, v.chapter, v.verse, r.current_text, r.proposed_text
               FROM restorations r
               JOIN verses v ON v.id=r.verse_id
               JOIN books b ON b.translation='KJV' AND b.id=v.book_id
               WHERE r.status='approved' AND r.proposed_text IS NOT NULL
               ORDER BY b.id, v.chapter, v.verse"""):
        pdf.space(5)
        pdf.para(f"{name} {ch}:{vs}  (restoration #{rid})", 9, "F2")
        pdf.para(f"was: {cur}", 8, indent=12)
        pdf.para(f"now: {new}", 8, indent=12)
        md += [f"- **{name} {ch}:{vs}** (#{rid})", f"  - was: {cur}", f"  - now: {new}"]

    EXPORT_DIR.mkdir(exist_ok=True)
    (EXPORT_DIR / "MandelaBible-MVP.pdf").write_bytes(pdf.build())
    (EXPORT_DIR / "MandelaBible-MVP.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    size = (EXPORT_DIR / "MandelaBible-MVP.pdf").stat().st_size
    print(f"PDF: exports/MandelaBible-MVP.pdf ({size/1e6:.1f} MB, "
          f"{pdf.pageno} pages, {n_resto} restorations applied)")
    print("MD:  exports/MandelaBible-MVP.md")
    con.close()


if __name__ == "__main__":
    main()
