# Google Keep Extractor

Parse JSON files from Keep export and convert them to Markdown files. Attachments and images are preserved.

You can download Google Keep backup file by visiting:

<https://takeout.google.com/takeout/custom/keep>

You can export data to a `.zip` or `.tgz` archive which has the following structure:

```
takeout-<timestamp>.<zip/tgz>
└── Takeout
    └── Keep
        └── JSON & HTML files, and attachments
```

Copy `Takeout` folder into root of this repo, and run the script:

    python google_keep_extractor.py

Python 3.10 or later is supported. No additional packages are required.

After running the script, Markdown files with timestamp in the filename are created and written to `export` folder.

## Main features

- Exports notes to individual `.md` files
- Includes attachments
- Adds Keep's Labels into the files
- Pinned notes have their titles starting with `[PINNED]`
- Archived notes have their titles starting with `[ARCHIVED]`
- Trashed notes are skipped (note that they're included in the backup, but we explicitly skip them)

Inspect [testing](testing) folder to see sample Keep backup files and output produced for it by this tool.

## Use Cases

## Obsidian

Export is a collection of Markdown files which can be easily imported into Obsidian vault.

## Apple Notes

You can also export your Google Keep backup into Apple Notes. Notes supports RTFD (Rich Text Format Directory) imports of multiple files. Bear (available in the [App Store](https://apps.apple.com/us/app/bear-markdown-notes/id1091189122?mt=12)) can be used to import the Markdown files into it, and export RTF files. This should be easier than tinkering with other tools like Pandoc and creating RTF files directly.

## Development

Run unit tests against all supported Python versions:

    tox

Measure code coverage:

    tox run -e coverage

Regenerate expected output after any changes in the extraction process:

    tox run -e regenerate
