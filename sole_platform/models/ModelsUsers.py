from .entities.users import User
from sole_platform import db

class ModelUser:

    @staticmethod
    def login(email, password):
        try:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                return user
            return None
        except Exception as e:
            raise Exception(f"Error en login: {str(e)}")

    @staticmethod
    def add_user(user):
        try:
            existing_user = User.query.filter_by(email=user.email).first()
            if existing_user:
                return False

            # Hashear la contraseña antes de guardar
            user.password = User.generate_hash(user.password)
            db.session.add(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al agregar usuario: {str(e)}")

    @staticmethod
    def get_by_id(user_id):
        try:
            return User.query.get(user_id)
        except Exception as e:
            raise Exception(f"Error: {str(e)}")

    @staticmethod
    def update_user(user_id, fullname=None, password=None):
        try:
            user = User.query.get(user_id)
            if not user:
                return False

            if fullname:
                user.fullname = fullname
            
            if password:
                user.password = User.generate_hash(password)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al actualizar usuario: {str(e)}")