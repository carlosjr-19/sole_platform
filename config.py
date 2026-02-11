import os
import re

# Directorio raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto")

    # Rutas personalizadas
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'sole_platform', 'static', 'storage')
    DOWNLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'sole_platform', 'static', 'downloads')
    IMAGES_FOLDER = os.path.join(PROJECT_ROOT, 'sole_platform', 'static', 'img')

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    # Configuraciones específicas para desarrollo
    # Ejemplo: Base de datos SQLite para desarrollo
    MYSQL_HOST = os.getenv("MYSQLHOST")
    MYSQL_USER = os.getenv("MYSQLUSER")
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD")
    MYSQL_DB = os.getenv("MYSQLDB")

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    MYSQL_HOST = os.getenv("MYSQLHOST")  # O el nombre que Railway te da
    MYSQL_USER = os.getenv("MYSQLUSER")
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD")
    MYSQL_DB = os.getenv("MYSQLDATABASE")
    MYSQL_PORT = int(os.getenv("MYSQLPORT", 3306))
    
    # En Railway, usar /tmp para archivos temporales si es necesario
    if os.getenv("RAILWAY_ENVIRONMENT"):
        DOWNLOAD_FOLDER = "/tmp"
        UPLOAD_FOLDER = "/tmp"

