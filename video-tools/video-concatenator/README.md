# video-concatenator — User manual & guide

- Quick summary
- Prerequisites
- Installation
- Basic usage and CLI options
- Examples
- How it works (detailed)
- ffmpeg behaviour & caveats
- Temporary files & cleanup
- Troubleshooting
- Performance & best practices
- Recommended improvements (developer notes)

## Quick summary

- Input: directory containing video files (.mp4, .avi, .mkv, .mov, .wmv).
- Output: single concatenated video file (user‑specified path).
- Defaults: resolution 640x480, framerate 30, codec libx264.
- The script transcodes each found file into a uniform intermediate MP4, then concatenates them with ffmpeg's concat demuxer.

## Prerequisites

- Python 3.6+
- ffmpeg installed and on PATH (required)
  - Debian/Ubuntu: sudo apt install ffmpeg
  - macOS (Homebrew): brew install ffmpeg
  - Windows: install from ffmpeg.org and add to PATH
- Sufficient disk space for temporary transcoded files (script creates a temp dir).

No additional Python packages are required.

## Installation

1.  Clone or place video-concatenator.py in a working folder:
    - /home/sysop/work/code/video-tools/video-concatenator.py
2.  Ensure ffmpeg is installed and executable from the terminal.
3.  Make script executable or run with the Python interpreter:
    - python video-concatenator.py ...

## Basic usage & CLI options

Syntax:

python video-concatenator.py \<input_directory\> \<output_file\> [options]

Positional arguments

- input_directory — directory containing source videos
- output_file — path to write the concatenated video

Options

- -r, --resolution
  - Output resolution (e.g., 1920x1080). Default: 640x480.
- -f, --framerate
  - Output framerate (frames per second). Default: 30.
- -c, --codec
  - Output video codec (e.g., libx264, libx265). Default: libx264.

Notes

- Files inside input_directory are discovered by extension filter and processed in sorted order.
- The script writes intermediate transcoded files to a temporary directory, then concatenates them, and removes the temporary directory when finished.

## Examples

1.  Default settings (640x480, 30fps, libx264):

python video-concatenator.py ./raw-clips/ ./deliverables/final.mp4

2.  Full HD, 25fps, x264:

python video-concatenator.py ./raw-clips/ ./deliverables/final_hd.mp4 -r 1920x1080 -f 25 -c libx264

3.  Use HEVC (note: playback compatibility varies):

python video-concatenator.py ./raw-clips/ ./deliverables/final_hevc.mp4 -c libx265

4.  Running on Windows PowerShell (quote paths with spaces):

python video-concatenator.py "C:\Users\Media\Clips" "C:\Users\Media\deliverables\merged.mp4" -r 1280x720 -f 30

## How it works — detailed flow

1.  Validate input_directory exists and contains supported video files (.mp4/.avi/.mkv/.mov/.wmv).
2.  Create a temporary directory (via tempfile.mkdtemp) to hold transcoded intermediates.
3.  For each video file (sorted alphabetically):
    - Call ffmpeg to transcode to the specified resolution, framerate, and codec. The script sets codec options: -preset fast -crf 23 (reasonable speed/quality tradeoff).
    - Output intermediate file named video_000.mp4, video_001.mp4, ...
4.  Create a concat list file (file '/tmp/.../video_000.mp4' etc.).
5.  Call ffmpeg with the concat demuxer:
    - ffmpeg -f concat -safe 0 -i list.txt -c copy output_file
6.  Remove the temporary directory (cleanup in finally block).

## ffmpeg behaviour & important caveats

- Concat demuxer requirements:
  - The concat demuxer expects input files to share the same codec, pixel format, resolution, framerate, and timebase. The script transcodes each source file to the same parameters, so the concat step can use stream copy (-c copy) — no second encode occurs.
- Audio tracks:
  - The script focuses on video codec selection. Audio codec handling follows ffmpeg defaults unless explicitly added; if you need control over audio codec/bitrate, extend the script to pass -c:a and audio options per ffmpeg.
- Container format:
  - The script writes MP4 intermediates. If you choose certain codecs (e.g., HEVC) or containers, ensure the chosen container supports them.
- Codec compatibility & player support:
  - libx264 in an MP4 container is broadly compatible. libx265 produces HEVC streams which may not play on older devices.
- Quality & speed:
  - -crf 23 and -preset fast are defaults. For higher quality, lower CRF (e.g., 18–20) or slower preset; for faster runs increase CRF or use -preset veryfast.

## Temporary files & cleanup

- The script creates a temporary directory for transcoded files using tempfile and removes it with shutil.rmtree() in a finally block.
- If ffmpeg crashes or the Python process is killed forcefully, temporary files may remain. Check and remove leftover transcoded_videos\_\* dirs if needed.

## Troubleshooting

Problem: "ffmpeg not found"

- Install ffmpeg and ensure it is on PATH. Test: ffmpeg -version

Problem: "No supported video files found"

- Confirm file extensions are in the supported list (.mp4, .avi, .mkv, .mov, .wmv). Files with uppercase extensions are handled (lowercased). Ensure files are directly in the input directory (script does not recurse).

Problem: ffmpeg crashes during transcode

- Inspect ffmpeg output printed to terminal for error details. Try transcoding one file manually:

> ffmpeg -i input.mov -vf scale=1280:720 -r 25 -c:v libx264 -preset fast -crf 23 out.mp4

- Check disk space and permissions.

Problem: audio sync or playback issues in concatenated file

- Ensure all source clips have consistent framerate and timebase. Try re-encoding with -vsync 2 -async 1 or use ffmpeg concat filter if more control needed.

Problem: large temporary disk usage

- Ensure enough free space. Consider streaming approaches or lower‑quality intermediate settings to reduce size.

Problem: Windows path quoting issues

- Wrap paths containing spaces in quotes. Use forward slashes or escape backslashes.

## Performance & best practices

- CPU & I/O bound: transcoding is CPU intensive; use machines with modern CPUs for faster results.
- Parallel transcoding: the script transcodes sequentially. For many files, consider parallelizing transcoding per source file (careful with disk I/O and CPU saturation).
- Batch size: if memory/disk are limited, transcode and concatenate in batches (concatenate group outputs later).
- Preserve originals: keep originals unchanged; the script writes intermediates to temp dir and deletes them after producing the final file.

## Recommended improvements (developer notes)

- Add progress reporting and per‑file ffmpeg stderr logging to a logfile.
- Add options for:
  - audio codec (--audio-codec), audio bitrate, and sample rate
  - container format (mp4/mkv)
  - in-place ordering (use playlist file to preserve custom order)
  - recursive search and file filtering patterns (globs)
  - parallel transcoding with a configurable worker pool
  - dry-run mode to show what would be done without running ffmpeg
- Add error handling:
  - retry on transient ffmpeg failures
  - more robust cleanup on keyboard interrupt
- Replace concat demuxer with concat filter if you need to concatenate sources with different parameters without transcoding each file (more complex).
- Emit sidecar manifest with source file list, timestamps, and ffmpeg commandlines for provenance.
