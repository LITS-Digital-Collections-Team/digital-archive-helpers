# doc-scanner — User manual & walkthrough

## Summary

`doc-scanner` recursively scans a directory for `.txt`, `.docx`, and (optionally) `.doc` files, performs a case‑insensitive substring search, and reports matches with line numbers (for `.txt`) or paragraph indices (for `.docx`/`.doc`). Optional flags let you write results to a file and copy matched files to a folder.

## Requirements

- Python 3.8+ recommended
- `python-docx` for `.docx` support: `pip install python-docx`
- Optional: a `.doc` reader. The script attempts to import a module named `python_doc` (imported as `python_doc` in the code). That module is uncommon; for robust `.doc` extraction prefer `textract` or system tools (antiword/catdoc).

## Quick install

```bash
python -m venv venv
source venv/bin/activate
pip install python-docx
# Optional: pip install textract (and its system deps) for .doc support
```

## Usage

```bash
python doc-scanner.py <directory> <search_string> [options]
```

- `directory` — root folder to scan (recursive)
- `search_string` — case‑insensitive substring to find by default (quote if contains spaces). Use `--regex` to treat this as a regular expression.
- `-o / --output` — write plain‑text results to the specified file (will overwrite)
- `-c / --copy` — copy matched files to an existing folder (uses `shutil.copy2`)
- `-r / --regex` — treat `search_string` as a case‑insensitive regular expression
- `-e / --exclude` — glob pattern to exclude (repeatable). Patterns match file basenames, relative paths, and path segments (e.g. `node_modules`, `*.log`)
- `-v / --verbose` — increase verbosity (use `-v` for INFO, `-vv` for DEBUG)
- `-w / --workers` — number of parallel worker threads (default `1` disables parallelism)

## Examples

- Basic (substring search):
  ```bash
  python doc-scanner.py /path/to/dir "search phrase"
  ```
- Regex search (case-insensitive):
  ```bash
  python doc-scanner.py /path/to/dir "^search.*phrase$" -r
  ```
- Write results to file (overwrites) and increase verbosity:
  ```bash
  python doc-scanner.py /path/to/dir "search" -o results.txt -v
  ```
- Exclude `node_modules` and `*.log`, use 4 threads:
  ```bash
  python doc-scanner.py /path/to/dir "search" -e node_modules -e "*.log" -w 4
  ```
- Copy matched files to an existing folder:
  ```bash
  python doc-scanner.py /path/to/dir "search" -c /tmp/matches
  ```

## Output format

Each reported match appears as:

/full/path/to/file.ext: [num1, num2, ...]

- `.txt` → numbers = line numbers (1-based)
- `.docx` / `.doc` → numbers = paragraph indices (1-based)

When `-o` is used the script writes one match per line to the output file. When `-c` is used the script copies matched files to the destination (destination must exist; the script will exit if it does not).

## How it works (short)

- Scans the tree with `os.walk` and selects files ending in `.txt`, `.docx`, or `.doc`.
- `.txt`: opened with `errors='ignore'`, searched line-by-line; matches collect line numbers.
- `.docx`: uses `python-docx` (`Document`) and iterates `document.paragraphs`; matches collect paragraph indices.
- `.doc`: attempts `python_doc` (if installed) or `textract` as a fallback; if neither is present `.doc` files are skipped.
- Matching: case‑insensitive substring by default, or a case‑insensitive regex when `--regex` is used.

## Limitations & notes

- Substring matching by default; use `--regex` for regex searches.
- `.txt` files opened with `errors='ignore'` — some characters may be silently dropped.
- Paragraph indices for Word docs are a convenience and may not match line semantics.
- Parallel scanning uses threads; very large workloads may benefit from process-based workers or optimized extraction tools.

## Enabling robust `.doc` support

Recommended approaches:

- `textract` (Python): `pip install textract` and ensure its system dependencies are installed; use `textract.process()` to extract text from `.doc` files before searching.
- System tools: install `antiword` or `catdoc` and call them via `subprocess` to extract plain text.

## Security & permissions

- The script reads all readable files under the provided root. Avoid scanning sensitive system directories.
- Copying retains metadata (via `shutil.copy2`) — ensure destination and policy allow storing copies.

## Troubleshooting

- `ModuleNotFoundError: No module named 'docx'` → `pip install python-docx`
- `.doc files skipped` → enable a `.doc` extractor (see above)
- Permission errors → run as a user with read access to target files
- Output file not written → verify path and write permissions; output is overwritten when `-o` is used

## Contact & license

- Author: Patrick R. Wallace <mail.prw@gmail.com>
- License: GNU General Public License v3 (see header in `doc-scanner.py`)
