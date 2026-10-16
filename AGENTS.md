# AGENTS.md

## Project

Single-module tool (`google_keep_extractor.py`, stdlib only, Python 3.10+) that converts Google Keep Takeout JSON exports into Markdown files plus copied attachments.

## Commands

- `just regenerate` -- rebuild `testing/expected/export` after changing extraction logic
- `python3 google_keep_extractor.py` -- converts Keep dump (`Takeout/Keep`) to individual markdown files in `export/`
- `just help` -- shows available `just` commands

Requires `uv` and `just`. `just` drives `tox` commands with a standard `tox.ini` config file.

## Testing

Pre-commit (`just pre-commit`) + pytest against supported py versions (`just test`) + coverage (`just coverage`).

Prefer testing all of it at once:

    just all

## Layout

- `google_keep_extractor.py` -- the whole self-contained extraction script
- `pyproject.toml` -- project config file
- `requirements-dev.txt` -- dev deps for the project
- `justfile` -- `just` commands for building and testing the project
- `tests` -- unit tests
- `testing` -- input and expected output for tests
- `.github/workflows` -- GitHub Actions workflows

## Conventions

- Standard Python 3 conventions but with single quotes, line length 79
- Use type annotations (skip them in tests), and verify with pre-commit (mypy hook defined)
