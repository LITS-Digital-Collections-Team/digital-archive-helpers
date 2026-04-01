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
createItemManifests.py

Generate a IIIF Presentation API 2.x Collection manifest from a CSV of
Internet Archive identifiers and item labels.

-------------------------------------------------------------------------------
DESCRIPTION
-------------------------------------------------------------------------------
Reads a CSV file with 'identifier' and 'label' columns and produces a IIIF
Collection JSON file referencing the standard Internet Archive IIIF item
manifest URL for each identifier. The output file is written to the same
directory as the input CSV, with the same base name and '_iiif.json' appended.

The collection's @id is set to a GitHub raw content URL pointing to the output
filename. Edit the GITHUB_MANIFEST_BASE constant to match your own repository.

-------------------------------------------------------------------------------
INPUT CSV FORMAT
-------------------------------------------------------------------------------
Required columns (header row mandatory):
    identifier   Internet Archive item identifier
    label        Human-readable label for the item

-------------------------------------------------------------------------------
OUTPUT
-------------------------------------------------------------------------------
<input_basename>_iiif.json  — IIIF Collection manifest

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
    python createItemManifests.py <input.csv> <collection_label>

Arguments:
    input.csv          CSV file with 'identifier' and 'label' columns
    collection_label   Human-readable name for the collection

Example:
    python createItemManifests.py hemingway.csv "Hemingway Family Archive"

-------------------------------------------------------------------------------
REQUIREMENTS
-------------------------------------------------------------------------------
- Python 3.x (no third-party packages required)

-------------------------------------------------------------------------------
"""

import json
import argparse
import os
from csv import DictReader

# Base URL where completed manifests are published (GitHub raw content).
# Edit this to match your repository.
GITHUB_MANIFEST_BASE = (
    "https://raw.githubusercontent.com/pwallace/iiif-manifests-for-transcription/main/"
)


def parse_args():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a IIIF Collection manifest from an Internet Archive identifier CSV."
    )
    parser.add_argument(
        "infile",
        help="CSV file with 'identifier' and 'label' columns",
    )
    parser.add_argument(
        "collection_label",
        help="Human-readable name for the collection",
    )
    return parser.parse_args()


def build_manifest(infilename, collection_label):
    """
    Read infilename (CSV with 'identifier' and 'label' columns) and return
    a IIIF Collection manifest dict.
    """
    outfilename = os.path.splitext(infilename)[0] + "_iiif.json"

    item_manifests = []
    with open(infilename, "r") as f:
        for row in DictReader(f):
            item_manifests.append({
                "@id": f"http://iiif.archivelab.org/iiif/{row['identifier']}/manifest.json",
                "@type": "sc:Manifest",
                "label": row["label"],
            })

    manifest = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@type": "sc:Collection",
        "@id": GITHUB_MANIFEST_BASE + os.path.basename(outfilename),
        "label": f"IIIF Collection for the {collection_label} collection at Internet Archive",
        "manifests": item_manifests,
    }
    return manifest, outfilename


def main():
    args = parse_args()
    manifest, outfilename = build_manifest(args.infile, args.collection_label)
    with open(outfilename, "w") as f:
        json.dump(manifest, f, indent=4)
    print(f"Done. Manifest written to: {outfilename}")


if __name__ == "__main__":
    main()
