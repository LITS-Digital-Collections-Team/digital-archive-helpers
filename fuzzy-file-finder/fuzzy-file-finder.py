# Copyright (C) 2026 Patrick R. Wallace <mail.prw@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""fuzzy-file-finder.py

Locate files or directories from a target list within a recursive directory
listing (e.g., output of ``ls -R``, ``rclone ls``, or a Windows dir tree).

Inputs
------
directory_listing : plaintext file
    One path per line.  Lines matching ``<size> <path>`` (rclone/ls -l format)
    have the size prefix stripped.  Lines ending with ``:`` are treated as
    directory headers.  Blank lines and exact duplicates are ignored.
filename_list : plaintext file
    One target per line.  May be a bare filename, a partial path, or a full
    path.  Blank lines and exact duplicates are ignored.  Input order is
    preserved in the output.

Matching strategy (per target)
-------------------------------
For **directory** targets (basename has no file extension):
    1. Case-sensitive substring match  -> note: ``directory``
    2. Case-insensitive substring match -> note: ``directory``
    3. Fuzzy match (fuzzywuzzy)         -> note: ``directory;fuzzy``
    No match                            -> note: ``directory;not found``

For **file** targets:
    1. If basename + immediate parent dir both match a listing entry, the
       match is recorded with note ``name-only`` (search continues).
    2. Case-sensitive substring match  -> note: blank (or ``duplicate``)
    3. Case-insensitive substring match -> note: blank (or ``duplicate``)
    4. Fuzzy match (score >= 60)        -> note: ``fuzzy`` (or ``fuzzy;duplicate``)
    No match                            -> note: ``not found``

When a strategy yields more than one match, ``duplicate`` is appended to the
notes for every row produced by that strategy.

Output CSV columns
------------------
``file location`` : full path from listing (or ``not found``)
``target``        : original target string
``notes``         : match status flags, semicolon-separated

Usage
-----
    python fuzzy-file-finder.py <directory_listing.txt> <filename_list.txt> <output.csv>
"""

import argparse
import csv
import os
import re
from fuzzywuzzy import process
from tqdm import tqdm

def clean_listing(listing_lines):
    """
    Cleans the directory listing by removing empty lines, duplicates, and extraneous info.
    Returns a set of cleaned file paths and a set of cleaned directory names.
    """
    cleaned_files = set()
    cleaned_dirs = set()
    print("Cleaning directory listing...")
    for line in tqdm(listing_lines, desc="Processing listing lines", unit="lines"):
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Directory header (e.g., "dir/subdir:") is a directory
        if line.endswith(':'):
            dir_path = line[:-1]
            cleaned_dirs.add(dir_path)
            continue
        # Remove lines that look like file size/date info (common in rclone/ls output)
        if re.match(r'^\d+\s', line):  # e.g., "12345 filename.txt"
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                line = parts[1]
            else:
                continue
        cleaned_files.add(line)
    print(f"Found {len(cleaned_files)} files and {len(cleaned_dirs)} directories after cleaning.")
    return cleaned_files, cleaned_dirs

def clean_filenames(filename_lines):
    """
    Cleans the filename list by removing empty lines, duplicates, and whitespace.
    Returns a list of unique targets (filenames or directory names) in input order.
    """
    print("Cleaning target list...")
    seen = set()
    cleaned = []
    for line in tqdm(filename_lines, desc="Processing target lines", unit="lines"):
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            cleaned.append(line)
    print(f"Found {len(cleaned)} unique targets after cleaning.")
    return cleaned

def is_directory_name(name):
    """
    Returns True if the name looks like a directory (no file extension).
    """
    # If it ends with a slash, treat as directory
    if name.endswith('/'):
        return True
    # If it has no dot after last slash, treat as directory
    base = os.path.basename(name.rstrip('/'))
    return '.' not in base

def find_matches(cleaned_files, cleaned_dirs, cleaned_targets):
    """
    For each target, find the best match in the cleaned listing.

    Matching is attempted in order (strategies described in module docstring).
    Returns a list of (file_location, target, notes) tuples.
    """
    print("Searching for matches...")
    results = []
    cleaned_files_list = list(cleaned_files)
    cleaned_dirs_list = list(cleaned_dirs)
    # Build lowercase-keyed dicts for fast case-insensitive lookup
    files_lower = {f.lower(): f for f in cleaned_files}
    dirs_lower = {d.lower(): d for d in cleaned_dirs}

    for target in tqdm(cleaned_targets, desc="Matching targets", unit="targets"):
        notes = []

        if is_directory_name(target):
            # --- Directory matching ---
            matches_cs = [d for d in cleaned_dirs if target in d]
            if matches_cs:
                note = "directory;duplicate" if len(matches_cs) > 1 else "directory"
                for match in matches_cs:
                    results.append((match, target, note))
                continue
            target_lower = target.lower()
            matches_ci = [dirs_lower[d] for d in dirs_lower if target_lower in d]
            if matches_ci:
                note = "directory;duplicate" if len(matches_ci) > 1 else "directory"
                for match in matches_ci:
                    results.append((match, target, note))
                continue
            result = process.extractOne(target, cleaned_dirs_list)
            if result is not None:
                fuzzy_match, score = result
                tqdm.write(f"  fuzzy dir match ({score}): {target!r} -> {fuzzy_match!r}")
                results.append((fuzzy_match, target, "directory;fuzzy"))
            else:
                results.append(("not found", target, "directory;not found"))
        else:
            # --- File matching ---
            # Strategy 1: name-only — basename + immediate parent dir both match
            target_basename = os.path.basename(target)
            target_parent = os.path.basename(os.path.dirname(target))
            if target_parent:
                name_only_matches = [
                    f for f in cleaned_files
                    if os.path.basename(f) == target_basename
                    and os.path.basename(os.path.dirname(f)) == target_parent
                ]
                for match in name_only_matches:
                    results.append((match, target, "name-only"))

            # Strategy 2: case-sensitive substring match
            matches_cs = [f for f in cleaned_files if target in f]
            if matches_cs:
                note = "duplicate" if len(matches_cs) > 1 else ""
                for match in matches_cs:
                    results.append((match, target, note))
                continue

            # Strategy 3: case-insensitive substring match
            target_lower = target.lower()
            matches_ci = [files_lower[f] for f in files_lower if target_lower in f]
            if matches_ci:
                note = "duplicate" if len(matches_ci) > 1 else ""
                for match in matches_ci:
                    results.append((match, target, note))
                continue

            # Strategy 4: fuzzy match (threshold: score >= 60)
            fuzzy_matches = [(m, s) for m, s in process.extract(target, cleaned_files_list, limit=2) if s >= 60]
            if fuzzy_matches:
                note = "fuzzy;duplicate" if len(fuzzy_matches) > 1 else "fuzzy"
                for fuzzy_match, score in fuzzy_matches:
                    tqdm.write(f"  fuzzy file match ({score}): {target!r} -> {fuzzy_match!r}")
                    results.append((fuzzy_match, target, note))
            else:
                results.append(("not found", target, "not found"))

    print(f"Matching complete. {len(results)} result row(s) for {len(cleaned_targets)} target(s).")
    return results

def main():
    parser = argparse.ArgumentParser(description="Fuzzy file finder utility.")
    parser.add_argument("directory_listing", help="Path to recursive directory listing text file")
    parser.add_argument("filename_list", help="Path to plaintext file containing filenames or directory names to search for")
    parser.add_argument("output_csv", help="Path to output CSV file")
    args = parser.parse_args()

    print("Reading input files...")
    with open(args.directory_listing, 'r', encoding='utf-8') as f:
        listing_lines = f.readlines()
    with open(args.filename_list, 'r', encoding='utf-8') as f:
        filename_lines = f.readlines()

    cleaned_files, cleaned_dirs = clean_listing(listing_lines)
    cleaned_targets = clean_filenames(filename_lines)

    results = find_matches(cleaned_files, cleaned_dirs, cleaned_targets)

    print("Writing results to CSV...")
    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file location", "target", "notes"])
        writer.writerows(results)
    print(f"Results written to {args.output_csv}")

if __name__ == "__main__":
    main()
