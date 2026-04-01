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
text-collapser.py

Remove all empty lines from a text file and write the result to a new file.
The output file is written to the current working directory with "_collapsed"
appended to the original filename stem.

USAGE:
    python text-collapser.py <input_file>

Output:
    <stem>_collapsed.txt  (written to the current working directory)

Example:
    python text-collapser.py notes.txt  ->  notes_collapsed.txt
"""

import argparse
import os


def collapse_text_file(input_file, output_file):
    """Read input_file, drop all blank lines, and write result to output_file."""
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    non_empty_lines = [line for line in lines if line.strip()]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(non_empty_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove all empty lines from a text file."
    )
    parser.add_argument("input_file", help="Path to the input text file")
    args = parser.parse_args()

    stem = os.path.splitext(os.path.basename(args.input_file))[0]
    output_file = f"{stem}_collapsed.txt"

    collapse_text_file(args.input_file, output_file)
    print(f"Collapsed text saved to {output_file}")

