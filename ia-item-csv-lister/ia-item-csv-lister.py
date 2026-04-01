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

"""
ia-item-lister.py

Read a list of Internet Archive identifiers and export their file listings
to a CSV file, one row per item, one column per file extension.

-------------------------------------------------------------------------------
DESCRIPTION
-------------------------------------------------------------------------------
Reads a plain-text file of Internet Archive identifiers (one per line),
fetches the file list for each item, and writes a CSV where each column
corresponds to a file extension. If an item has multiple files with the same
extension, only the first is recorded. Standard IA-generated files are
excluded automatically (see IGNORED FILES below).

-------------------------------------------------------------------------------
IGNORED FILES
-------------------------------------------------------------------------------
The following standard IA files are excluded from every item:
    __ia_thumb.jpg
    {identifier}_archive.torrent
    {identifier}_meta.xml
    {identifier}_files.xml
    {identifier}_meta.sqlite

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
    python ia-item-lister.py <input_file> <output_file>

Arguments:
    input_file   Plain-text file with one IA identifier per line
    output_file  Path to the output CSV file

-------------------------------------------------------------------------------
REQUIREMENTS
-------------------------------------------------------------------------------
- Python 3.x
- internetarchive Python package (pip install internetarchive)

-------------------------------------------------------------------------------
"""

import sys
import csv
import argparse
import os
import internetarchive

# Files whose names are fixed across all IA items (exact match).
IGNORED_EXACT = {"__ia_thumb.jpg"}

# Filename suffixes that are always prefixed with the item identifier.
IGNORED_SUFFIXES = [
    "_archive.torrent",
    "_meta.xml",
    "_files.xml",
    "_meta.sqlite",
]


def is_ignored(filename, identifier):
    """Return True if filename is a standard IA-generated file to be skipped."""
    if filename in IGNORED_EXACT:
        return True
    for suffix in IGNORED_SUFFIXES:
        if filename == f"{identifier}{suffix}":
            return True
    return False


def parse_args():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="List files for Internet Archive items and export to CSV."
    )
    parser.add_argument("input_file", help="Text file with one IA identifier per line")
    parser.add_argument("output_file", help="Path to the output CSV file")
    return parser.parse_args()


def main(input_file, output_file):
    with open(input_file, "r") as f:
        identifiers = [line.strip() for line in f if line.strip()]

    ext_set = set()
    item_files = {}

    for identifier in identifiers:
        print(f"Processing: {identifier}")
        try:
            item = internetarchive.get_item(identifier)
            ext_to_file = {}
            for f in item.files:
                fname = f["name"]
                if is_ignored(fname, identifier):
                    continue
                ext = os.path.splitext(fname)[1].lower().lstrip(".")
                if ext and ext not in ext_to_file:
                    ext_to_file[ext] = fname
                    ext_set.add(ext)
            item_files[identifier] = ext_to_file
        except Exception as e:
            print(f"Error processing {identifier}: {e}")
            item_files[identifier] = {}

    columns = ["identifier"] + sorted(ext_set)
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for identifier in identifiers:
            row = {"identifier": identifier}
            for ext in ext_set:
                row[ext] = item_files.get(identifier, {}).get(ext, "")
            writer.writerow(row)

    print(f"Done. Output written to: {output_file}")


if __name__ == "__main__":
    args = parse_args()
    main(args.input_file, args.output_file)