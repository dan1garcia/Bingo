# mvc/controllers/index.py
# Factory de Flask y endpoints (APIs) para servir las vistas y assets públicos.
import os
from flask import Flask, send_from_directory, abort


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

    return app
