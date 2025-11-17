import mysql.connector
from mysql.connector import Error

# Configuración de la conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='bingo_colaborativo',
            user='root',  # Cambia esto por tu usuario de MySQL
            password='12345'  # Cambia esto por tu contraseña de MySQL
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Cierra la conexión a la base de datos
def close_db_connection(connection):
    if connection and connection.is_connected():
        connection.close()