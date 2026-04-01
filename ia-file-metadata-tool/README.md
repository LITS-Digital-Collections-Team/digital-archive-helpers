# ia-file-metadata-tool: User Manual

## Overview

**ia-file-metadata-tool.py** allows you to list, set metadata, download, and export `files.xml` for specific files in Internet Archive (IA) items. It supports filtering files by filename pattern (regex) or by file format (as reported in the item's metadata). Only files with `source="original"` are included in any operation.

You can operate on a single IA item (by identifier) or on a batch of items (using `--filelist`).

---

## Usage

```sh
python ia-file-metadata-tool.py <identifier> [options]
python ia-file-metadata-tool.py --filelist <file> [options]
```

---

## Flags

| Flag | Short | Description |
|---|---|---|
| `identifier` | | IA item identifier (positional; omit when using `--filelist`) |
| `--filelist` | `-f` | Path to a file containing IA identifiers, one per line |
| `--pattern` | `-p` | Regex pattern to match filenames |
| `--format` | `-F` | Prompt interactively for a file format to match |
| `--modify FIELD:VALUE` | | Set a metadata field on matched files (repeatable) |
| `--list` | `-l` | List metadata for matched files |
| `--download DIR` | `-D` | Download matching files to `DIR/{identifier}/` |
| `--xml DIR` | `-X` | Save `{identifier}_files.xml` to `DIR/{identifier}/` (only for items with matching files) |

---

## Usage Examples

**List metadata for files matching a pattern in a single item:**
```sh
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --list
```

**List matching files across a batch of items:**
```sh
python ia-file-metadata-tool.py --filelist my_ids.txt --pattern "\.zip$" --list
```

**Set multiple metadata fields on matching files:**
```sh
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" \
    --modify "title:Original Images" --modify "creator:John Doe"
```

**Download matching files:**
```sh
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --download ./downloads
# Files are saved to: ./downloads/{identifier}/filename
```

**Save files.xml for items with matching files:**
```sh
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --xml ./xml_out
# XML is saved to: ./xml_out/{identifier}/{identifier}_files.xml
```

---

## File Filtering

All operations filter files to `source="original"` only. You may further narrow results with:

- `--pattern` — a Python regex matched against the filename (e.g., `"\.zip$"`, `"_images"`)
- `--format` — presents a numbered list of all format values found in the item(s); prompts you to select one

Both `--pattern` and `--format` can be used together.

---

## --format Interactive Mode

When `--format` is specified, the script scans all items in the batch and collects every unique format value, then presents a numbered selection:

```
Available formats:
1: Generic Raw Book Zip
2: Item Tile
3: Metadata
4: Text PDF
Select format by number:
```

---

## Input File Format (--filelist)

A plain text file with one IA identifier per line. Blank lines and leading/trailing whitespace are ignored.

**Example `my_ids.txt`:**
```
c45.05.parsonsl.1812-03-28_images
c45.13.parsonsl.1815-06-21_images
c45.27.parsonsl.1821-12-28_images
```

---

## Output Locations

| Operation | Output path |
|---|---|
| `--download DIR` | `DIR/{identifier}/{filename}` |
| `--xml DIR` | `DIR/{identifier}/{identifier}_files.xml` |

If the specified directory does not exist, you will be prompted to create it.

---

## Requirements

- Python 3.x
- [`internetarchive`](https://pypi.org/project/internetarchive/) Python package
- IA credentials configured (required for `--modify`; not required for `--list`, `--download`, or `--xml`)

---

## License

Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

---

## Documentation License

Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>

Permission is granted to copy, distribute, and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation; with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts. A copy of the license is available at <https://www.gnu.org/licenses/fdl-1.3.html>.
