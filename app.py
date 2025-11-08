# Importación de librerías necesarias
from flask import Flask, request, render_template, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import traceback

# -------------------------------
# Configuración de la aplicación
# -------------------------------
app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "FORMULARIO",  # Nombre de la base de datos
    "user": "postgres",
    "password": "123456",
    "port": 5432
}

# ---------------------------------------------------------
# Función para conectar la base de datos PostgreSQL
# ---------------------------------------------------------
def conectar_bd():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Error al conectarse con la base de datos: {e}")
        return None

# ---------------------------------------------------------
# Página principal - Carga el archivo index.html
# ---------------------------------------------------------
@app.route('/')
def inicio():
    return render_template('index.html')

# ---------------------------------------------------------
# Ruta para guardar los datos del formulario
# ---------------------------------------------------------
@app.route('/Formularios', methods=['POST'])
def guardar_contacto():
    try:
        datos = request.form.to_dict()

        nombre = datos.get('nombre', '').strip()
        apellido = datos.get('apellido', '').strip()
        direccion = datos.get('direccion', '').strip()
        telefono = datos.get('telefono', '').strip()
        correo = datos.get('correo', '').strip()
        mensaje = datos.get('mensaje', '').strip()

        # Validación de campos obligatorios
        if not nombre or not apellido or not correo:
            return "Error: Faltan datos obligatorios", 400

        conexion = conectar_bd()
        if conexion is None:
            return "Error al conectar con la base de datos", 500

        cursor = conexion.cursor()

        # Sentencia SQL
        cursor.execute('''
            INSERT INTO "Formularios" 
            ("Nombre", "Apellido", "Direccion", "Telefono", "CorreoElectronico", "Mensaje")
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre, apellido, direccion, telefono, correo, mensaje))

        conexion.commit()
        cursor.close()
        conexion.close()

        # 👉 En lugar de devolver JSON, recargamos la página principal
        return redirect(url_for('inicio'))

    except Exception as e:
        print(f"Error al guardar el contacto: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno al guardar el contacto'}), 500

# ---------------------------------------------------------
# Ruta para ver todos los contactos registrados
# ---------------------------------------------------------
@app.route('/ver', methods=['GET'])
def ver_contacto():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Formularios" ORDER BY id DESC;')
        Formularios = cursor.fetchall()
        cursor.close()
        conexion.close()

        return jsonify(Formularios), 200

    except Exception as e:
        print(f"Error al obtener los contactos: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error interno al obtener los contactos'}), 500

# ---------------------------------------------------------
# Inicio del servidor Flask
# ---------------------------------------------------------
if __name__ == '__main__':
    print("Iniciando el servidor...")
    app.run(debug=True)
