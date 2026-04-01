# text-collapser: User Manual

## Overview

**text-collapser.py** removes all empty lines from a text file and writes the result to a new file in the current working directory. The original file is not modified.

---

## Usage

```sh
python text-collapser.py <input_file>
```

| Argument | Description |
|---|---|
| `input_file` | Path to the input text file |

---

## Output

The output file is written to the **current working directory** with `_collapsed` appended to the input filename stem:

```
<stem>_collapsed.txt
```

**Example:**
```sh
python text-collapser.py notes.txt
# Output: notes_collapsed.txt
```

---

## Example

**Input `notes.txt`:**
```
line one

line two


line three
```

**Output `notes_collapsed.txt`:**
```
line one
line two
line three
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
