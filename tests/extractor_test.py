from __future__ import annotations

import pathlib
import shutil

import google_keep_extractor


def test_main_extraction(tmp_path, monkeypatch):
    testing_dir = pathlib.Path('testing')
    input_dir = testing_dir / 'input' / 'Takeout' / 'Keep'
    expected_export_dir = testing_dir / 'expected' / 'export'

    temp_takeout_dir = tmp_path / 'Takeout' / 'Keep'
    temp_takeout_dir.mkdir(parents=True)
    temp_export_dir = tmp_path / 'export'

    [
        shutil.copy(item, temp_takeout_dir)
        for item in input_dir.iterdir()
        if item.is_file()
    ]

    monkeypatch.setattr(google_keep_extractor, 'IMPORT_PATH', temp_takeout_dir)
    monkeypatch.setattr(google_keep_extractor, 'EXPORT_PATH', temp_export_dir)

    google_keep_extractor.main()

    generated_files = list(temp_export_dir.rglob('*'))
    expected_files = list(expected_export_dir.rglob('*'))

    generated_only_files = [f for f in generated_files if f.is_file()]
    expected_only_files = [f for f in expected_files if f.is_file()]

    assert len(generated_only_files) == len(expected_only_files)

    for expected_file in expected_only_files:
        relative_path = expected_file.relative_to(expected_export_dir)
        generated_file = temp_export_dir / relative_path

        assert generated_file.exists(), f'{relative_path} was not generated'

        if expected_file.suffix == '.md':
            with open(expected_file, encoding='utf-8') as f:
                expected_content = f.read()
            with open(generated_file, encoding='utf-8') as f:
                generated_content = f.read()
            assert generated_content == expected_content, (
                f'Content mismatch in {relative_path}'
            )
        else:
            with open(expected_file, 'rb') as bin_f:
                expected_bytes = bin_f.read()
            with open(generated_file, 'rb') as bin_f:
                generated_bytes = bin_f.read()
            assert generated_bytes == expected_bytes, (
                f'Binary content mismatch in {relative_path}'
            )
