from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()  # instancia global
migrate = Migrate() # instancia global

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Detecta entorno: primero FLASK_ENV, si no existe usa RAILWAY_ENVIRONMENT
    env = os.getenv("FLASK_ENV") or os.getenv("RAILWAY_ENVIRONMENT") or "development"
    print("Entorno detectado:", env)  # 👀 Útil para logs en Railway

    if env == "production":
        app.config.from_object("config.ProductionConfig")
        db_url = os.getenv("MYSQL_URL")
        if not db_url:
            raise RuntimeError("MYSQL_URL no está definido en Railway")
        if db_url.startswith("mysql://"):
            db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        app.config.from_object("config.DevelopmentConfig")
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}"
            f"@{app.config['MYSQL_HOST']}:3306/{app.config['MYSQL_DB']}"
        )
        
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Inicializa SQLAlchemy
    migrate.init_app(app, db)  # Inicializa Flask-Migrate

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

    #with app.app_context():
    #    db.create_all()  # 🔥 Crea las tablas si no existen

    return app