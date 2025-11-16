"""Launcher en la raíz para arrancar la aplicación Flask definida en mvc/controllers/index.py

Ejecuta:
  python index.py

Esto levantará el servidor en 0.0.0.0:5000 por defecto.
"""
import os
from mvc.controllers.index import create_app


def main():
    app = create_app()
    # Puerto configurable desde variable de entorno PORT
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    main()
