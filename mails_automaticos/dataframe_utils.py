import pandas as pd
from datetime import date, timedelta, datetime
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.utils import load_config

config = load_config()
data_paths = config["data_paths"]


def generate_combined_json(output_path):
    """
    Genera el archivo JSON `combined_data.json` una sola vez a partir de `df_combined_merge`.
    
    Args:
        output_path (str): Ruta donde se guardará el archivo JSON.
    """
    # Crear DataFrame combinado a partir de los archivos Excel
    df_validacion = pd.read_excel(data_paths["file_validacion"]).dropna(how='all')
    df_reporte_empleados = pd.read_excel(data_paths["file_total_socios"], sheet_name='Reporte de empleados', skiprows=1).dropna(how='all')
    df_total_socios = pd.read_excel(data_paths["file_total_socios"], sheet_name='Total Socios').dropna(how='all')
    df_utilizacion_actual = pd.read_excel(data_paths["file_utilizacion_actual"]).dropna(how='all')
    df_personal = pd.read_excel(data_paths["file_personal"]).dropna(how='all')

    # Eliminar espacios adicionales de todas las columnas de los DataFrames
    df_validacion = df_validacion.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_reporte_empleados = df_reporte_empleados.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_total_socios = df_total_socios.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_utilizacion_actual = df_utilizacion_actual.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_personal = df_personal.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Renombrar columnas para alinear los datos
    df_validacion.rename(columns={'No. Personal': 'SAP_Profesional'}, inplace=True)
    df_reporte_empleados.rename(columns={'SAP': 'SAP_Profesional', 'SAP SOCIO': 'SAP_Socio'}, inplace=True)
    df_total_socios.rename(columns={'SAP': 'SAP_Socio'}, inplace=True)
    df_utilizacion_actual.rename(columns={'SAP': 'SAP_Profesional'}, inplace=True)
    df_personal.rename(columns={'No. SAP': 'SAP_Profesional'}, inplace=True)

    # Realizar uniones
    df_combined_merge = pd.merge(df_validacion, df_reporte_empleados, on='SAP_Profesional', how='left')
    df_combined_merge = pd.merge(df_combined_merge, df_total_socios, on='SAP_Socio', how='left')
    df_combined_merge = pd.merge(df_combined_merge, df_utilizacion_actual, on='SAP_Profesional', how='left')
    df_combined_merge = pd.merge(df_combined_merge, df_personal, on='SAP_Profesional', how='left')

    # Filtra por reportes no entregados
    df_combined_merge = df_combined_merge[df_combined_merge["Texto Explicativo PT.1"]=="No entregó reporte"]

    # Filtra por reportes no entregados
    df_combined_merge = df_combined_merge[df_combined_merge["Texto Explicativo PT.1"]=="No entregó reporte"]

    # Guardar como JSON
    df_combined_merge.to_json(output_path, orient='records', force_ascii=False,date_format='iso', indent=4)
    print(f"Archivo JSON creado en: {output_path}")


def load_json_to_dataframe(json_path):
    """Carga un archivo JSON y lo convierte en un DataFrame."""
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return pd.DataFrame(data)
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo JSON no se encontró en la ruta: {json_path}")

def get_weekly_ranges():
    "Retorna una lista con los rangos de todas las semanas, desde el día actual hasta el fin de mes"
    # Obtener la fecha actual
    today = date.today()
    today = pd.to_datetime("2024/08/01") #? Prueba

    # Lista para almacenar los rangos de fechas
    date_ranges = []

    # Obtener el último día del mes
    end_date = today.replace(day=28) + timedelta(days=4)
    end_date = end_date - timedelta(days=end_date.day)

    current_date = today

    # Generar rangos semanales hasta el final del mes
    while current_date <= end_date:
        # Encontrar el próximo domingo
        next_sunday = current_date + timedelta(days=(6 - current_date.weekday()))

        # Si el próximo domingo está fuera del mes, ajustar al último día del mes
        if next_sunday > end_date:
            next_sunday = end_date

        # Agregar el rango a la lista
        date_ranges.append((current_date.strftime('%Y-%m-%d'), next_sunday.strftime('%Y-%m-%d')))

        # Mover la fecha actual al lunes siguiente
        current_date = next_sunday + timedelta(days=1)

    return date_ranges

def get_week_label(date: datetime):
    "Verifica que cada fecha de un dataframe sea mayor o igual al inicio y menor o igual al fin del rango de fechas."
    week_ranges = get_weekly_ranges()

    for start, end in week_ranges:
        if (date.strftime('%d/%m/%Y') >= start) and (date.strftime('%d/%m/%Y') <= end):
            return f"{start} - {end}"

    return None

def generate_all_weeks():
    week_ranges = get_weekly_ranges()
    all_weeks = [f"{start} - {end}" for start, end in week_ranges]
    return all_weeks


def create_excel_with_sheets(
        df1: pd.DataFrame, 
        df2: pd.DataFrame, 
        df3: pd.DataFrame,
        nombres: list,
        output_path: str
) -> None:
    """
    Crea un archivo Excel con tres hojas, cada una conteniendo un DataFrame.

    Args:
        df1 (pd.DataFrame): Primer DataFrame a escribir en la primera hoja.
        df2 (pd.DataFrame): Segundo DataFrame a escribir en la segunda hoja.
        df3 (pd.DataFrame): Tercer DataFrame a escribir en la tercera hoja.
        nombres (list): Nombres de las respectivas sheets.
        output_path (str): Ruta donde se guardará el archivo Excel.
    """
    with pd.ExcelWriter(output_path) as writer:
        df1.to_excel(writer, sheet_name=nombres[0], index=False)
        df2.to_excel(writer, sheet_name=nombres[1], index=False)
        df3.to_excel(writer, sheet_name=nombres[2], index=False)

    print(f"Archivo Excel creado en: {output_path}")