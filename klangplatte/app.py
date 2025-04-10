# klangplatte/app.py
import os
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from .config import Config
from .utils.file_helpers import allowed_file
from mutagen.mp3 import MP3
from .audio.normalization import normalize_file, normalize_folder
import pygame


def register_routes(app):
    @app.route('/')
    def index():
        categories = {}
        upload_folder = app.config['UPLOAD_FOLDER']
        for root, dirs, files in os.walk(upload_folder):
            category = os.path.relpath(root, upload_folder)
            categories[category] = [f for f in files if os.path.isfile(os.path.join(root, f))]
        return render_template('index.html', categories=categories)

    @app.route('/play/<category>/<sound_file>', methods=['POST'])
    def play_sound(category, sound_file):
        upload_folder = app.config['UPLOAD_FOLDER']
        sound_path = os.path.join(upload_folder, category, sound_file)
        # Security check: ensure the path is within the UPLOAD_FOLDER
        if not os.path.commonpath([os.path.abspath(upload_folder), os.path.abspath(sound_path)]) == os.path.abspath(
                upload_folder):
            return jsonify({'status': 'error', 'message': 'Invalid path.'}), 400

        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            return jsonify({'status': 'success', 'message': f"Playing '{sound_file}'."})
        else:
            return jsonify({'status': 'error', 'message': f"The sound '{sound_file}' is no longer available."}), 404

    @app.route('/upload', methods=['POST'])
    def upload_file():
        category = request.form.get('category', '').strip()
        if 'file' not in request.files or category == '':
            flash('No file selected or category specified.')
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.')
            return redirect(url_for('index'))
        if not allowed_file(file.filename, app.config['SUPPORTED_EXTENSIONS']):
            flash('Unsupported file type. Only MP3, WAV, and OGG are allowed.')
            return redirect(url_for('index'))

        filename = secure_filename(file.filename)
        upload_folder = app.config['UPLOAD_FOLDER']
        category_path = os.path.join(upload_folder, category)
        os.makedirs(category_path, exist_ok=True)
        filepath = os.path.join(category_path, filename)
        file.save(filepath)
        if not normalize_file(filepath):
            print(f"Failed to normalize file {filepath}")

        # Check audio validity and length (max 10 seconds)
        try:
            if filename.lower().endswith('.mp3'):
                audio = MP3(filepath)
                length = audio.info.length
            else:
                audio = pygame.mixer.Sound(filepath)
                length = audio.get_length()

            if length > 10:
                os.remove(filepath)
                flash('File is too long. Maximum allowed duration is 10 seconds.')
                app.logger.warning(f"Rejected file '{filename}' in category '{category}' due to length.")
                return redirect(url_for('index'))
        except Exception as e:
            os.remove(filepath)
            flash(f'Invalid audio file: {e}')
            app.logger.error(f"Error processing file '{filename}' in category '{category}': {e}")
            return redirect(url_for('index'))

        flash('File uploaded successfully!')
        app.logger.info(f"File uploaded successfully: {filename} in category {category}")
        return redirect(url_for('index'))

    @app.route('/sounds/<path:filename>')
    def serve_sound(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
