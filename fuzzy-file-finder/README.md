# Fuzzy File Finder Utility: User Manual

## Overview

The **Fuzzy File Finder Utility** helps you locate files or directories from a target list within a recursive directory listing (such as the output of `ls -R`, `rclone ls`, or a Windows directory tree). It works through a cascade of matching strategies—name-only, case-sensitive, case-insensitive, and fuzzy—and outputs results to a CSV file for further analysis.

## Features

- Cleans and deduplicates both input files before matching.
- Distinguishes **file** targets (basename has a file extension) from **directory** targets (no extension).
- Matches using a cascade of strategies:
  - **name-only:** Basename and immediate parent directory both match.
  - Blank note: Full path matches (case-sensitive substring).
  - Blank note: Full path matches (case-insensitive substring).
  - **fuzzy:** Close match found via `fuzzywuzzy` (threshold: score ≥ 60).
- Adds **duplicate** to the notes when a strategy produces more than one match.
- Processes targets in input order.
- Displays a progress bar during the search.

## How It Works

1. **Input Preparation**
   - Prepare a plaintext recursive directory listing (e.g., output from `ls -R`, `rclone ls`, or a Windows dir export).
   - Prepare a plaintext list of target filenames or directory names (one per line; may be bare filenames or full/partial paths).
2. **Cleaning**
   - Lines matching `<size> <path>` (rclone/`ls -l` format) have the size prefix stripped.
   - Lines ending with `:` in the listing are treated as directory headers.
   - Empty lines and exact duplicates are removed from both files.
   - Target input order is preserved.
3. **Matching Process** — for each target:
   - A target is treated as a **directory** if its basename has no file extension; otherwise as a **file**.
   - **Directory targets:**
     1. Case-sensitive substring search in directory list → note: `directory`
     2. Case-insensitive substring search → note: `directory`
     3. Fuzzy match → note: `directory;fuzzy`
     4. No match → note: `directory;not found`
   - **File targets:**
     1. If basename + immediate parent directory both match a listing entry → note: `name-only` (search continues)
     2. Case-sensitive substring search → note: blank
     3. Case-insensitive substring search → note: blank
     4. Fuzzy match (score ≥ 60) → note: `fuzzy`
     5. No match → note: `not found`
   - When a strategy produces more than one match, `duplicate` is appended to the note for every row from that strategy.
4. **Output**
   - Results are written to a CSV file with three columns:
     - `file location`: full path from the listing (or `not found`)
     - `target`: the original target string
     - `notes`: match status flags, semicolon-separated (see *Match Status Notes* below)

## Usage

python fuzzy-file-finder.py \<directory_listing.txt\> \<filename_list.txt\> \<output.csv\>

- \<directory_listing.txt\>: Plaintext recursive directory listing.
- \<filename_list.txt\>: Plaintext list of target filenames or directory names.
- \<output.csv\>: Path to the output CSV file.

## Input Example

**directory_listing.txt**

*A18 - Mahaney Arts Center/a18.ii_officer_clemmons_2021-09-22.mp4*

*A18 - Mahaney Arts Center/some_other_file.txt*

*Archives/F4 Academic Departments/f4_architectural-studies/f4_architectural-studies_six-program-aspects_2021-05.mp4*

**filename_list.txt**

*A18 Mahaney Arts Center/a18.ii_officer_clemmons_2021-09-22.mp4*

*F4_architectural-studies_six-program-aspects_2021-05.mp4*

*some_other_file.txt*

## Output Example

**output.csv**

| **file location** | **target** | **notes** |
|----|----|----|
| A18 - Mahaney Arts Center/a18.ii_officer_clemmons_2021-09-22.mp4 | A18 Mahaney Arts Center/a18.ii_officer_clemmons_2021-09-22.mp4 | name-only |
| Archives/F4 Academic Departments/f4_architectural-studies/f4_architectural-studies_six-program-aspects_2021-05.mp4 | F4_architectural-studies_six-program-aspects_2021-05.mp4 | name-only |
| A18 - Mahaney Arts Center/some_other_file.txt | some_other_file.txt | *(blank)* |

## Match Status Notes

| Note | Meaning |
|------|---------|
| *(blank)* | Single case-sensitive or case-insensitive substring match |
| `name-only` | Basename and immediate parent directory both match (search continues for additional matches) |
| `directory` | Match is a directory entry |
| `fuzzy` | Match found via fuzzy matching (score ≥ 60) |
| `duplicate` | More than one match found by the same strategy |
| `not found` | No match found by any strategy |

Notes are combined with semicolons where more than one applies, e.g. `directory;fuzzy`.

## Progress Reporting

A `tqdm` progress bar is shown during the matching stage. Fuzzy matches are printed to the terminal as they are found (score included).

## Requirements

- Python 3.8+
- `fuzzywuzzy` — `pip install fuzzywuzzy`
- `python-Levenshtein` (optional but strongly recommended for speed) — `pip install python-Levenshtein`
- `tqdm` — `pip install tqdm`

## Troubleshooting

- Ensure your input files are plaintext and properly formatted.
- For best results, use high-quality directory listings and accurate target lists.
- If you encounter errors, check for encoding issues or unusual file paths.

## License

GNU General Public License v3 — see the license header in `fuzzy-file-finder.py` or <https://www.gnu.org/licenses/gpl-3.0.html>.

---

## Documentation License

Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>

Permission is granted to copy, distribute, and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation; with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts. A copy of the license is available at <https://www.gnu.org/licenses/fdl-1.3.html>.
