# list-cleaner: User Manual

This folder contains two utility scripts for preparing and cleaning file path lists:

- **`list-cleaner.py`** — strips leading file sizes from a recursive directory listing and sorts the result
- **`convert-dos-to-linux-paths.py`** — converts DOS-style backslash paths to Linux-style forward-slash paths

---

## list-cleaner.py

### Overview

Processes a text file containing a recursive directory listing (e.g., output from `rclone ls` or similar tools). Each line is expected to start with a file size or other leading number, followed by a space, then the path. The script strips the leading number, sorts the result, and writes it to an output file. `.DS_Store` and `Thumbs.db` entries are automatically omitted.

### Usage

```sh
python list-cleaner.py [--directories-only | --files-only] <input_file> <output_file>
```

| Argument | Description |
|---|---|
| `input_file` | Text file containing the raw directory listing |
| `output_file` | Output file for the cleaned and sorted paths |
| `--directories-only`, `-d` | Only include directory paths (paths ending in `/` or without a file extension) |
| `--files-only`, `-f` | Only include file paths (paths with a file extension, not ending in `/`) |

Only one of `--directories-only` or `--files-only` may be specified. If neither is given, all paths are included.

### Output Format

- Without a mode flag: directories (paths ending in `/`) are listed first alphabetically, followed by files alphabetically.
- With `--directories-only` or `--files-only`: matching paths are sorted alphabetically.

### Notes

- Lines without a leading number are kept as-is (treated as plain paths).
- Lines matching `.DS_Store` or `Thumbs.db` (with or without a trailing `/`) are automatically omitted.
- Paths are not validated against the filesystem; the file is processed as plain text.

### Example

**Input `rclone-list.txt`:**
```
    14340 0HHF/Ballad Collection/.DS_Store
 53869044 0HHF/Ballad Collection/audio.mp4
   192902 0000/document.pdf
```

**Command:**
```sh
python list-cleaner.py --files-only rclone-list.txt cleaned.txt
```

**Output `cleaned.txt`:**
```
0000/document.pdf
0HHF/Ballad Collection/audio.mp4
```

---

## convert-dos-to-linux-paths.py

### Overview

Converts a list of DOS-style file paths (using backslashes as separators) to Linux-style paths (using forward slashes). Paths without a file extension are treated as directories and have a trailing `/` appended if not already present.

### Usage

```sh
python convert-dos-to-linux-paths.py <input_file> <output_file>
```

| Argument | Description |
|---|---|
| `input_file` | Text file containing DOS-style file paths, one per line |
| `output_file` | Output file for the converted Linux-style paths |

### Example

**Input `dos-paths.txt`:**
```
TopDir\SubDir\file.txt
TopDir\SubDir\photo.jpg
TopDir\SubDir\SubSubDir\
```

**Output `linux-paths.txt`:**
```
TopDir/SubDir/file.txt
TopDir/SubDir/photo.jpg
TopDir/SubDir/SubSubDir/
```

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
