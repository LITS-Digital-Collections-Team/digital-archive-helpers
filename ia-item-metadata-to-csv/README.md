# ia-item-metadata-to-csv: User Manual

## Overview

**ia-item-metadata-to-csv.py** searches Internet Archive using a Lucene query and exports the metadata of all matching items to a CSV file. The `identifier` column is always included. Additional metadata fields can be specified as arguments; if omitted, the script defaults to `title`, `creator`, `date`, and `description`.

---

## Usage

```sh
python ia-item-metadata-to-csv.py <query> <output.csv> [field ...]
```

| Argument | Description |
|---|---|
| `query` | Internet Archive search query (Lucene syntax) |
| `output.csv` | Path to the output CSV file |
| `field ...` | One or more metadata field names to export (optional) |

**Default fields** (used when none are specified): `title`, `creator`, `date`, `description`

---

## Examples

**Export default fields for all items in a collection:**
```sh
python ia-item-metadata-to-csv.py "collection:opensea AND mediatype:texts" output.csv
```

**Export specific fields for a single item:**
```sh
python ia-item-metadata-to-csv.py "identifier:my_item_id" output.csv title creator notes
```

**Export notes field for items matching a subject:**
```sh
python ia-item-metadata-to-csv.py "subject:letters AND collection:middleburycollege" letters.csv title date notes
```

---

## Output

A UTF-8 encoded CSV file with `identifier` as the first column, followed by the requested fields in the order specified. If a metadata field is absent for an item, that cell is left blank.

**Example output (`title`, `creator`, `date`, `notes`):**
```
identifier,title,creator,date,notes
1808.rockwoodc.18410304,"Letter from William Slade...","Slade, William",1841-03-04,A full-text transcription...
```

---

## IA Query Syntax

Queries use Lucene syntax as supported by the Internet Archive search API. Common patterns:

| Pattern | Example |
|---|---|
| Search a specific collection | `collection:middleburycollege` |
| Match a single item by identifier | `identifier:my_item_id` |
| Combine conditions | `collection:foo AND mediatype:texts` |
| Exclude a term | `collection:foo NOT mediatype:audio` |

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
