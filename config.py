import os

# Directorio raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto")

    # Rutas personalizadas
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'sole_platform', 'static', 'storage')
    DOWNLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'sole_platform', 'static', 'downloads')
    IMAGES_FOLDER = os.path.join(PROJECT_ROOT, 'sole_platform', 'static', 'img')

