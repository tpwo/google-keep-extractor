# Google Keep Extractor

Parse JSON files from Keep export and convert them to Markdown files. Attachments and images are preserved.

You can download Google Keep backup file by visiting:

<https://takeout.google.com/takeout/custom/keep>

You can export data to a `.zip` or `.tgz` archive which has the following structure:

```
└── Takeout
    ├── Keep
    │   ├── JSON & HTML files, and attachments
    └── archive_browser.html
```

Copy `Takeout` folder into root of this repo, and run the script:

    python google_keep_extractor.py

Python 3.10 or later is supported. No additional packages are required.

After running the script, Markdown files with timestamp in the filename are created and written to an `export` folder.

## Main features

- Writes individual `.md` files.
- Includes attachments.
- Writes Keep's Labels into the files.

## Use Case

Personally, I wanted to get these into Apple Notes. Notes supports RTFD imports of multiple files. I've used Bear (from the App Store) to import the Markdown files into it, and export RTF files. This was easier than tinkering with Pandoc.
