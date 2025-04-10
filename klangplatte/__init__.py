# klangplatte/__init__.py
import os
import logging
from flask import Flask
from .config import Config
import pygame


def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(Config)

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    # Initialize pygame mixer for audio playback
    pygame.mixer.init()

    # Register Flask routes
    from .app import register_routes
    register_routes(app)

    return app
