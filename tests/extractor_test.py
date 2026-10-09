from __future__ import annotations

import json
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
def import_path(tmp_path):
    path = tmp_path / 'Takeout' / 'Keep'
    path.mkdir(parents=True)
    return path


@pytest.fixture
def export_path(tmp_path):
    return tmp_path / 'export'


@pytest.fixture
def patched_paths(import_path, export_path):
    """Point extractor input and output paths at tmp dirs."""
    with (
        mock.patch.object(google_keep_extractor, 'IMPORT_PATH', import_path),
        mock.patch.object(google_keep_extractor, 'EXPORT_PATH', export_path),
    ):
        yield


@pytest.fixture
def export_dir(import_path, export_path, patched_paths):
    """Copy test input to tmp input dir and return the tmp export dir."""
    input_dir = TESTING_DIR / 'input' / 'Takeout' / 'Keep'
    shutil.copytree(input_dir, import_path, dirs_exist_ok=True)
    return export_path


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


def test_empty_input_dir(export_path, patched_paths, capsys):
    result = google_keep_extractor.main()

    assert result == 0
    assert list(export_path.iterdir()) == []
    assert 'Export successful!' in capsys.readouterr().out


def test_note_without_text_or_list_prints_message(
    import_path, patched_paths, capsys
):
    note = {
        'title': 'Empty note',
        'createdTimestampUsec': 1780152657754481,
        'isTrashed': False,
        'isArchived': False,
        'isPinned': False,
    }
    (import_path / 'note.json').write_text(json.dumps(note), encoding='utf-8')

    google_keep_extractor.main()

    assert (
        "Note `Empty note` doesn't have `textContent` or `listContent`. "
        'No text will be extracted.'
    ) in capsys.readouterr().out
