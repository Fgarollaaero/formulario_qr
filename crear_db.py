import os
import sqlite3

# Ruta de la base de datos
ruta_db = "C:\\Users\\Fede\\formulario_qr\\datos.db"

if os.path.exists(ruta_db):
    print("La base de datos ya existe ✅")
else:
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Crear tabla 'respuesta' según tu modelo SQLAlchemy
    cursor.execute("""
    CREATE TABLE respuesta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        area TEXT,
        descripcion TEXT,
        acciones TEXT,
        fecha TEXT,
        severidad TEXT,
        estado TEXT,
        aeronave TEXT,
        componente TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Base de datos y tabla 'respuesta' creadas ✅")