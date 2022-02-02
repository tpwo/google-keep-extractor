from __future__ import annotations

import dataclasses
import json
import pathlib
from datetime import datetime

EXPORT_TIME = datetime.now()
FILE_TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
TITLE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

IMPORT_PATH = pathlib.Path("Takeout/Keep")
EXPORT_PATH = pathlib.Path(f"export/export_{EXPORT_TIME.strftime(FILE_TIME_FORMAT)}.md")

JSON_NOTE_TITLE = "title"
JSON_NOTE_TEXT = "textContent"


@dataclasses.dataclass
class Note:
    title: str
    text: str


def main():
    EXPORT_PATH.parent.mkdir(exist_ok=True)
    with open(EXPORT_PATH, "w", encoding="utf-8") as file:
        file.write(_get_md_header())
        for note in _load_notes(IMPORT_PATH):
            file.write(_note_to_str(note))


def _get_md_header() -> str:
    return (
        f"# Google Keep Export created at {EXPORT_TIME.strftime(TITLE_TIME_FORMAT)}\n\n"
        "Created with: <https://github.com/wojdatto/google-keep-extractor.git>\n\n"
        "---\n\n"
    )


def _load_notes(folder: pathlib.Path) -> list[Note]:
    notes = []
    for item in pathlib.Path(folder).iterdir():
        if item.suffix == ".json":
            notes.append(_load_note(item))
    return notes


def _load_note(path: pathlib.Path) -> Note:
    with open(path, encoding="utf-8") as file:
        note_obj = json.load(file)
        # If note has no title, date from filename will be used instead.
        # It has the following format:
        # 2022-01-31T22_05_49.358+01_00
        creation_date = path.stem.split("T")[0]
        title = (
            note_obj[JSON_NOTE_TITLE] if note_obj[JSON_NOTE_TITLE] else creation_date
        )
        return Note(title=title, text=note_obj[JSON_NOTE_TEXT])


def _note_to_str(note: Note) -> str:
    """Creates a single Markdown note"""
    return f"## {note.title}\n\n{note.text}\n\n---\n\n"


if __name__ == "__main__":
    main()
