# klangplatte/audio/normalization.py
import os
from pydub import AudioSegment
from klangplatte.config import Config

# Calculate absolute path to ffmpeg based on the config setting.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ffmpeg_abs_path = os.path.join(project_root, Config.FFMPEG_PATH)
AudioSegment.converter = ffmpeg_abs_path

TARGET_DBFS = -20.0


def normalize_file(filepath: str, overwrite: bool = True) -> str:
    # Compute and log the absolute path to the audio file.
    abs_filepath = os.path.abspath(filepath)
    print("Attempting to normalize file at:", abs_filepath)

    # Check whether the file exists.
    if not os.path.exists(abs_filepath):
        print("DEBUG ERROR: Audio file not found at", abs_filepath)
        return ""

    try:
        # Attempt to load the audio file. This internally calls ffmpeg.
        sound = AudioSegment.from_file(filepath)
        change_in_dBFS = TARGET_DBFS - sound.dBFS
        normalized_sound = sound.apply_gain(change_in_dBFS)

        output_path = filepath if overwrite else filepath.replace(".", "_normalized.", 1)
        ext = os.path.splitext(output_path)[1][1:]
        normalized_sound.export(output_path, format=ext)
        print("Normalization successful. Output file:", os.path.abspath(output_path))
        return output_path
    except Exception as e:
        print(f"Error normalizing {filepath}: {e}")
        return ""


def normalize_folder(folder_path: str, overwrite: bool = True):
    supported_extensions = (".mp3", ".wav", ".ogg", ".flac", ".m4a")
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_extensions):
            filepath = os.path.join(folder_path, filename)
            result_path = normalize_file(filepath, overwrite)
            if result_path:
                print(f"✅ Normalized: {result_path}")
