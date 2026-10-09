from __future__ import annotations

import pathlib
import shutil
from unittest import mock

import pytest

import google_keep_extractor

TESTING_DIR = pathlib.Path('testing')
EXPECTED_EXPORT_DIR = TESTING_DIR / 'expected' / 'export'
EXPECTED_FILES = sorted(
    path.relative_to(EXPECTED_EXPORT_DIR)
    for path in EXPECTED_EXPORT_DIR.rglob('*')
    if path.is_file()
)


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


@pytest.fixture
def generated_dir(export_dir):
    """Run the extractor on test input and return the export dir."""
    google_keep_extractor.main()
    return export_dir


def test_generated_file_set(generated_dir):
    assert EXPECTED_FILES, f'no expected files in {EXPECTED_EXPORT_DIR}'

    generated_rel = sorted(
        path.relative_to(generated_dir)
        for path in generated_dir.rglob('*')
        if path.is_file()
    )

    assert generated_rel == EXPECTED_FILES


@pytest.mark.parametrize('relative_path', EXPECTED_FILES, ids=str)
def test_generated_file_content(generated_dir, relative_path):
    expected_file = EXPECTED_EXPORT_DIR / relative_path
    generated_file = generated_dir / relative_path

    if expected_file.suffix == '.md':
        assert generated_file.read_text(
            encoding='utf-8'
        ) == expected_file.read_text(encoding='utf-8')
    else:
        assert generated_file.read_bytes() == expected_file.read_bytes()
