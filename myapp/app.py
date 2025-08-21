from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
import pandas as pd
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

@app.route('/export')
def export():
    respuestas = Respuesta.query.all()
    df = pd.DataFrame([(r.nombre, r.comentario) for r in respuestas], columns=['Nombre', 'Comentario'])
    df.to_csv('respuestas.csv', index=False)
    return send_file('respuestas.csv', mimetype='text/csv', as_attachment=True)

# Generar y guardar QR
@app.route("/qr")
def generar_qr():
    url = request.host_url
    img = qrcode.make(url)
    if not os.path.exists('static'):
        os.makedirs('static')
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
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))