# vault-checksum-csv-converter

Convert Archive-It Vault checksum text exports into CSV format.

Overview

This small utility converts plain-text checksum exports (as downloaded
from Archive‑It Vault) into a CSV file with three columns: `checksum`,
`path`, and `filename`.

Requirements

- Python 3.6+

Usage

```bash
# default: output filename is input with .csv extension
python vault-checksum-csv-converter.py /path/to/vault-export.txt

# specify output file explicitly
python vault-checksum-csv-converter.py /path/to/vault-export.txt /tmp/checksums.csv
```

Input format

Each input line should contain the checksum, a single space, then the
stored path and filename. The script splits on the first space so paths
may include spaces. Example input line:

```
088f9b365eca31afdeca7acab5f66dd2 a1-i_board-of-trustees-records/.../2019-10-03_19-45-27_UTC.txt
```

Output

The output is a UTF-8 encoded CSV with a header row:

```
checksum,path,filename
```

Notes

- Lines that are empty or that do not match the expected pattern are
  skipped; non-empty invalid lines generate a warning message.
- The script prints progress messages every 1000 processed lines.
- If the output filename is omitted, the script writes a CSV with the
  same base name as the input file.

Exit codes

- `0` — completed (summary printed)
- `1` — input file missing or IO error

Examples

```bash
# Convert a Vault export to CSV (default output name)
python vault-checksum-csv-converter.py vault-export.txt

# Convert and write to a chosen output path
python vault-checksum-csv-converter.py vault-export.txt vault-checksums.csv
```

See also

- `csv-checksum-comparator.py` — compare CSVs from different sources
- `csv-checksum-lister.py` — list checksums exported from other systems

License

This project is distributed under the GNU General Public License v3 (GPL-3.0).

Contact

Author: Patrick R. Wallace <mail.prw@gmail.com>
