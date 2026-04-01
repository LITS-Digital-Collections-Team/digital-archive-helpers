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
Vault checksum text-to-CSV converter

Converts a text file (as exported from Archive-It Vault) containing
checksum and path data into a CSV format suitable for downstream
comparison and reporting tools.

Input format:
    CHECKSUM<space>path/filename

Output format:
    CSV with columns: checksum, path, filename

USAGE:
        python vault-checksum-csv-converter.py <input_file> [output_file]

EXAMPLES:
        python vault-checksum-csv-converter.py a11aum.txt
        python vault-checksum-csv-converter.py a11aum.txt checksums.csv
        python vault-checksum-csv-converter.py /path/to/input.txt /path/to/output.csv

Notes:
    - The input files this script is intended to handle are text exports
        downloaded from Archive-It Vault that contain a checksum followed
        by a space and the stored path/filename.
    - The resulting CSV is encoded in UTF-8 and includes a header row.
"""

import csv
import os
import sys
import argparse
from pathlib import Path


def parse_checksum_line(line: str) -> tuple:
    """
    Parse a line containing checksum and path information.
    
    Args:
        line: Input line in format "CHECKSUM path/filename"
        
    Returns:
        Tuple of (checksum, full_path, filename) or None if line is invalid
    """
    line = line.strip()
    if not line:
        return None
    
    # Split on first space - checksum is first part, path is everything after
    parts = line.split(' ', 1)
    if len(parts) != 2:
        return None
    
    checksum, full_path = parts
    
    # Extract filename from path
    filename = os.path.basename(full_path)
    
    return checksum, full_path, filename


def convert_text_to_csv(input_file: str, output_file: str) -> None:
    """
    Convert text file with checksum data to CSV format.
    
    Args:
        input_file: Path to input text file
        output_file: Path to output CSV file
    """
    processed_lines = 0
    skipped_lines = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            # Create CSV writer
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['checksum', 'path', 'filename'])
            
            # Process each line
            for line_num, line in enumerate(infile, 1):
                parsed = parse_checksum_line(line)
                
                if parsed is None:
                    if line.strip():  # Only report non-empty lines as skipped
                        print(f"Warning: Skipping invalid line {line_num}: {line.strip()}")
                        skipped_lines += 1
                    continue
                
                checksum, full_path, filename = parsed
                writer.writerow([checksum, full_path, filename])
                processed_lines += 1
                
                # Progress feedback for large files
                if processed_lines % 1000 == 0:
                    print(f"Processed {processed_lines} lines...")
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    except IOError as e:
        print(f"Error processing files: {e}")
        sys.exit(1)
    
    print(f"\nConversion complete!")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Lines processed: {processed_lines}")
    print(f"Lines skipped: {skipped_lines}")


def convert_stream_to_csv(infile, outfile_stream):
    """
    Convert a file-like input stream of checksum lines into CSV written
    to the provided file-like output stream.
    """
    processed_lines = 0
    skipped_lines = 0

    writer = csv.writer(outfile_stream)
    writer.writerow(['checksum', 'path', 'filename'])

    for line_num, line in enumerate(infile, 1):
        parsed = parse_checksum_line(line)
        if parsed is None:
            if line.strip():
                print(f"Warning: Skipping invalid line {line_num}: {line.strip()}")
                skipped_lines += 1
            continue

        checksum, full_path, filename = parsed
        writer.writerow([checksum, full_path, filename])
        processed_lines += 1

        if processed_lines % 1000 == 0:
            print(f"Processed {processed_lines} lines...")

    print(f"\nConversion complete!")
    print(f"Input: stream")
    print(f"Output: stream")
    print(f"Lines processed: {processed_lines}")
    print(f"Lines skipped: {skipped_lines}")


def main():
    """Main function to parse arguments and execute the conversion."""
    parser = argparse.ArgumentParser(
        description='Convert checksum text file to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input format: CHECKSUM<space>path/filename
Output format: CSV with columns: checksum, path, filename

Examples:
  python vault-checksum-csv-converter.py input.txt
  python vault-checksum-csv-converter.py input.txt output.csv
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input text file containing checksum data (omit when using --stdin)'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Output CSV file (default: input_file with .csv extension)'
    )

    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read input lines from stdin instead of a file'
    )
    
    args = parser.parse_args()
    
    # Handle stdin mode
    if args.stdin:
        if args.input_file:
            print("Warning: input_file positional argument will be ignored when --stdin is used")

        # Determine output destination: stdout when not provided or when '-' specified
        if args.output_file is None or args.output_file == '-':
            out_stream = sys.stdout
        else:
            out_stream = open(args.output_file, 'w', newline='', encoding='utf-8')

        print("Converting from stdin to CSV...")
        convert_stream_to_csv(sys.stdin, out_stream)

        if out_stream is not sys.stdout:
            out_stream.close()
    else:
        # Validate input file exists
        if not args.input_file or not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' does not exist")
            sys.exit(1)

        # Generate output filename if not provided
        if args.output_file is None:
            input_path = Path(args.input_file)
            args.output_file = str(input_path.with_suffix('.csv'))

        print(f"Converting '{args.input_file}' to CSV format...")
        print(f"Output will be saved as: '{args.output_file}'")
        print("-" * 50)

        # Perform conversion
        convert_text_to_csv(args.input_file, args.output_file)


if __name__ == "__main__":
    main()