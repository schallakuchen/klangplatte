from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import pygame
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'sounds'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the pygame mixer to play sounds
pygame.mixer.init()

@app.route('/')
def index():
    categories = {}
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        category = os.path.relpath(root, app.config['UPLOAD_FOLDER'])
        categories[category] = [f for f in files if os.path.isfile(os.path.join(root, f))]
    return render_template('index.html', categories=categories)

@app.route('/play/<category>/<sound_file>')
def play_sound(category, sound_file):
    sound_path = os.path.join(app.config['UPLOAD_FOLDER'], category, sound_file)
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    category = request.form.get('category', '').strip()
    if 'file' not in request.files or category == '':
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
    os.makedirs(category_path, exist_ok=True)
    filepath = os.path.join(category_path, file.filename)
    file.save(filepath)
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

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    while True:
        command = input("Enter command (play <file-name>, quit): ").strip()
        if command.startswith("play"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                play_sound_terminal(parts[1])
            else:
                print("Please specify a file name to play.")
        elif command == "quit":
            print("Exiting.")
            break
        else:
            print("Unknown command.")
