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
ia-metadata-to-csv.py

Search Internet Archive and export item metadata to a CSV file.

-------------------------------------------------------------------------------
DESCRIPTION
-------------------------------------------------------------------------------
Runs an Internet Archive search query and writes the metadata of all matching
items to a CSV file. The 'identifier' column is always included. Additional
metadata fields can be specified as positional arguments; if omitted, the
script defaults to: title, creator, date, description.

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
    python ia-metadata-to-csv.py <query> <output.csv> [field ...]

Arguments:
    query       Internet Archive search query (Lucene syntax)
    output      Path to the output CSV file
    field ...   One or more metadata field names to include (optional)

Defaults (when no fields are specified): title creator date description

-------------------------------------------------------------------------------
EXAMPLES
-------------------------------------------------------------------------------
# Export default fields for items in a collection:
    python ia-metadata-to-csv.py "collection:opensea AND mediatype:texts" output.csv

# Export specific fields:
    python ia-metadata-to-csv.py "identifier:my_item" output.csv title creator notes

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
import internetarchive


def parse_args():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Search Internet Archive and export item metadata to CSV."
    )
    parser.add_argument("query", help="Internet Archive search query (Lucene syntax)")
    parser.add_argument("output", help="Path to the output CSV file")
    parser.add_argument(
        "fields",
        nargs="*",
        default=["title", "creator", "date", "description"],
        help="Metadata fields to include (default: title creator date description)",
    )
    return parser.parse_args()


def convert_to_csv(search_query, output_file, fieldnames):
    """
    Search Internet Archive for items matching search_query and write metadata
    for each result to output_file as CSV. The 'identifier' column is always
    written first, followed by the requested fieldnames.
    """
    results = internetarchive.search_items(search_query)
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["identifier"] + fieldnames)
        writer.writeheader()
        for result in results:
            item_id = result["identifier"]
            item = internetarchive.get_item(item_id)
            row = {"identifier": item_id}
            for field in fieldnames:
                row[field] = item.metadata.get(field, "")
            writer.writerow(row)


def main():
    args = parse_args()
    convert_to_csv(args.query, args.output, args.fields)
    print(f"Done. Output written to: {args.output}")


if __name__ == "__main__":
    main()

