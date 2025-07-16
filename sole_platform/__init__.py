from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    
    load_dotenv()  # Carga variables de entorno desde .env
    app = Flask(__name__, template_folder="templates", static_folder="static")
    # Configuraciones
    app.config.from_object('config.Config')

    # Crear carpetas si no existen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)

    # Importar y registrar blueprints o las rutas
    from . import routes
    routes.init_app(app)

    return app