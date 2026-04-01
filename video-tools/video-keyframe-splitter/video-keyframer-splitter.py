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
video-keyframer-splitter.py

Transcode a video file to add periodic keyframes, then split it into segments
at those keyframe boundaries. Supported input formats: MP4, AVI, MKV, MOV, WMV.
Requires ffmpeg to be installed and on the system PATH.

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
    python video-keyframer-splitter.py <input_file> <output_directory> [options]

Options:
    -r, --resolution <WxH>      Output resolution (default: 640x480)
    -f, --framerate <N>         Output framerate in fps (default: 30)
    -c, --codec <name>          Output video codec (default: libx264)
    -k, --keyframe_interval <N> Keyframe interval in seconds (default: 2)

Example:
    python video-keyframer-splitter.py interview.mp4 segments/
    python video-keyframer-splitter.py source.mov out/ -r 1920x1080 -f 25 -k 3

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

# Supported video file extensions
VIDEO_EXTS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv')

def add_keyframes(input_file, output_file, resolution, framerate, codec, keyframe_interval):
    """
    Transcodes the input video to add keyframes at the specified interval.
    """
    cmd = [
        'ffmpeg', '-y', '-i', input_file,
        '-vf', f'scale={resolution}',
        '-r', str(framerate),
        '-c:v', codec,
        '-g', str(int(framerate * keyframe_interval)),  # GOP size = framerate * interval
        '-force_key_frames', f"expr:gte(t,n_forced*{keyframe_interval})",
        '-preset', 'fast', '-crf', '23',
        output_file
    ]
    print(f"Adding keyframes every {keyframe_interval} seconds and transcoding to {output_file}...")
    subprocess.run(cmd, check=True)

def split_video_on_keyframes(input_file, output_dir, keyframe_interval):
    """
    Splits the transcoded video into segments at keyframe boundaries using
    ffmpeg's segment muxer. Uses stream copy (-c copy) since the input has
    already been transcoded to the target format in the previous step.
    """
    segment_pattern = os.path.join(output_dir, "segment_%03d.mp4")
    cmd = [
        'ffmpeg', '-y', '-i', input_file,
        '-c', 'copy',
        '-map', '0',
        '-f', 'segment',
        '-segment_time', str(keyframe_interval),
        '-reset_timestamps', '1',
        segment_pattern
    ]
    print(f"Splitting video into segments in {output_dir}...")
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Add keyframes to a video and split it into segments.")
    parser.add_argument('input_file', help='Path to input video file')
    parser.add_argument('output_directory', help='Directory to save split segments')
    parser.add_argument('-r', '--resolution', default='640x480', help='Output resolution (default: 640x480)')
    parser.add_argument('-f', '--framerate', type=int, default=30, help='Output framerate (default: 30)')
    parser.add_argument('-c', '--codec', default='libx264', help='Output codec (default: libx264)')
    parser.add_argument('-k', '--keyframe_interval', type=float, default=2, help='Keyframe interval in seconds (default: 2)')
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    if not args.input_file.lower().endswith(VIDEO_EXTS):
        print("Error: Unsupported video file format.")
        sys.exit(1)

    os.makedirs(args.output_directory, exist_ok=True)
    temp_keyframed_file = os.path.join(args.output_directory, "keyframed_temp.mp4")
    add_keyframes(args.input_file, temp_keyframed_file, args.resolution, args.framerate, args.codec, args.keyframe_interval)
    split_video_on_keyframes(temp_keyframed_file, args.output_directory, args.keyframe_interval)

    if os.path.exists(temp_keyframed_file):
        os.remove(temp_keyframed_file)
    print("Done.")

if __name__ == "__main__":
    main()