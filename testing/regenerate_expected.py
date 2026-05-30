from __future__ import annotations

import pathlib
import shutil

import google_keep_extractor

# Paths relative to the script
base_dir = pathlib.Path(__file__).parent
input_dir = base_dir / 'input' / 'Takeout' / 'Keep'
expected_export_dir = base_dir / 'expected' / 'export'

# Clean up existing expected export dir
if expected_export_dir.exists():
    shutil.rmtree(expected_export_dir)
expected_export_dir.mkdir(parents=True)

# Monkeypatch
google_keep_extractor.IMPORT_PATH = input_dir
google_keep_extractor.EXPORT_PATH = expected_export_dir

# Run
google_keep_extractor.main()
print(f'Regenerated expected data in {expected_export_dir}')
