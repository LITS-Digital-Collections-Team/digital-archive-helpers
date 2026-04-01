# video-tools

A collection of Python scripts for processing and manipulating video files. All scripts require [ffmpeg](https://ffmpeg.org/) to be installed and available on the system PATH.

---

## Scripts

### [video-concatenator](video-concatenator/)

Searches a directory for video files, transcodes each one to a standard resolution and framerate, and concatenates them into a single output file.

**Inputs:** directory of video files (MP4, AVI, MKV, MOV, WMV)  
**Output:** single concatenated MP4

Key options: `-r` resolution, `-f` framerate, `-c` codec

```
python video-concatenator/video-concatenator.py <input_directory> <output_file> [options]
```

---

### [video-keyframe-splitter](video-keyframe-splitter/)

Transcodes a video file to insert periodic keyframes at a specified interval, then splits it into segments at those keyframe boundaries.

**Input:** single video file (MP4, AVI, MKV, MOV, WMV)  
**Output:** directory of numbered segment MP4s

Key options: `-r` resolution, `-f` framerate, `-c` codec, `-k` keyframe interval (seconds)

```
python video-keyframe-splitter/video-keyframer-splitter.py <input_file> <output_directory> [options]
```

---

## Requirements

- Python 3.x (standard library only)
- ffmpeg on the system PATH

| Platform | Install command |
|---|---|
| macOS (Homebrew) | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Windows | Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH |
