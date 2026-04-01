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

This python script takes a list of file paths in DOS format (with backslashes) and converts them to Linux format (with forward slashes).
If a path does not end in a file extension, it is assumed to be a directory and a "/" is appended if not present.

Usage:
    python convert-dos-to-linux-paths.py <input_file> <output_file>

Arguments:
    input_file   - Path to the text file containing DOS-style file paths.
    output_file  - Path to the output file where Linux-style file paths will be saved.

Example:
    python convert-dos-to-linux-paths.py dos-paths.txt linux-paths.txt
"""

import argparse
import os


def has_extension(path):
    # Returns True if path ends with a file extension (e.g., .txt, .jpg)
    return bool(os.path.splitext(path)[1])

def convert_paths(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            linux_path = line.replace('\\', '/').strip()
            if not linux_path:
                continue
            if not has_extension(linux_path):
                if not linux_path.endswith('/'):
                    linux_path += '/'
            outfile.write(linux_path + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert DOS-style (backslash) file paths to Linux-style (forward slash)."
    )
    parser.add_argument("input_file", help="Text file containing DOS-style file paths")
    parser.add_argument("output_file", help="Output file for Linux-style file paths")
    args = parser.parse_args()
    convert_paths(args.input_file, args.output_file)

