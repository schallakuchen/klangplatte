# klangplatte/config.py

class Config:
    UPLOAD_FOLDER = 'sounds'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB limit
    SECRET_KEY = 'supersecretkey'
    SUPPORTED_EXTENSIONS = {'mp3', 'wav', 'ogg'}
    FFMPEG_PATH = r'audio\ffmpeg\bin\ffmpeg.exe'
    FFPROBE_PATH = r'audio\ffmpeg\bin\ffprobe.exe'