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

'''

This python script searches a directory for audio files and concatenates them into a single audio file. 

It uses the pydub library to handle audio file manipulation. 

Usage:
    python audio-track-concatenator.py <input_directory> <output_file>

Where:
    <input_directory> is the path to the directory containing audio files to concatenate.
    <output_file> is the path to the output file where the concatenated audio will be saved.
'''

import os
import sys
from pydub import AudioSegment

def get_audio_files(directory):
    """
    Searches the given directory for audio files.
    Returns a sorted list of file paths for supported audio formats.
    """
    # Supported audio file extensions
    supported_exts = ('.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a')
    audio_files = []
    for fname in os.listdir(directory):
        if fname.lower().endswith(supported_exts):
            audio_files.append(os.path.join(directory, fname))
    # Sort files alphabetically for predictable concatenation order
    audio_files.sort()
    return audio_files

def concatenate_audio(files):
    """
    Concatenates a list of audio files into a single AudioSegment.
    Returns the concatenated AudioSegment.
    """
    if not files:
        raise ValueError("No audio files found to concatenate.")
    # Load the first audio file
    print(f"Loading first audio file: {files[0]}")
    combined = AudioSegment.from_file(files[0])
    # Append each subsequent audio file
    for f in files[1:]:
        print(f"Appending audio file: {f}")
        segment = AudioSegment.from_file(f)
        combined += segment
    return combined

def main():
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python audio-track-concatenator.py <input_directory> <output_file>")
        sys.exit(1)
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    print(f"Searching for audio files in directory: {input_dir}")
    audio_files = get_audio_files(input_dir)
    print(f"Found {len(audio_files)} audio file(s).")

    if not audio_files:
        print("No supported audio files found in the input directory.")
        sys.exit(1)

    print("Concatenating audio files...")
    combined_audio = concatenate_audio(audio_files)

    # Determine output format from file extension
    output_ext = os.path.splitext(output_file)[1][1:].lower()
    if output_ext not in ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']:
        print(f"Warning: Output file extension '{output_ext}' may not be supported. Defaulting to 'mp3'.")
        output_ext = 'mp3'

    print(f"Exporting concatenated audio to: {output_file}")
    combined_audio.export(output_file, format=output_ext)
    print("Audio concatenation complete.")

if __name__ == "__main__":
    main()
