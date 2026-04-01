# createItemManifests: User Manual

## Overview

**createItemManifests.py** generates a [IIIF Presentation API 2.x](https://iiif.io/api/presentation/2/) Collection manifest JSON file from a CSV of Internet Archive identifiers and item labels. The resulting manifest can be uploaded to GitHub and ingested into a transcription platform such as [FromThePage](https://fromthepage.com).

---

## Usage

```sh
python createItemManifests.py <input.csv> <collection_label>
```

| Argument | Description |
|---|---|
| `input.csv` | CSV file with `identifier` and `label` columns |
| `collection_label` | Human-readable name for the collection (use quotes if it contains spaces) |

**Example:**
```sh
python createItemManifests.py hemingway.csv "Hemingway Family Archive"
```

---

## Input CSV Format

A CSV with a header row and exactly two required columns:

| Column | Description |
|---|---|
| `identifier` | Internet Archive item identifier |
| `label` | Human-readable label for the item |

**Example `hemingway.csv`:**
```
"identifier","label"
"C50_I_EMH_FR_17_19370818_001","Envelope addressed to Ernest Hemingway from Ivan Beede"
"C50_I_EMH_KW_48_19360725","Letter to Ernest Hemingway from Orlando Ferrer"
```

---

## Output

The script writes a single file to the same directory as the input CSV:

```
<input_basename>_iiif.json
```

**Example:** `hemingway.csv` → `hemingway_iiif.json`

The output is a IIIF Collection manifest where each item in the CSV becomes a `sc:Manifest` entry pointing to the standard Internet Archive IIIF manifest URL:

```
http://iiif.archivelab.org/iiif/{identifier}/manifest.json
```

**Example output structure:**
```json
{
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@type": "sc:Collection",
    "@id": "https://raw.githubusercontent.com/.../hemingway_iiif.json",
    "label": "IIIF Collection for the Hemingway Family Archive collection at Internet Archive",
    "manifests": [
        {
            "@id": "http://iiif.archivelab.org/iiif/C50_I_EMH_FR_17_19370818_001/manifest.json",
            "@type": "sc:Manifest",
            "label": "Envelope addressed to Ernest Hemingway from Ivan Beede"
        }
    ]
}
```

---

## GitHub Base URL

The collection `@id` is constructed from the `GITHUB_MANIFEST_BASE` constant at the top of the script combined with the output filename. Edit this constant to match your repository before use:

```python
GITHUB_MANIFEST_BASE = (
    "https://raw.githubusercontent.com/pwallace/iiif-manifests-for-transcription/main/"
)
```

---

## FromThePage Workflow

To create a collection for transcription in FromThePage:

1. Build a CSV with `identifier` and `label` columns (see above).
2. Run the script to generate `<name>_iiif.json`.
3. Upload the JSON file to GitHub.
4. Use the GitHub raw URL to ingest the collection into FromThePage.

See `fromthepage_manifest_howto.txt` for the full step-by-step workflow including how to pre-filter items by transcription status using the `ia` command-line tool.

---

## Requirements

- Python 3.x (no third-party packages required)

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
