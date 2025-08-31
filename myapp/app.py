from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))  # Opcional
    area = db.Column(db.String(100))    # Área del evento
    descripcion = db.Column(db.String(500))  # Descripción requerida
    acciones = db.Column(db.String(500))     # Acciones tomadas (opcional)
    fecha = db.Column(db.String(50))        # Fecha y hora (ej. "2025-08-31 09:00")
    severidad = db.Column(db.String(20))    # Severidad (Baja, Media, Alta)
    estado = db.Column(db.String(20))       # Estado (Abierto, En progreso, Cerrado)
    aeronave = db.Column(db.String(100))    # Opcional, número de serie o matrícula
    componente = db.Column(db.String(100))  # Opcional, componente afectado

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        area = request.form.get("area")
        descripcion = request.form.get("descripcion")
        acciones = request.form.get("acciones", "")
        fecha = request.form.get("fecha")
        severidad = request.form.get("severidad", "")
        estado = request.form.get("estado", "")
        aeronave = request.form.get("aeronave", "")
        componente = request.form.get("componente", "")
        if area and descripcion:  # Área y descripción son requeridos
            try:
                nueva = Respuesta(nombre=nombre, area=area, descripcion=descripcion, acciones=acciones,
                                 fecha=fecha, severidad=severidad, estado=estado, aeronave=aeronave, componente=componente)
                db.session.add(nueva)
                db.session.commit()
                return redirect(url_for("index"))
            except Exception as e:
                return f"Error al guardar: {str(e)}", 500
        else:
            return "Por favor, completa al menos el área y la descripción.", 400
    return render_template("index.html")

@app.route("/qr")
def generar_qr():
    url = request.host_url
    img = qrcode.make(url)
    if not os.path.exists('static'):
        os.makedirs('static')
    img.save("static/qr.png")
    return '<img src="/static/qr.png?v=1" alt="QR Code">'

@app.route('/admin', methods=['GET'])
def admin():
    clave = request.args.get('clave')
    if clave == 'secreta123':
        respuestas = Respuesta.query.all()
        return render_template('index.html', respuestas=respuestas)
    return "Acceso denegado. Usa ?clave=secreta123", 403

@app.route('/export')
def export():
    respuestas = Respuesta.query.all()
    df = pd.DataFrame([(r.nombre or '', r.area, r.descripcion, r.acciones or '', r.fecha or '', r.severidad or '',
                       r.estado or '', r.aeronave or '', r.componente or '') for r in respuestas],
                      columns=['Nombre', 'Área', 'Descripción', 'Acciones', 'Fecha', 'Severidad', 'Estado', 'Aeronave', 'Componente'])
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        df.to_csv(tmp.name, index=False)
        return send_file(tmp.name, mimetype='text/csv', as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))