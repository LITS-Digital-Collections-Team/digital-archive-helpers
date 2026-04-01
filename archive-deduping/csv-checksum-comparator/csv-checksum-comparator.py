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
CSV Checksum Comparator

This script compares two CSV files containing checksum data and identifies
unmatched checksums between them. It's designed for filesystem migration
verification, comparing source and destination checksums to find differences.

INPUT FORMAT:
    Both input CSV files must have at least a 'checksum' column.
    Optional columns: 'path', 'filename' for better reporting.
    
    Expected CSV structure:
        checksum,path,filename
        abc123...,/path/to/file1.txt,file1.txt
        def456...,/path/to/file2.pdf,file2.pdf

OUTPUT:
    Creates a CSV report containing:
    - Files only in first CSV (missing from second)
    - Files only in second CSV (missing from first)
    - Summary statistics of the comparison

USAGE:
    python csv-checksum-comparator.py <file1.csv> <file2.csv> [options]

EXAMPLES:
    Basic comparison:
        python csv-checksum-comparator.py source.csv destination.csv

    Custom output file:
        python csv-checksum-comparator.py source.csv dest.csv -o differences.csv

    Specify checksum column name:
        python csv-checksum-comparator.py file1.csv file2.csv -c hash_value

    Detailed output with all columns:
        python csv-checksum-comparator.py file1.csv file2.csv --verbose

USE CASES:
    - Filesystem migration verification
    - Backup integrity checking
    - Archive comparison and validation
    - Data synchronization verification
    - Identifying missing or extra files between systems
"""

import csv
import argparse
import sys
import os
import io
from typing import Dict, Set, Tuple, List
from collections import defaultdict


def load_csv_checksums(file_path: str, checksum_column: str = 'checksum', delimiter: str = None) -> Tuple[Dict[str, Dict], Set[str]]:
    """
    Load checksums and associated data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        checksum_column: Name of the column containing checksums
        delimiter: CSV delimiter to use (None for auto-detection)
        
    Returns:
        Tuple of (checksum_to_data_dict, set_of_checksums)
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If checksum column not found
    """
    checksum_data = {}
    checksums = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Use provided delimiter or detect automatically with fallback to comma
            if delimiter:
                print(f"Using specified delimiter: '{delimiter}' for {file_path}")
            else:
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                try:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                    print(f"Detected delimiter: '{delimiter}' in {file_path}")
                except csv.Error:
                    # Fallback to comma if detection fails
                    delimiter = ','
                    print(f"Could not detect delimiter in {file_path}, defaulting to comma")
                
                # Additional validation - ensure delimiter actually exists in sample
                if delimiter not in sample and ',' in sample:
                    delimiter = ','
                    print(f"Detected delimiter not found in sample, using comma for {file_path}")
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Validate checksum column exists
            if checksum_column not in reader.fieldnames:
                raise ValueError(f"Column '{checksum_column}' not found in {file_path}. "
                               f"Available columns: {', '.join(reader.fieldnames)}")
            
            row_count = 0
            skipped_count = 0
            for row in reader:
                # Skip system files
                filename = row.get('filename', '').lower()
                path = row.get('path', '').lower()
                
                # Check if the file is .DS_Store or Thumbs.db
                if filename in ['.ds_store', 'thumbs.db'] or \
                   path.endswith('/.ds_store') or path.endswith('/thumbs.db') or \
                   path.endswith('\\.ds_store') or path.endswith('\\thumbs.db'):
                    skipped_count += 1
                    continue
                
                checksum = row[checksum_column].strip()
                if checksum:  # Skip empty checksums
                    checksums.add(checksum)
                    checksum_data[checksum] = row
                    row_count += 1
            
            print(f"Loaded {row_count} checksums from {file_path}")
            if skipped_count > 0:
                print(f"Skipped {skipped_count} system files (.DS_Store, Thumbs.db)")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file {file_path}: {e}")
    
    return checksum_data, checksums


def load_csv_checksums_stream(stream, checksum_column: str = 'checksum', delimiter: str = None, name: str = '<stdin>') -> Tuple[Dict[str, Dict], Set[str]]:
    """
    Load checksums from a file-like stream (e.g., stdin).

    Notes:
      - If `delimiter` is provided, the stream is processed without
        buffering. If no delimiter is provided, the stream will be
        buffered into memory for delimiter sniffing.
    """
    checksum_data = {}
    checksums = set()

    try:
        # If delimiter is provided we can stream directly
        if delimiter:
            reader = csv.DictReader(stream, delimiter=delimiter)
        else:
            # Buffer a portion (and the rest) since stdin may not be seekable
            full = stream.read()
            if not full:
                print(f"No data read from {name}")
                return checksum_data, checksums
            try:
                sniffer = csv.Sniffer()
                sniff_sample = full[:65536]
                detected = sniffer.sniff(sniff_sample)
                delimiter = detected.delimiter
                print(f"Detected delimiter: '{delimiter}' in {name}")
            except csv.Error:
                delimiter = ','
                print(f"Could not detect delimiter in {name}, defaulting to comma")

            stream = io.StringIO(full)
            reader = csv.DictReader(stream, delimiter=delimiter)

        # Validate checksum column
        if reader.fieldnames is None or checksum_column not in reader.fieldnames:
            available = [] if reader.fieldnames is None else reader.fieldnames
            raise ValueError(f"Column '{checksum_column}' not found in {name}. Available columns: {', '.join(available)}")

        row_count = 0
        skipped_count = 0
        for row in reader:
            filename = row.get('filename', '').lower()
            path = row.get('path', '').lower()

            if filename in ['.ds_store', 'thumbs.db'] or \
               path.endswith('/.ds_store') or path.endswith('/thumbs.db') or \
               path.endswith('\\.ds_store') or path.endswith('\\thumbs.db'):
                skipped_count += 1
                continue

            checksum = row[checksum_column].strip()
            if checksum:
                checksums.add(checksum)
                checksum_data[checksum] = row
                row_count += 1

        print(f"Loaded {row_count} checksums from {name}")
        if skipped_count > 0:
            print(f"Skipped {skipped_count} system files (.DS_Store, Thumbs.db)")

    except Exception as e:
        raise ValueError(f"Error reading CSV stream {name}: {e}")

    return checksum_data, checksums


def compare_checksums(checksums1: Set[str], checksums2: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Compare two sets of checksums and find differences.
    
    Args:
        checksums1: Set of checksums from first file
        checksums2: Set of checksums from second file
        
    Returns:
        Tuple of (only_in_first, only_in_second, common)
    """
    only_in_first = checksums1 - checksums2
    only_in_second = checksums2 - checksums1
    common = checksums1 & checksums2
    
    return only_in_first, only_in_second, common


def write_comparison_report(output_file: str, 
                          file1_name: str, file1_data: Dict[str, Dict], only_in_file1: Set[str],
                          file2_name: str, file2_data: Dict[str, Dict], only_in_file2: Set[str],
                          common_checksums: Set[str],
                          verbose: bool = False) -> None:
    """
    Write comparison results to CSV file.
    
    Args:
        output_file: Path to output CSV file
        file1_name: Name of first input file
        file1_data: Checksum data from first file
        only_in_file1: Checksums only in first file
        file2_name: Name of second input file
        file2_data: Checksum data from second file
        only_in_file2: Checksums only in second file
        common_checksums: Checksums found in both files
        verbose: Include all available columns in output
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Determine output columns
            if verbose:
                # Get all unique column names from both files
                all_columns = set()
                if file1_data:
                    all_columns.update(next(iter(file1_data.values())).keys())
                if file2_data:
                    all_columns.update(next(iter(file2_data.values())).keys())
                
                base_columns = ['source_file', 'status', 'checksum']
                extra_columns = sorted(all_columns - {'checksum'})
                fieldnames = base_columns + extra_columns
            else:
                fieldnames = ['source_file', 'status', 'checksum', 'path', 'filename']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write files only in first CSV
            for checksum in sorted(only_in_file1):
                row = {
                    'source_file': file1_name,
                    'status': 'missing_from_second',
                    'checksum': checksum
                }
                
                # Add additional data if available
                if checksum in file1_data:
                    file_data = file1_data[checksum]
                    for col in fieldnames[3:]:  # Skip the first 3 base columns
                        row[col] = file_data.get(col, '')
                
                writer.writerow(row)
            
            # Write files only in second CSV
            for checksum in sorted(only_in_file2):
                row = {
                    'source_file': file2_name,
                    'status': 'missing_from_first',
                    'checksum': checksum
                }
                
                # Add additional data if available
                if checksum in file2_data:
                    file_data = file2_data[checksum]
                    for col in fieldnames[3:]:  # Skip the first 3 base columns
                        row[col] = file_data.get(col, '')
                
                writer.writerow(row)
                
        print(f"Comparison report written to: {output_file}")
        
    except IOError as e:
        print(f"Error writing output file {output_file}: {e}")
        sys.exit(1)


def print_summary(file1_name: str, file2_name: str, 
                 only_in_file1: Set[str], only_in_file2: Set[str], 
                 common_checksums: Set[str]) -> None:
    """
    Print a summary of the comparison results.
    
    Args:
        file1_name: Name of first file
        file2_name: Name of second file
        only_in_file1: Checksums only in first file
        only_in_file2: Checksums only in second file
        common_checksums: Checksums in both files
    """
    print("\n" + "=" * 60)
    print("CHECKSUM COMPARISON SUMMARY")
    print("=" * 60)
    print(f"File 1: {file1_name}")
    print(f"File 2: {file2_name}")
    print("-" * 60)
    print(f"Total checksums in file 1: {len(only_in_file1) + len(common_checksums):,}")
    print(f"Total checksums in file 2: {len(only_in_file2) + len(common_checksums):,}")
    print(f"Common checksums (matches): {len(common_checksums):,}")
    print(f"Only in file 1 (missing from file 2): {len(only_in_file1):,}")
    print(f"Only in file 2 (missing from file 1): {len(only_in_file2):,}")
    print(f"Total differences: {len(only_in_file1) + len(only_in_file2):,}")
    print("-" * 60)
    
    if len(common_checksums) > 0:
        total_files = len(only_in_file1) + len(only_in_file2) + len(common_checksums)
        match_percentage = (len(common_checksums) / total_files) * 100
        print(f"Match percentage: {match_percentage:.2f}%")
    
    if len(only_in_file1) == 0 and len(only_in_file2) == 0:
        print("✅ PERFECT MATCH: All checksums match between files!")
    else:
        print("⚠️  DIFFERENCES FOUND: See output file for details.")


def main():
    """Main function to parse arguments and execute the comparison."""
    parser = argparse.ArgumentParser(
        description='Compare checksums between two CSV files and identify differences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv-checksum-comparator.py source.csv destination.csv
  python csv-checksum-comparator.py file1.csv file2.csv -o report.csv
  python csv-checksum-comparator.py vault.csv library.csv -c hash --verbose
  python csv-checksum-comparator.py file1.csv file2.csv -d ";" -c checksum
        """
    )
    
    parser.add_argument(
        'file1',
        nargs='?',
        help='First CSV file to compare (use "-" or see --stdin-file1)'
    )
    
    parser.add_argument(
        'file2',
        nargs='?',
        help='Second CSV file to compare (use "-" or see --stdin-file2)'
    )

    parser.add_argument(
        '--stdin-file1',
        action='store_true',
        help='Read the first CSV from stdin'
    )

    parser.add_argument(
        '--stdin-file2',
        action='store_true',
        help='Read the second CSV from stdin'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='checksum_differences.csv',
        help='Output CSV file for differences (default: checksum_differences.csv)'
    )
    
    parser.add_argument(
        '-c', '--checksum-column',
        default='checksum',
        help='Name of the checksum column (default: checksum)'
    )
    
    parser.add_argument(
        '-d', '--delimiter',
        help='CSV delimiter character (default: auto-detect, fallback to comma)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Include all columns from input files in output'
    )
    
    args = parser.parse_args()
    
    # Validate input combinations (support stdin)
    if args.stdin_file1 and args.stdin_file2:
        print("Error: Cannot read both inputs from a single stdin stream")
        sys.exit(1)

    # If user passed '-' as a filename treat that as stdin for that file
    file1_from_stdin = args.stdin_file1 or (args.file1 == '-') if args.file1 else args.stdin_file1
    file2_from_stdin = args.stdin_file2 or (args.file2 == '-') if args.file2 else args.stdin_file2

    if file1_from_stdin and file2_from_stdin:
        print("Error: Cannot read both inputs from a single stdin stream")
        sys.exit(1)

    # Ensure we have at least one source for each side
    if not file1_from_stdin and not args.file1:
        print("Error: First input not provided. Use positional file1 or --stdin-file1 or '-' for stdin.")
        sys.exit(1)
    if not file2_from_stdin and not args.file2:
        print("Error: Second input not provided. Use positional file2 or --stdin-file2 or '-' for stdin.")
        sys.exit(1)
    
    print("CSV Checksum Comparator")
    print("=" * 40)
    print(f"Comparing: {args.file1}")
    print(f"     with: {args.file2}")
    print(f"Output to: {args.output}")
    print("-" * 40)
    
    try:
        # Load checksums from inputs (files or stdin)
        print("Loading checksums from inputs...")
        if file1_from_stdin:
            print("Reading first CSV from stdin...")
            file1_data, checksums1 = load_csv_checksums_stream(sys.stdin, args.checksum_column, args.delimiter, name='stdin')
        else:
            file1_data, checksums1 = load_csv_checksums(args.file1, args.checksum_column, args.delimiter)

        if file2_from_stdin:
            # If first input consumed stdin, file2 cannot also be stdin (validated earlier)
            print("Reading second CSV from stdin...")
            file2_data, checksums2 = load_csv_checksums_stream(sys.stdin, args.checksum_column, args.delimiter, name='stdin')
        else:
            file2_data, checksums2 = load_csv_checksums(args.file2, args.checksum_column, args.delimiter)
        
        # Compare checksums
        print("Comparing checksums...")
        only_in_file1, only_in_file2, common = compare_checksums(checksums1, checksums2)
        
        # Write results
        print("Writing comparison report...")
        write_comparison_report(
            args.output,
            args.file1, file1_data, only_in_file1,
            args.file2, file2_data, only_in_file2,
            common, args.verbose
        )
        
        # Print summary
        print_summary(args.file1, args.file2, only_in_file1, only_in_file2, common)
        
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()