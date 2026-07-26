#!/usr/bin/env python3
"""80_export_custom_modern.py — automatic modernization of a custom edition.

This exporter sits on top of `79_export_custom.py`. It re-derives the text
from the database rather than parsing script 79's output, and stacks three
layers on the restored Mandela text (base KJV plus every owner-approved
restoration — the memories are already applied):

  1. the FIRST settings file — the same "original version" custom settings
     script 79 uses, so this edition carries those changes
  2. the built-in Early Modern → Modern English rules (thee/thou/thy/ye,
     hath/doth/saith, the -eth/-est verb forms, archaic spellings) with the
     SECOND settings file merged into them: its GlobalReplacements override
     the built-in rule for the same word and add new ones, and its
     VerseReplacements replace whole verses outright

The edition's title and its BookIndex / BookLinks / ChangeAppendix /
CustomSettingAppendix flags come from the second (last) settings file.

Usage:
    python3 scripts/80_export_custom_modern.py [original.json] [modern.json]
                                               [--out-dir DIR]

    original.json  defaults to custom/example-original.json
    modern.json    defaults to custom/example-modern.json

Writes exports/custom/<version-title-slug>.md and .pdf. Idempotent: every run
rebuilds both files from the database and the settings files. Nothing is
written to db/mandela.db.

See the README ("Build your own edition") for the settings-file reference and
for how to override a built-in modernization rule.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from custom_export import (  # noqa: E402
    CUSTOM_DIR, OUT_DIR, Layer, SettingsError, build_edition, load_settings,
    modernization_layer, report,
)

DEFAULT_ORIGINAL = CUSTOM_DIR / "example-original.json"
DEFAULT_MODERN = CUSTOM_DIR / "example-modern.json"


def parse_args(argv):
    paths, out_dir = [], OUT_DIR
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
        elif len(paths) < 2:
            paths.append(Path(arg))
        else:
            raise SettingsError(f"unexpected argument: {arg}")
    original = paths[0] if paths else DEFAULT_ORIGINAL
    modern = paths[1] if len(paths) > 1 else DEFAULT_MODERN
    return original, modern, out_dir


def main(argv) -> None:
    original_path, modern_path, out_dir = parse_args(argv)
    original = load_settings(original_path)
    modern = load_settings(modern_path)
    layers = [
        Layer(f"custom settings ({original_path.name})",
              original.global_replacements, original.verse_replacements,
              original),
        modernization_layer(modern),
    ]
    report(build_edition(layers, out_dir=out_dir))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except SettingsError as exc:
        print(f"ERROR  {exc}")
        raise SystemExit(1)
