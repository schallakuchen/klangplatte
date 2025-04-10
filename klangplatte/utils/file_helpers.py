# klangplatte/utils/file_helpers.py
import os
from werkzeug.utils import secure_filename

def allowed_file(filename: str, supported_extensions: set) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in supported_extensions

def delete_file(upload_folder: str, category: str, filename: str):
    file_path = os.path.join(upload_folder, category, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {filename}")
    else:
        print(f"File {filename} does not exist in category {category}.")

def delete_category(upload_folder: str, category: str):
    category_path = os.path.join(upload_folder, category)
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
        else:
            print("Deletion cancelled.")
    else:
        print(f"Category {category} does not exist.")

def list_all(upload_folder: str):
    print("Available categories and sounds:")
    for root, dirs, files in os.walk(upload_folder):
        category = os.path.relpath(root, upload_folder)
        if files:
            print(f"Category: {category}")
            for file in files:
                print(f"  - {file}")

def list_category(upload_folder: str, category: str):
    category_path = os.path.join(upload_folder, category)
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
