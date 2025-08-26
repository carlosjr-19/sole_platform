from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()  # instancia global

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Config
    if os.getenv("FLASK_ENV") == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    # URI usando PyMySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}"
        f"@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Inicializa SQLAlchemy

    # Crear carpetas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)

    # Rutas y auth
    from . import routes
    routes.init_app(app)

    from . import auth
    auth.auth_init_app(app, db)

    app.db = db

    return app