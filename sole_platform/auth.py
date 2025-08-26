# sole_platform/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required



# Modelos
from .models.ModelsUsers import ModelUser

# Entidades
from .models.entities.users import User

# Definimos db global, pero aún no inicializada
db = None

LoggedUser = None

auth_bp = Blueprint("auth", __name__)

# --- Definimos las rutas aquí ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        #print(f"Email: {email}, Password: {password}")
        user = User(None, email, password)

        # Intentar autenticar usuario
        LoggedUser = ModelUser.login(db, user)
        if LoggedUser != None:
            if LoggedUser.password:
                print("Usuario autenticado")
                login_user(LoggedUser)
                #print(f"Usuario logueado: {LoggedUser.fullname}")
                return redirect(url_for("inicio"))
            else:
                print("Contraseña incorrecta")
                flash("Contraseña incorrecta", "danger")
                return render_template("auth/login.html")
        else:
            print("Usuario no encontrado")
            flash("Usuario no encontrado", "danger")
            return render_template("auth/login.html")
    else:

        return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(None, email, password, fullname)

        try:
            success = ModelUser.add_user(ModelUser, db, user)
            if success:
                flash("Usuario registrado con éxito. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("El correo ya está registrado.", "warning")
                return render_template("auth/register.html")
        except Exception as e:
            flash(str(e), "danger")
            return render_template("auth/register.html")
    else:
        return render_template("auth/register.html")


# --- Solo registra el blueprint ---
def auth_init_app(app, database):
    global db
    db = database
    app.register_blueprint(auth_bp)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        return ModelUser.get_by_id(db, user_id)


