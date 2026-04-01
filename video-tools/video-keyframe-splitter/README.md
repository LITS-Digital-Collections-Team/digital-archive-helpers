# video-keyframer-splitter — User manual & guide

- Quick summary
- Prerequisites
- Installation
- Command syntax & options
- Examples
- How it works (detailed)
- Recommended ffmpeg options and caveats
- Temporary files & cleanup
- Troubleshooting & common problems
- Performance & best practices
- Developer roadmap / recommended improvements

## Quick summary

- Input: single video file (MP4, AVI, MKV, MOV, WMV).
- Action: transcode to add periodic keyframes (GOP + forced keyframes) and split into per‑keyframe segments.
- Output: a directory of numbered segments (segment_000.mp4, segment_001.mp4, ...).
- Configurable: resolution (-r), framerate (-f), video codec (-c), and keyframe interval in seconds (-k).

## Prerequisites

- Python 3.6+
- ffmpeg installed and available on PATH
  - Debian/Ubuntu: sudo apt-get install ffmpeg
  - macOS (Homebrew): brew install ffmpeg
  - Windows: install from ffmpeg.org and add to PATH
- Sufficient disk space for transcoded temporary files and final segments.

## Installation / placement

Place the script in your working project folder:

- /home/sysop/work/code/video-tools/video-keyframer-splitter.py

Make it executable or run via Python:

- python video-keyframer-splitter.py input.mp4 output_dir

## Command syntax & options

Usage:

python video-keyframer-splitter.py \<input_file\> \<output_directory\> \[options\]

Positional arguments:

- input_file — path to source video file.
- output_directory — directory where segment files will be saved.

Options:

- -r, --resolution
  - Output resolution (default: 640x480). Example: 1920x1080
- -f, --framerate
  - Output framerate (default: 30). Example: 25
- -c, --codec
  - Output codec (default: libx264). Example: libx264, libx265
- -k, --keyframe_interval
  - Add a keyframe at this interval in seconds (default: 2)
- -h, --help
  - Show help and exit

Notes

- The script checks input extension against supported list (.mp4, .avi, .mkv, .mov, .wmv) and will exit on unsupported types.
- Output files are written as MP4 segments by default (segment\_%03d.mp4).

## Examples

1.  Basic run (default settings)

python video-keyframer-splitter.py interview.mp4 segments/

Creates transcoded keyframed temp file in segments/ and splits into segments/segment_000.mp4, etc.

2.  Full HD, 25 fps, 3s keyframes

python video-keyframer-splitter.py source.mov output_segments/ -r 1920x1080 -f 25 -k 3

3.  Use HEVC (note playback compatibility)

python video-keyframer-splitter.py raw_clip.mkv out/ -c libx265 -r 1280x720

## How it works — detailed flow

1.  Validate input file exists and extension is supported.
2.  Construct a temporary output filename: \<output_dir\>/keyframed_temp.mp4. (Ensure output dir exists or create it.)
3.  add_keyframes():
    - Calls ffmpeg to transcode the input with:
      - scale filter: -vf scale=\<resolution\>
      - framerate: -r \<framerate\>
      - GOP size: -g \<framerate \* keyframe_interval\> (ensures fixed group-of-pictures size)
      - forced keyframes: -force_key_frames expr:gte(t,n_forced\*\<interval\>) (requests keyframes every interval seconds)
      - codec and quality: -c:v \<codec\> -preset fast -crf 23
    - Result: a single file with regular keyframes at or near the requested interval.
4.  split_video_on_keyframes():
    - Uses ffmpeg segment muxer with -f segment -segment_time <keyframe_interval> -reset_timestamps 1 and -c copy (stream copy — no re-encode) to split the already-transcoded temp file into segments.
    - Because keyframes were inserted at the requested interval, the segmenter cuts cleanly at each keyframe boundary.
5.  Remove the temporary keyframed file when processing completes.

Why two steps?

- The segmenter needs accessible keyframes to produce clean GOP‑aligned segments. Re‑encoding to regular keyframes ensures consistent, predictable cut points.

## Recommended ffmpeg settings & caveats

- GOP size vs keyframe forcing:
  - GOP (-g) sets maximum distance between keyframes. -force_key_frames ensures keyframes at exact time intervals (useful for consistent splitting).
- Quality / speed:
  - -crf 23 and -preset fast balance quality and speed. Use lower CRF (18–20) for higher quality or slower preset for better compression.
- Audio:
  - The script leaves audio codec selection to ffmpeg defaults. For consistent audio behavior, add -c:a aac -b:a 128k or similar.
- Segment muxer behavior:
  - The script uses -c copy (stream copy) at the split step since the temp file is already transcoded to the target format. Segment boundaries align to keyframes; segment length equals the keyframe interval.
- Container compatibility:
  - MP4 is broadly compatible. If you use libx265, ensure target players support HEVC.

## Temporary files & cleanup

- Temporary keyframed file: \<output_dir\>/keyframed_temp.mp4.
- The script deletes the temp file on success. If the script is interrupted, temp files may remain—remove them manually.
- For robust operations, consider running in a wrapper that cleans up on failure or writes temp files to a dedicated tmpfs.

## Troubleshooting & common problems

ffmpeg not found

- Ensure ffmpeg is installed and on PATH. Test: ffmpeg -version.

Unsupported file type

- Rename or transcode to a supported container (MP4/MKV) or extend script's VIDEO_EXTS.

ffmpeg errors during transcoding

- Run the same ffmpeg command printed by the script (or capture stderr) to see precise ffmpeg error cause. Check disk space and input file integrity.

Segments missing or zero length

- Confirm keyframes were actually inserted. Re-run with a shorter keyframe interval or inspect temp file with ffprobe.

Audio out of sync after splitting

- Audio/timebase mismatches can occur. Try adding -vsync 2 -async 1 to transcoding step or use ffmpeg concat filter for finer control.

Large temporary disk usage

- Transcoding creates full‑size temp files. Ensure free disk space or transcode at lower bitrate/crf.

Permissions errors writing output_dir

- Create output dir and ensure user has write permission: mkdir -p output_dir && chmod u+w output_dir.

## Performance & best practices

- Transcoding is CPU bound. Use multi‑core machines or schedule late‑night runs.
- Sequential processing keeps resource usage predictable. For many files, consider parallelizing across independent nodes or containerized workers.
- Keep originals unchanged and store segments alongside provenance (source filename, timestamp, keyframe interval) for audits.

## Developer roadmap / recommended improvements

- Add CLI improvements:
  - Provide --audio-codec, --audio-bitrate, --container flags.
  - Verbose / dry‑run flags and a --no-cleanup option.
- Improve robustness:
  - Capture ffmpeg stderr to log files for each step.
  - Retry logic for transient failures.
  - Atomic tempdir creation and guaranteed cleanup on KeyboardInterrupt (try/finally).
- Add options for splitting:
  - Fixed‑time segmentation, concat filter fallback, or HLS output.
- Add unit tests covering ffmpeg command generation and path handling.
- Emit sidecar JSON manifest with:
  - source file, input MD5/SHA1, ffmpeg commandline, segment list, timestamp.
- Consider a streaming approach for extremely large inputs to reduce temp file footprint.
