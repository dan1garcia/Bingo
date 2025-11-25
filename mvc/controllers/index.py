# mvc/controllers/index.py
# Factory de Flask y endpoints (APIs) para servir las vistas y assets públicos.
import os
from flask import Flask, send_from_directory, abort, request, jsonify
from mvc.models.db import get_db_connection, close_db_connection


# Rutas relativas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VIEWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'views')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')


def create_app():
    """Crea y devuelve la aplicación Flask con rutas para las vistas y assets.

    Endpoints principales agregados:
    - /, /login, /register
    - /usuarios, /usuarios/<file>
    - /admin, /admin/users
    - /public/<file> para assets
    - /mvc/views/<file> para acceso directo a vistas
    """
    app = Flask(__name__, static_folder=PUBLIC_DIR)

    @app.route('/')
    def home():
        index_path = os.path.join(VIEWS_DIR, 'login.html')
        if os.path.exists(index_path):
            return send_from_directory(VIEWS_DIR, 'login.html')
        abort(404)

    # Rutas amigables para las vistas solicitadas
    @app.route('/login')
    def login():
        file_path = os.path.join(VIEWS_DIR, 'login.html')
        if os.path.exists(file_path):
            return send_from_directory(VIEWS_DIR, 'login.html')
        abort(404)

    @app.route('/register')
    def register():
        file_path = os.path.join(VIEWS_DIR, 'register.html')
        if os.path.exists(file_path):
            return send_from_directory(VIEWS_DIR, 'register.html')
        abort(404)

    @app.route('/usuarios')
    def usuarios():
        users_index = os.path.join(VIEWS_DIR, 'usuarios', 'index.html')
        if os.path.exists(users_index):
            return send_from_directory(os.path.join(VIEWS_DIR, 'usuarios'), 'index.html')
        abort(404)

    @app.route('/usuarios/<path:filename>')
    def usuarios_files(filename):
        dirpath = os.path.join(VIEWS_DIR, 'usuarios')
        file_path = os.path.join(dirpath, filename)
        if os.path.exists(file_path):
            return send_from_directory(dirpath, filename)
        abort(404)

    @app.route('/admin')
    def admin_dashboard():
        dash = os.path.join(VIEWS_DIR, 'admin', 'dashboard.html')
        if os.path.exists(dash):
            return send_from_directory(os.path.join(VIEWS_DIR, 'admin'), 'dashboard.html')
        abort(404)

    @app.route('/admin/users')
    def admin_users():
        users = os.path.join(VIEWS_DIR, 'admin', 'users.html')
        if os.path.exists(users):
            return send_from_directory(os.path.join(VIEWS_DIR, 'admin'), 'users.html')
        abort(404)

    # Rutas genéricas para acceder a vistas y assets
    @app.route('/mvc/views/<path:filename>')
    def views_files(filename):
        file_path = os.path.join(VIEWS_DIR, filename)
        if os.path.exists(file_path):
            return send_from_directory(VIEWS_DIR, filename)
        abort(404)

    @app.route('/public/<path:filename>')
    def public_files(filename):
        file_path = os.path.join(PUBLIC_DIR, filename)
        if os.path.exists(file_path):
            return send_from_directory(PUBLIC_DIR, filename)
        abort(404)

    # Endpoint para obtener todos los usuarios
    @app.route('/api/usuarios', methods=['GET'])
    def get_usuarios():
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        close_db_connection(connection)
        return jsonify(usuarios)

    # Endpoint para crear un usuario
    @app.route('/api/usuarios', methods=['POST'])
    def create_usuario():
        data = request.json
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo, contrasena, tipo) VALUES (%s, %s, %s, %s)",
                (data['nombre'], data['correo'], data['contrasena'], data.get('tipo', 'jugador'))
            )
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Usuario creado exitosamente'}), 201
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    # Endpoint para actualizar un usuario
    @app.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
    def update_usuario(id_usuario):
        data = request.json
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, correo=%s, contrasena=%s, tipo=%s WHERE id_usuario=%s",
                (data['nombre'], data['correo'], data['contrasena'], data['tipo'], id_usuario)
            )
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Usuario actualizado exitosamente'})
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    # Endpoint para eliminar un usuario
    @app.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
    def delete_usuario(id_usuario):
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Usuario eliminado exitosamente'})
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    # Endpoint para obtener todas las partidas
    @app.route('/api/partidas', methods=['GET'])
    def get_partidas():
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM partidas")
        partidas = cursor.fetchall()
        close_db_connection(connection)
        return jsonify(partidas)

    # Endpoint para crear una partida
    @app.route('/api/partidas', methods=['POST'])
    def create_partida():
        data = request.json
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO partidas (nombre_partida, fecha_inicio, estado) VALUES (%s, %s, %s)",
                (data['nombre_partida'], data.get('fecha_inicio'), data.get('estado', 'en_curso'))
            )
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Partida creada exitosamente'}), 201
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    # Endpoint para actualizar una partida
    @app.route('/api/partidas/<int:id_partida>', methods=['PUT'])
    def update_partida(id_partida):
        data = request.json
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE partidas SET nombre_partida=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s WHERE id_partida=%s",
                (data['nombre_partida'], data['fecha_inicio'], data['fecha_fin'], data['estado'], id_partida)
            )
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Partida actualizada exitosamente'})
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    # Endpoint para eliminar una partida
    @app.route('/api/partidas/<int:id_partida>', methods=['DELETE'])
    def delete_partida(id_partida):
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM partidas WHERE id_partida=%s", (id_partida,))
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Partida eliminada exitosamente'})
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    return app
