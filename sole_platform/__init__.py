from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # Carga variables de entorno desde .env

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuraciones
    app.config.from_object('config.Config')

    # Importar y registrar blueprints o las rutas
    from . import routes
    routes.init_app(app)

    return app