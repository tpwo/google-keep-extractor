from __future__ import annotations

import pathlib
import shutil

import google_keep_extractor


def test_main_extraction(tmp_path, monkeypatch):
    # Setup
    testing_dir = pathlib.Path('testing')
    input_dir = testing_dir / 'input' / 'Takeout' / 'Keep'
    expected_export_dir = testing_dir / 'expected' / 'export'

    # Create temporary input and export directories
    temp_takeout_dir = tmp_path / 'Takeout' / 'Keep'
    temp_takeout_dir.mkdir(parents=True)
    temp_export_dir = tmp_path / 'export'

    # Copy input files to the temporary input directory
    [
        shutil.copy(item, temp_takeout_dir)
        for item in input_dir.iterdir()
        if item.is_file()
    ]

    # Monkeypatch the constants in google_keep_extractor
    monkeypatch.setattr(google_keep_extractor, 'IMPORT_PATH', temp_takeout_dir)
    monkeypatch.setattr(google_keep_extractor, 'EXPORT_PATH', temp_export_dir)

    # Execute
    google_keep_extractor.main()

    # Verification
    # Compare generated files with expected files
    generated_files = list(temp_export_dir.rglob('*'))
    expected_files = list(expected_export_dir.rglob('*'))

    # Check if the number of files (excluding directories) matches
    generated_only_files = [f for f in generated_files if f.is_file()]
    expected_only_files = [f for f in expected_files if f.is_file()]

    assert len(generated_only_files) == len(expected_only_files)

    for expected_file in expected_only_files:
        relative_path = expected_file.relative_to(expected_export_dir)
        generated_file = temp_export_dir / relative_path

        assert generated_file.exists(), f'{relative_path} was not generated'

        if expected_file.suffix == '.md':
            # Compare text content for Markdown files
            with open(expected_file, encoding='utf-8') as f:
                expected_content = f.read()
            with open(generated_file, encoding='utf-8') as f:
                generated_content = f.read()
            assert generated_content == expected_content, (
                f'Content mismatch in {relative_path}'
            )
        else:
            # Compare binary content for attachments (e.g., images)
            with open(expected_file, 'rb') as f:
                expected_content = f.read()
            with open(generated_file, 'rb') as f:
                generated_content = f.read()
            assert generated_content == expected_content, (
                f'Binary content mismatch in {relative_path}'
            )
