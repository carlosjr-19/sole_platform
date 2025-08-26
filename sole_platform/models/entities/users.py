from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, fullname="") -> None:
        self.id = id
        self.email = email
        self.password = password
        self.fullname = fullname

    @classmethod
    def check_password(self, hashed_password, password):
        # Aquí deberías implementar la verificación de la contraseña
        # Por ejemplo, si usas hashing:
        return check_password_hash(hashed_password, password)
    
    @staticmethod
    def generate_hash(password):
        return generate_password_hash(password)
    
#print(generate_password_hash("brasil0812"))  # Ejemplo de cómo generar un hash de contraseña
#print(generate_password_hash("123456"))  # Ejemplo de cómo generar un hash de contraseña