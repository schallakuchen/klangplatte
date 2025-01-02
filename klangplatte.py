from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
import os
import pygame
import threading
from mutagen.mp3 import MP3
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'sounds'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB size limit
app.secret_key = 'supersecretkey'  # Required for flashing messages
SUPPORTED_EXTENSIONS = {'mp3', 'wav', 'ogg'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize the pygame mixer to play sounds
pygame.mixer.init()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in SUPPORTED_EXTENSIONS

@app.route('/')
def index():
    categories = {}
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        category = os.path.relpath(root, app.config['UPLOAD_FOLDER'])
        categories[category] = [f for f in files if os.path.isfile(os.path.join(root, f))]
    return render_template('index.html', categories=categories)

from flask import jsonify

@app.route('/play/<category>/<sound_file>', methods=['POST'])
def play_sound(category, sound_file):
    sound_path = os.path.join(app.config['UPLOAD_FOLDER'], category, sound_file)
    if not os.path.commonpath([os.path.abspath(app.config['UPLOAD_FOLDER']), os.path.abspath(sound_path)]) == os.path.abspath(app.config['UPLOAD_FOLDER']):
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
    if not allowed_file(file.filename):
        flash('Unsupported file type. Only MP3, WAV, and OGG are allowed.')
        return redirect(url_for('index'))

    # Secure filename and check file size
    filename = secure_filename(file.filename)
    category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
    os.makedirs(category_path, exist_ok=True)
    filepath = os.path.join(category_path, filename)
    file.save(filepath)

    # Check audio validity and length
    try:
        if filename.endswith('.mp3'):
            audio = MP3(filepath)
            length = audio.info.length
        else:
            audio = pygame.mixer.Sound(filepath)
            length = audio.get_length()

        if length > 10:
            os.remove(filepath)
            flash('File is too long. Maximum allowed duration is 10 seconds.')
            logging.warning(f"Rejected file '{filename}' in category '{category}' due to length.")
            return redirect(url_for('index'))

    except Exception as e:
        os.remove(filepath)
        flash(f'Invalid audio file: {e}')
        logging.error(f"Error processing file '{filename}' in category '{category}': {e}")
        return redirect(url_for('index'))

    flash('File uploaded successfully!')
    logging.info(f"File uploaded successfully: {filename} in category {category}")
    return redirect(url_for('index'))

@app.route('/sounds/<path:filename>')
def serve_sound(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def run_server():
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

def play_sound_terminal(file_name):
    for root, _, files in os.walk(app.config['UPLOAD_FOLDER']):
        if file_name in files:
            sound_path = os.path.join(root, file_name)
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            print(f"Playing {file_name}.")
            return
    print(f"Sound file {file_name} does not exist.")

def delete_file(category, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {filename}")
        logging.info(f"Deleted file: {filename} in category {category}")
    else:
        print(f"File {filename} does not exist in category {category}.")
        logging.warning(f"Attempt to delete nonexistent file: {filename} in category {category}")

def delete_category(category):
    category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
    if os.path.exists(category_path) and os.path.isdir(category_path):
        confirm = input(f"Are you sure you want to delete the entire category '{category}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            for root, dirs, files in os.walk(category_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(category_path)
            print(f"Deleted category: {category}")
            logging.info(f"Deleted category: {category}")
        else:
            print("Deletion cancelled.")
            logging.info(f"Deletion cancelled for category: {category}")
    else:
        print(f"Category {category} does not exist.")
        logging.warning(f"Attempt to delete nonexistent category: {category}")

def list_all():
    print("Available categories and sounds:")
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        category = os.path.relpath(root, app.config['UPLOAD_FOLDER'])
        if files:
            print(f"Category: {category}")
            for file in files:
                print(f"  - {file}")

def list_category(category):
    category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
    if os.path.exists(category_path) and os.path.isdir(category_path):
        files = os.listdir(category_path)
        if files:
            print(f"Sounds in category '{category}':")
            for file in files:
                print(f"  - {file}")
        else:
            print(f"No sounds found in category '{category}'.")
    else:
        print(f"Category '{category}' does not exist.")

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    while True:
        command = input("Enter command (play <file-name>, delete <category>/<filename>, delete <category>, list, list <category>, quit): ").strip()
        if command.startswith("play"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                play_sound_terminal(parts[1])
            else:
                print("Please specify a file name to play.")
        elif command.startswith("delete"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                target = parts[1]
                if "/" in target:
                    category, filename = target.split("/", 1)
                    delete_file(category, filename)
                else:
                    delete_category(target)
            else:
                print("Please specify a file or category to delete.")
        elif command == "list":
            list_all()
        elif command.startswith("list"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                list_category(parts[1])
            else:
                print("Please specify a category to list.")
        elif command == "quit":
            print("Exiting.")
            break
        else:
            print("Unknown command.")
