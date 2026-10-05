#!/usr/bin/env python3
"""104_import_eya_video_transcripts.py — import the caption transcripts of
every video on the EYA Censored | Supernatural Bible Changes YouTube channel
(https://www.youtube.com/@eyacensored-biblechanges, Videos tab only; owner
request 2026-10-04) into references/eya-video-transcripts/.

Fetching uses yt-dlp as an external command-line tool (Decision Log #25) —
it is never imported, so the project's own code stays stdlib-only. Install
it once into the gitignored tool venv:

    python3 -m venv .venv-tools && .venv-tools/bin/pip install yt-dlp

(or point the YTDLP environment variable at any yt-dlp executable).

Each video gets its own directory, `<YYYY-MM-DD>_<videoId>/`, holding:
  captions.<lang>.vtt — the raw caption file as downloaded (permanent cache)
  metadata.json       — id, title, URL, upload date, duration, description,
                        caption kind and language, fetch date
  transcript.md       — the readable transcript, de-duplicated, with
                        [mm:ss] timestamps per paragraph
plus a channel-wide `index.md`.

Caption choice per video: creator-uploaded English captions when they exist,
otherwise YouTube's auto-generated English track (owner choice 2026-10-04).
Auto-generated captions are speech recognition: unpunctuated in places and
prone to mishearing — the transcript header says which kind each one is.

Idempotent: a video whose directory already holds transcript.md is skipped
(pass --refresh to re-fetch; a refreshed transcript shorter than the existing
one is refused — Generated Artifacts are permanent). Videos with no English
captions are listed in the index and retried on the next run.

Advisory corroboration only — never a veto (Premise Revision).
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "references" / "eya-video-transcripts"
INDEX = OUT_DIR / "index.md"
CHANNEL = "https://www.youtube.com/@eyacensored-biblechanges"
VIDEOS_TAB = CHANNEL + "/videos"
PARAGRAPH_SECONDS = 30
TAG_RE = re.compile(r"<[^>]+>")
CUE_RE = re.compile(r"^(\d+):(\d\d):(\d\d)\.\d+ -->")


def ytdlp():
    exe = os.environ.get("YTDLP") or ROOT / ".venv-tools" / "bin" / "yt-dlp"
    if Path(exe).exists():
        return str(exe)
    found = shutil.which("yt-dlp")
    if found:
        return found
    sys.exit("ERROR: yt-dlp not found. Install it with:\n"
             "  python3 -m venv .venv-tools && .venv-tools/bin/pip install yt-dlp")


def run(args):
    res = subprocess.run([ytdlp(), "--quiet", "--no-warnings", *args],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or f"yt-dlp exited {res.returncode}")
    return res.stdout


def list_videos():
    out = run(["--flat-playlist", "--print", "%(id)s", VIDEOS_TAB])
    ids = [line.strip() for line in out.splitlines() if line.strip()]
    if not ids:
        sys.exit("ERROR: the Videos tab returned no videos — layout or network problem.")
    return ids


def pick_track(info):
    """Creator-uploaded English first, then auto-generated (original
    language track 'en-orig' before the translated 'en')."""
    manual = info.get("subtitles") or {}
    for lang in sorted(manual, key=lambda k: (k != "en", k)):
        if lang == "en" or lang.startswith("en-"):
            return "manual", lang
    auto = info.get("automatic_captions") or {}
    for lang in ("en-orig", "en"):
        if lang in auto:
            return "auto-generated", lang
    return None, None


def parse_vtt(text, kind):
    """Return [(start_seconds, line)] with the rolling duplicates removed.

    Auto-generated tracks repeat every line: each cue shows the previous
    line again plus the new line, and a 10 ms cue then shows the finished
    line once more. Keeping only lines that differ from the last kept line
    removes the echoes. (The new line usually carries inline <c> word
    timings, but a one-word line such as "much." carries none, so the
    markup cannot be used as the test.) The same rule serves manual tracks."""
    out = []
    start = 0
    for block in re.split(r"\n\s*\n", text.replace("\r", "")):
        lines = block.strip("\n").split("\n")
        cue = next((i for i, l in enumerate(lines) if CUE_RE.match(l)), None)
        if cue is None:
            continue
        h, m, s = CUE_RE.match(lines[cue]).groups()
        start = int(h) * 3600 + int(m) * 60 + int(s)
        for line in lines[cue + 1:]:
            clean = html.unescape(TAG_RE.sub("", line)).strip()
            if not clean or (out and out[-1][1] == clean):
                continue
            out.append((start, clean))
    return out


def paragraphs(lines):
    paras, cur, cur_start = [], [], None
    for start, line in lines:
        if cur_start is None:
            cur_start = start
        elif start - cur_start >= PARAGRAPH_SECONDS:
            paras.append((cur_start, " ".join(cur)))
            cur, cur_start = [], start
        cur.append(line)
    if cur:
        paras.append((cur_start, " ".join(cur)))
    return paras


def stamp(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def iso(d):
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if d and len(d) == 8 else "unknown-date"


def render(meta, paras):
    word_count = sum(len(p.split()) for _, p in paras)
    head = [
        f"# {meta['title']}",
        "",
        f"- **Video:** <{meta['url']}>",
        f"- **Channel:** {meta['channel']}",
        f"- **Uploaded:** {meta['upload_date']}",
        f"- **Duration:** {stamp(meta['duration'] or 0)}",
        f"- **Captions:** {meta['caption_kind']} (`{meta['caption_lang']}`)"
        + (" — speech recognition; expect missing punctuation and misheard words"
           if meta["caption_kind"] == "auto-generated" else ""),
        f"- **Words:** {word_count:,}",
        f"- **Fetched:** {meta['fetched']} by `scripts/104_import_eya_video_transcripts.py`",
        "",
        "Advisory corroboration only (Premise Revision).",
        "",
        "## Transcript",
        "",
        "",
    ]
    body = [f"**[{stamp(t)}]** {p}\n" for t, p in paras]
    return "\n".join(head) + "\n".join(body), word_count


def existing_dir(vid):
    hits = sorted(OUT_DIR.glob(f"*_{vid}"))
    return hits[0] if hits else None


def import_video(vid, refresh):
    old = existing_dir(vid)
    if old and (old / "transcript.md").exists() and not refresh:
        return "skipped", old
    url = f"https://www.youtube.com/watch?v={vid}"
    info = json.loads(run(["--skip-download", "--dump-json", url]))
    kind, lang = pick_track(info)
    if not kind:
        return "no-captions", info
    with tempfile.TemporaryDirectory() as tmp:
        flag = "--write-subs" if kind == "manual" else "--write-auto-subs"
        run(["--skip-download", flag, "--sub-langs", lang, "--sub-format", "vtt",
             "-o", str(Path(tmp) / "cap.%(ext)s"), url])
        vtts = list(Path(tmp).glob("cap*.vtt"))
        if not vtts:
            raise RuntimeError(f"caption track {lang} listed but not downloaded")
        raw = vtts[0].read_text(encoding="utf-8")
    paras = paragraphs(parse_vtt(raw, kind))
    meta = {
        "id": vid,
        "title": info.get("title", ""),
        "url": url,
        "channel": info.get("channel", ""),
        "upload_date": iso(info.get("upload_date")),
        "duration": info.get("duration"),
        "description": info.get("description", ""),
        "caption_kind": kind,
        "caption_lang": lang,
        "fetched": datetime.date.today().isoformat(),
    }
    md, words = render(meta, paras)
    vdir = OUT_DIR / f"{meta['upload_date']}_{vid}"
    tfile = vdir / "transcript.md"
    if tfile.exists() and len(md) < len(tfile.read_text(encoding="utf-8")):
        print(f"  REFUSED {vid}: refreshed transcript is shorter than the existing one")
        return "skipped", vdir
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / f"captions.{lang}.vtt").write_text(raw, encoding="utf-8")
    (vdir / "metadata.json").write_text(
        json.dumps({**meta, "words": words}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    tfile.write_text(md, encoding="utf-8")
    return "imported", vdir


def write_index(missing):
    rows = []
    for meta_file in sorted(OUT_DIR.glob("*/metadata.json"), reverse=True):
        m = json.loads(meta_file.read_text(encoding="utf-8"))
        rows.append(f"| {m['upload_date']} | [{m['title'].replace('|', '/')}]"
                    f"({meta_file.parent.name}/transcript.md) | {stamp(m['duration'] or 0)} "
                    f"| {m['caption_kind']} | {m['words']:,} | <{m['url']}> |")
    lines = [
        "# EYA Censored — Video Transcripts",
        "",
        f"Caption transcripts of the Videos tab of <{CHANNEL}>, imported by",
        "`scripts/104_import_eya_video_transcripts.py`. One directory per video",
        "(`<upload date>_<video id>/`: `transcript.md`, `metadata.json`, and the raw",
        "`captions.*.vtt`). Creator-uploaded captions are used where they exist,",
        "otherwise YouTube's auto-generated speech recognition. Advisory",
        "corroboration only (Premise Revision).",
        "",
        f"**{len(rows)} transcripts.**",
        "",
        "| Uploaded | Title | Length | Captions | Words | Video |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    if missing:
        lines += ["## No English captions available (retried on every run)", ""]
        lines += [f"- {m.get('title', '?')} — <https://www.youtube.com/watch?v={m['id']}>"
                  for m in missing]
        lines.append("")
    INDEX.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true",
                    help="re-fetch videos that already have a transcript")
    ap.add_argument("--sleep", type=float, default=2.0,
                    help="seconds to pause between videos (default 2)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ids = list_videos()
    print(f"Videos tab: {len(ids)} videos")
    counts = {"imported": 0, "skipped": 0, "no-captions": 0, "failed": 0}
    missing = []
    for n, vid in enumerate(ids, 1):
        try:
            status, detail = import_video(vid, args.refresh)
        except (RuntimeError, json.JSONDecodeError) as exc:
            status, detail = "failed", None
            print(f"  [{n}/{len(ids)}] FAILED {vid}: {exc}")
        counts[status] += 1
        if status == "no-captions":
            missing.append(detail)
            print(f"  [{n}/{len(ids)}] no English captions: {vid}")
        elif status == "imported":
            print(f"  [{n}/{len(ids)}] imported {detail.name}")
        if status != "skipped" and n < len(ids):
            time.sleep(args.sleep)
    total = write_index(missing)
    print(f"Done: {counts['imported']} imported, {counts['skipped']} already present, "
          f"{counts['no-captions']} without English captions, {counts['failed']} failed.")
    print(f"index.md: {total} transcripts listed")
    if counts["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
