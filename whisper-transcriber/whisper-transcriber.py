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
whisper-transcriber.py

Transcribes an audio file to text using OpenAI's Whisper model.
If the input file exceeds 25 MB, it is split into smaller chunks for
processing and the results are concatenated into a single transcript.

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
    python whisper-transcriber.py --input <input_file> --output <output_file> [--model <model>]

Options:
    --input <path>   Path to input audio file (required)
    --output <path>  Path to output text file (required)
    --model <name>   Whisper model size: tiny, base, small, medium, large
                     (default: medium)

Example:
    python whisper-transcriber.py --input interview.mp3 --output transcript.txt
    python whisper-transcriber.py --input recording.wav --output out.txt --model small

-------------------------------------------------------------------------------
REQUIREMENTS
-------------------------------------------------------------------------------
- Python 3.x
- openai-whisper  (pip install openai-whisper)
- pydub           (pip install pydub)
- ffmpeg          (must be installed and available on the system PATH)

-------------------------------------------------------------------------------
"""

import argparse
import os
import sys
import tempfile
import time

# Try importing whisper, exit with a message if not installed
try:
    import whisper
except ImportError:
    print("Error: The 'whisper' package is required. Install with 'pip install openai-whisper'.")
    sys.exit(1)

# Import AudioSegment from pydub for audio manipulation
from pydub import AudioSegment

# Maximum chunk size in megabytes for splitting large audio files
MAX_SIZE_MB = 25

def split_audio(input_path, chunk_size_mb=MAX_SIZE_MB):
    """
    Splits the input audio file into smaller chunks if it exceeds chunk_size_mb.
    Returns a list of file paths to the chunks (or the original file if no splitting needed).
    """
    print(f"Analyzing audio file size for splitting: {input_path}")
    audio = AudioSegment.from_file(input_path)
    total_size = os.path.getsize(input_path) / (1024 * 1024)
    print(f"Audio file size: {total_size:.2f} MB")
    if total_size <= chunk_size_mb:
        print("No splitting needed.")
        return [input_path]
    print(f"Splitting audio into chunks of up to {chunk_size_mb} MB each...")
    chunk_length_ms = int(len(audio) * (chunk_size_mb / total_size))
    chunks = []
    start = 0
    idx = 0
    while start < len(audio):
        end = min(start + chunk_length_ms, len(audio))
        chunk = audio[start:end]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_path = temp_file.name
        temp_file.close()
        chunk.export(temp_path, format="wav")
        print(f"  Created chunk {idx+1}: {temp_path} ({(end-start)/1000:.2f} seconds)")
        chunks.append(temp_path)
        start = end
        idx += 1
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def transcribe_audio(model, audio_path):
    """
    Uses the Whisper model to transcribe the given audio file.
    Returns the transcribed text.
    """
    print(f"  Starting transcription for: {audio_path}")
    result = model.transcribe(audio_path, language="en")
    print(f"  Finished transcription for: {audio_path}")
    return result["text"]

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI Whisper.")
    parser.add_argument('--input', required=True, help='Path to input audio file')
    parser.add_argument('--output', required=True, help='Path to output text file')
    parser.add_argument('--model', default='medium', help='Whisper model size (tiny, base, small, medium, large)')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)

    print(f"Selected Whisper model: '{args.model}'")
    print("Loading Whisper model (this may take a moment)...")
    model = whisper.load_model(args.model)
    print("Model loaded successfully.")

    print(f"Preparing to transcribe: {args.input}")
    start_time = time.time()

    chunks = split_audio(args.input)
    print(f"Beginning transcription of {len(chunks)} chunk(s)...")

    segments = []
    for idx, chunk_path in enumerate(chunks):
        print(f"Transcribing chunk {idx+1}/{len(chunks)}: {chunk_path}")
        segments.append(transcribe_audio(model, chunk_path).strip())
        if chunk_path != args.input:
            print(f"Deleting temporary chunk file: {chunk_path}")
            os.remove(chunk_path)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(segments))

    print(f"\nTranscription complete. Output saved to '{args.output}'.")
    print(f"Total transcription runtime: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()