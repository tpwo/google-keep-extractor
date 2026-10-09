from __future__ import annotations

import pathlib
import shutil
from unittest import mock

import pytest

import google_keep_extractor

TESTING_DIR = pathlib.Path('testing')
EXPECTED_EXPORT_DIR = TESTING_DIR / 'expected' / 'export'


@pytest.fixture
def export_dir(tmp_path):
    """Copy test input to tmp dir and point extractor paths at tmp dirs."""
    input_dir = TESTING_DIR / 'input' / 'Takeout' / 'Keep'
    temp_takeout_dir = tmp_path / 'Takeout' / 'Keep'
    temp_export_dir = tmp_path / 'export'

    shutil.copytree(input_dir, temp_takeout_dir)

    with (
        mock.patch.object(
            google_keep_extractor, 'IMPORT_PATH', temp_takeout_dir
        ),
        mock.patch.object(
            google_keep_extractor, 'EXPORT_PATH', temp_export_dir
        ),
    ):
        yield temp_export_dir


def test_main_extraction(export_dir):
    google_keep_extractor.main()

    generated_rel = {
        path.relative_to(export_dir)
        for path in export_dir.rglob('*')
        if path.is_file()
    }
    expected_rel = {
        path.relative_to(EXPECTED_EXPORT_DIR)
        for path in EXPECTED_EXPORT_DIR.rglob('*')
        if path.is_file()
    }

    assert generated_rel == expected_rel

    for relative_path in expected_rel:
        expected_file = EXPECTED_EXPORT_DIR / relative_path
        generated_file = export_dir / relative_path

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
