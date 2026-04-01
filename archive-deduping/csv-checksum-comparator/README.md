# CSV Checksum Comparator - User Guide

## Overview

The CSV Checksum Comparator is a Python utility that compares two CSV
files containing file checksum data and identifies differences between
them. This tool is essential for verifying filesystem migrations,
validating backups, and ensuring data integrity across different storage
systems.

## Table of Contents
- [<u>Features</u>](#features)
- [<u>Requirements</u>](#requirements)
- [<u>Installation</u>](#installation)
- [<u>Input Format</u>](#input-format)
- [<u>Usage</u>](#usage)
- [<u>Command-Line Options</u>](#command-line-options)
- [<u>Output Format</u>](#output-format)
- [<u>Examples</u>](#examples)
- [<u>Use Cases</u>](#use-cases)
- [<u>Troubleshooting</u>](#troubleshooting)

## Features
- **Intelligent CSV Parsing**: Automatically detects CSV delimiters
  (comma, semicolon, tab, etc.)
- **Flexible Column Naming**: Supports custom checksum column names
- **System File Filtering**: Automatically ignores .DS_Store and
  Thumbs.db files
- **Comprehensive Reporting**: Generates detailed CSV reports of
  differences
- **Statistical Summary**: Provides match percentages and file counts
- **Verbose Mode**: Optionally includes all metadata columns in the
  output
- **Error Handling**: Robust error detection with helpful messages

## Requirements
- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

No installation required. Simply download the script and make it
executable:

chmod +x csv-checksum-comparator.py

Or run it directly with Python:

python csv-checksum-comparator.py \[options\]

## Input Format

Both input CSV files must follow these requirements:

### Required Column
- **checksum**: Contains the file checksum hash (MD5, SHA-256, or any
  hash algorithm)

### Optional Columns (Recommended)
- **path**: Full or relative path to the file
- **filename**: Name of the file
- **size**: File size in bytes
- Any other metadata columns you want to track

### Example CSV Structure

checksum,path,filename,size

abc123def456789...,/documents/report.pdf,report.pdf,1048576

def456abc789012...,/images/photo.jpg,photo.jpg,2097152

### Supported Delimiters

The script automatically detects the following delimiters:
- Comma (,)
- Semicolon (;)
- Tab (\t)
- Pipe (\|)

If auto-detection fails, it defaults to comma or you can specify a
delimiter manually.

## Usage

### Basic Syntax

python csv-checksum-comparator.py \<file1.csv\> \<file2.csv\>
\[options\]

### Quick Start

Compare two CSV files with default settings:

python csv-checksum-comparator.py source.csv destination.csv

This will:
1.  Load checksums from both files
2.  Compare them
3.  Generate checksum_differences.csv with the results
4.  Display a summary in the terminal

### Reading from stdin

The comparator can read one of its input CSVs from stdin. This is
useful when chaining commands or when one CSV is being streamed.

Examples:

```bash
# Read first CSV from stdin, second from file
cat source.csv | python csv-checksum-comparator.py --stdin-file1 destination.csv

# Read second CSV from stdin (first is a file)
cat dest.csv | python csv-checksum-comparator.py source.csv --stdin-file2

# Use '-' as a shorthand for stdin for one input
cat source.csv | python csv-checksum-comparator.py - destination.csv
```

## Command-Line Options

| **Option** | **Short** | **Description** | **Default** |
|----|----|----|----|
| file1 | \- | First CSV file to compare (positional) | Required |
| file2 | \- | Second CSV file to compare (positional) | Required |
| --output | -o | Output CSV file path | checksum_differences.csv |
| --checksum-column | -c | Name of the checksum column | checksum |
| --delimiter | -d | CSV delimiter character | Auto-detect |
| --verbose | \- | Include all columns in output | False |
| --help | -h | Show help message and exit | \- |

### Detailed Option Descriptions

#### --output / -o

Specify the path and filename for the comparison report.

python csv-checksum-comparator.py file1.csv file2.csv -o report.csv

#### --checksum-column / -c

Use this if your CSV uses a different column name for checksums (e.g.,
"hash", "md5", "sha256").

python csv-checksum-comparator.py file1.csv file2.csv -c md5_hash

#### --delimiter / -d

Manually specify the CSV delimiter if auto-detection fails or you want
to override it.

\# For semicolon-delimited files

python csv-checksum-comparator.py file1.csv file2.csv -d ";"

\# For tab-delimited files

python csv-checksum-comparator.py file1.csv file2.csv -d \$'\t'

#### --verbose

Include all available columns from the input files in the output report.

python csv-checksum-comparator.py file1.csv file2.csv --verbose

## Output Format

### Output CSV Structure

The comparison report contains the following columns:

#### Standard Mode (Default)

| **Column**  | **Description**                           |
|-------------|-------------------------------------------|
| source_file | Which input file the checksum came from   |
| status      | missing_from_first or missing_from_second |
| checksum    | The checksum hash value                   |
| path        | File path (if available in input)         |
| filename    | Filename (if available in input)          |

#### Verbose Mode

Includes all columns from the input CSVs in addition to the standard
columns.

### Output Statuses
- **missing_from_second**: Checksum exists in file1 but not in file2
- **missing_from_first**: Checksum exists in file2 but not in file1

### Terminal Summary

The script displays a summary showing:

============================================================

CHECKSUM COMPARISON SUMMARY

============================================================

File 1: source.csv

File 2: destination.csv

------------------------------------------------------------

Total checksums in file 1: 1,523

Total checksums in file 2: 1,498

Common checksums (matches): 1,485

Only in file 1 (missing from file 2): 38

Only in file 2 (missing from file 1): 13

Total differences: 51

------------------------------------------------------------

Match percentage: 97.34%

⚠️ DIFFERENCES FOUND: See output file for details.

## Examples

### Example 1: Basic Comparison

Compare two checksum files from a migration:

python csv-checksum-comparator.py vault-source.csv vault-destination.csv

**Output:**
- Creates checksum_differences.csv with all differences
- Shows summary in terminal

### Example 2: Custom Output Location

Save the comparison report to a specific location:

python csv-checksum-comparator.py old-system.csv new-system.csv -o
reports/migration-2024.csv

### Example 3: Different Checksum Column Name

If your CSV uses "md5" instead of "checksum":

python csv-checksum-comparator.py file1.csv file2.csv -c md5

### Example 4: Semicolon-Delimited Files

For European CSV formats that use semicolons:

python csv-checksum-comparator.py european-format1.csv
european-format2.csv -d ";"

### Example 5: Verbose Output with All Metadata

Include all columns from input files in the comparison report:

python csv-checksum-comparator.py source.csv dest.csv --verbose -o
detailed-report.csv

### Example 6: Complete Workflow

Full migration verification workflow:

\# Step 1: Generate checksums from source system

python csv-checksum-lister.py /mnt/source-vault -o source-checksums.csv

\# Step 2: Generate checksums from destination system

python csv-checksum-lister.py /mnt/destination-vault -o
dest-checksums.csv

\# Step 3: Compare the checksums

python csv-checksum-comparator.py source-checksums.csv
dest-checksums.csv -o migration-report.csv

## Use Cases

### 1. Filesystem Migration Verification

**Scenario**: You've migrated files from one storage system to another.

**Workflow**:
1.  Generate checksums from the source system before migration
2.  Generate checksums from the destination system after migration
3.  Compare both checksum files to verify all files transferred
    correctly

python csv-checksum-comparator.py source-before.csv
destination-after.csv -o migration-verification.csv

### 2. Backup Integrity Checking

**Scenario**: Verify that a backup contains all files from the original
system.

python csv-checksum-comparator.py original-system.csv backup-system.csv
-o backup-verification.csv

Files in "missing_from_second" indicate files not backed up.

### 3. Archive Comparison

**Scenario**: Compare two versions of an archive to find what changed.

python csv-checksum-comparator.py archive-v1.csv archive-v2.csv -o
archive-changes.csv

### 4. Data Synchronization Verification

**Scenario**: Ensure two systems that should be in sync actually contain
the same files.

python csv-checksum-comparator.py system-a.csv system-b.csv -o
sync-status.csv

### 5. Quality Assurance Testing

**Scenario**: Verify that a processing pipeline hasn't accidentally
dropped or corrupted files.

python csv-checksum-comparator.py pre-processing.csv post-processing.csv
-o qa-check.csv

## Troubleshooting

### Problem: "Column 'checksum' not found"

**Solution**: Your CSV uses a different column name. Use the -c option:

python csv-checksum-comparator.py file1.csv file2.csv -c
your_column_name

### Problem: "Could not detect delimiter"

**Solution**: Manually specify the delimiter with -d:

python csv-checksum-comparator.py file1.csv file2.csv -d ";"

### Problem: No differences found but files are different

**Possible Causes**:
1.  System files (.DS_Store, Thumbs.db) are being ignored (this is
    intentional)
2.  Empty checksum rows are being skipped
3.  Checksums are actually the same (content is identical even if
    filenames differ)

**Investigation**:
- Check that both CSVs have the same checksum algorithm
- Verify checksums were generated correctly
- Look for whitespace in checksum values

### Problem: Script runs but output file is empty

**Possible Causes**:
1.  All checksums match perfectly (no differences to report)
2.  No valid checksums in input files

**Solution**: Check the terminal summary for statistics. If "Total
differences: 0", the files match perfectly.

### Problem: "File not found" error

**Solution**: Verify file paths are correct and files exist:

ls -l file1.csv file2.csv

### Problem: Memory issues with large files

**Solution**: The script loads all checksums into memory. For very large
files (millions of rows):
1.  Consider splitting the CSVs into smaller chunks
2.  Increase available system memory
3.  Process in batches

### Problem: Special characters in filenames not displaying correctly

**Solution**: The script uses UTF-8 encoding. Ensure your terminal
supports UTF-8:

export LANG=en_US.UTF-8

## Advanced Tips

### Filtering Results

After generating the comparison report, you can filter it using standard
command-line tools:

\# Find only files missing from destination

grep "missing_from_second" checksum_differences.csv

\# Count differences by status

awk -F',' '{print \$2}' checksum_differences.csv \| sort \| uniq -c

### Automated Monitoring

Use in a cron job for regular verification:

\#!/bin/bash

\# daily-verification.sh

python csv-checksum-comparator.py /path/to/source.csv
/path/to/backup.csv -o daily-report-\$(date +%Y%m%d).csv

\# Alert if differences found

if \[ \$(wc -l \< daily-report-\$(date +%Y%m%d).csv) -gt 1 \]; then

echo "Differences detected!" \| mail -s "Backup Alert" admin@example.com

fi

### Integration with Other Tools

Pipe output to other analysis tools:

\# Generate report and analyze with jq (convert to JSON first)

python csv-checksum-comparator.py file1.csv file2.csv -o report.csv

## Performance Considerations
- **Speed**: Comparison time is linear with the number of checksums
  (O(n))
- **Memory**: All checksums are loaded into memory (approximately 100
  bytes per checksum)
- **Disk I/O**: Minimal - only reads input files once and writes output
  once

**Typical Performance**:
- 10,000 files: \< 1 second
- 100,000 files: ~5 seconds
- 1,000,000 files: ~30 seconds

## System File Filtering

The script automatically ignores these system files:
- .DS_Store (macOS)
- Thumbs.db (Windows)

These files are skipped during comparison and logged in the output:

Loaded 1,523 checksums from source.csv

Skipped 15 system files (.DS_Store, Thumbs.db)

## Best Practices
1.  **Use Consistent Hash Algorithms**: Ensure both CSVs use the same
    checksum algorithm (MD5, SHA-256, etc.)
2.  **Generate Fresh Checksums**: For best results, generate checksums
    shortly before comparison
3.  **Verify File Sizes**: Include file size in your CSVs to catch
    truncated files
4.  **Archive Results**: Keep comparison reports for audit trails
5.  **Test First**: Run on a small subset to verify your CSV format is
    correct
6.  **Document Your Process**: Note which systems and dates were
    compared

## Support and Contributions

For issues, questions, or suggestions, please contact your system
administrator or refer to the script's inline documentation.

## License

This script is provided as-is for internal use. Modify as needed for
your specific requirements.

## Version History
- **v1.0**: Initial release with basic comparison functionality
- **v1.1**: Added automatic delimiter detection
- **v1.2**: Added system file filtering (.DS_Store, Thumbs.db)
- **v1.3**: Enhanced error handling and verbose mode

**Last Updated**: December 2024
