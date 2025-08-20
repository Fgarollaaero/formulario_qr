from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
from io import BytesIO

# Configuración base
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de datos
class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    comentario = db.Column(db.String(500))

# Página con formulario
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        comentario = request.form.get("comentario")
        nueva = Respuesta(nombre=nombre, comentario=comentario)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("index.html")

# Generar y guardar QR
@app.route("/qr")
def generar_qr():
    url = "http://127.0.0.1:5000/"  # URL para pruebas locales, ajusta para producción
    img = qrcode.make(url)
    # Crear carpeta static si no existe
    if not os.path.exists('static'):
        os.makedirs('static')
    # Guardar el QR como archivo
    img.save("static/qr.png")
    return '<img src="/static/qr.png" alt="QR Code">'

# Opcional: Ruta admin
@app.route('/admin', methods=['GET'])
def admin():
    clave = request.args.get('clave')
    if clave == 'secreta123':  # Cambia esta clave
        respuestas = Respuesta.query.all()
        return render_template('index.html', respuestas=respuestas)
    return "Acceso denegado. Usa ?clave=secreta123", 403

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)