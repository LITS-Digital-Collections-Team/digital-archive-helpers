# Archive Deduping: DarkArchive → Vault

Short helper scripts and workflow for generating and comparing checksums
between a local filesystem (DarkArchive) and checksums exported from
Archive‑It Vault. Each tool in this folder has its own README with
detailed usage; this document provides a concise overview and the
recommended workflow.

**Included scripts**

- `csv-checksum-lister/` — `csv-checksum-lister.py`: walk a directory tree,
  compute checksums, and emit a CSV suitable for comparison. See
  `csv-checksum-lister/README.md` for options and examples.
- `vault-checksum-csv-converter/` — `vault-checksum-csv-converter.py`:
  convert a Vault plaintext checksum export (Archive‑It Vault) into the
  same CSV format used by the lister/comparator. See
  `vault-checksum-csv-converter/README.md` for details and stdin support.
- `csv-checksum-comparator/` — `csv-checksum-comparator.py`: compare two
  checksum CSVs (local vs Vault) and produce a differences CSV that lists
  files missing from one side or the other. See
  `csv-checksum-comparator/README.md` for flags and output format.

**Typical workflow**

1. Generate local checksums (filesystem):

```bash
python3 csv-checksum-lister/csv-checksum-lister.py /path/to/data -o local-checksums.csv
```

2. Export checksums from Archive‑It Vault (via web UI or API) and convert
   the exported text to CSV:

```bash
# file -> csv
python3 vault-checksum-csv-converter/vault-checksum-csv-converter.py vault-export.txt -o vault-checksums.csv

# or via stdin
cat vault-export.txt | python3 vault-checksum-csv-converter/vault-checksum-csv-converter.py --stdin > vault-checksums.csv
```

3. Compare local and Vault CSVs to find missing files:

```bash
python3 csv-checksum-comparator/csv-checksum-comparator.py local-checksums.csv vault-checksums.csv -o diff.csv
```

4. Inspect `diff.csv` to identify candidates missing from Vault (or local
   missing files). Create a simple list (`missing.txt`) containing the
   file paths you intend to copy to Vault.

5. Upload missing files to Vault using your transfer tool (for example
   `rclone` / `rclone-vault`). Example (adapt to your mapping and tool):

```bash
while IFS= read -r path; do
  # map 'path' to the actual local source if needed
  rclone copy "/path/to/source/$path" vault:collection/path
done < missing.txt
```

6. Optionally re-run the lister and comparator for a verification pass.

**Notes & recommendations**

- Read each tool's individual README for full command-line options and
  examples. The scripts accept common patterns (files, directories, and
  some support stdin where appropriate).
- Work in small batches when copying into Vault and verify a few files
  before committing a large transfer.
- These scripts are intended as helpers; adjust path mappings and flags
  to match your repository layout and Vault configuration.
