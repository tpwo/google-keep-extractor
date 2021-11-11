from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Note:
    title: str
    text: str


def main():
    note = load_note(Path("Keep/2020-06-19T17_42_48.215+02_00.json"))
    print(note)


def load_note(path: Path) -> Note:
    with open(path, "r", encoding="utf-8") as file:
        note_object = json.load(file)
        title = note_object["title"] if note_object["title"] else path

        return Note(title=title, text=note_object["textContent"])


if __name__ == "__main__":
    main()
