import pymssql
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

SERVER = 'localhost'
DATABASE = 'master'
USERNAME = 'sa'
PASSWORD = 'YourPassword123!'


def get_db_connection():
    try:
        conn = pymssql.connect(
            server=SERVER, port=1433, database=DATABASE, user=USERNAME, password=PASSWORD)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
    return stored_password_hash == hashed_provided_password


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(
                "SELECT username, contrasena FROM usuarios WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                return jsonify({'mensaje': 'Autenticacion exitosa'}), 200
            else:
                return jsonify({'error': 'Usuario o password incorrectas'}), 401
        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

# --- Servicios CRUD para la tabla 'personajes' ---

# Obtener todos los personajes


@app.route('/personajes', methods=['GET'])
def get_personajes():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT id, name, email FROM personajes")
            personajes = cursor.fetchall()
            return jsonify(personajes), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener personajes: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

# Obtener un personaje por ID


@app.route('/personajes/<int:id>', methods=['GET'])
def get_personaje(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(
                "SELECT id, name, email FROM personajes WHERE id = %d", (id,))
            personaje = cursor.fetchone()
            if personaje:
                return jsonify(personaje), 200
            else:
                return jsonify({'mensaje': 'Personaje no encontrado'}), 404
        except Exception as e:
            return jsonify({'error': f'Error al obtener personaje: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

# Crear un nuevo personaje


@app.route('/personajes', methods=['POST'])
def create_personaje():
    data = request.get_json()
    id = data.get('id')
    name = data.get('name')
    email = data.get('email')

    if not id or not name or not email:
        return jsonify({'error': 'Se requiere id, nombre y correo electrónico'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO personajes (id, name, email) VALUES (%d, %s, %s)", (id, name, email))
            conn.commit()
            return jsonify({'mensaje': 'Personaje creado exitosamente'}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al crear personaje: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

# Actualizar un personaje existente


@app.route('/personajes/<int:id>', methods=['PUT'])
def update_personaje(id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'error': 'Se requiere nombre y correo electrónico'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE personajes SET name = %s, email = %s WHERE id = %d", (name, email, id))
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({'mensaje': 'Personaje actualizado exitosamente'}), 200
            else:
                return jsonify({'mensaje': 'Personaje no encontrado'}), 404
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al actualizar personaje: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

# Eliminar un personaje por ID


@app.route('/personajes/<int:id>', methods=['DELETE'])
def delete_personaje(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM personajes WHERE id = %d", (id,))
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({'mensaje': 'Personaje eliminado exitosamente'}), 200
            else:
                return jsonify({'mensaje': 'Personaje no encontrado'}), 404
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al eliminar personaje: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
