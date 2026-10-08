from __future__ import annotations

import dataclasses
import json
import pathlib
import re
import shutil
import warnings
from datetime import datetime
from datetime import timezone

TITLE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FILE_TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

IMPORT_PATH = pathlib.Path('Takeout/Keep')
EXPORT_PATH = pathlib.Path('export')

JSON_NOTE_TITLE = 'title'
JSON_NOTE_TEXT = 'textContent'
JSON_NOTE_LIST = 'listContent'
JSON_NOTE_COLOR = 'color'

DEFAULT_COLOR = 'DEFAULT'

COLOR_LABEL_PREFIX = 'color_'
BACKGROUND_LABEL_PREFIX = 'background_'

# Map Google Keep internal color enums to Keep UI color names
COLOR_NAME_MAP: dict[str, str] = {
    'RED': 'coral',
    'ORANGE': 'peach',
    'YELLOW': 'sand',
    'GREEN': 'mint',
    'TEAL': 'sage',
    'BLUE': 'fog',
    'CERULEAN': 'storm',
    'PURPLE': 'dusk',
    'PINK': 'blossom',
    'BROWN': 'clay',
    'GRAY': 'chalk',
}

# User-configurable mapping from internal color (or UI name) to
# custom color label. This supports visual sorters who want to assign
# a specific name, or default to deriving one from the color name.
COLOR_LABEL_MAP: dict[str, str] = {
    'RED': f'{COLOR_LABEL_PREFIX}coral',
    'ORANGE': f'{COLOR_LABEL_PREFIX}peach',
    'YELLOW': f'{COLOR_LABEL_PREFIX}sand',
    'GREEN': f'{COLOR_LABEL_PREFIX}mint',
    'TEAL': f'{COLOR_LABEL_PREFIX}sage',
    'BLUE': f'{COLOR_LABEL_PREFIX}fog',
    'CERULEAN': f'{COLOR_LABEL_PREFIX}storm',
    'PURPLE': f'{COLOR_LABEL_PREFIX}dusk',
    'PINK': f'{COLOR_LABEL_PREFIX}blossom',
    'BROWN': f'{COLOR_LABEL_PREFIX}clay',
    'GRAY': f'{COLOR_LABEL_PREFIX}chalk',
}

# Example map using user-define custom colors, uncomment to enable
###
# COLOR_LABEL_MAP: dict[str, str] = {
#     'RED': 'rojo',
#     'ORANGE': 'anaranjado',
#     'YELLOW': 'amarillo',
#     'GREEN': 'verde',
#     'TEAL': 'azulado',
#     'BLUE': 'cielo',
#     'CERULEAN': 'noche',
#     'PURPLE': 'violeta',
#     'PINK': 'rosa',
#     'BROWN': 'tierra',
#     'GRAY': 'piedra',
# }

# User-configurable mapping from background name to custom background label.
## FIXME:  Takeout for Keep does not currently implement this
BACKGROUND_LABEL_MAP: dict[str, str] = {
    'celebration': f'{BACKGROUND_LABEL_PREFIX}celebration',
    'food': f'{BACKGROUND_LABEL_PREFIX}food',
    'groceries': f'{BACKGROUND_LABEL_PREFIX}groceries',
    'music': f'{BACKGROUND_LABEL_PREFIX}music',
    'notes': f'{BACKGROUND_LABEL_PREFIX}notes',
    'places': f'{BACKGROUND_LABEL_PREFIX}places',
    'recipes': f'{BACKGROUND_LABEL_PREFIX}recipes',
    'travel': f'{BACKGROUND_LABEL_PREFIX}travel',
    'video': f'{BACKGROUND_LABEL_PREFIX}video',
}

ADD_CUSTOM_COLOR_LABELS = True


@dataclasses.dataclass
class Note:
    title: str
    created_at: datetime
    text: str
    attachments: list[str] = dataclasses.field(default_factory=list)
    labels: list[str] = dataclasses.field(default_factory=list)
    color: str | None = None
    background: str | None = None


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
        color = _get_color(note_obj)
        background = _get_background(note_obj)
        labels = _get_labels(note_obj)
        if ADD_CUSTOM_COLOR_LABELS:
            raw_color = note_obj.get(JSON_NOTE_COLOR)
            if color:
                custom_color_label = COLOR_LABEL_MAP.get(
                    raw_color if isinstance(raw_color, str) else '',
                    COLOR_LABEL_MAP.get(color, f'{COLOR_LABEL_PREFIX}{color}'),
                )
                if custom_color_label and custom_color_label not in labels:
                    labels.append(custom_color_label)
            if background:
                custom_bg_label = BACKGROUND_LABEL_MAP.get(
                    background, f'{BACKGROUND_LABEL_PREFIX}{background}'
                )
                if custom_bg_label and custom_bg_label not in labels:
                    labels.append(custom_bg_label)
        return Note(
            title=title,
            created_at=created_at,
            text=_get_text(note_obj),
            attachments=_get_attachments(note_obj),
            labels=labels,
            color=color,
            background=background,
        )


def _get_title_and_date(note: dict[str, object]) -> tuple[str, datetime]:
    usec_to_sec = 1e-6
    timestamp_usec = note['createdTimestampUsec']
    if not isinstance(timestamp_usec, int):
        raise NotImplementedError
    created_at = datetime.fromtimestamp(
        timestamp_usec * usec_to_sec, tz=timezone.utc
    )

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


def _get_color(note: dict[str, object]) -> str | None:
    raw_color = note.get(JSON_NOTE_COLOR)
    if isinstance(raw_color, str) and raw_color and raw_color != DEFAULT_COLOR:
        return COLOR_NAME_MAP.get(raw_color, raw_color.lower())
    return None


# FIXME: Google Keep Takeout exports currently do not include background
# theme or image metadata in either JSON or HTML files.
# If background metadata is encountered in note JSON (or future Takeout
# schemas), issue a warning indicating background support is experimental,
# but attempt to extract and add background anyway.
def _get_background(note: dict[str, object]) -> str | None:
    for key in ('background', 'backgroundTheme', 'theme'):
        val = note.get(key)
        if isinstance(val, str) and val:
            warnings.warn(
                f"Background metadata key '{key}' encountered ('{val}'), "
                'but background extraction is not yet officially supported '
                'by Google Takeout exports; attempting to add Background '
                'anyway.',
                UserWarning,
                stacklevel=2,
            )
            return val.lower()
    return None


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
    color_str = f'Color: {note.color}' if note.color else ''

    # FIXME: Google Keep Takeout currently omits background theme/image
    # metadata from export files. If background metadata were present and
    # not None, insert it too (e.g. "Background: groceries"), attempting
    # to add background anyway.
    background_str = (
        f'Background: {note.background}' if note.background else ''
    )

    all_elems = (
        f'# {note.title}',
        note.text,
        attachments_str,
        labels_str,
        color_str,
        background_str,
    )
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
