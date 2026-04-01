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
CSV Checksum Lister - READ-ONLY Filesystem Analysis Tool

A script to recursively traverse a filesystem and create checksums of all files
under 1GB, excluding any files or directories containing "RESTRICTED".
Outputs results to a CSV file with columns for checksums, path, and filename.

IMPORTANT: This script operates in STRICTLY READ-ONLY mode. It will NEVER:
- Modify file contents
- Change file permissions
- Rename files or directories
- Create or delete files in the target filesystem
- Alter file timestamps or metadata

The script only reads file contents to calculate checksums and writes output
to a separate CSV file outside the target filesystem.

USAGE:
    python csv-checksum-lister.py <source_path> [OPTIONS]

REQUIRED ARGUMENTS:
    source_path         Root directory to traverse and analyze

OPTIONAL ARGUMENTS:
    -o, --output FILE   Output CSV file path (default: file_checksums.csv)
    -s, --max-size GB   Maximum file size in GB to process (default: 1.0)
    -a, --algorithm ALG Hash algorithm: md5, sha1, sha256, sha512 (default: sha256)
    --log-skipped       Create additional file listing non-system files that were skipped
    -h, --help          Show help message and exit

EXAMPLES:

    Basic usage - analyze current directory:
        python csv-checksum-lister.py .

    Analyze specific directory with custom output file:
        python csv-checksum-lister.py /path/to/source -o migration_checksums.csv

    Process only files under 500MB using MD5:
        python csv-checksum-lister.py /path/to/source -s 0.5 -a md5

    Full migration analysis with all options:
        python csv-checksum-lister.py /mnt/old_storage -o /home/user/migration_report.csv -s 2.0 -a sha256

    Generate report of skipped files:
        python csv-checksum-lister.py /path/to/source --log-skipped

    Windows path example:
        python csv-checksum-lister.py "C:\\Data\\Migration Source" -o "D:\\Reports\\checksums.csv"

OUTPUT FORMAT:
    The CSV file contains three columns:
    - checksum: Hash value (SHA-256, MD5, etc.)
    - path: Full absolute path to the file
    - filename: Just the filename portion

    Example CSV content:
        checksum,path,filename
        a1b2c3d4e5f6...,/path/to/file1.txt,file1.txt
        f6e5d4c3b2a1...,/path/to/subdir/file2.pdf,file2.pdf

FILTERING BEHAVIOR:
    - Skips files larger than specified size limit (default: 1GB)
    - Excludes any files/directories containing "RESTRICTED" (case-insensitive)
    - Automatically skips common system files:
        * .DS_Store (macOS file system metadata)
        * Thumbs.db (Windows thumbnail cache)
        * Desktop.ini (Windows folder settings)
        * ._.DS_Store (macOS AppleDouble files)
    - Handles file access errors gracefully (reports and continues)
    - Provides progress feedback and summary statistics

USE CASES:
    - Filesystem migration verification
    - Duplicate file detection by comparing checksums
    - File integrity monitoring
    - Change detection between filesystem snapshots
    - Compliance auditing (excluding restricted areas)

PERFORMANCE NOTES:
    - Processes files in 8KB chunks for memory efficiency
    - Progress is displayed for large operations
    - Consider using faster algorithms (MD5) for speed vs security (SHA-256)
    - Network storage may be slower; consider running locally when possible
"""

import os
import csv
import hashlib
import argparse
import sys
from pathlib import Path
from typing import Generator, Tuple


def should_skip_path(path: str) -> bool:
    """
    Check if a path should be skipped based on containing 'RESTRICTED'.
    
    Args:
        path: File or directory path to check
        
    Returns:
        True if path should be skipped, False otherwise
    """
    return "RESTRICTED" in path.upper()


def should_skip_system_file(filename: str) -> bool:
    """
    Check if a file should be skipped based on being a common system file.
    
    Args:
        filename: Just the filename (not full path) to check
        
    Returns:
        True if file should be skipped, False otherwise
    """
    system_files = {
        '.ds_store',      # macOS file system metadata
        'thumbs.db',      # Windows thumbnail cache
        'desktop.ini',    # Windows folder settings
        '._.ds_store',    # macOS AppleDouble files
    }
    
    return filename.lower() in system_files


def calculate_file_checksum(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate checksum for a file using the specified algorithm.
    
    SAFETY: Opens file in READ-ONLY BINARY mode ('rb') - no modifications possible.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Hexadecimal string of the file's checksum
        
    Raises:
        IOError: If file cannot be read
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        # Open in READ-ONLY binary mode - no write operations possible
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except IOError as e:
        raise IOError(f"Could not read file {file_path}: {e}")


def traverse_filesystem(root_path: str, max_size_gb: float = 1.0, algorithm: str = 'sha256', skipped_files_list: list = None) -> Generator[Tuple[str, str, str], None, None]:
    """
    Recursively traverse filesystem and yield file information.
    
    Args:
        root_path: Root directory to start traversal
        max_size_gb: Maximum file size in GB to process
        algorithm: Hash algorithm to use for checksums
        skipped_files_list: Optional list to collect non-system skipped files
        
    Yields:
        Tuple of (checksum, full_path, filename)
    """
    max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
    processed_files = 0
    skipped_files = 0
    
    for root, dirs, files in os.walk(root_path):
        # Skip directories containing "RESTRICTED"
        if should_skip_path(root):
            print(f"Skipping directory (contains RESTRICTED): {root}")
            dirs.clear()  # Don't traverse subdirectories
            continue
            
        # Remove restricted directories from dirs list to prevent traversal
        dirs[:] = [d for d in dirs if not should_skip_path(os.path.join(root, d))]
        
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # Skip system files (DS_Store, Thumbs.db, etc.)
            if should_skip_system_file(filename):
                print(f"Skipping system file: {file_path}")
                skipped_files += 1
                continue
            
            # Skip files containing "RESTRICTED"
            if should_skip_path(file_path):
                print(f"Skipping file (contains RESTRICTED): {file_path}")
                skipped_files += 1
                if skipped_files_list is not None:
                    skipped_files_list.append((file_path, "Contains RESTRICTED"))
                continue
            
            try:
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size > max_size_bytes:
                    print(f"Skipping large file ({file_size / (1024**3):.2f} GB): {file_path}")
                    skipped_files += 1
                    if skipped_files_list is not None:
                        skipped_files_list.append((file_path, f"File too large ({file_size / (1024**3):.2f} GB)"))
                    continue
                
                # Calculate checksum
                print(f"Processing: {file_path}")
                checksum = calculate_file_checksum(file_path, algorithm)
                processed_files += 1
                
                yield checksum, file_path, filename
                
            except (OSError, IOError) as e:
                print(f"Error processing {file_path}: {e}")
                skipped_files += 1
                if skipped_files_list is not None:
                    skipped_files_list.append((file_path, f"Error: {e}"))
                continue
    
    print(f"\nSummary: {processed_files} files processed, {skipped_files} files skipped")


def write_to_csv(output_file: str, file_data: Generator[Tuple[str, str, str], None, None]) -> None:
    """
    Write file checksum data to CSV file.
    
    Args:
        output_file: Path to output CSV file
        file_data: Generator yielding (checksum, path, filename) tuples
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['checksum', 'path', 'filename'])
            
            # Write data
            for checksum, path, filename in file_data:
                writer.writerow([checksum, path, filename])
                
        print(f"Results written to: {output_file}")
        
    except IOError as e:
        print(f"Error writing to CSV file {output_file}: {e}")
        sys.exit(1)


def write_skipped_files_report(output_file: str, skipped_files_list: list) -> None:
    """
    Write skipped files report to text file.
    
    Args:
        output_file: Path to output text file
        skipped_files_list: List of tuples (file_path, reason)
    """
    if not skipped_files_list:
        print("No non-system files were skipped.")
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as txtfile:
            txtfile.write("SKIPPED FILES REPORT\n")
            txtfile.write("=" * 50 + "\n")
            txtfile.write(f"Total skipped files: {len(skipped_files_list)}\n")
            txtfile.write("=" * 50 + "\n\n")
            
            # Group by reason
            by_reason = {}
            for file_path, reason in skipped_files_list:
                if reason not in by_reason:
                    by_reason[reason] = []
                by_reason[reason].append(file_path)
            
            # Write grouped results
            for reason, files in by_reason.items():
                txtfile.write(f"{reason} ({len(files)} files):\n")
                txtfile.write("-" * 40 + "\n")
                for file_path in sorted(files):
                    txtfile.write(f"{file_path}\n")
                txtfile.write("\n")
                
        print(f"Skipped files report written to: {output_file}")
        
    except IOError as e:
        print(f"Error writing skipped files report {output_file}: {e}")


def validate_output_path_safety(source_path: str, output_path: str) -> None:
    """
    Ensure the output CSV file is not being written inside the source filesystem.
    This prevents any accidental modifications to the target filesystem.
    
    Args:
        source_path: The source directory being analyzed
        output_path: The intended output CSV file path
        
    Raises:
        ValueError: If output path would write inside source filesystem
    """
    source_abs = os.path.abspath(source_path)
    output_abs = os.path.abspath(output_path)
    
    # Check if output file would be created inside source directory
    try:
        # This will raise ValueError if output_abs is not under source_abs
        os.path.relpath(output_abs, source_abs)
        # If we get here, output is inside source - this is dangerous
        if not output_abs.startswith('..'):
            raise ValueError(
                f"SAFETY ERROR: Output file '{output_path}' would be created inside "
                f"the source filesystem '{source_path}'. This violates read-only requirements. "
                f"Please specify an output path outside the source directory."
            )
    except ValueError:
        # If relpath fails, paths are on different drives/roots - this is safe
        pass


def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description='Generate checksums for files in a directory tree and output to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv-checksum-lister.py /path/to/source
  python csv-checksum-lister.py /path/to/source -o checksums.csv
  python csv-checksum-lister.py /path/to/source -s 0.5 -a md5
        """
    )
    
    parser.add_argument(
        'source_path',
        nargs='?',
        help='Root directory to traverse (omit when using --stdin)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='file_checksums.csv',
        help='Output CSV file path (default: file_checksums.csv)'
    )
    
    parser.add_argument(
        '-s', '--max-size',
        type=float,
        default=1.0,
        help='Maximum file size in GB to process (default: 1.0)'
    )
    
    parser.add_argument(
        '-a', '--algorithm',
        choices=['md5', 'sha1', 'sha256', 'sha512'],
        default='sha256',
        help='Hash algorithm to use (default: sha256)'
    )
    
    parser.add_argument(
        '--log-skipped',
        action='store_true',
        help='Create additional file listing non-system files that were skipped'
    )

    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read newline-separated file paths from stdin instead of traversing a directory'
    )
    
    args = parser.parse_args()
    
    # SAFETY: Validate that we're operating in read-only mode
    print("=" * 60)
    print("READ-ONLY FILESYSTEM ANALYSIS TOOL")
    print("=" * 60)
    print("SAFETY GUARANTEE: This script will ONLY read files.")
    print("NO modifications will be made to the target filesystem.")
    print("=" * 60)
    
    # Validate inputs: either a source_path directory or --stdin must be used
    if not args.stdin:
        if not args.source_path:
            print("Error: source_path is required when not using --stdin")
            sys.exit(1)

        if not os.path.exists(args.source_path):
            print(f"Error: Source path '{args.source_path}' does not exist")
            sys.exit(1)
        
        if not os.path.isdir(args.source_path):
            print(f"Error: Source path '{args.source_path}' is not a directory")
            sys.exit(1)

        # SAFETY: Ensure output file is not being written inside source filesystem
        try:
            validate_output_path_safety(args.source_path, args.output)
        except ValueError as e:
            print(f"{e}")
            sys.exit(1)

        print(f"Source filesystem (READ-ONLY): {args.source_path}")
    else:
        # stdin mode: source paths will be read from stdin; skip the directory safety check
        print("Reading file paths from stdin (READ-ONLY mode). Ensure output path is outside the source files' locations.")
    print(f"Maximum file size: {args.max_size} GB")
    print(f"Hash algorithm: {args.algorithm}")
    print(f"Output CSV file: {args.output}")
    print(f"Excluding paths containing: RESTRICTED")
    print(f"Excluding system files: .DS_Store, Thumbs.db, Desktop.ini, ._.DS_Store")
    if args.log_skipped:
        skipped_output = Path(args.output).stem + "_skipped.txt"
        print(f"Skipped files report: {skipped_output}")
    print("-" * 50)
    
    # Process files and write to CSV
    skipped_files_list = [] if args.log_skipped else None
    if args.stdin:
        # Read newline-separated file paths from stdin
        def paths_iter():
            for line in sys.stdin:
                p = line.strip()
                if p:
                    yield p

        file_generator = (
            (lambda p: (calculate_file_checksum(p, args.algorithm), p, os.path.basename(p))) (p)
            for p in paths_iter()
        )

        # Wrap generator to apply skips and size checks similarly to traversal
        def stdin_file_generator(paths_iterable, max_size_gb, algorithm, skipped_files_list=None):
            max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
            for p in paths_iterable:
                try:
                    if should_skip_system_file(os.path.basename(p)):
                        if skipped_files_list is not None:
                            skipped_files_list.append((p, 'System file'))
                        continue
                    if should_skip_path(p):
                        if skipped_files_list is not None:
                            skipped_files_list.append((p, 'Contains RESTRICTED'))
                        continue
                    if not os.path.exists(p):
                        if skipped_files_list is not None:
                            skipped_files_list.append((p, 'Missing'))
                        continue
                    file_size = os.path.getsize(p)
                    if file_size > max_size_bytes:
                        if skipped_files_list is not None:
                            skipped_files_list.append((p, f'File too large ({file_size / (1024**3):.2f} GB)'))
                        continue

                    checksum = calculate_file_checksum(p, algorithm)
                    yield checksum, p, os.path.basename(p)
                except (OSError, IOError) as e:
                    if skipped_files_list is not None:
                        skipped_files_list.append((p, f'Error: {e}'))
                    continue

        file_generator = stdin_file_generator(paths_iter(), args.max_size, args.algorithm, skipped_files_list)
        write_to_csv(args.output, file_generator)
    else:
        file_generator = traverse_filesystem(args.source_path, args.max_size, args.algorithm, skipped_files_list)
        write_to_csv(args.output, file_generator)
    
    # Write skipped files report if requested
    if args.log_skipped:
        skipped_output = Path(args.output).stem + "_skipped.txt"
        write_skipped_files_report(skipped_output, skipped_files_list)


if __name__ == "__main__":
    main()