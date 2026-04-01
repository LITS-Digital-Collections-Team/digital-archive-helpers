#!/usr/bin/env python3
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
TIFF Metadata Extractor
Extracts metadata from TIFF image files in a directory and saves to CSV.
"""

import os
import csv
import argparse
from datetime import datetime
from PIL import Image
from PIL.TiffImagePlugin import IFDRational


def get_tiff_metadata(filepath):
    """
    Extract metadata from a TIFF file.
    
    Args:
        filepath: Path to the TIFF file
        
    Returns:
        Dictionary containing metadata
    """
    metadata = {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'file_size_bytes': os.path.getsize(filepath),
        'file_modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
    }
    
    try:
        with Image.open(filepath) as img:
            # Basic image properties
            metadata['format'] = img.format
            metadata['mode'] = img.mode
            metadata['width'] = img.width
            metadata['height'] = img.height
            
            # DPI/Resolution
            if hasattr(img, 'info') and 'dpi' in img.info:
                dpi = img.info['dpi']
                metadata['dpi_x'] = dpi[0] if isinstance(dpi, tuple) else dpi
                metadata['dpi_y'] = dpi[1] if isinstance(dpi, tuple) else dpi
            
            # EXIF and TIFF tags
            if hasattr(img, 'tag_v2'):
                # Common TIFF tags
                tag_mapping = {
                    270: 'ImageDescription',
                    271: 'Make',
                    272: 'Model',
                    282: 'XResolution',
                    283: 'YResolution',
                    296: 'ResolutionUnit',
                    305: 'Software',
                    306: 'DateTime',
                    315: 'Artist',
                    33432: 'Copyright',
                }
                
                for tag_id, tag_name in tag_mapping.items():
                    if tag_id in img.tag_v2:
                        value = img.tag_v2[tag_id]
                        # Convert IFDRational to float
                        if isinstance(value, IFDRational):
                            value = float(value)
                        metadata[tag_name] = value
            
            # Additional info
            if hasattr(img, 'info'):
                for key, value in img.info.items():
                    if key not in metadata and isinstance(value, (str, int, float)):
                        metadata[key] = value
                        
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata


def find_tiff_files(directory):
    """
    Recursively find all TIFF files in a directory.
    
    Args:
        directory: Path to search
        
    Returns:
        List of TIFF file paths
    """
    tiff_extensions = ('.tif', '.tiff')
    tiff_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(tiff_extensions):
                tiff_files.append(os.path.join(root, file))
    
    return sorted(tiff_files)


def extract_metadata_to_csv(target_directory, output_csv=None):
    """
    Extract metadata from all TIFF files in a directory and save to CSV.
    
    Args:
        target_directory: Directory to scan for TIFF files
        output_csv: Output CSV filename (default: tiff-metadata.csv)
    """
    if not os.path.isdir(target_directory):
        print(f"Error: Directory '{target_directory}' does not exist.")
        raise SystemExit(1)
    
    if output_csv is None:
        output_csv = 'tiff-metadata.csv'
    
    print(f"Scanning directory: {target_directory}")
    tiff_files = find_tiff_files(target_directory)
    
    if not tiff_files:
        print("No TIFF files found.")
        return
    
    print(f"Found {len(tiff_files)} TIFF file(s)")
    print("Extracting metadata...")
    
    # Extract metadata from all files
    all_metadata = []
    for i, filepath in enumerate(tiff_files, 1):
        print(f"Processing {i}/{len(tiff_files)}: {os.path.basename(filepath)}")
        metadata = get_tiff_metadata(filepath)
        all_metadata.append(metadata)
    
    # Get all unique keys for CSV headers
    all_keys = set()
    for metadata in all_metadata:
        all_keys.update(metadata.keys())
    
    # Build ordered fieldnames: identity columns first, then remaining keys alphabetically
    identity_cols = ['filename', 'filepath', 'file_size_bytes', 'file_modified']
    remaining = sorted(k for k in all_keys if k not in identity_cols)
    fieldnames = identity_cols + remaining
    
    # Write to CSV
    print(f"\nWriting metadata to: {output_csv}")
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_metadata)
    
    print(f"Done! Metadata for {len(all_metadata)} files written to {output_csv}")


def main():
    """Parse command-line arguments and run the extractor."""
    parser = argparse.ArgumentParser(
        description="Extract metadata from TIFF files in a directory and save to CSV."
    )
    parser.add_argument("target_directory", help="Directory to scan for TIFF files")
    parser.add_argument(
        "output_csv",
        nargs="?",
        default=None,
        help="Output CSV filename (default: tiff-metadata.csv)",
    )
    args = parser.parse_args()
    extract_metadata_to_csv(args.target_directory, args.output_csv)


if __name__ == '__main__':
    main()
