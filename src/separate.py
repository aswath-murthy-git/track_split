import os
import sys
import shutil
import glob
import logging
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


# -----------------------------
# Directory helpers
# -----------------------------
def create_directory(path):
    os.makedirs(path, exist_ok=True)


# -----------------------------
# Banner 
# -----------------------------
def print_banner(text):
    # Royal color scheme: purple text with silver borders
    SILVER = "\033[38;5;250m"  # borders
    PURPLE = "\033[38;5;93m"   # text
    RESET = "\033[0m"

    border = "=" * (len(text) + 12)
    print(f"{SILVER}{border}{RESET}")
    print(f"{SILVER}===== {PURPLE}{text}{SILVER} ====={RESET}")
    print(f"{SILVER}{border}{RESET}\n")


# -----------------------------
# Separation methods
# -----------------------------
def separate_with_spleeter(input_path, temp_path):
    from spleeter.separator import Separator
    separator = Separator("spleeter:2stems")
    separator.separate_to_file(input_path, temp_path)
    logging.info("Spleeter completed separation.")


def separate_with_demucs(input_path, temp_path):
    import demucs.separate
    args = [
        "--two-stems",
        "vocals",
        "--out",
        temp_path,
        input_path
    ]
    demucs.separate.main(args)
    logging.info("Demucs completed separation.")


# -----------------------------
# Move output files
# -----------------------------
def move_outputs(temp_path, vocals_path, karaoke_path, base_name):
    lvl1 = [f for f in os.listdir(temp_path)
            if os.path.isdir(os.path.join(temp_path, f))]

    if not lvl1:
        logging.error("No folders in temp directory.")
        sys.exit(1)

    demucs_root = os.path.join(temp_path, lvl1[0])

    lvl2 = [f for f in os.listdir(demucs_root)
            if os.path.isdir(os.path.join(demucs_root, f))]

    if not lvl2:
        logging.error("No song folder inside Demucs output.")
        sys.exit(1)

    song_folder = os.path.join(demucs_root, lvl2[0])

    wav_files = glob.glob(os.path.join(song_folder, "*.wav"))

    vocals = next((f for f in wav_files if "vocals" in f), None)
    karaoke = next((f for f in wav_files if "accompaniment" in f or "no_vocals" in f), None)

    if not vocals or not karaoke:
        logging.error("Vocals or Karaoke .wav file missing.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    vocals_out = os.path.join(vocals_path, f"{base_name}_vocals_{timestamp}.wav")
    karaoke_out = os.path.join(karaoke_path, f"{base_name}_karaoke_{timestamp}.wav")

    shutil.move(vocals, vocals_out)
    shutil.move(karaoke, karaoke_out)

    logging.info(f"Saved vocals: {vocals_out}")
    logging.info(f"Saved karaoke: {karaoke_out}")


# -----------------------------
# New function for web app
# -----------------------------
def separate_audio(input_path, method="demucs", quality="high"):
    """
    Separate audio file into vocals and karaoke (instrumental)
    
    Args:
        input_path: Full path to the input audio file
        method: "demucs" or "spleeter"
        quality: "high" (WAV 44.1kHz) or "low" (MP3 128kbps 22kHz)
    
    Returns:
        tuple: (vocals_path, karaoke_path) of the output files
    """
    temp_path = os.path.join(BASE_DIR, "temp")
    vocals_path = os.path.join(BASE_DIR, "output", "vocals")
    karaoke_path = os.path.join(BASE_DIR, "output", "karaoke")

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    create_directory(temp_path)
    create_directory(vocals_path)
    create_directory(karaoke_path)

    try:
        if method.lower() == "spleeter":
            separate_with_spleeter(input_path, temp_path)
        else:
            separate_with_demucs(input_path, temp_path)

        move_outputs(temp_path, vocals_path, karaoke_path, base_name)
        
        # Get the paths to the output files
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        vocals_file = os.path.join(vocals_path, f"{base_name}_vocals_{timestamp}.wav")
        karaoke_file = os.path.join(karaoke_path, f"{base_name}_karaoke_{timestamp}.wav")
        
        # Convert to lower quality if requested (for guest users)
        if quality == "low":
            vocals_file = convert_to_low_quality(vocals_file)
            karaoke_file = convert_to_low_quality(karaoke_file)
        
        return vocals_file, karaoke_file

    finally:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
            logging.info("Temporary files cleaned up.")


def convert_to_low_quality(wav_file):
    """
    Convert high-quality WAV to low-quality MP3 (for guest users)
    
    Args:
        wav_file: Path to WAV file
    
    Returns:
        Path to MP3 file
    """
    try:
        from pydub import AudioSegment
        
        # Load WAV file
        audio = AudioSegment.from_wav(wav_file)
        
        # Downsample to 22kHz and convert to mono for lower quality
        audio = audio.set_frame_rate(22050)
        audio = audio.set_channels(1)
        
        # Create MP3 filename
        mp3_file = wav_file.replace('.wav', '.mp3')
        
        # Export as MP3 with low bitrate
        audio.export(
            mp3_file,
            format='mp3',
            bitrate='128k',
            parameters=["-ar", "22050"]
        )
        
        # Remove original WAV file to save space
        os.remove(wav_file)
        
        logging.info(f"Converted to low quality: {mp3_file}")
        return mp3_file
        
    except ImportError:
        logging.warning("pydub not available, keeping WAV format")
        return wav_file
    except Exception as e:
        logging.error(f"Error converting to low quality: {e}")
        return wav_file


# -----------------------------
# Main program (for CLI usage)
# -----------------------------
def main():
    title = "Track Separator"
    print_banner(title)

    # Ask user for file name
    file_name = input("File name (without extension): ").strip()
    if not file_name:
        logging.error("File name cannot be empty.")
        sys.exit(1)
    print_banner(file_name)

    # Ask user for method with partial matching
    method_input = input("Separation method (demucs/spleeter): ").strip().lower()
    methods = ["demucs", "spleeter"]
    matches = [m for m in methods if m.startswith(method_input)]
    if len(matches) == 1:
        method = matches[0]
    elif len(matches) > 1:
        print(f"[ERROR] Ambiguous input: {method_input}. Matches: {matches}")
        logging.error(f"Ambiguous separation method: {method_input}")
        sys.exit(1)
    else:
        print(f"[ERROR] Invalid method: {method_input}")
        logging.error(f"Invalid separation method: {method_input}")
        sys.exit(1)

    print_banner(method)

    # Look for input file with multiple supported formats
    supported_exts = ["mp3", "wav", "flac", "ogg", "m4a"]
    input_path = None
    for ext in supported_exts:
        potential_path = os.path.join(BASE_DIR, "input", f"{file_name}.{ext}")
        if os.path.exists(potential_path):
            input_path = potential_path
            break

    if not input_path:
        logging.error(f"Input file not found for: {file_name} with supported extensions {supported_exts}")
        sys.exit(1)

    # Use the separate_audio function
    separate_audio(input_path, method)


if __name__ == "__main__":
    main()