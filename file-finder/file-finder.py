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

"""file-finder.py

Recursively scan a directory tree for filenames or directory names from a list.

Reads a plaintext file containing one path per line, extracts the lowest-level
element (filename or directory name) from each, and searches the root directory
tree for matches. Results are written to two CSV files:

  - files-output.csv  — one row per input entry treated as a file
  - dir-output.csv    — one row per file found inside a matched directory

A path entry is treated as a file if its basename contains a file extension
(e.g. ".pdf", ".mp4"); otherwise it is treated as a directory.

Usage:
    python file-finder.py <root_directory> <file_list.txt>
"""

import argparse
import csv
import os
from typing import List, Optional

from tqdm import tqdm

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively scan a directory tree for filenames or directories from a list."
    )
    parser.add_argument("root_dir", help="Root directory to start the search")
    parser.add_argument("file_list", help="Plaintext file containing one path per line")
    return parser.parse_args()


def read_file_list(file_list_path: str) -> List[str]:
    """Read file_list_path and return non-empty, stripped lines."""
    with open(file_list_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def extract_lowest_level_elements(file_paths: List[str]) -> List[str]:
    """Return the basename (filename or directory name) from each path."""
    return [os.path.basename(path) for path in file_paths]

def search_name(root_dir: str, name: str) -> Optional[List[str]]:
    """Search root_dir recursively for a file or directory named `name`.

    - If a directory named `name` is found, returns the full paths of all files
      it contains (recursively). If the directory is empty, returns its path.
    - If a file named `name` is found, returns its full path(s).
    - Returns None if nothing is found.

    Directory matches take priority over file matches with the same name.
    """
    found_files = []
    found_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if name in filenames:
            found_files.append(os.path.join(dirpath, name))
        if name in dirnames:
            found_dirs.append(os.path.join(dirpath, name))
    if found_dirs:
        # Expand each matched directory to the files it contains
        all_files = []
        for dir_full_path in found_dirs:
            for subdirpath, _, sub_filenames in os.walk(dir_full_path):
                for sub_filename in sub_filenames:
                    all_files.append(os.path.join(subdirpath, sub_filename))
        return all_files if all_files else found_dirs
    return found_files if found_files else None

def main() -> None:
    args = parse_arguments()
    root_dir = args.root_dir
    file_list_path = args.file_list

    file_paths = read_file_list(file_list_path)
    last_elements = extract_lowest_level_elements(file_paths)

    files_rows: List[List[str]] = []
    dirs_rows: List[List[str]] = []

    for orig_path, last_elem in tqdm(
        zip(file_paths, last_elements), total=len(file_paths), desc="Searching"
    ):
        matched = search_name(root_dir, last_elem)
        # Treat as a file if the basename has a file extension; otherwise a directory
        if os.path.splitext(last_elem)[1]:
            files_rows.append([orig_path, last_elem, ";".join(matched) if matched else ""])
        else:
            if matched:
                for found_file in matched:
                    dirs_rows.append([orig_path, last_elem, found_file])
            else:
                dirs_rows.append([orig_path, last_elem, ""])

    with open("files-output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Original Path", "Last Element", "Matched Path(s)"])
        writer.writerows(files_rows)

    with open("dir-output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Original Path", "Last Element", "Matched File"])
        writer.writerows(dirs_rows)

    print(f"Done. {len(files_rows)} file row(s), {len(dirs_rows)} directory row(s) written.")

if __name__ == "__main__":
    main()