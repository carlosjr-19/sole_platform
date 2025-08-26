from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sole_platform import db

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(200))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def generate_hash(password):
        return generate_password_hash(password)

#print(generate_password_hash("brasil0812"))  # Ejemplo de uso