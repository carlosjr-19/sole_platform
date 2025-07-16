from flask import render_template, redirect

def init_app(app):

    @app.route("/")
    def home():
        return redirect("/inicio")

    @app.route("/inicio")
    def inicio():
        return render_template('inicio.html')

    @app.route("/pruebas")
    def pruebas():
        return render_template('pruebas.html')

    @app.route("/comisiones/")
    def comisiones():
        return render_template('commisions/comisiones.html')
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error_404.html'), 404