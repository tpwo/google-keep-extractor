# Google Keep Extractor

It parses JSON files from Keep export and converts them to a single
structured Markdown file. Attachments and images are ignored.

You can download Google Keep backup file by visiting:

<https://takeout.google.com/takeout/custom/keep?hl=en&continue=https://myaccount.google.com/dashboard>

You can export data to a `.zip` or `.tgz` archive which has the following structure:

```
└── Takeout
    ├── Keep
    │   ├── JSON & HTML files, and attachments
    └── archive_browser.html
```

Copy `Takeout` folder into root of this repo, and run the script:

    python google_keep_extractor.py

Python 3.8 or later is needed. No additional packages are required.

After running the script, Markdown file with timestamp in filename is
created in the `export` folder. This single file contains all notes
separated with `---`.
