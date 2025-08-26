from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from .models.ModelsUsers import ModelUser
from .models.entities.users import User

auth_bp = Blueprint("auth", __name__)
db = None

def auth_init_app(app, database):
    global db
    db = database
    app.register_blueprint(auth_bp)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        return ModelUser.get_by_id(user_id)

# --- Rutas ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = ModelUser.login(email, password)
        if user:
            login_user(user)
            #flash(f"Bienvenido {user.fullname}", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Email o contraseña incorrectos", "danger")
            return render_template("auth/login.html")
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    #flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(email=email, password=password, fullname=fullname)
        try:
            success = ModelUser.add_user(user)
            if success:
                flash("Usuario registrado con éxito. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash("El correo ya está registrado.", "warning")
        except Exception as e:
            flash(str(e), "danger")
    return render_template("auth/register.html")