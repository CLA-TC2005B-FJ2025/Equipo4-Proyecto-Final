from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import bcrypt
import os 
from datetime import datetime
import traceback
from PIL import Image
from werkzeug.utils import secure_filename
app = Flask(__name__, static_folder='static')
CORS(app)



# Configura tu conexión a SQL Server
server = 'localhost'  # Nombre de tu servidor
port = 1433
database = 'master'  
username = 'sa'
password = 'YourPassword123!'


connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server},{port};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

def get_db_connection():
    return pyodbc.connect(connection_string)

# Conectar a SQL Server
conn = pyodbc.connect(connection_string)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, y password son requeridos'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash.decode('utf-8')))
            conn.commit()
        
        return jsonify({'message': 'Usuario registrado exitosamente'}), 201

    except pyodbc.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Este correo ya está registrado'}), 409

    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT password_hash, es_admin
                FROM usuarios
                WHERE email = ?
            """, (email,))
            row = cur.fetchone()

            if row:
                stored_password_hash, is_admin = row

                # Verificar contraseña
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                    # Obtener los grixeles desbloqueados para este usuario
                    cur.execute("""
                        SELECT GrixelID
                        FROM responde
                        WHERE email_usuario = ? AND correcta = 1
                    """, (email,))
                    desbloqueados = [row[0] for row in cur.fetchall()]

                    return jsonify({
                        'message': 'Login exitoso',
                        'is_admin': bool(is_admin),
                        'grixeles_desbloqueados': desbloqueados  # Devolver grixeles desbloqueados
                    }), 200
                else:
                    return jsonify({'error': 'Contraseña incorrecta'}), 401
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/api/preguntas', methods=['GET'])
def obtener_preguntas():
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.idPregunta, p.pregunta, r.Respuesta, r.Correcta
                FROM Pregunta p
                LEFT JOIN Respuesta r ON p.idPregunta = r.idPregunta
                ORDER BY p.idPregunta
            """)
            rows = cur.fetchall()

        preguntas = {}
        for row in rows:
            id_pregunta, pregunta_texto, respuesta_texto, es_correcta = row
            if id_pregunta not in preguntas:
                preguntas[id_pregunta] = {
                    "id": id_pregunta,  # <= TE FALTA ESTE CAMPO EN TU JSON
                    "texto": pregunta_texto,
                    "opciones": [],
                    "correcta": None
                }
            preguntas[id_pregunta]["opciones"].append(respuesta_texto)
            if es_correcta:
                preguntas[id_pregunta]["correcta"] = len(preguntas[id_pregunta]["opciones"]) - 1

        return jsonify([{
            "id": p["id"],  # <= Agrega el id
            "texto": p["texto"],
            "opciones": p["opciones"],
            "correcta": p["correcta"]
        } for p in preguntas.values()]), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/preguntas', methods=['POST'])
def agregar_pregunta():
    data = request.json
    pregunta_texto = data.get('texto')
    respuestas = data.get('respuestas')  # Lista de respuestas (con el texto y cuál es la correcta)
    
    if not pregunta_texto or not respuestas or len(respuestas) != 3:
        return jsonify({'error': 'Pregunta y 3 respuestas son requeridas'}), 400
    
    try:
        with conn.cursor() as cur:
            # Insertar la nueva pregunta
            cur.execute("""
                INSERT INTO Pregunta (pregunta)
                VALUES (?)
            """, (pregunta_texto,))
            conn.commit()

            # Obtener el ID de la nueva pregunta insertada
            cur.execute("SELECT @@IDENTITY")
            id_pregunta = cur.fetchone()[0]

            # Insertar las respuestas correspondientes
            for i, respuesta in enumerate(respuestas):
                respuesta_texto = respuesta.get('texto')
                correcta = 1 if respuesta.get('correcta') else 0

                cur.execute("""
                    INSERT INTO Respuesta (idPregunta, Respuesta, Correcta)
                    VALUES (?, ?, ?)
                """, (id_pregunta, respuesta_texto, correcta))
            conn.commit()

        return jsonify({'message': 'Pregunta y respuestas agregadas exitosamente'}), 201

    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500
    

@app.route('/api/imagenes', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se encontró ninguna imagen en la solicitud'}), 400

    imagen = request.files['imagen']
    nombre = request.form.get('nombre')

    if not imagen or not nombre:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

    try:
        filename = secure_filename(imagen.filename)
        ruta_relativa = os.path.join('static', 'uploads', filename)
        ruta_absoluta = os.path.join(app.root_path, ruta_relativa)

        os.makedirs(os.path.dirname(ruta_absoluta), exist_ok=True)
        imagen.save(ruta_absoluta)

        with conn.cursor() as cur:
            cur.execute(""" 
                INSERT INTO imagenes (nombre, url_imagen)
                VALUES (?, ?) 
            """, (nombre, filename))  # Guardamos solo el nombre del archivo
            conn.commit()

        return jsonify({'message': 'Imagen subida exitosamente'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/api/imagenes/<int:imagen_id>', methods=['PUT'])
def actualizar_email_imagen(imagen_id):
    data = request.json
    nuevo_email = data.get('email_usuario')

    if not nuevo_email:
        return jsonify({'error': 'El email es requerido'}), 400

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE imagenes
                SET email_usuario = ?
                WHERE ImagenID = ?
            """, (nuevo_email, imagen_id))
            conn.commit()

        return jsonify({'message': 'Email actualizado exitosamente'}), 200

    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({'error': 'Error al actualizar el email'}), 500



@app.route('/api/imagenes', methods=['GET'])
def obtener_imagenes():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ImagenID, nombre, url_imagen FROM imagenes")
            rows = cur.fetchall()

            imagenes = []
            for row in rows:
                ImagenID, nombre, url_imagen = row
                imagenes.append({
                    'id': ImagenID,
                    'nombre': nombre,
                    'url_imagen': url_imagen
                })

        return jsonify(imagenes), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error interno del servidor'}), 500
    



#@app.route('/api/imagenes/ultima', methods=['GET'])
#def obtener_ultima_imagen():
#    try:
#        with conn.cursor() as cur:
#            cur.execute("""
#                SELECT TOP 1 ImagenID, nombre, url_imagen
#                FROM imagenes
#                ORDER BY ImagenID DESC
#            """)
#            row = cur.fetchone()
#
#        if row:
#            imagen_id, nombre, url_imagen = row
#            return jsonify({
#                "imagen_id": imagen_id,
#                "nombre": nombre,
#                "url_imagen": url_imagen
#            }), 200
#        else:
#            return jsonify({"error": "No hay imágenes."}), 404
#    except Exception as e:
#        print(e)
#        return jsonify({'error': 'Error interno del servidor'}), 500





@app.route('/api/preguntas/<int:pregunta_id>', methods=['GET'])
def obtener_pregunta(pregunta_id):
    cursor = conn.cursor()
    
    # Obtener la pregunta
    cursor.execute("""
        SELECT PreguntaID, pregunta
        FROM pregunta
        WHERE PreguntaID = ?
    """, (pregunta_id,))
    pregunta = cursor.fetchone()
    
    if not pregunta:
        return jsonify({"error": "Pregunta no encontrada"}), 404
    
    # Obtener las respuestas asociadas
    cursor.execute("""
        SELECT RespuestaID, Respuesta, Correcta
        FROM respuestas
        WHERE PreguntaID = ?
    """, (pregunta_id,))
    respuestas = cursor.fetchall()
    
    # Formatear la respuesta
    resultado = {
        "pregunta_id": pregunta[0],
        "texto_pregunta": pregunta[1],
        "respuestas": [
            {
                "respuesta_id": r[0],
                "texto": r[1],
                "correcta": bool(r[2])  # Convertir a booleano si es 0/1
            } for r in respuestas
        ]
    }
    
    return jsonify(resultado)

from datetime import datetime

@app.route('/api/responde', methods=['POST'])
def registrar_respuesta():
    try:
        data = request.json
        print("Datos recibidos:", data)

        respuesta_id = data.get('respuesta_id')
        email_usuario = data.get('email_usuario')
        grixel_id = data.get('grixel_id')
        correcta = data.get('correcta')

        if not all([respuesta_id, email_usuario, grixel_id, correcta is not None]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO responde (RespuestaID, email_usuario, GrixelID, fecha_respuesta, correcta)
                VALUES (?, ?, ?, GETDATE(), ?)
            """, (respuesta_id, email_usuario, grixel_id, correcta))
            conn.commit()

        return jsonify({'message': 'Respuesta registrada correctamente'}), 201

    except Exception as e:
        print("Error al registrar respuesta:", e)
        return jsonify({'error': 'Error interno del servidor'}), 500





@app.route('/api/grixeles', methods=['GET'])
def obtener_grixeles_resueltos():
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT GrixelID, email_usuario
                FROM responde
                WHERE correcta = 1
            """)
            rows = cur.fetchall()
        desbloqueados = [{'grixel_id': row[0], 'email_usuario': row[1]} for row in rows]
        return jsonify(desbloqueados), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Error al obtener grixeles'}), 500


@app.route('/api/responde', methods=['GET'])
def obtener_respuestas():
    email_usuario = request.args.get('email_usuario')  # Parámetro opcional para filtrar por email

    try:
        with conn.cursor() as cur:
            # Si el email_usuario está presente, filtrar las respuestas por ese usuario
            if email_usuario:
                cur.execute("""
                    SELECT RespuestaID, GrixelID, correcta, email_usuario, fecha_respuesta
                    FROM responde
                    WHERE email_usuario = ?
                """, (email_usuario,))
            else:
                cur.execute("""
                    SELECT RespuestaID, GrixelID, correcta, email_usuario, fecha_respuesta
                    FROM responde
                """)

            rows = cur.fetchall()

        # Estructurar las respuestas como una lista de diccionarios
        respuestas = [{
            'respuesta_id': row[0],
            'grixel_id': row[1],
            'correcta': row[2],
            'email_usuario': row[3],
            'fecha_respuesta': row[4].strftime("%Y-%m-%d %H:%M:%S")  # Formatear la fecha
        } for row in rows]

        return jsonify(respuestas), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error al obtener respuestas'}), 500

@app.route('/api/ultima-imagen', methods=['GET'])
def obtener_ultima_imagen():
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TOP 1 url_imagen 
                FROM imagenes 
                ORDER BY ImagenID DESC
            """)
            row = cur.fetchone()

            if row:
                return jsonify({'nombre': row[0]})
            else:
                return jsonify({'message': 'No hay imágenes registradas'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/api/name', methods=['GET'])
def obtener_name():
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TOP 1 nombre 
                FROM imagenes 
                ORDER BY ImagenID DESC
            """)
            row = cur.fetchone()

            if row:
                return jsonify({'nombre': row[0]})
            else:
                return jsonify({'message': 'No hay imágenes registradas'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/grixeles_completos', methods=['GET'])
def obtener_grixeles_desbloqueados():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No se pudo establecer conexión con la base de datos'}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT GrixelID FROM responde WHERE correcta = 1")
            resultados = cursor.fetchall()

            # Si no hay resultados
            if not resultados:
                return jsonify({'message': 'No se encontraron grixeles desbloqueados'}), 404

            grixeles = [{'grixel_id': int(row[0])} for row in resultados]
        return jsonify(grixeles)
    except pyodbc.Error as e:
        print("Error en la consulta:", e)
        return jsonify({'error': 'Error al ejecutar la consulta en la base de datos'}), 500
    except Exception as e:
        print("Error inesperado:", e)
        return jsonify({'error': f'Ocurrió un error inesperado: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/borrar_responde', methods=['DELETE'])
def borrar_responde():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No se pudo establecer conexión con la base de datos'}), 500

    try:
        with conn.cursor() as cursor:
            print("Ejecutando DELETE desde la tabla responde...")
            cursor.execute("DELETE FROM responde")  # Eliminamos los registros
            conn.commit()  # Asegúrate de guardar los cambios
            print("Datos eliminados con éxito")

        return jsonify({'message': 'Todos los datos de la tabla responde han sido eliminados exitosamente'}), 200
    except pyodbc.Error as e:
        print("Error al borrar los datos:", e)
        return jsonify({'error': 'Error al intentar eliminar los datos de la tabla responde'}), 500
    except Exception as e:
        print("Error inesperado:", e)
        return jsonify({'error': f'Ocurrió un error inesperado: {str(e)}'}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

