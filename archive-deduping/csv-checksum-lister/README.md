# csv-checksum-lister

Generate checksums for files in a directory tree (read-only)

Overview

`csv-checksum-lister` recursively traverses a source directory and
calculates checksums for files, writing results to a CSV file with
columns `checksum`, `path`, and `filename`.

This tool is intended for read-only filesystem analysis (migration
verification, integrity checks, duplicate detection). It explicitly
avoids modifying the source filesystem.

Requirements

- Python 3.6+

Quick start

```bash
# analyze current directory, default output file is file_checksums.csv
python csv-checksum-lister.py .

# analyze /data/source and write to migration_checksums.csv
python csv-checksum-lister.py /data/source -o migration_checksums.csv

Read file list from stdin

You can provide a newline-separated list of file paths on stdin instead of
traversing a directory. This is useful when you already have a list of
files to checksum (for example, from another tool or a filtered list).

```bash
# Provide a file list on stdin
printf '/path/to/file1\n/path/to/file2\n' | python csv-checksum-lister.py --stdin -o selected_checksums.csv
```
```

Usage

```text
usage: csv-checksum-lister.py <source_path> [-o OUTPUT] [-s MAX_SIZE] [-a ALGORITHM] [--log-skipped]

Arguments:
  source_path         Root directory to traverse

Options:
  -o, --output FILE   Output CSV file path (default: file_checksums.csv)
  -s, --max-size GB   Maximum file size in GB to process (default: 1.0)
  -a, --algorithm ALG Hash algorithm: md5, sha1, sha256, sha512 (default: sha256)
  --log-skipped       Create additional file listing non-system files that were skipped
  -h, --help          Show help message and exit
```

Examples

```bash
# Basic usage - analyze current directory
python csv-checksum-lister.py .

# Use MD5 and limit files to 500MB
python csv-checksum-lister.py /path/to/source -s 0.5 -a md5

# Write a skipped-files report alongside output CSV
python csv-checksum-lister.py /mnt/old_storage -o /tmp/checksums.csv --log-skipped

# Windows example
python csv-checksum-lister.py "C:\\Data\\Migration Source" -o "D:\\Reports\\checksums.csv"
```

Behavior and notes

- Read-only: The script only opens files for reading (`rb`) and writes
  output to a CSV outside the source tree. It validates that the chosen
  output path is not inside the source path and will exit if it is.
- Size filtering: Files larger than the `--max-size` (GB) are skipped.
- Restricted paths: Any file or directory whose path contains
  `RESTRICTED` (case-insensitive) is excluded from traversal.
- System files automatically skipped: `.DS_Store`, `Thumbs.db`,
  `Desktop.ini`, and `._.DS_Store`.
- Error handling: Files that cannot be read are reported and skipped;
  processing continues.
- Chunked reads: Files are read in 8 KB chunks for memory efficiency.

Output format

CSV (UTF-8) with header row:

```
checksum,path,filename
<hex-hash>,/absolute/path/to/file.ext,file.ext
```

Skipped-files report

If `--log-skipped` is provided, a text report named
`<output_basename>_skipped.txt` is written that groups skipped files by
reason (e.g., "File too large", "Contains RESTRICTED", "Error: ...").

Exit codes

- `0` — success
- `1` — error (invalid source path, safety violation, I/O error, etc.)

Performance and tips

- Use `sha256` (default) for strong integrity checks; use `md5` for
  faster but less secure hashing when speed matters.
- Run the script on a machine with local access to the storage for best
  throughput; remote/network filesystems will be slower.
- For very large datasets, consider splitting the source or running in
  parallel (script is single-threaded by default).

Author & License

Author: Patrick R. Wallace <mail.prw@gmail.com>
License: GNU GPLv3
