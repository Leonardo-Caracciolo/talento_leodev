import pandas as pd
from datetime import datetime
import os
import sys
from send_email import send_email, read_and_modify_html
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.utils import load_config
from verifica_fecha_reporte_validacion import obtener_dia_anterior
from dataframe_utils import load_json_to_dataframe, generate_combined_json
from registrar_ejecuciones import registrar_ejecucion_db


def create_empleado(json_path : str, dia_anterior : datetime) -> pd.DataFrame:
    df_combined_merge = load_json_to_dataframe(json_path)

    columnas_requeridas = [
        'SAP_Profesional',
        'Empleado',
        'e-mail'
    ]
    
    # Filtro por fecha (dia anterior)
    df_combined_merge['Fecha'] = pd.to_datetime(df_combined_merge['Fecha'], unit='ms')
    # df_empleado = df_combined_merge[df_combined_merge['Fecha'].dt.date >= dia_anterior]
    df_empleado = df_combined_merge[df_combined_merge['Fecha'].dt.date <= dia_anterior]  #! Modificar a mayor o igual

    # Dejo las columnas requeridas
    df_empleado = df_empleado[columnas_requeridas].copy()

    return df_empleado


def main():
    # config = load_config()
    # data_paths = config["data_paths"]
    json_path = os.path.join(os.getcwd(), "combined_data.json")

    # Crear el JSON una sola vez
    if not os.path.exists(json_path):
        print("Generando el archivo JSON por primera vez...")
        generate_combined_json(json_path)
    else:
        print(f"Archivo JSON encontrado: {json_path}")

    # Creo el dataframe de los empleados con sus emails
    dia_anterior = obtener_dia_anterior()
    df_empleado = create_empleado(json_path, dia_anterior)
    df_empleado = df_empleado.drop_duplicates(subset=['SAP_Profesional'], keep='first')

    cont_errores = 0
    for index, row in df_empleado.iterrows():
        email = row.get('e-mail', None)
        if pd.isna(email):
            print(f"No se encontró correo electrónico para el No. Personal (SAP_Profesional): {row['SAP_Profesional']}")
        else:
            try:
                empleado = row.get('Empleado', None)
                html_content = read_and_modify_html(empleado, plantilla='empleado')
                subject = f'IMPORTANTE Reportes de tiempo PENDIENTE dia {dia_anterior}'
                # send_email(email, html_content, subject) #! Descomentar en producción
                # send_email("amiriarte@deloitte.com", html_content, subject) #? Pruebas
                print(f"{empleado} - {email}") #! Quitar
            except Exception as e:
                cont_errores += 1
                print(f"""Error al enviar el correo del empleado {empleado} con mail {email}.\n
                      Detalle del error: {e}""")
    
    estado = "Correcto" if cont_errores == 0 else "Erróneo"
    return estado

if __name__ == '__main__':
    main()