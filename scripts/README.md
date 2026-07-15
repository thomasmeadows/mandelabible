# Scripts

Numbered, idempotent Python scripts — one per roadmap task. Run them in
number order from the repo root:

```
python3 scripts/01_create_db.py
python3 scripts/02_import_kjv.py
```

Conventions:

- **Numbering**: `NN_task_name.py`, where `NN` matches the roadmap task order
  (01–02 = Phase 1, 03–04 = Phase 2, etc.). New tasks take the next number.
- **Idempotent**: every script is safe to re-run; it creates tables with
  `IF NOT EXISTS` and replaces its own data rather than duplicating it.
- **Standard library only** (`sqlite3`, `re`, `json`, ...). Adding a pip
  dependency requires a roadmap Decision Log entry first.
- All scripts read source data from the read-only sub-repos
  (`bible_databases/`, `bible_forge_db/`) and write only to `db/mandela.db`,
  which is gitignored and fully rebuildable from these scripts.
