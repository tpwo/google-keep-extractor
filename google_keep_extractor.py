from __future__ import annotations

import dataclasses
import json
import pathlib
import re
import shutil
from datetime import datetime

TITLE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FILE_TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

IMPORT_PATH = pathlib.Path('Takeout/Keep')
EXPORT_PATH = pathlib.Path('export')

JSON_NOTE_TITLE = 'title'
JSON_NOTE_TEXT = 'textContent'
JSON_NOTE_LIST = 'listContent'


@dataclasses.dataclass
class Note:
    title: str
    created_at: datetime
    text: str
    attachments: list[str] = dataclasses.field(default_factory=list)
    labels: list[str] = dataclasses.field(default_factory=list)


def main():
    EXPORT_PATH.mkdir(exist_ok=True)
    for note in _load_notes(IMPORT_PATH):
        timestamp = note.created_at.strftime(FILE_TIME_FORMAT)
        if note.title:
            title = re.sub(r'[^\w\-_\. ]', '', note.title).replace(' ', '_')
            note_export_path = EXPORT_PATH / f'{timestamp}__{title}.md'
        else:
            note_export_path = EXPORT_PATH / f'{timestamp}.md'

        with open(note_export_path, 'w', encoding='utf-8') as file:
            file.write(_note_to_str(note))
        _copy_attachments(note)
        print(f'File `{note_export_path}` saved.')
    print('Export successful!')


def _load_notes(folder: pathlib.Path) -> list[Note]:
    notes = []
    for item in pathlib.Path(folder).iterdir():
        if item.suffix == '.json':
            try:
                notes.append(_load_note(item))
            except Exception as err:
                print(f'Error processing file `{item}`: `{err}`')
    return sorted(notes, key=lambda x: x.created_at, reverse=True)


def _load_note(path: pathlib.Path) -> Note:
    with open(path, encoding='utf-8') as file:
        note_obj = json.load(file)
        if note_obj['isTrashed']:
            raise RuntimeError(
                f"Note '{note_obj[JSON_NOTE_TITLE]}' "
                f"from file '{path}' is trashed"
            )
        title, created_at = _get_title_and_date(note_obj)
        return Note(
            title=title,
            created_at=created_at,
            text=_get_text(note_obj),
            attachments=_get_attachments(note_obj),
            labels=_get_labels(note_obj),
        )


def _get_title_and_date(note: dict[str, object]) -> tuple[str, datetime]:
    usec_to_sec = 1e-6
    timestamp_usec = note['createdTimestampUsec']
    if not isinstance(timestamp_usec, int):
        raise NotImplementedError
    created_at = datetime.fromtimestamp(timestamp_usec * usec_to_sec)

    title_val = note[JSON_NOTE_TITLE]
    if isinstance(title_val, str) and title_val:
        title = title_val.strip()
        if note['isArchived']:
            title = f'[ARCHIVED] {title}'
        elif note['isPinned']:
            title = f'[PINNED] {title}'
    else:
        title = ''

    return title, created_at


def _get_text(note: dict[str, object]) -> str:
    if JSON_NOTE_TEXT in note:
        text = note[JSON_NOTE_TEXT]
        if not isinstance(text, str):
            raise NotImplementedError
        return text
    elif JSON_NOTE_LIST in note:
        items = []
        print(
            f'Note `{note[JSON_NOTE_TITLE]}` '
            "doesn't have text content. Converting..."
        )
        list_content = note[JSON_NOTE_LIST]
        if not isinstance(list_content, list):
            raise NotImplementedError
        for item in list_content:
            if not isinstance(item, dict):
                continue
            is_checked = item.get('isChecked')
            text = item.get('text')
            if not isinstance(text, str):
                text = ''
            checkbox = '[x]' if is_checked else '[ ]'
            items.append(f'* {checkbox} {text}')
        return '\n'.join(items) + '\n'
    else:
        print(
            f"Note `{note[JSON_NOTE_TITLE]}` doesn't have `textContent` "
            f'or `{JSON_NOTE_LIST}`. No text will be extracted.'
        )
        return ''


def _get_attachments(note: dict[str, object]) -> list[str]:
    attachments = note.get('attachments')
    if isinstance(attachments, list):
        file_paths = []
        for attachment in attachments:
            if isinstance(attachment, dict):
                file_path = attachment.get('filePath')
                if isinstance(file_path, str):
                    file_paths.append(file_path)
        return file_paths
    return []


def _get_labels(note: dict[str, object]) -> list[str]:
    labels = note.get('labels')
    if isinstance(labels, list):
        names = []
        for label in labels:
            if isinstance(label, dict):
                name = label.get('name')
                if isinstance(name, str):
                    names.append(name)
        return names
    return []


def _note_to_str(note: Note) -> str:
    """Creates a single Markdown note from `Note` object.

    If any note element is missing, it won't be included, and white-space is
    adjusted.

    Strips trailing white-space from each note element, so there's only a
    single newline between them.

    Ends note content with a single newline as in common Unix standard.
    """
    attachments_str = '\n'.join(
        f'![{pathlib.Path(attachment).name}](attachments/{attachment})'
        for attachment in note.attachments
    )
    labels_str = f'Labels: {", ".join(note.labels)}' if note.labels else ''
    all_elems = f'# {note.title}', note.text, attachments_str, labels_str
    existing_elems = []
    for elem in all_elems:
        if elem:
            existing_elems.append(elem.strip())
    md_content = '\n\n'.join(existing_elems)
    return md_content + '\n'


def _copy_attachments(note: Note):
    for attachment in note.attachments:
        src_path = IMPORT_PATH / attachment
        dest_path = EXPORT_PATH / 'attachments' / attachment
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_path, dest_path)
        print(f'Copied attachment `{src_path}` to `{dest_path}`')


if __name__ == '__main__':
    main()
