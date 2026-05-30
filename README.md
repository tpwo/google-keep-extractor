# Google Keep Extractor

Parse JSON files from Keep export and convert them to Markdown files. Attachments and images are preserved.

You can download Google Keep backup file by visiting:

<https://takeout.google.com/takeout/custom/keep>

You can export data to a `.zip` or `.tgz` archive which has the following structure:

```
└── Takeout
    └── Keep
        └── JSON & HTML files, and attachments
```

Copy `Takeout` folder into root of this repo, and run the script:

    python google_keep_extractor.py

Python 3.10 or later is supported. No additional packages are required.

After running the script, Markdown files with timestamp in the filename are created and written to an `export` folder.

## Main features

- Writes individual `.md` files.
- Includes attachments.
- Writes Keep's Labels into the files.

## Use Cases

## Obsidian

Export is a collection of Markdown files which can be easily imported into Obsidian vault.

## Apple Notes

You can also export your Google Keep backup into Apple Notes. Notes supports RTFD (Rich Text Format Directory) imports of multiple files. Bear (available in the [App Store](https://apps.apple.com/us/app/bear-markdown-notes/id1091189122?mt=12)) can be used to import the Markdown files into it, and export RTF files. This should be easier than tinkering with other tools like Pandoc and creating RTF files directly.
