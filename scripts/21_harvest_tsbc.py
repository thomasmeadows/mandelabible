#!/usr/bin/env python3
"""21_harvest_tsbc.py — Phase 5: harvest the TSBC Scribe database.

Owner directive 2026-07-16: pull the full TSBC Scribe dataset
(https://search.thesupernaturalbiblechanges.com — see sources.md §IV) into
db/mandela.db as advisory public memory testimony: 355 changes, 398 memories
(with restoredText), 249 residual images of the pre-change text.

API (POST, JSON, same origin):
  /v1/GetDBMetrics                {}                    -> counts
  /v1/GetChangeByID               {"id": n}             -> change (sparse ids)
  /v1/GetMemoriesOfChange         {"changeNumber": n}   -> [memory]
  /v1/GetResidueOfMemory          {"memoryID": n}       -> [residue] | null

Tables created (raw JSON kept alongside extracted columns so nothing from
the source is lost): tsbc_changes, tsbc_memories, tsbc_residue.
Residue files are downloaded to references/tsbc_residue/ when a fetchable
URL/path is present. Idempotent: rows upserted by source ID, downloads
skipped when the file already exists.
"""

import json
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "db" / "mandela.db"
RESIDUE_DIR = REPO_ROOT / "references" / "tsbc_residue"
BASE = "https://search.thesupernaturalbiblechanges.com"
MAX_CHANGE_ID = 800          # metrics say 355 changes; ids are sparse < ~400
PAUSE = 0.15                 # be polite to a small ministry server


def post(path: str, payload: dict, retries: int = 3):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "User-Agent": "mandelabible-harvest/1.0 (research)"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode()
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return body          # e.g. "Error: record not found"
        except Exception as e:      # noqa: BLE001 — transient net errors
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return None


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS tsbc_changes (
        id INTEGER PRIMARY KEY,          -- source ID
        book INTEGER, chapter INTEGER, verse INTEGER, book_name TEXT,
        change_type TEXT, notes TEXT, detected_at TEXT,
        is_missing INTEGER, is_meaning_change INTEGER,
        is_doctrine_change INTEGER, has_flipflops INTEGER,
        raw JSON NOT NULL
    );
    CREATE TABLE IF NOT EXISTS tsbc_memories (
        id INTEGER PRIMARY KEY,          -- source ID
        change_id INTEGER REFERENCES tsbc_changes(id),
        memory_date TEXT, restored_text TEXT, notes TEXT, source TEXT,
        raw JSON NOT NULL
    );
    CREATE TABLE IF NOT EXISTS tsbc_residue (
        id INTEGER PRIMARY KEY,          -- source ID
        memory_id INTEGER REFERENCES tsbc_memories(id),
        file_name TEXT, local_path TEXT,
        raw JSON NOT NULL
    );
    """)

    metrics = post("/v1/GetDBMetrics", {})
    print(f"server metrics: {metrics}")

    n_changes = 0
    change_ids = []
    for cid in range(1, MAX_CHANGE_ID + 1):
        c = post("/v1/GetChangeByID", {"id": cid})
        time.sleep(PAUSE)
        if not isinstance(c, dict):
            continue
        change_ids.append(cid)
        n_changes += 1
        con.execute(
            """INSERT OR REPLACE INTO tsbc_changes
               (id, book, chapter, verse, book_name, change_type, notes,
                detected_at, is_missing, is_meaning_change,
                is_doctrine_change, has_flipflops, raw)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (c["ID"], c.get("book"), c.get("chapter"), c.get("verse"),
             c.get("bookName"), c.get("changeType"), c.get("notes"),
             c.get("detectedAt"), int(bool(c.get("isMissing"))),
             int(bool(c.get("isMeaningChange"))),
             int(bool(c.get("isDoctrineChange"))),
             int(bool(c.get("hasFlipflops"))), json.dumps(c)))
        if n_changes % 50 == 0:
            con.commit()
            print(f"  {n_changes} changes (scanned to id {cid})")
    con.commit()
    print(f"{n_changes} changes harvested")

    n_mem = 0
    memory_ids = []
    for cid in change_ids:
        mems = post("/v1/GetMemoriesOfChange", {"changeNumber": cid})
        time.sleep(PAUSE)
        if not isinstance(mems, list):
            continue
        for m in mems:
            memory_ids.append(m["ID"])
            n_mem += 1
            con.execute(
                """INSERT OR REPLACE INTO tsbc_memories
                   (id, change_id, memory_date, restored_text, notes,
                    source, raw) VALUES (?,?,?,?,?,?,?)""",
                (m["ID"], cid, m.get("memoryDate"), m.get("restoredText"),
                 m.get("notes"), m.get("source"), json.dumps(m)))
    con.commit()
    print(f"{n_mem} memories harvested")

    RESIDUE_DIR.mkdir(exist_ok=True)
    n_res = n_dl = 0
    for mid in memory_ids:
        res = post("/v1/GetResidueOfMemory", {"memoryID": mid})
        time.sleep(PAUSE)
        if not isinstance(res, list):
            continue
        for r in res:
            n_res += 1
            # find a fetchable file reference in the record
            fname = next((str(v) for k, v in r.items()
                          if isinstance(v, str) and v
                          and k.lower() in ("filename", "file", "path",
                                            "url", "imageurl", "fileurl")),
                         None)
            local = None
            if fname:
                url = fname if fname.startswith("http") else \
                    f"{BASE}/{fname.lstrip('/')}"
                url = urllib.parse.quote(url, safe=":/")
                target = RESIDUE_DIR / f"{r['ID']}_{Path(fname).name}"
                if target.exists():
                    local = str(target.relative_to(REPO_ROOT))
                else:
                    try:
                        req = urllib.request.Request(
                            url, headers={"User-Agent":
                                          "mandelabible-harvest/1.0"})
                        with urllib.request.urlopen(req, timeout=60) as f:
                            target.write_bytes(f.read())
                        local = str(target.relative_to(REPO_ROOT))
                        n_dl += 1
                        time.sleep(PAUSE)
                    except Exception as e:  # noqa: BLE001
                        print(f"  residue {r['ID']}: download failed ({e})")
            con.execute(
                """INSERT OR REPLACE INTO tsbc_residue
                   (id, memory_id, file_name, local_path, raw)
                   VALUES (?,?,?,?,?)""",
                (r["ID"], mid, fname, local, json.dumps(r)))
    con.commit()
    print(f"{n_res} residue records harvested, {n_dl} files downloaded")
    print(f"expected per server metrics: {metrics}")
    con.close()


if __name__ == "__main__":
    main()
