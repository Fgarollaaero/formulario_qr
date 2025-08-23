from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
import pandas as pd
from io import BytesIO

# Ruta absoluta al directorio "templates"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "C:/Users/Fede/formulario_qr/templates")

# Configuración base
app = Flask(__name__, template_folder=TEMPLATES_DIR)
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
    
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name="respuestas.csv")
    
@app.route("/qr")
def generar_qr():
    # Si querés que el QR apunte al formulario principal
    url = url_for('index', _external=True)

    # Si querés que apunte al export, usá:
    # url = url_for('export', _external=True)

    img = qrcode.make(url)
    if not os.path.exists('static'):
        os.makedirs('static')
    img.save("static/qr.png")
    return f'<p>QR apuntando a: {url}</p><img src="/static/qr.png?v=2" alt="QR Code">'

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