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
video-concatenator.py

Search a directory for video files, transcode them to a standard resolution
and framerate, and concatenate them into a single output file.

Supported input formats: MP4, AVI, MKV, MOV, WMV.
Requires ffmpeg to be installed and on the system PATH.

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
    python video-concatenator.py <input_directory> <output_file> [options]

Options:
    -r, --resolution <WxH>   Output resolution (default: 640x480)
    -f, --framerate <N>      Output framerate in fps (default: 30)
    -c, --codec <name>       Output video codec (default: libx264)

Example:
    python video-concatenator.py ./clips output.mp4
    python video-concatenator.py ./clips output.mp4 -r 1920x1080 -f 24

-------------------------------------------------------------------------------
REQUIREMENTS
-------------------------------------------------------------------------------
- Python 3.x
- ffmpeg (must be installed and available on the system PATH)

-------------------------------------------------------------------------------
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil

# Supported video file extensions
VIDEO_EXTS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv')


def get_video_files(directory):
    """Return a sorted list of video files in the directory."""
    files = [os.path.join(directory, f) for f in os.listdir(directory)
             if f.lower().endswith(VIDEO_EXTS)]
    files.sort()
    return files


def transcode_video(input_file, output_file, resolution="640x480", framerate=30, codec="libx264"):
    """Transcode a video file to the specified resolution, framerate, and codec using ffmpeg."""
    cmd = [
        'ffmpeg', '-y', '-i', input_file,
        '-vf', f'scale={resolution}',
        '-r', str(framerate),
        '-c:v', codec,
        '-preset', 'fast', '-crf', '23',
        output_file,
    ]
    print(f"Transcoding {input_file} -> {output_file}")
    subprocess.run(cmd, check=True)


def concatenate_videos(video_files, output_file):
    """Concatenate transcoded video files into a single output file using ffmpeg."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as list_file:
        for vf in video_files:
            list_file.write(f"file '{vf}'\n")
        list_filename = list_file.name
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', list_filename,
        '-c', 'copy',
        output_file,
    ]
    print(f"Concatenating videos into {output_file}")
    subprocess.run(cmd, check=True)
    os.remove(list_filename)


def parse_args():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Transcode and concatenate video files in a directory."
    )
    parser.add_argument('input_directory', help='Directory containing video files')
    parser.add_argument('output_file', help='Output concatenated video file')
    parser.add_argument('-r', '--resolution', default='640x480',
                        help='Output resolution (default: 640x480)')
    parser.add_argument('-f', '--framerate', type=int, default=30,
                        help='Output framerate in fps (default: 30)')
    parser.add_argument('-c', '--codec', default='libx264',
                        help='Output video codec (default: libx264)')
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isdir(args.input_directory):
        print(f"Error: Input directory '{args.input_directory}' does not exist.")
        sys.exit(1)

    video_files = get_video_files(args.input_directory)
    if not video_files:
        print("No supported video files found in the input directory.")
        sys.exit(1)
    print(f"Found {len(video_files)} video file(s) to process.")

    temp_dir = tempfile.mkdtemp(prefix='transcoded_videos_')
    transcoded_files = []
    try:
        for idx, vf in enumerate(video_files):
            temp_out = os.path.join(temp_dir, f"video_{idx:03d}.mp4")
            transcode_video(vf, temp_out, args.resolution, args.framerate, args.codec)
            transcoded_files.append(temp_out)
        concatenate_videos(transcoded_files, args.output_file)
        print(f"Done. Output saved to '{args.output_file}'.")
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()