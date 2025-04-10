# main.py

# Use Python 3.11

import threading
from klangplatte import create_app
from klangplatte.audio.playback import play_sound_terminal
from klangplatte.utils.file_helpers import delete_file, delete_category, list_all, list_category

app = create_app()


def run_server():
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == '__main__':
    # Start Flask server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    upload_folder = app.config['UPLOAD_FOLDER']

    while True:
        command = input(
            "Enter command (play <file-name>, delete <category>/<filename>, delete <category>, list, list <category>, quit): ").strip()
        if command.startswith("play"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                play_sound_terminal(upload_folder, parts[1])
            else:
                print("Please specify a file name to play.")
        elif command.startswith("delete"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                target = parts[1]
                if "/" in target:
                    category, filename = target.split("/", 1)
                    delete_file(upload_folder, category, filename)
                else:
                    delete_category(upload_folder, target)
            else:
                print("Please specify a file or category to delete.")
        elif command == "list":
            list_all(upload_folder)
        elif command.startswith("list"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                list_category(upload_folder, parts[1])
            else:
                print("Please specify a category to list.")
        elif command == "quit":
            print("Exiting.")
            break
        else:
            print("Unknown command.")
