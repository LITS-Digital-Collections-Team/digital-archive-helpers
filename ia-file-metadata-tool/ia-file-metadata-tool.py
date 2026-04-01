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
ia-file-metadata-tool.py

-------------------------------------------------------------------------------
DESCRIPTION
-------------------------------------------------------------------------------
This script allows you to list, set metadata, download, and export files.xml for specific files in Internet Archive (IA) items.
It supports filtering files by filename pattern (regex) or by file format (as defined in the item's files.xml).
Only files with 'source="original"' are included in listing or modification.

You can operate on a single IA item (by identifier) or on a list of items (using --filelist/-f).
When matching by format, the script interactively presents all valid format values found in the item(s)
and prompts you to select one.

-------------------------------------------------------------------------------
USAGE EXAMPLES
-------------------------------------------------------------------------------
# List metadata for files matching a filename pattern in a single item:
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --list

# Set multiple metadata fields for files matching a pattern in a single item:
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --modify "title:Original" --modify "creator:John Doe"

# Download matching files to a directory:
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --download ./download_dir

# Save files.xml for items with matching files:
python ia-file-metadata-tool.py my_item_identifier --pattern "_images.zip$" --xml ./xml_dir

-------------------------------------------------------------------------------
FLAGS
-------------------------------------------------------------------------------
identifier            IA item identifier (unless --filelist is used)
--filelist, -f        Path to file containing IA identifiers (one per line)
--pattern, -p         Regex pattern to match filenames
--format, -F          Prompt for file format to match (interactive)
--modify              Set metadata field and value for matched files (repeatable, e.g., --modify "field:value")
--list, -l            List metadata for matched files
--download, -D        Download matching files to specified directory (e.g., --download ./download_dir)
--xml, -X             Save {identifier}_files.xml to specified directory for items with matching files

-------------------------------------------------------------------------------
"""

import sys
import re
import argparse
import os
from internetarchive import get_item, modify_metadata

def parse_args():
    """
    Parse command-line arguments and return the parsed object.
    """
    parser = argparse.ArgumentParser(description="List, set metadata, download, and export files.xml for IA items.")
    parser.add_argument("identifier", nargs="?", help="Internet Archive item identifier")
    parser.add_argument("--filelist", "-f", help="Path to file containing IA identifiers (one per line)")
    parser.add_argument("--pattern", "-p", help="Filename pattern (regex) to match files")
    parser.add_argument("--format", "-F", action="store_true", help="Prompt for file format to match")
    parser.add_argument("--modify", action="append", metavar="FIELD:VALUE", help='Set metadata field and value for matched files (repeatable, e.g., --modify "field:value")')
    parser.add_argument("--list", "-l", action="store_true", help="List metadata for matched files")
    parser.add_argument("--download", "-D", metavar="DIR", help="Download matching files to specified directory")
    parser.add_argument("--xml", "-X", metavar="DIR", help="Save {identifier}_files.xml to specified directory for items with matching files")
    return parser.parse_args()

def get_identifiers(args):
    """
    Get a list of IA item identifiers from either a file (--filelist) or a single identifier argument.
    """
    if args.filelist:
        with open(args.filelist) as f:
            # Strip quotes and whitespace from each line
            return [line.strip().strip('"').strip("'") for line in f if line.strip()]
    elif args.identifier:
        return [args.identifier]
    else:
        print("Error: Must provide an identifier or --filelist.")
        sys.exit(1)

def get_valid_formats(items):
    """
    Gather all unique format values from all items.
    Returns a sorted list of formats.
    """
    formats = set()
    for item in items:
        formats.update(f.get('format') for f in item.files if f.get('format'))
    return sorted(formats)

def prompt_for_format(formats):
    """
    Present a numbered list of format options to the user and prompt for selection.
    Returns the selected format string.
    """
    print("\nAvailable formats:")
    for idx, fmt in enumerate(formats, 1):
        print(f"{idx}: {fmt}")
    while True:
        choice = input("Select format by number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(formats):
            return formats[int(choice) - 1]
        else:
            print("Invalid selection. Please enter a valid number.")

def filter_files(item, pattern=None, fmt=None):
    """
    Filter files in an IA item by source='original', filename pattern, and/or format.
    Returns a list of matching file dicts.
    """
    files = []
    for f in item.files:
        # Only include files with source="original"
        if f.get('source') != 'original':
            continue
        # If pattern is specified, match filename
        if pattern and not re.search(pattern, f['name']):
            continue
        # If format is specified, match format
        if fmt and f.get('format') != fmt:
            continue
        files.append(f)
    return files

def list_metadata(files):
    """
    Print metadata for each file in the provided list.
    """
    for f in files:
        print(f"File: {f['name']}")
        for k, v in f.items():
            print(f"  {k}: {v}")
        print("-" * 40)

def parse_modify_args(modify_args):
    """
    Parse a list of 'field:value' strings into a dictionary.
    Ensures all inputs are valid.
    """
    metadata = {}
    for arg in modify_args:
        if ':' not in arg:
            print(f"Error: --modify argument '{arg}' must be in the format 'field:value'")
            sys.exit(1)
        field, value = arg.split(':', 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            print(f"Error: Both field and value must be non-empty in --modify argument '{arg}'.")
            sys.exit(1)
        if field in metadata:
            print(f"Warning: Duplicate field '{field}' in --modify arguments. Overwriting previous value.")
        metadata[field] = value
    return metadata

def set_metadata(identifier, files, metadata_dict):
    """
    Set multiple metadata fields for each file in the list.
    Prints success or error message for each file.
    """
    for f in files:
        target_path = f"files/{f['name']}"
        r = modify_metadata(identifier, metadata=metadata_dict, target=target_path)
        if r.status_code == 200:
            print(f"Updated {list(metadata_dict.keys())} for '{f['name']}'")
        else:
            print(f"Error updating '{f['name']}': {r.status_code}")

def validate_or_prompt_dir(dir_path, purpose):
    """
    Validate that a directory exists, or prompt user to create it.
    Returns True if directory exists or was created, False otherwise.
    """
    if os.path.exists(dir_path):
        if not os.path.isdir(dir_path):
            print(f"Error: {purpose} directory '{dir_path}' exists but is not a directory.")
            return False
        return True
    else:
        response = input(f"{purpose} directory '{dir_path}' does not exist. Create it? [y/n]: ").strip().lower()
        if response == 'y':
            try:
                os.makedirs(dir_path)
                print(f"Created directory '{dir_path}'.")
                return True
            except Exception as e:
                print(f"Error creating directory '{dir_path}': {e}")
                return False
        else:
            print(f"Directory '{dir_path}' not created. Operation cancelled.")
            return False

def download_files(item, files, target_dir):
    """
    Download each matching file from the IA item to the specified directory.
    """
    for f in files:
        dest_path = os.path.join(target_dir, item.identifier)
        print(f"Downloading '{f['name']}' from item '{item.identifier}' to '{dest_path}'...")
        try:
            item.download(files=[f['name']], destdir=target_dir, verbose=True, ignore_existing=True)
        except Exception as e:
            print(f"Error downloading '{f['name']}': {e}")

def save_files_xml(item, target_dir):
    """
    Save the {identifier}_files.xml file to the specified directory.
    Creates the directory if it doesn't exist.
    """
    xml_filename = f"{item.identifier}_files.xml"
    dest_path = os.path.join(target_dir, item.identifier)
    try:
        item.download(files=[xml_filename], destdir=target_dir, verbose=True, ignore_existing=True)
        print(f"Saved {xml_filename} to {dest_path}")
    except Exception as e:
        print(f"Error saving {xml_filename}: {e}")

def main():
    """
    Main entry point: parses arguments, loads items, prompts for format if needed,
    filters files, and lists, sets metadata, downloads, or exports files.xml as requested.
    """
    args = parse_args()
    identifiers = get_identifiers(args)
    items = [get_item(identifier) for identifier in identifiers]

    selected_format = None
    if args.format:
        valid_formats = get_valid_formats(items)
        if not valid_formats:
            print("No valid formats found in the selected items.")
            sys.exit(1)
        selected_format = prompt_for_format(valid_formats)

    for item in items:
        files = filter_files(item, pattern=args.pattern, fmt=selected_format)
        if args.list:
            list_metadata(files)
        if args.modify:
            metadata_dict = parse_modify_args(args.modify)
            set_metadata(item.identifier, files, metadata_dict)
        if args.download:
            if validate_or_prompt_dir(args.download, "Download"):
                download_files(item, files, args.download)
        if args.xml and files:
            if validate_or_prompt_dir(args.xml, "XML"):
                save_files_xml(item, args.xml)
        if not (args.list or args.modify or args.download or args.xml):
            print(f"No action specified for item '{item.identifier}'.")


if __name__ == "__main__":
    main()