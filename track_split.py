import os
import sys
import shutil
import glob
import logging
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

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
    SILVER = "\033[38;5;250m"
    PURPLE = "\033[38;5;93m"
    RESET = "\033[0m"

    border = "=" * (len(text) + 12)
    print(f"{SILVER}{border}{RESET}")
    print(f"{SILVER}===== {PURPLE}{text}{SILVER} ====={RESET}")
    print(f"{SILVER}{border}{RESET}\n")


# -----------------------------
# File listing + selection
# -----------------------------
def list_audio_files(input_dir):
    exts = ("mp3", "wav", "flac", "ogg", "m4a")
    files = []

    for f in os.listdir(input_dir):
        if f.lower().endswith(exts):
            files.append(os.path.join(input_dir, f))

    return sorted(files)


def select_file(files):
    if not files:
        logging.error("No audio files found in input folder.")
        logging.info("Place audio files into the 'input' directory.")
        return None

    print("\nAvailable audio files:\n")
    for i, f in enumerate(files, 1):
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  {i}. {os.path.basename(f)} ({size_mb:.1f} MB)")

    print("\n  0. Exit")

    while True:
        try:
            choice = int(input("\nSelect file (number): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(files):
                return files[choice - 1]
            print("[ERROR] Invalid selection.")
        except ValueError:
            print("[ERROR] Enter a valid number.")


# -----------------------------
# Audio separation
# -----------------------------
def separate_audio_file(input_path, temp_path):
    import demucs.separate
    args = [
        "--two-stems",
        "vocals",
        "--out",
        temp_path,
        input_path
    ]
    demucs.separate.main(args)
    logging.info("Separation completed.")


# -----------------------------
# Move output files
# -----------------------------
def move_outputs(temp_path, vocals_path, karaoke_path, base_name):
    lvl1 = [f for f in os.listdir(temp_path)
            if os.path.isdir(os.path.join(temp_path, f))]

    if not lvl1:
        logging.error("No folders in temp directory.")
        sys.exit(1)

    root_folder = os.path.join(temp_path, lvl1[0])

    lvl2 = [f for f in os.listdir(root_folder)
            if os.path.isdir(os.path.join(root_folder, f))]

    if not lvl2:
        logging.error("No song folder inside output.")
        sys.exit(1)

    song_folder = os.path.join(root_folder, lvl2[0])
    wav_files = glob.glob(os.path.join(song_folder, "*.wav"))

    vocals = next((f for f in wav_files if "vocals" in f), None)
    karaoke = next((f for f in wav_files if "accompaniment" in f or "no_vocals" in f), None)

    if not vocals or not karaoke:
        logging.error("Vocals or karaoke .wav file missing.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    vocals_out = os.path.join(vocals_path, f"{base_name}_vocals_{timestamp}.wav")
    karaoke_out = os.path.join(karaoke_path, f"{base_name}_karaoke_{timestamp}.wav")

    shutil.move(vocals, vocals_out)
    shutil.move(karaoke, karaoke_out)

    logging.info(f"Saved vocals: {vocals_out}")
    logging.info(f"Saved karaoke: {karaoke_out}")


# -----------------------------
# Main separation entry point
# -----------------------------
def separate_audio(input_path):
    temp_path = os.path.join(BASE_DIR, "temp")
    vocals_path = os.path.join(BASE_DIR, "output", "vocals")
    karaoke_path = os.path.join(BASE_DIR, "output", "karaoke")

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    create_directory(temp_path)
    create_directory(vocals_path)
    create_directory(karaoke_path)

    try:
        separate_audio_file(input_path, temp_path)
        move_outputs(temp_path, vocals_path, karaoke_path, base_name)

    finally:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
            logging.info("Temporary files cleaned up.")


# -----------------------------
# Main CLI
# -----------------------------
def main():
    print_banner("Track Separator")

    input_dir = os.path.join(BASE_DIR, "input")
    create_directory(input_dir)

    files = list_audio_files(input_dir)
    selected = select_file(files)

    if not selected:
        logging.info("No file selected. Exiting.")
        sys.exit(0)

    base_name = os.path.splitext(os.path.basename(selected))[0]
    print_banner(base_name)

    logging.info("Processing audio file…")
    separate_audio(selected)


if __name__ == "__main__":
    main()
