from __future__ import annotations

import pathlib
import shutil

import google_keep_extractor


def test_main_extraction(tmp_path, monkeypatch):
    testing_dir = pathlib.Path('testing')
    input_dir = testing_dir / 'input' / 'Takeout' / 'Keep'
    expected_export_dir = testing_dir / 'expected' / 'export'

    temp_takeout_dir = tmp_path / 'Takeout' / 'Keep'
    temp_export_dir = tmp_path / 'export'

    shutil.copytree(input_dir, temp_takeout_dir)

    monkeypatch.setattr(google_keep_extractor, 'IMPORT_PATH', temp_takeout_dir)
    monkeypatch.setattr(google_keep_extractor, 'EXPORT_PATH', temp_export_dir)

    google_keep_extractor.main()

    generated_rel = {
        path.relative_to(temp_export_dir)
        for path in temp_export_dir.rglob('*')
        if path.is_file()
    }
    expected_rel = {
        path.relative_to(expected_export_dir)
        for path in expected_export_dir.rglob('*')
        if path.is_file()
    }

    assert generated_rel == expected_rel

    for relative_path in expected_rel:
        expected_file = expected_export_dir / relative_path
        generated_file = temp_export_dir / relative_path

        if expected_file.suffix == '.md':
            assert generated_file.read_text(
                encoding='utf-8'
            ) == expected_file.read_text(encoding='utf-8'), (
                f'Content mismatch in {relative_path}'
            )
        else:
            assert generated_file.read_bytes() == expected_file.read_bytes(), (
                f'Binary content mismatch in {relative_path}'
            )
