# file-finder.py

## Description

`file-finder.py` is a Python script designed to help locate files or directories within a large directory tree based on a list of paths. The script reads a plaintext file containing a list of file or directory paths (one per line), extracts only the lowest-level element (the filename or directory name), and then recursively searches the specified root directory for matches.

- If the lowest-level element is a filename, the script returns the full path(s) to the file(s) found.
- If the lowest-level element is a directory name, the script returns the full path(s) to every file found within that directory.

The results are written to two CSV files:
- `files-output.csv`: Contains matches for filenames.
- `dir-output.csv`: Contains matches for directories (one row per file found in each matched directory).

## Usage

```bash
python file-finder.py <root_directory> <file_list.txt>
```

- `<root_directory>`: The directory where the recursive search will begin.
- `<file_list.txt>`: A plaintext file containing a list of file or directory paths (one per line).

## Example

Suppose you have the following in `file_list.txt`:

```
Archives/A29 environmental affairs/a29-iii_environmental-affairs-projects/a29-iii_energy2028/a29_sustainability_energy2028_sustainability_challenge_2021-01.pdf
Archives/A26 student life/a26-iii_message-on-costumes-and-cultural-appropriation_2015-10-29.mp4
Archives/A30 events
```

And your directory tree is rooted at `/media/sysop/MCL_36046/bd-backlog/`.

Run:

```bash
python file-finder.py /media/sysop/MCL_36046/bd-backlog/ file_list.txt
```

### Output

- `files-output.csv` will contain:
    - The original path from the input file
    - The lowest-level element (filename)
    - The full path(s) to the file(s) found (semicolon-delimited if multiple)
- `dir-output.csv` will contain:
    - The original path from the input file
    - The lowest-level element (directory name)
    - The full path to each file found within the matched directory (one row per file)

## CSV Output Format

### files-output.csv

| Original Path | Last Element | Matched Path(s) |
|---------------|-------------|-----------------|
| ...           | ...         | ...             |

### dir-output.csv

| Original Path | Last Element | Matched File    |
|---------------|-------------|-----------------|
| ...           | ...         | ...             |

## Notes

- The script ignores all path elements except the last (filename or directory name).
- If a directory is matched, all files within that directory (recursively) are listed in the output.
- If a filename is matched in multiple locations, all matches are included (semicolon-delimited in `files-output.csv`).
- A path entry is treated as a **file** if its basename contains a file extension (e.g. `.pdf`, `.mp4`); otherwise it is treated as a **directory**.
- A progress bar is displayed during the search.
- When the same name matches both a file and a directory in the tree, the directory match takes priority.

## Requirements

- Python 3.8+
- Required package: `tqdm` — `pip install tqdm`

## Troubleshooting

- If you do not see expected output, check `file_finder.log` for errors.
- Ensure you have read permissions for the root directory and write permissions for the output location.
- The script treats any path ending with a filename extension as a file; otherwise, it assumes a directory.

## License

GNU General Public License v3 — see the license header in `file-finder.py` or <https://www.gnu.org/licenses/gpl-3.0.html>.

---

## Documentation License

Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>

Permission is granted to copy, distribute, and/or modify this document under the terms of the GNU Free Documentation License, Version 1.3 or any later version published by the Free Software Foundation; with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts. A copy of the license is available at <https://www.gnu.org/licenses/fdl-1.3.html>.
