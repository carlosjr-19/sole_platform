import os
from flask import current_app

def limpiar_storage():
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    print(f"Limpiando carpeta: {UPLOAD_FOLDER}")
    for f in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Eliminado archivo: {file_path}")

def limpiar_downloads():
    DOWNLOAD_FOLDER = current_app.config['DOWNLOAD_FOLDER']
    print(f"Limpiando carpeta: {DOWNLOAD_FOLDER}")
    for f in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Eliminado archivo: {file_path}")