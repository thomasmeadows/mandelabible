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
- **Un-numbered `.py` files are shared modules**, not tasks: `residuals.py`,
  and `custom_export.py` (the engine behind the custom-edition exporters).

## Custom editions

Two exporters build a reader's own variation of the restored text from a JSON
settings file, writing markdown + PDF to `exports/custom/`. They read the
database and never write to it:

```
python3 scripts/79_export_custom.py custom/example-original.json
python3 scripts/80_export_custom_modern.py custom/example-original.json \
                                           custom/example-modern.json
```

Script 79 applies one settings file to the restored text; script 80 re-derives
that same result and stacks the built-in Early Modern → Modern English rules
plus a second settings file on top. Both share `custom_export.py`. The
settings-file reference is in the root [`README.md`](../README.md) →
"Build your own edition".

The two editions published on the website are the same machinery pointed at the
committed `custom/site-original.json` / `custom/site-modern.json`:

```
python3 scripts/81_publish_site_editions.py
```

It writes both editions into `docs/downloads/` and refreshes the download
buttons in `docs/index.html`. **Run it after any database change that alters
the text** — see [`CLAUDE.md`](../CLAUDE.md) → "Publishing to the Website".
