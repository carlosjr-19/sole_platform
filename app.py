from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "¡Hola desde Flask en Docker y Railway! 🚀"

@app.route("/saludo")
def saludo():
    return render_template('saludo.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Railway o 5000 en local
    app.run(host="0.0.0.0", port=port)