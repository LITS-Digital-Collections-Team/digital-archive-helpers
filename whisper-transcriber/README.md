# whisper-transcriber

Transcribes an audio file to text using OpenAI's [Whisper](https://github.com/openai/whisper) speech recognition model. If the input file exceeds 25 MB, it is automatically split into chunks, each chunk is transcribed, and the results are joined into a single output file.

---

## Usage

```
python whisper-transcriber.py --input <input_file> --output <output_file> [--model <model>]
```

### Options

| Flag | Required | Default | Description |
|---|---|---|---|
| `--input` | yes | — | Path to the input audio file |
| `--output` | yes | — | Path to write the transcript text file |
| `--model` | no | `medium` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large` |

---

## Examples

Transcribe with default model (medium):

```
python whisper-transcriber.py --input interview.mp3 --output transcript.txt
```

Transcribe with the small model (faster, less accurate):

```
python whisper-transcriber.py --input recording.wav --output out.txt --model small
```

---

## How it works

1. Checks that the input file exists.
2. If the file is larger than 25 MB, splits it into time-proportional WAV chunks using pydub. Otherwise uses the file as-is.
3. Loads the selected Whisper model. The model is downloaded automatically on first use and cached locally.
4. Transcribes each chunk with `language="en"` (English).
5. Joins the chunk transcripts with newlines and writes to the output file.
6. Deletes any temporary chunk files.

> **Model selection:** `tiny` and `base` are fastest but least accurate. `medium` (default) is a good general-purpose choice. `large` is most accurate but slow on CPU. Whisper automatically uses GPU (MPS on Apple Silicon, CUDA on supported NVIDIA GPUs) if available.

---

## Requirements

- Python 3.x
- `openai-whisper` — `pip install openai-whisper`
- `pydub` — `pip install pydub`
- ffmpeg (required by pydub for non-WAV formats; must be on the system PATH)

### Installing ffmpeg

| Platform | Command |
|---|---|
| macOS (Homebrew) | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| Windows | Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH |

> **Note:** WAV files can be processed without ffmpeg. Other formats (MP3, M4A, FLAC, etc.) require ffmpeg to be installed.

---

## License

GNU General Public License v3.0 — see source file header for full terms.
