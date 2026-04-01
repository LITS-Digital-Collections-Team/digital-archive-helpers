# audio-track-concatenator

Concatenate multiple audio files in a directory into a single output file using `pydub`.

The script discovers supported audio files by extension, sorts them alphabetically, loads them sequentially, and appends them into a single `AudioSegment` that is exported to the requested output path.

## Prerequisites

- Python 3.7 or newer is recommended.
- `ffmpeg` is required by `pydub`.
- Python package: `pydub`

Install `ffmpeg`:

```sh
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

On Windows, install `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/) and add it to `PATH`.

Install `pydub`:

```sh
python -m venv venv
source venv/bin/activate
pip install pydub
```

Verify the setup:

```sh
ffmpeg -version
python -c "import pydub; print('pydub ok')"
```

## Usage

Basic example:

```sh
python audio-track-concatenator.py ./tracks/ output/album.mp3
```

Example creating WAV output:

```sh
python audio-track-concatenator.py ./recordings/ ./deliverable/meeting.wav
```

For explicit ordering, name files with a sortable scheme such as `01_intro.mp3`, `02_song.mp3`, and `03_outro.mp3`. The script sorts files alphabetically before concatenation.

## Behavior

- Output format is inferred from the output filename extension.
- If the extension is unknown or unsupported, the script defaults to `mp3` and prints a warning.
- The script loads the full concatenated result into memory before exporting.
- The script does not recurse into subdirectories.

## How It Works

`get_audio_files(directory)`:

- Lists files in the input directory.
- Filters by supported extensions: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`
- Sorts matching files alphabetically.

`concatenate_audio(files)`:

- Loads the first file with `AudioSegment.from_file()`.
- Loads and appends each subsequent segment with `combined += segment`.

Export step:

```python
combined_audio.export(output_file, format=output_ext)
```

Error handling:

- Raises `ValueError` when no audio files are found.
- Exits with a message if the input directory does not exist.

## Supported Formats

Supported input formats are case-insensitive:

- `.mp3`
- `.wav`
- `.ogg`
- `.flac`
- `.aac`
- `.m4a`

Supported output extensions accepted by the script:

- `mp3`
- `wav`
- `ogg`
- `flac`
- `aac`
- `m4a`

If the requested output extension is unsupported, the script exports as `mp3`.

Recommended default:

- Use `wav` for lossless concatenation.
- Use `mp3` or `aac` for compressed deliverables.

## Troubleshooting

### ffmpeg not found

Make sure `ffmpeg` is installed and available on `PATH`:

```sh
ffmpeg -version
```

### No audio files found

- Confirm files are located directly in the input directory.
- Confirm they use one of the supported extensions.

### Audio format discrepancies

If output sounds wrong, normalize segments before appending them:

```python
segment = segment.set_frame_rate(44100).set_channels(2)
```

Add that line in `concatenate_audio()` before `combined += segment`.

### Memory errors on large inputs

For large batches, prefer the `ffmpeg` concat demuxer instead of in-memory concatenation with `pydub`.

### Garbage or silence between tracks

- Check source files for leading or trailing silence.
- Trim segments before concatenation if needed.
- Consider using `pydub` silence-processing helpers before appending.

### Metadata not preserved

`pydub` export does not automatically preserve input metadata. Use `ffmpeg` metadata options or extend the script to write metadata separately.

## Performance And Best Practices

For many files or very large inputs, use the `ffmpeg` concat demuxer:

Create `list.txt`:

```text
file 'path/to/01.mp3'
file 'path/to/02.mp3'
```

Run:

```sh
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp3
```

This avoids unnecessary decoding and re-encoding when inputs are codec-compatible, and it uses much less memory.

Additional recommendations:

- Pre-normalize sample rate and channel count for consistent output.
- Run on a machine with adequate RAM.

## Recommended Improvements

Potential enhancements for the script:

- Add `argparse`-based CLI options such as `--recursive`, `--order`, `--gap-seconds`, `--fade`, `--normalize`, `--format`, and `--bitrate`.
- Add streaming or temporary-file concatenation to reduce memory usage.
- Add optional normalization per segment with `set_frame_rate()`, `set_channels()`, and `set_sample_width()`.
- Add metadata handling and a sidecar JSON manifest.
- Add progress reporting and verbose logging.
- Add unit tests and input validation.

Suggested CLI stub:

```python
import argparse

p = argparse.ArgumentParser(description="Concatenate audio tracks in a directory")
p.add_argument("input_dir")
p.add_argument("output_file")
p.add_argument("--format", help="Output format (mp3,wav,flac,... )")
p.add_argument("--gap", type=float, default=0.0, help="Seconds of silence between tracks")

args = p.parse_args()
```