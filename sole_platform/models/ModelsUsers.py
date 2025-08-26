from .entities.users import User

class ModelUser():

    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, email, password, fullname FROM users WHERE email = %s"
            cursor.execute(sql, (user.email,))
            row = cursor.fetchone()

            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3])
                return user
            else:
                return None
        except Exception as e:
            raise Exception(f"Error en login: {str(e)}")
        
    def add_user(self, db, user):
        try:
            cursor = db.connection.cursor()

            # Verificar si el email ya existe
            sql_check = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql_check, (user.email,))
            existing_user = cursor.fetchone()
            if existing_user:
                return False  # El correo ya está registrado

            # Hashear la contraseña antes de guardar
            hashed_password = User.generate_hash(user.password)

            sql = "INSERT INTO users (email, password, fullname) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user.email, hashed_password, user.fullname))
            db.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error al agregar usuario: {str(e)}")
        
    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, email, fullname FROM users WHERE id = %s"
            cursor.execute(sql, (id,))
            row = cursor.fetchone()

            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as e:
            raise Exception(f"Error: {str(e)}")