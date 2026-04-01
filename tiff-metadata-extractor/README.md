# tiff-metadata-extractor: User Manual

## Overview

**tiff-metadata-extractor.py** recursively scans a directory for TIFF image files, extracts metadata from each file, and writes the results to a CSV file. Extension matching is case-insensitive (`.tif`, `.tiff`, `.TIF`, `.TIFF` are all found). The original files are not modified.

---

## Usage

```sh
python tiff-metadata-extractor.py <target_directory> [output.csv]
```

| Argument | Description |
|---|---|
| `target_directory` | Directory to scan recursively for TIFF files |
| `output.csv` | Output CSV filename (optional; default: `tiff-metadata.csv`) |

---

## Examples

**Scan a directory with default output filename:**
```sh
python tiff-metadata-extractor.py ./images
# Output: tiff-metadata.csv
```

**Scan with a custom output filename:**
```sh
python tiff-metadata-extractor.py ./images metadata.csv
```

---

## Output

A CSV file with one row per TIFF file. Columns always appear in this order:

| Column group | Columns |
|---|---|
| Identity (always first) | `filename`, `filepath`, `file_size_bytes`, `file_modified` |
| Image properties | `format`, `mode`, `width`, `height` |
| Resolution | `dpi_x`, `dpi_y`, `XResolution`, `YResolution`, `ResolutionUnit` |
| TIFF/EXIF tags | `ImageDescription`, `Make`, `Model`, `Software`, `DateTime`, `Artist`, `Copyright` |
| Other | Any additional `img.info` fields with scalar values; `error` if extraction fails |

Columns from TIFF tags and `img.info` are only present if at least one file in the scan contains that field. Missing values are left blank.

---

## Extracted Metadata Fields

The following TIFF tag IDs are read when present:

| Tag ID | Field name |
|---|---|
| 270 | `ImageDescription` |
| 271 | `Make` |
| 272 | `Model` |
| 282 | `XResolution` |
| 283 | `YResolution` |
| 296 | `ResolutionUnit` |
| 305 | `Software` |
| 306 | `DateTime` |
| 315 | `Artist` |
| 33432 | `Copyright` |

`IFDRational` values (fractional resolution values) are automatically converted to `float`.

---

## Requirements

- Python 3.x
- [`Pillow`](https://pypi.org/project/Pillow/) (`pip install Pillow`)

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
