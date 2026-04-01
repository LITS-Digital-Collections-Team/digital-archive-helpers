#!/usr/bin/env python3
"""
ia-missing-item-checker.py
==========================
Finds identifiers present in a Corpus (one or more CSV files) that are
MISSING from a Source list, and writes all matching Corpus rows to an
output CSV.

Usage
-----
    python ia-missing-item-checker.py SOURCE CORPUS [CORPUS ...] [-o OUTPUT]

Arguments
---------
    SOURCE
        A CSV file containing at least an "identifier" column (header
        required), or a plain-text .txt file containing one identifier
        per line (no header).

    CORPUS
        One or more CSV files, or one or more directories whose contents
        will be scanned for CSV files.  Files that are not CSVs or that
        lack an "identifier" column are silently ignored.

    -o / --output  OUTPUT
        Path for the output CSV file.
        Default: missing-from-source_output.csv

Examples
--------
    # Single source + single corpus file
    python ia-missing-item-checker.py source-ids.csv corpus.csv

    # Single source + directory of corpus files
    python ia-missing-item-checker.py source-ids.csv /path/to/corpus/

    # Multiple corpus files, explicit output path
    python ia-missing-item-checker.py source.txt part01.csv part02.csv -o missing.csv

Notes
-----
    - The Source is validated before processing begins.  The script exits
      with a clear error message if the Source is unreadable or malformed.
    - Corpus CSV files that do not contain an "identifier" column are
      skipped with a warning printed to stderr.
    - Because different Corpus files may carry different columns, headers
      are collected dynamically.  When a new column is encountered in a
      later file, it is appended to the output schema and all previously
      written rows are *not* lost — the output is accumulated in memory
      and written in a single pass at the end, so every column is
      populated correctly.
    - Identifiers are matched case-sensitively (Internet Archive
      identifiers are lower-case by convention).

License
-------
    Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import csv
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------

def load_source(path: str) -> set:
    """
    Load identifiers from the Source file.

    Accepts:
      - .txt  — one identifier per line, no header expected
      - .csv  — must contain an "identifier" column header

    Returns a set of identifier strings.
    Exits with a descriptive error if the file is invalid.
    """
    p = Path(path)

    if not p.exists():
        sys.exit(f"ERROR: Source file not found: {path}")
    if not p.is_file():
        sys.exit(f"ERROR: Source path is not a file: {path}")

    ext = p.suffix.lower()

    # ---- plain-text source ------------------------------------------------
    if ext == ".txt":
        identifiers = set()
        with p.open(encoding="utf-8-sig", newline="") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.strip()
                if line:
                    identifiers.add(line)
        if not identifiers:
            sys.exit(f"ERROR: Source .txt file contains no identifiers: {path}")
        print(f"  Source (.txt): loaded {len(identifiers):,} identifier(s) from '{p.name}'")
        return identifiers

    # ---- CSV source --------------------------------------------------------
    if ext == ".csv":
        identifiers = set()
        with p.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            # Validate that fieldnames were detected
            if reader.fieldnames is None:
                sys.exit(f"ERROR: Source CSV appears to be empty: {path}")
            # Normalise fieldnames for lookup (strip whitespace)
            norm_fields = [f.strip() for f in reader.fieldnames]
            if "identifier" not in norm_fields:
                sys.exit(
                    f"ERROR: Source CSV does not contain an 'identifier' column.\n"
                    f"       Columns found: {reader.fieldnames}\n"
                    f"       File: {path}"
                )
            for row in reader:
                val = row.get("identifier", "").strip()
                if val:
                    identifiers.add(val)
        if not identifiers:
            sys.exit(f"ERROR: Source CSV contains no identifier values: {path}")
        print(f"  Source (.csv): loaded {len(identifiers):,} identifier(s) from '{p.name}'")
        return identifiers

    # ---- unsupported extension --------------------------------------------
    sys.exit(
        f"ERROR: Unrecognised Source file type '{ext}'.\n"
        f"       Source must be a .csv or .txt file."
    )


# ---------------------------------------------------------------------------
# Corpus discovery
# ---------------------------------------------------------------------------

def collect_corpus_files(corpus_args: list) -> list:
    """
    Expand a list of file paths and/or directory paths into a flat list of
    Path objects pointing to CSV files.  Directories are scanned one level
    deep for *.csv files (non-recursive by default; sub-directories are
    skipped with a notice).
    """
    files = []
    for arg in corpus_args:
        p = Path(arg)
        if not p.exists():
            print(f"  WARNING: Corpus path not found, skipping: {arg}", file=sys.stderr)
            continue
        if p.is_file():
            if p.suffix.lower() == ".csv":
                files.append(p)
            else:
                print(
                    f"  WARNING: Corpus file is not a CSV, skipping: {p.name}",
                    file=sys.stderr,
                )
        elif p.is_dir():
            csv_files = sorted(p.glob("*.csv"))
            if not csv_files:
                print(
                    f"  WARNING: No CSV files found in directory: {arg}",
                    file=sys.stderr,
                )
            files.extend(csv_files)
        else:
            print(
                f"  WARNING: Corpus path is neither a file nor a directory, skipping: {arg}",
                file=sys.stderr,
            )
    return files


# ---------------------------------------------------------------------------
# Corpus processing
# ---------------------------------------------------------------------------

def process_corpus(corpus_files: list, source_ids: set) -> tuple:
    """
    Iterate over every corpus CSV file.  For each row whose identifier is
    NOT present in source_ids, accumulate the row dict.

    Returns:
        (rows, ordered_columns)
        rows            — list of dicts, one per missing-identifier row
        ordered_columns — list of column names in encounter order
    """
    ordered_columns = []   # preserves encounter order across all files
    column_set = set()     # fast membership test

    rows = []              # collected output rows

    for csv_path in corpus_files:
        try:
            with csv_path.open(encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)

                if reader.fieldnames is None:
                    print(
                        f"  WARNING: Corpus file appears empty, skipping: {csv_path.name}",
                        file=sys.stderr,
                    )
                    continue

                norm_fields = [f.strip() for f in reader.fieldnames]

                if "identifier" not in norm_fields:
                    print(
                        f"  WARNING: No 'identifier' column in '{csv_path.name}', skipping.",
                        file=sys.stderr,
                    )
                    continue

                # Register any new columns from this file
                for col in norm_fields:
                    if col not in column_set:
                        ordered_columns.append(col)
                        column_set.add(col)

                file_missing = 0
                for row in reader:
                    # Normalise keys (strip whitespace from header names)
                    row = {k.strip(): v for k, v in row.items() if k is not None}
                    ident = row.get("identifier", "").strip()
                    if not ident:
                        continue
                    if ident not in source_ids:
                        rows.append(row)
                        file_missing += 1

                print(
                    f"  Corpus '{csv_path.name}': "
                    f"{file_missing:,} missing-identifier row(s) collected."
                )

        except Exception as exc:
            print(
                f"  WARNING: Could not read '{csv_path.name}': {exc}",
                file=sys.stderr,
            )

    return rows, ordered_columns


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def write_output(rows: list, columns: list, output_path: str) -> None:
    """
    Write collected rows to a CSV file.  Every known column is included as
    a header; rows that lack a given column receive an empty string for that
    field, preserving data integrity across files with differing schemas.
    """
    out = Path(output_path)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=columns,
            extrasaction="ignore",   # silently drop unexpected keys
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        for row in rows:
            # Fill missing columns with empty string
            writer.writerow({col: row.get(col, "") for col in columns})

    print(f"\n  Output written: '{out}' ({len(rows):,} row(s), {len(columns)} column(s))")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="ia-missing-item-checker.py",
        description=(
            "Find identifiers present in a Corpus but MISSING from a Source "
            "list, and write all matching Corpus rows to an output CSV."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python ia-missing-item-checker.py source.csv corpus.csv\n"
            "  python ia-missing-item-checker.py source.txt /path/to/corpus/\n"
            "  python ia-missing-item-checker.py source.csv part01.csv part02.csv -o missing.csv\n"
        ),
    )
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help=(
            "CSV file with an 'identifier' column, or a plain-text .txt "
            "file with one identifier per line."
        ),
    )
    parser.add_argument(
        "corpus",
        metavar="CORPUS",
        nargs="+",
        help=(
            "One or more CSV files or directories of CSV files to search. "
            "Files without an 'identifier' column are skipped."
        ),
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        default="ia-missing-item-checker_output.csv",
        help=(
            "Path for the output CSV file. "
            "Default: ia-missing-item-checker_output.csv"
        ),
    )

    args = parser.parse_args()

    print("\n=== ia-missing-item-checker.py ===\n")

    # 1. Load source identifiers
    print("Loading Source...")
    source_ids = load_source(args.source)

    # 2. Collect corpus files
    print("\nCollecting Corpus files...")
    corpus_files = collect_corpus_files(args.corpus)
    if not corpus_files:
        sys.exit("ERROR: No valid Corpus CSV files were found.")
    print(f"  {len(corpus_files)} CSV file(s) to process.")

    # 3. Process corpus
    print("\nProcessing Corpus...")
    rows, columns = process_corpus(corpus_files, source_ids)

    if not rows:
        print("\n  No missing identifiers found. Output file will not be created.")
        return

    if not columns:
        sys.exit("ERROR: No column headers could be determined from the Corpus.")

    # 4. Write output
    print("\nWriting output...")
    write_output(rows, columns, args.output)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
