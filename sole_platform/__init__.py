from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

def create_app():
    
    load_dotenv()  # Carga variables de entorno desde .env
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    
    # Configuraciones

    # Verificar entorno
    if os.getenv("FLASK_ENV") == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    db = MySQL(app)

    # Crear carpetas si no existen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)

    # Importar y registrar blueprints o las rutas
    from . import routes
    routes.init_app(app)

    # importar y registrar autenticación
    from . import auth
    auth.auth_init_app(app, db)

    auth.db = db  # Asignar la instancia de db al blueprint de autenticación 
    app.db = db  # Asignar la instancia de db a la aplicación principal

    return app