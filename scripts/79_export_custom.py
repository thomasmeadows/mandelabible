#!/usr/bin/env python3
"""79_export_custom.py — export a CUSTOM edition of the restored text.

This is the "original version" exporter: it starts from the restored Mandela
text (base KJV plus every owner-approved restoration — the same text
`17_export_full.py` publishes) and applies ONE settings file of global
word/phrase replacements and whole-verse replacements, keeping the King James
voice unless the settings say otherwise.

Usage:
    python3 scripts/79_export_custom.py [settings.json] [--out-dir DIR]

    settings.json  defaults to custom/example-original.json

Writes exports/custom/<version-title-slug>.md and .pdf. Idempotent: every run
rebuilds both files from the database and the settings file. Nothing is
written to db/mandela.db.

See the README ("Build your own edition") for the settings-file reference.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from custom_export import (  # noqa: E402
    CUSTOM_DIR, OUT_DIR, Layer, SettingsError, build_edition, load_settings,
    report,
)

DEFAULT_SETTINGS = CUSTOM_DIR / "example-original.json"


def parse_args(argv):
    settings, out_dir = None, OUT_DIR
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg in ("-o", "--out-dir"):
            if not args:
                raise SettingsError("--out-dir needs a directory")
            out_dir = Path(args.pop(0))
        elif arg in ("-h", "--help"):
            print(__doc__)
            raise SystemExit(0)
        elif settings is None:
            settings = Path(arg)
        else:
            raise SettingsError(f"unexpected argument: {arg}")
    return settings or DEFAULT_SETTINGS, out_dir


def main(argv) -> None:
    settings_path, out_dir = parse_args(argv)
    settings = load_settings(settings_path)
    layer = Layer(f"custom settings ({settings_path.name})",
                  settings.global_replacements,
                  settings.verse_replacements, settings)
    report(build_edition([layer], out_dir=out_dir))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except SettingsError as exc:
        print(f"ERROR  {exc}")
        raise SystemExit(1)
