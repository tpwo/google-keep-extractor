from __future__ import annotations

import json
import pathlib
from datetime import datetime
from datetime import timezone

import google_keep_extractor
from google_keep_extractor import Color

INPUT_DATA_DIR = pathlib.Path('testing') / 'input' / 'Takeout' / 'Keep'


def test_color_enum_values():
    assert Color.RED.value == 'coral'
    assert Color.ORANGE.value == 'peach'
    assert Color.YELLOW.value == 'sand'
    assert Color.GREEN.value == 'mint'
    assert Color.TEAL.value == 'sage'
    assert Color.BLUE.value == 'fog'
    assert Color.CERULEAN.value == 'storm'
    assert Color.PURPLE.value == 'dusk'
    assert Color.PINK.value == 'blossom'
    assert Color.BROWN.value == 'clay'
    assert Color.GRAY.value == 'chalk'
    assert Color.DEFAULT.value == 'default'


def test_get_color_edge_cases():
    assert google_keep_extractor._get_color({}) == Color.DEFAULT
    assert (
        google_keep_extractor._get_color({'color': 'DEFAULT'}) == Color.DEFAULT
    )
    assert google_keep_extractor._get_color({'color': ''}) == Color.DEFAULT
    assert google_keep_extractor._get_color({'color': 123}) == Color.DEFAULT
    assert (
        google_keep_extractor._get_color({'color': 'UNKNOWN_COLOR'})
        == Color.DEFAULT
    )
    assert google_keep_extractor._get_color({'color': 'RED'}) == Color.RED
    assert google_keep_extractor._get_color({'color': 'coral'}) == Color.RED


def test_color_extraction_coral_note():
    coral_file = INPUT_DATA_DIR / 'Lorem Ipsum with color coral.json'
    assert coral_file.exists()

    note = google_keep_extractor._load_note(coral_file)
    assert note.color == Color.RED
    assert 'color_coral' in note.labels
    assert 'testcolor' in note.labels

    rendered = google_keep_extractor._note_to_str(note)
    assert 'Color: coral' in rendered
    assert 'Labels: color_coral, testcolor' in rendered


def test_color_extraction_default_note():
    default_file = INPUT_DATA_DIR / 'Lorem Ipsum with default color.json'
    assert default_file.exists()

    note = google_keep_extractor._load_note(default_file)
    assert note.color == Color.DEFAULT
    assert len(note.labels) == 0

    rendered = google_keep_extractor._note_to_str(note)
    assert 'Color:' not in rendered
    assert 'Labels:' not in rendered


def test_custom_color_label_toggle(monkeypatch):
    coral_file = INPUT_DATA_DIR / 'Lorem Ipsum with color coral.json'
    monkeypatch.setattr(
        google_keep_extractor, 'ADD_CUSTOM_COLOR_LABELS', False
    )

    note = google_keep_extractor._load_note(coral_file)
    assert note.color == Color.RED
    assert 'color_coral' not in note.labels
    assert 'testcolor' in note.labels


def test_custom_color_label_prefix(monkeypatch):
    coral_file = INPUT_DATA_DIR / 'Lorem Ipsum with color coral.json'
    monkeypatch.setattr(google_keep_extractor, 'COLOR_LABEL_PREFIX', 'c_')

    note = google_keep_extractor._load_note(coral_file)
    assert note.color == Color.RED
    assert 'c_coral' in note.labels
    assert 'testcolor' in note.labels


def test_label_deduplication(tmp_path):
    note_data = {
        'title': 'Deduplication test',
        'isTrashed': False,
        'isPinned': False,
        'isArchived': False,
        'textContent': 'Sample content',
        'color': 'RED',
        'createdTimestampUsec': 1791391136357000,
        'labels': [{'name': 'color_coral'}, {'name': 'sample'}],
    }
    test_file = tmp_path / 'dedup_note.json'
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(note_data, f)

    note = google_keep_extractor._load_note(test_file)
    assert note.labels == {'color_coral', 'sample'}
    assert len(note.labels) == 2


def test_deterministic_label_sorting():
    note = google_keep_extractor.Note(
        title='Sorting test',
        created_at=datetime.now(timezone.utc),
        text='Some text',
        labels={'zebra', 'alpha', 'medium'},
    )
    rendered = google_keep_extractor._note_to_str(note)
    assert 'Labels: alpha, medium, zebra' in rendered
