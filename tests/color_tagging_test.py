from __future__ import annotations

import json
import pathlib
import re

import pytest

import google_keep_extractor

INPUT_DATA_DIR = pathlib.Path('testing') / 'input' / 'Takeout' / 'Keep'


def _parse_title_hints(title: str) -> dict[str, str]:
    hints: dict[str, str] = {}
    if 'default color' in title:
        hints['color'] = 'default'
    else:
        color_match = re.search(r'\bwith color (\w+)', title)
        if color_match:
            hints['color'] = color_match.group(1).lower()

    bg_match = re.search(r'\bbackground (\w+)', title)
    if bg_match:
        hints['background'] = bg_match.group(1).lower()
    return hints


def test_color_native_extraction():
    """Validates that color is natively extracted from test notes."""
    json_files = list(INPUT_DATA_DIR.glob('*.json'))
    assert len(json_files) > 0, 'No JSON files found in input test data'

    colors_tested: set[str] = set()
    for file_path in json_files:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        if data.get('isTrashed'):
            continue

        raw_title = data.get('title', '')
        hints = _parse_title_hints(raw_title)
        validation_labels = [
            lbl.get('name')
            for lbl in data.get('labels', [])
            if isinstance(lbl, dict)
        ]

        note = google_keep_extractor._load_note(file_path)

        if 'color' in hints:
            expected_color = hints['color']
            if expected_color == 'default':
                assert note.color is None, (
                    f'Expected no color for note {raw_title}, got {note.color}'
                )
            else:
                assert note.color == expected_color, (
                    f'Expected color {expected_color} for note {raw_title}, '
                    f'got {note.color}'
                )
                colors_tested.add(note.color)

        if (
            'testcolor' in validation_labels
            and hints.get('color') != 'default'
        ):
            assert note.color is not None, (
                f'Note {raw_title} has validation #testcolor but no color'
            )

    # Validate that all 11 non-default Keep colors were tested
    assert len(colors_tested) == 11


def test_independent_labels_preserved():
    """Validates that independent labels (label1, label2, etc.) are
    preserved."""
    json_files = list(INPUT_DATA_DIR.glob('*.json'))
    for file_path in json_files:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        if data.get('isTrashed'):
            continue

        raw_labels = [
            lbl.get('name')
            for lbl in data.get('labels', [])
            if isinstance(lbl, dict)
        ]
        independent_labels = [
            lbl
            for lbl in raw_labels
            if lbl
            in (
                'label1',
                'label2',
                'label3',
                'Sample label',
                'Another label',
            )
        ]

        note = google_keep_extractor._load_note(file_path)
        for expected in independent_labels:
            assert expected in note.labels, (
                f'Label {expected} missing in note {note.title}'
            )


def test_custom_color_label_tagging():
    """Validates custom color label categorization with default and custom
    mappings."""
    clay_note_path = INPUT_DATA_DIR / 'Lorem Ipsum with color clay.json'
    assert clay_note_path.exists()

    expected_clay_label = (
        google_keep_extractor.COLOR_LABEL_MAP.get('BROWN')
        or google_keep_extractor.COLOR_LABEL_MAP.get('clay')
        or f'{google_keep_extractor.COLOR_LABEL_PREFIX}clay'
    )
    note_default = google_keep_extractor._load_note(clay_note_path)
    assert expected_clay_label in note_default.labels
    assert note_default.color == 'clay'

    # Custom mapping to custom color label with prefix
    original_map = dict(google_keep_extractor.COLOR_LABEL_MAP)
    custom_map = dict(google_keep_extractor.COLOR_LABEL_MAP)
    custom_map['BROWN'] = 'color:clay'
    try:
        google_keep_extractor.COLOR_LABEL_MAP = custom_map
        note_custom = google_keep_extractor._load_note(clay_note_path)
        assert 'color:clay' in note_custom.labels
    finally:
        google_keep_extractor.COLOR_LABEL_MAP = original_map


def test_custom_color_label_toggle():
    """Validates toggling off ADD_CUSTOM_COLOR_LABELS."""
    clay_note_path = INPUT_DATA_DIR / 'Lorem Ipsum with color clay.json'
    expected_clay_label = (
        google_keep_extractor.COLOR_LABEL_MAP.get('BROWN')
        or google_keep_extractor.COLOR_LABEL_MAP.get('clay')
        or f'{google_keep_extractor.COLOR_LABEL_PREFIX}clay'
    )
    try:
        google_keep_extractor.ADD_CUSTOM_COLOR_LABELS = False
        note = google_keep_extractor._load_note(clay_note_path)
        assert expected_clay_label not in note.labels
        assert 'clay' not in note.labels
        assert 'testcolor' in note.labels
        assert note.color == 'clay'
    finally:
        google_keep_extractor.ADD_CUSTOM_COLOR_LABELS = True


def test_background_extraction_and_custom_label(tmp_path):
    """Validates background extraction and custom label categorization."""
    fake_note_data = {
        'color': 'DEFAULT',
        'isTrashed': False,
        'isPinned': False,
        'isArchived': False,
        'textContent': 'Sample text with background',
        'title': 'Synthetic background note',
        'createdTimestampUsec': 1791391504499000,
        'userEditedTimestampUsec': 1791391504499000,
        'background': 'groceries',
        'labels': [{'name': 'mylabel'}],
    }
    fake_note_file = tmp_path / 'fake_bg.json'
    with open(fake_note_file, 'w', encoding='utf-8') as f:
        json.dump(fake_note_data, f)

    note = google_keep_extractor._load_note(fake_note_file)
    assert note.background == 'groceries'
    assert 'background_groceries' in note.labels
    assert 'mylabel' in note.labels
    assert 'Background: groceries' in google_keep_extractor._note_to_str(note)

    # With backgroundTheme key
    fake_note_data['background'] = None
    fake_note_data['backgroundTheme'] = 'places'
    with open(fake_note_file, 'w', encoding='utf-8') as f:
        json.dump(fake_note_data, f)

    note2 = google_keep_extractor._load_note(fake_note_file)
    assert note2.background == 'places'
    assert 'background_places' in note2.labels
    assert 'Background: places' in google_keep_extractor._note_to_str(note2)


def test_get_color_and_background_edge_cases():
    """Tests edge cases for _get_color and _get_background."""
    assert google_keep_extractor._get_color({}) is None
    assert google_keep_extractor._get_color({'color': 'DEFAULT'}) is None
    assert google_keep_extractor._get_color({'color': ''}) is None
    assert google_keep_extractor._get_color({'color': 123}) is None
    assert (
        google_keep_extractor._get_color({'color': 'UNKNOWN_COLOR'})
        == 'unknown_color'
    )

    assert google_keep_extractor._get_background({}) is None
    assert google_keep_extractor._get_background({'background': ''}) is None
    assert google_keep_extractor._get_background({'background': 123}) is None
    with pytest.warns(
        UserWarning, match='attempting to add Background anyway'
    ):
        assert (
            google_keep_extractor._get_background({'theme': 'MUSIC'})
            == 'music'
        )


def test_main_export_with_color_data(tmp_path, monkeypatch):
    """Validates running main() end-to-end on test data including colors."""
    temp_export_dir = tmp_path / 'export'
    monkeypatch.setattr(google_keep_extractor, 'IMPORT_PATH', INPUT_DATA_DIR)
    monkeypatch.setattr(google_keep_extractor, 'EXPORT_PATH', temp_export_dir)

    google_keep_extractor.main()

    exported_files = list(temp_export_dir.glob('*.md'))
    # 13 original active notes + 25 new test notes = 38
    assert len(exported_files) == 38

    # Check that a colored note export contains the custom color label
    # and Color line
    clay_exports = [
        f for f in exported_files if 'Lorem_Ipsum_with_color_clay' in f.name
    ]
    assert len(clay_exports) == 1
    with open(clay_exports[0], encoding='utf-8') as f:
        content = f.read()
    expected_clay_label = (
        google_keep_extractor.COLOR_LABEL_MAP.get('BROWN')
        or google_keep_extractor.COLOR_LABEL_MAP.get('clay')
        or f'{google_keep_extractor.COLOR_LABEL_PREFIX}clay'
    )
    assert 'Labels:' in content
    assert expected_clay_label in content
    assert 'testcolor' in content
    assert 'Color: clay' in content
