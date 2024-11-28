import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
DATABASE = os.getenv("DATABASE")
# Conectar a la base de datos (o crearla si no existe)
conn = sqlite3.connect(DATABASE)
# Crear un cursor
cursor = conn.cursor()


def create_table_registro_ejecuciones() -> None:
    # Crear la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_ejecuciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_proceso TEXT,
            estado TEXT,
            iniciado TEXT,
            finalizado TEXT
        )
    ''')

    # Confirmar los cambios
    conn.commit()


def registrar_ejecucion_db(nombre_proceso : str, estado : str, fecha_inicio : datetime = None) -> None:
    # Obtener la fecha y hora actuales
    fecha_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    fecha_inicio = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') if fecha_inicio != None else fecha_fin

    # Insertar los datos en la tabla
    cursor.execute('''
        INSERT INTO registro_ejecuciones (nombre_proceso, estado, iniciado, finalizado)
        VALUES (?, ?, ?, ?)
    ''', (nombre_proceso, estado, fecha_inicio, fecha_fin))

    # Confirmar los cambios
    conn.commit()


def consultar_datos_ejecuciones() -> None:
    cursor.execute('SELECT * FROM registro_ejecuciones')
    registros = cursor.fetchall()

    for registro in registros:
        print(registro)


from time import sleep

if __name__=="__main__":
    iniciado = datetime.now()
    # Creo la tabla de registros de ejecuciones
    create_table_registro_ejecuciones()
    sleep(3)
    # Agrego un registro
    registrar_ejecucion_db("enviar_correos_socio", "Correcto")

    consultar_datos_ejecuciones()