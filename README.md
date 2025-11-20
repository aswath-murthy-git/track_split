# Track Splitter

Simple terminal-based audio separation tool that splits songs into vocals and instrumentals (karaoke) using AI.

## Features

- 🎵 Separates vocals from instrumentals (karaoke)
- 🖥️ Simple terminal interface
- 🎯 Single-purpose, focused tool
- 🚀 Fast and efficient
- 📁 Organized output

## Installation

### 1. Install Python 3.8+

Make sure you have Python 3.8 or higher installed.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install demucs torch torchaudio
```

### 3. Install ffmpeg (Required)

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Usage

### 1. Place audio files

Put your audio files (MP3, WAV, FLAC, OGG, M4A) in the `input` folder.

### 2. Run the program

```bash
python track_split.py
```

### 3. Select file

Choose a file from the numbered list.

### 4. Wait

Processing takes 1-3 minutes per song.

### 5. Get results

Find separated files in:
- `output/vocals/` - Vocal tracks
- `output/karaoke/` - karaoke tracks

## Example

```
$ python track_split.py

╔════════════════════════════════════════╗
║         TRACK SPLITTER v1.0            ║
║    AI-Powered Audio Separation         ║
╚════════════════════════════════════════╝

ℹ Checking dependencies...
✓ All dependencies installed
✓ Directories ready

Available audio files:

  1. my_song_1.mp3 (8.5 MB)
  2. my_song_2.wav (45.2 MB)

  0. Exit

Select file (1-2) or 0 to exit: 1

Processing: my_song.mp3

ℹ This may take 1-3 minutes depending on file length...

[Progress bar appears here]

✓ Vocals saved: my_song_vocals_timestamp.wav
✓ Instrumental (karaoke) saved: my_song_karaoke_timestamp.wav

✓ Separation complete!
ℹ Output files saved in 'output' folder

Process another file? (y/n): n
ℹ Goodbye!
```

## Folder Structure

```
track_split/
├── track_split.py          # Main program
├── requirements.txt        # Dependencies
├── README.md              # This file
├── input/                 # Place audio files here
└── output/
    ├── vocals/           # Separated vocals
    └── karaoke/          # Separated instrumentals
```

## Output Format

- **Format:** WAV (uncompressed)
- **Sample Rate:** 44.1 kHz
- **Bit Depth:** 16-bit
- **Channels:** Stereo

## Troubleshooting

### "No module named 'demucs'"
```bash
pip install demucs
```

### "ffmpeg not found"
Install ffmpeg (see Installation section)

### "Out of memory"
Try processing shorter files or close other applications

### Slow processing
Normal on CPU. Processing takes 1-3 minutes per 3-minute song.

## Technical Details

- **AI Model:** Demucs (Facebook Research)
- **Algorithm:** Hybrid Transformer model
- **Quality:** Professional-grade separation
- **Speed:** ~1-2 minutes per song (CPU)

## License

MIT License

## Credits

- Audio separation: Demucs by Facebook Research
- Created for simple, focused audio processing

## Support

For issues or questions, check:
- Demucs documentation: https://github.com/facebookresearch/demucs
- ffmpeg documentation: https://ffmpeg.org/documentation.html