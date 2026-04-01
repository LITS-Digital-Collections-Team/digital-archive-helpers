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
list-cleaner.py

This Python script processes a text file containing a recursive directory listing, such as one produced by rclone or similar tools.
Each line in the input file is expected to start with a file size (or other numeric value), followed by a space, and then the file or directory path.
The script removes the leading numeric value and space from each line, leaving only the file or directory path.
It then sorts the paths so that directories (paths ending with a "/") are listed first in alphabetical order, followed by files in alphabetical order.
The cleaned and sorted list is written to the specified output file, one path per line.

Usage:
    python list-cleaner.py [--directories-only | -d | --files-only | -f] <input_file> <output_file>

Arguments:
    --directories-only, -d   - Only include directory paths (omit files with extensions)
    --files-only, -f         - Only include file paths (omit directories)
    input_file               - Path to the text file containing the raw directory listing.
    output_file              - Path to the output file where the cleaned and sorted paths will be saved.

Example:
    python list-cleaner.py --directories-only rclone-list.txt cleaned-list.txt
    python list-cleaner.py --files-only rclone-list.txt cleaned-list.txt

Notes:
    - Lines that do not contain a space after the leading number are skipped.
    - Directories are identified by paths ending with a '/'.
    - The script does not check if the paths actually exist on disk; it processes the text as-is.
    - Paths ending in ".DS_Store/", ".DS_Store", or "Thumbs.db" are automatically omitted.
    - Only one of --directories-only/-d or --files-only/-f may be specified.
"""

import argparse
import os
import re

def should_omit(path):
    omit_names = ['.DS_Store', 'Thumbs.db']
    for name in omit_names:
        if path.endswith(name) or path.endswith(name + '/'):
            return True
    return False

def has_extension(path):
    # Returns True if path ends with a file extension (e.g., .txt, .jpg)
    return bool(os.path.splitext(path.rstrip('/'))[1])

def clean_listing(input_file, output_file, mode=None):
    paths = []
    with open(input_file, 'r') as f:
        for line in f:
            # Remove leading number and space using regex
            cleaned = re.sub(r'^\s*\d+\s+', '', line).strip()
            if not cleaned:
                continue
            if should_omit(cleaned):
                continue
            # Apply mode filtering
            if mode == 'directories':
                if not cleaned.endswith('/') and has_extension(cleaned):
                    continue
            elif mode == 'files':
                if cleaned.endswith('/') or not has_extension(cleaned):
                    continue
            paths.append(cleaned)

    # Sort: directories first, then files (both alphabetically); within a mode, just sort
    if mode in ('directories', 'files'):
        sorted_paths = sorted(paths)
    else:
        dirs = sorted([p for p in paths if p.endswith('/')])
        files = sorted([p for p in paths if not p.endswith('/')])
        sorted_paths = dirs + files

    with open(output_file, 'w') as f:
        for path in sorted_paths:
            f.write(path + '\n')

def parse_args():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean and sort a recursive directory listing (e.g., from rclone)."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--directories-only", "-d",
        action="store_true",
        help="Only include directory paths",
    )
    group.add_argument(
        "--files-only", "-f",
        action="store_true",
        help="Only include file paths",
    )
    parser.add_argument("input_file", help="Input file containing the raw directory listing")
    parser.add_argument("output_file", help="Output file for the cleaned and sorted paths")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.directories_only:
        mode = 'directories'
    elif args.files_only:
        mode = 'files'
    else:
        mode = None
    clean_listing(args.input_file, args.output_file, mode)