# klangplatte/audio/playback.py
import os
import pygame

def play_sound_terminal(upload_folder: str, file_name: str):
    """
    Searches for and plays a sound file from the upload folder.
    """
    for root, _, files in os.walk(upload_folder):
        if file_name in files:
            sound_path = os.path.join(root, file_name)
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            print(f"Playing {file_name}.")
            return
    print(f"Sound file {file_name} does not exist.")
