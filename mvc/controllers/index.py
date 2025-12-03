# mvc/controllers/index.py
# Factory de Flask y endpoints (APIs) para servir las vistas y assets públicos.
import os
from flask import Flask, send_from_directory, abort, request, jsonify
from flask import session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from mvc.models.db import get_db_connection, close_db_connection
from functools import wraps


# Rutas relativas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VIEWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'views')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')


def login_required(f):
    """Decorador para requerir inicio de sesión en una ruta."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # Si el usuario no está en la sesión, redirigir al login.
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    """Crea y devuelve la aplicación Flask con rutas para las vistas y assets.

    Endpoints principales agregados:
    - /, /login, /register
    - /usuarios, /usuarios/<file>
    - /admin, /admin/users
    - /public/<file> para assets
    - /mvc/views/<file> para acceso directo a vistas
    """
    app = Flask(__name__, static_folder=PUBLIC_DIR, template_folder=VIEWS_DIR)
    # Es crucial configurar una SECRET_KEY para que las sesiones funcionen.
    # En producción, esto debería ser un valor complejo y guardado de forma segura.
    app.secret_key = os.urandom(24)

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
    @login_required
    def usuarios():
        users_index = os.path.join(VIEWS_DIR, 'usuarios', 'index.html')
        if os.path.exists(users_index):
            return send_from_directory(os.path.join(VIEWS_DIR, 'usuarios'), 'index.html')
        abort(404)

    @app.route('/usuarios/<path:filename>')
    @login_required
    def usuarios_files(filename):
        dirpath = os.path.join(VIEWS_DIR, 'usuarios')
        file_path = os.path.join(dirpath, filename)
        if os.path.exists(file_path):
            return send_from_directory(dirpath, filename)
        abort(404)

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        dash = os.path.join(VIEWS_DIR, 'admin', 'dashboard.html')
        if os.path.exists(dash):
            return send_from_directory(os.path.join(VIEWS_DIR, 'admin'), 'dashboard.html')
        abort(404)

    @app.route('/admin/users')
    @login_required
    def admin_users():
        users = os.path.join(VIEWS_DIR, 'admin', 'users.html')
        if os.path.exists(users):
            return send_from_directory(os.path.join(VIEWS_DIR, 'admin'), 'users.html')
        abort(404)

    @app.route('/game/<code>')
    @login_required
    def game_view(code): # 'code' aquí es el id_partida
        # En lugar de servir un archivo estático, renderizamos una plantilla
        # y le pasamos el ID de la partida.
        # Asegúrate de que tienes una carpeta 'templates' en la raíz de 'mvc'.
        # Flask busca las plantillas en una carpeta llamada 'templates' por defecto.
        if os.path.exists(os.path.join(VIEWS_DIR, 'game.html')):
            return render_template('game.html', game_id=code)
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

    # --- API de Autenticación ---

    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        if not data or not data.get('nombre') or not data.get('correo') or not data.get('contrasena'):
            return jsonify({'ok': False, 'message': 'Faltan datos requeridos'}), 400

        nombre = data['nombre']
        correo = data['correo']
        contrasena = data['contrasena']

        connection = get_db_connection()
        if not connection:
            return jsonify({'ok': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor()
            # Verificar si el correo ya existe
            cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
            if cursor.fetchone():
                return jsonify({'ok': False, 'message': 'El correo electrónico ya está registrado'}), 409

            # Hashear la contraseña antes de guardarla
            hashed_password = generate_password_hash(contrasena)

            # Usamos 'contraseña' que es el nombre de la columna en la BD
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo, contraseña, tipo) VALUES (%s, %s, %s, %s)",
                (nombre, correo, hashed_password, 'jugador')
            )
            connection.commit()
            return jsonify({'ok': True, 'message': 'Registro exitoso'}), 201
        except Exception as e:
            return jsonify({'ok': False, 'message': f'Error interno del servidor: {e}'}), 500
        finally:
            close_db_connection(connection)

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        if not data or not data.get('correo') or not data.get('contrasena'):
            return jsonify({'ok': False, 'message': 'Faltan datos requeridos'}), 400

        correo = data['correo']
        contrasena = data['contrasena']

        connection = get_db_connection()
        if not connection:
            return jsonify({'ok': False, 'message': 'Error de conexión a la base de datos'}), 500

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id_usuario, nombre, correo, contraseña, tipo FROM usuarios WHERE correo=%s", (correo,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['contraseña'], contrasena):
                return jsonify({'ok': False, 'message': 'Credenciales inválidas'}), 401

            # Guardar información del usuario en la sesión
            session['user'] = {
                'id': user['id_usuario'],
                'nombre': user['nombre'],
                'tipo': user['tipo']
            }
            return jsonify({'ok': True, 'message': 'Inicio de sesión exitoso', 'redirectUrl': '/usuarios'})
        except Exception as e:
            print(f"Error en el login: {e}")
            return jsonify({'ok': False, 'message': 'Error interno del servidor al iniciar sesión'}), 500
        finally:
            close_db_connection(connection)

    @app.route('/api/auth/logout', methods=['POST'])
    def api_logout():
        session.pop('user', None)  # Elimina al usuario de la sesión
        return jsonify({'ok': True, 'message': 'Sesión cerrada exitosamente', 'redirectUrl': '/login'})


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
            # NOTA: Este endpoint no hashea la contraseña. Considerar añadirlo por seguridad.
            hashed_password = generate_password_hash(data['contrasena'])
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo, contraseña, tipo) VALUES (%s, %s, %s, %s)",
                (data['nombre'], data['correo'], hashed_password, data.get('tipo', 'jugador'))
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
            # NOTA: Este endpoint no hashea la contraseña. Considerar añadirlo por seguridad.
            hashed_password = generate_password_hash(data['contrasena'])
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, correo=%s, contraseña=%s, tipo=%s WHERE id_usuario=%s",
                (data['nombre'], data['correo'], hashed_password, data['tipo'], id_usuario)
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
    @login_required
    def get_partidas():
        user_id = session['user']['id']
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)
        # Devolvemos solo las partidas creadas por el usuario logueado
        cursor.execute("SELECT * FROM partidas WHERE creador_id = %s ORDER BY fecha_inicio DESC", (user_id,))
        partidas = cursor.fetchall()
        close_db_connection(connection)
        return jsonify(partidas)

    # Endpoint para crear una partida
    @app.route('/api/partidas', methods=['POST'])
    @login_required
    def create_partida():
        user_id = session['user']['id']
        data = request.json
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        if not data.get('nombre_partida'):
            return jsonify({'ok': False, 'message': 'El nombre de la partida es requerido'}), 400

        cursor = connection.cursor(dictionary=True)
        try:
            # Añadimos el creador_id al insertar la partida
            cursor.execute(
                "INSERT INTO partidas (nombre_partida, fecha_inicio, estado, creador_id) VALUES (%s, %s, %s, %s)",
                (data['nombre_partida'], data.get('fecha_inicio'), data.get('estado', 'en_curso'), user_id)
            )
            partida_id = cursor.lastrowid
            connection.commit()

            # Recuperar la partida recién creada para devolverla
            cursor.execute("SELECT * FROM partidas WHERE id_partidas = %s", (partida_id,))
            new_partida = cursor.fetchone()
            close_db_connection(connection)
            return jsonify(new_partida), 201
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
                "UPDATE partidas SET nombre_partida=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s WHERE id_partidas=%s",
                (data['nombre_partida'], data.get('fecha_inicio'), data.get('fecha_fin'), data.get('estado'), id_partida)
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
            cursor.execute("DELETE FROM partidas WHERE id_partidas=%s", (id_partida,))
            connection.commit()
            close_db_connection(connection)
            return jsonify({'message': 'Partida eliminada exitosamente'})
        except Exception as e:
            close_db_connection(connection)
            return jsonify({'error': str(e)}), 400

    return app
