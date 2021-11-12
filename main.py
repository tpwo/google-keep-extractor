import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Note:
    title: str
    text: str


def main():
    # https://stackoverflow.com/a/60634040/14458327
    # This makes it possible to do: python main.py > notes.md
    # It also makes it work with grep etc.
    sys.stdout.reconfigure(encoding='utf-8')

    for note in load_notes(Path("Keep")):
        print_note(note)


def load_notes(folder: Path) -> list[Note]:
    notes = []
    for item in Path(folder).iterdir():
        if item.suffix == ".json":
            notes.append(load_note(item))
    return notes


def load_note(path: Path) -> Note:
    with open(path, "r", encoding="utf-8") as file:
        note_object = json.load(file)
        title = note_object["title"] if note_object["title"] else path.stem

        return Note(title=title, text=note_object["textContent"])


def print_note(note: Note) -> None:
    print(f"# {note.title}\n")
    print(note.text)
    print("\n---\n")


if __name__ == "__main__":
    main()
