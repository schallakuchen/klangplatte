import os
from pydub import AudioSegment
from klangplatte.config import Config

# __file__ is at klangplatte/audio/__init__.py.
# We need to go up one level to get the package root (klangplatte).
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build absolute paths using the relative paths from the config.
ffmpeg_abs_path = os.path.join(package_root, Config.FFMPEG_PATH)
ffprobe_abs_path = os.path.join(package_root, Config.FFPROBE_PATH)

# Set pydub's converter and ffprobe paths.
AudioSegment.converter = ffmpeg_abs_path
AudioSegment.ffprobe = ffprobe_abs_path

print("Using ffmpeg at:", ffmpeg_abs_path)
print("Using ffprobe at:", ffprobe_abs_path)
