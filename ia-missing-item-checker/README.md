# ia-missing-item-checker

Finds Internet Archive item identifiers present in a **Corpus** (one or more CSV files) that are **missing** from a **Source** list, and writes all matching Corpus rows to an output CSV. Useful for identifying items that exist in a local metadata export but have not yet been uploaded to, or confirmed in, an Internet Archive collection.

---

## Requirements

- Python 3.6 or later
- No third-party packages required (standard library only)

---

## Usage

```
python ia-missing-item-checker.py SOURCE CORPUS [CORPUS ...] [-o OUTPUT]
```

### Positional arguments

| Argument | Description |
|----------|-------------|
| `SOURCE` | A CSV file containing at least an `identifier` column (header required), **or** a plain-text `.txt` file containing one identifier per line (no header). |
| `CORPUS` | One or more CSV files, or one or more directories whose contents will be scanned for CSV files. Multiple values are accepted. |

### Optional arguments

| Flag | Description |
|------|-------------|
| `-o` / `--output OUTPUT` | Path for the output CSV file. Default: `ia-missing-item-checker_output.csv` |
| `-h` / `--help` | Show help message and exit. |

---

## Examples

```bash
# Single source file + single corpus file
python ia-missing-item-checker.py source-ids.csv corpus.csv

# Single source file + directory of corpus CSV files
python ia-missing-item-checker.py source-ids.csv /path/to/corpus/

# Plain-text source + multiple corpus files, explicit output path
python ia-missing-item-checker.py source.txt part01.csv part02.csv -o missing.csv
```

---

## Input file formats

### Source file

The Source represents the set of identifiers already accounted for (e.g., items confirmed to be live on Internet Archive).

- **CSV**: Must contain an `identifier` column. Additional columns are ignored.
- **TXT**: One identifier per line. Blank lines are ignored. No header row expected.

### Corpus files / directories

The Corpus represents your full local metadata set (e.g., a MODS-to-IA export). Each CSV file must contain an `identifier` column. Files without that column are skipped with a warning. When a directory path is supplied, the script scans it for `*.csv` files (one level deep; subdirectories are not recursed into).

---

## Output

A single CSV containing every Corpus row whose `identifier` was **not** found in the Source. All columns from all processed Corpus files are included; rows that lack a column present in another file receive an empty string for that field.

If no missing identifiers are found, no output file is created and the script exits cleanly.

---

## Behavior notes

- The Source file is validated before any Corpus processing begins. The script exits with a clear error message if the Source is unreadable or malformed.
- Identifiers are matched **case-sensitively**. Internet Archive identifiers are lower-case by convention, but no automatic case normalization is applied.
- Because different Corpus files may carry different column sets, output headers are collected dynamically across all files and written in a single pass at the end. No rows are lost when a new column is encountered in a later file.
- Files that cannot be read (permissions errors, encoding issues, etc.) are skipped with a warning to stderr; processing continues with the remaining files.

---

## License

Copyright (C) 2026 Patrick R. Wallace

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License** as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **without any warranty**; without even the implied warranty of **merchantability** or **fitness for a particular purpose**. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

---

## Documentation License

Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>

Permission is granted to copy, distribute, and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation; with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts. A copy of the license is available at <https://www.gnu.org/licenses/fdl-1.3.html>.
