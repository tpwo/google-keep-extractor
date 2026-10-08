# Google Keep Extractor - Color & Background Tagging Plan & Implementation Summary

## Overview & Goal
Implement a feature in the Google Keep Extractor tool to natively extract note `color` and `background` attributes from Google Takeout exports, and integrate them into note Markdown exports as both dedicated metadata fields and user-configurable custom labels (for visual sorting and organizational workflows).

---

## What Was Done

### 1. Color Extraction & UI Name Mapping
* **Enum to UI Mapping:** Google Keep exports internal uppercase color enums (`RED`, `ORANGE`, `BROWN`, etc.). Defined `COLOR_NAME_MAP` in `google_keep_extractor.py` to translate these to standard Keep UI names (`coral`, `peach`, `clay`, etc.).
* **Data Model:** Extended the `Note` dataclass with `color: str | None = None`.
* **Markdown Output:** Appended a dedicated `Color: <color>` line in `_note_to_str` when a non-default color is present, positioned right below `Labels:`.

### 2. Custom Color Labels (Visual Sorting)
* **Design Rationale:** Designed for users who visually sort notes by color so they can assign meaningful custom labels (e.g., Spanish color names or categories) or use auto-prefixed labels derived from the color.
* **Configurable Mappings:**
  * Defined `COLOR_LABEL_PREFIX = 'color_'`.
  * Defined `COLOR_LABEL_MAP` explicitly line-by-line (e.g. `'BROWN': f'{COLOR_LABEL_PREFIX}clay'`) so users can easily edit or rewrite target labels.
  * Added an example comment block in `google_keep_extractor.py` illustrating how users can define custom labels (e.g., Spanish names: `rojo`, `tierra`, etc.).
  * Added `ADD_CUSTOM_COLOR_LABELS = True` toggle to enable or disable adding custom color labels to the note's `Labels:` list.
* **Non-destructive:** Existing user tags (e.g., `label1`, `#testcolor`) are preserved untouched without prefixing.

### 3. Background Theme Handling & Takeout Limitations
* **Investigation Findings:** Discovered that current Google Keep Takeout exports omit background theme and image metadata from both JSON and HTML files.
* **Forward Compatibility & Diagnostics:**
  * Documented `# FIXME` comments in `google_keep_extractor.py` highlighting this limitation.
  * Implemented `_get_background` looking for potential keys (`background`, `backgroundTheme`, `theme`).
  * Emits an informative `UserWarning` if background metadata is detected, (untested!) while attempting to extract and add it anyway (won't happen... for now).
  * Defined `BACKGROUND_LABEL_PREFIX = 'background_'` and `BACKGROUND_LABEL_MAP`.
  * Added `Background: <theme>` line in Markdown export if background is present.
  * Extended `Note` dataclass with `background: str | None = None`.

### 4. Test Suite & Validation
* **Consolidated Test Data (`testing/input/Takeout/Keep`):**
  * Migrated 25 test notes into the standard test data directory, adopting the repository's `Lorem Ipsum with ...` naming convention (e.g. `Lorem Ipsum with color blossom.json`, `Lorem Ipsum with background food.json`, `Lorem Ipsum with color coral and background groceries.json`).
  * Regenerated expected export files (`testing/expected/export`) via `testing/regenerate_expected.py`.
  **Dedicated Test Suite (`tests/color_tagging_test.py`):**
  * `test_color_native_extraction`: Verifies color extraction and UI naming across all Keep color test notes in `testing/input/Takeout/Keep`.
  * `test_independent_labels_preserved`: Confirms native labels (`label1`, `label2`, etc.) are retained unmodified.
  * `test_custom_color_label_tagging`: Dynamically checks against `COLOR_LABEL_MAP` values and verifies overriding mappings at runtime.
  * `test_custom_color_label_toggle`: Verifies toggling `ADD_CUSTOM_COLOR_LABELS = False`.
  * `test_background_extraction_and_custom_label`: Tests synthetic notes with background metadata and validates warning emission.
  * `test_get_color_and_background_edge_cases`: Tests null, empty, unexpected types, and default color values.
  * `test_main_export_with_color_data`: Runs `main()` end-to-end on test data and verifies exported Markdown files.
* **Baseline Compatibility:** Original test suite (`tests/extractor_test.py`) continues to pass with zero regressions against all 38 test notes in `testing/expected/export`.
* **Code Hygiene & Linters:**
  * Strict adherence to 79-character line length (`pyproject.toml`).
  * Ruff linter and formatter passed with zero warnings.
  * Mypy type-checking passed with zero errors.

---

## Test Data & Verification Details
* **Validation Labels in Test Data:** Test notes include validation hints (`#testcolor`, `#testbackground`) and independent labels (`label1`, `label2`, `label3`).
* Confirmed that extraction relies purely on native attributes rather than hint labels.
* Exported markdown verified in `testing/expected/export`.
