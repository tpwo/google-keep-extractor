# Google Keep Extractor

It will parse the JSON files and convert them to a big Markdown file.

Backup can be manually downloaded via:

<https://takeout.google.com/takeout/custom/keep?hl=en&continue=https://myaccount.google.com/dashboard>

It will be a `.zip` or `.tgz` archive with the following structure:

    └── Takeout
        ├── Keep
        │   ├── JSON, HTML, and attachments
        └── archive_browser.html

Please, copy `Takeout` folder into this repo root, and run the script:

    python main.py

Python 3.7 or later is needed. No additional packages are required.

After running the script, Markdown file with timestamp in filename in
created in the `export` folder. This single file will contain all notes
which will be separated with `---`.

For a better readability in the source form, consider wrapping lines,
e.g. with [Rewrap](https://github.com/stkb/Rewrap.git) extension
available for VS Code.
