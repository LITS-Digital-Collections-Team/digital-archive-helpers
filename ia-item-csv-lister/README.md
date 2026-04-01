# ia-item-lister: User Manual

## Overview

**ia-item-lister.py** reads a plain-text list of Internet Archive identifiers, fetches the file listing for each item, and writes the results to a CSV file. Each row represents one item; each column represents a file extension found across all items. If an item has multiple files with the same extension, only the first is recorded. Standard IA-generated files are excluded automatically.

---

## Usage

```sh
python ia-item-lister.py <input_file> <output_file>
```

| Argument | Description |
|---|---|
| `input_file` | Plain-text file with one IA identifier per line |
| `output_file` | Path to the output CSV file |

---

## Example

**`my_ids.txt`:**
```
c45.05.parsonsl.1812-03-28_images
c45.13.parsonsl.1815-06-21_images
```

**Command:**
```sh
python ia-item-lister.py my_ids.txt output.csv
```

**`output.csv`:**
```
identifier,gz,html,json,pdf,xml,zip
c45.05.parsonsl.1812-03-28_images,...,...,...,...,...,c45.05.parsonsl.1812-03-28_images.zip
c45.13.parsonsl.1815-06-21_images,...,...,...,...,...,c45.13.parsonsl.1815-06-21_images.zip
```

---

## Input File Format

A plain-text file with one IA identifier per line. Blank lines and lines with only whitespace are ignored.

---

## Output Format

A CSV with `identifier` as the first column, followed by one column per file extension found across all items (sorted alphabetically). If an item has no file for a given extension, that cell is blank. If an item has more than one file with the same extension, only the first is recorded.

---

## Ignored Files

The following standard IA-generated files are excluded from all items:

| File | Note |
|---|---|
| `__ia_thumb.jpg` | Item thumbnail |
| `{identifier}_archive.torrent` | BitTorrent file |
| `{identifier}_meta.xml` | Item metadata XML |
| `{identifier}_files.xml` | File listing XML |
| `{identifier}_meta.sqlite` | Metadata SQLite database |

---

## Requirements

- Python 3.x
- [`internetarchive`](https://pypi.org/project/internetarchive/) Python package (`pip install internetarchive`)

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
