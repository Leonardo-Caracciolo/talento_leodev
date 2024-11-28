import pandas as pd
import numpy as np
import datetime
import json
import os
from send_email import send_email, read_and_modify_html
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.utils import load_config
from dataframe_utils import create_excel_with_sheets, load_json_to_dataframe, generate_combined_json, generate_all_weeks, \
                            get_week_label, get_weekly_ranges


config = load_config()
data_paths = config["data_paths"]


def create_socio_utilizacion(json_path: str) -> pd.DataFrame:
    """Crea el DataFrame `df_socio_utilizacion` directamente desde un JSON."""
    df_combined_merge = load_json_to_dataframe(json_path)
    
    # Matchea con df_personal para obtener el mail de cada socio
    df_personal = pd.read_excel(data_paths["file_personal"]).dropna(how='all')
    df_personal = df_personal.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df_personal.rename(columns={'e-mail': 'e-mail-socio'}, inplace=True)

    df_socio_utilizacion = pd.merge(df_combined_merge, df_personal, left_on='SAP_Socio', right_on='No. SAP', how='left')

    df_grouped = df_socio_utilizacion.groupby('PROFESIONAL_y').size().reset_index(name='reportes_no_entregados')
    df_socio_utilizacion = pd.merge(df_socio_utilizacion, df_grouped, on='PROFESIONAL_y', how='left')

    columnas_requeridas = [
        'SAP_Socio',      # Sap del socio
        'PROFESIONAL_y',  # Socio
        'Empleado',       # Profesional asociado al socio
        '% UTILIZACIÓN (JUN - OCT)',  # Utilización acumulada
        '% UTILIZACIÓN MES',  # Meta de utilización %
        'reportes_no_entregados',
        'e-mail-socio'  # Email del socio
    ]

    for columna in columnas_requeridas:
        if columna not in df_socio_utilizacion.columns:
            raise ValueError(f"La columna {columna} no está presente en el JSON.")

    df_socio_utilizacion = df_socio_utilizacion[columnas_requeridas].copy()
    df_socio_utilizacion.rename(columns={
        'PROFESIONAL_y': 'Socio',
        'Empleado': 'Profesional',
        '% UTILIZACIÓN (JUN - OCT)': 'Utilización acumulada',
        '% UTILIZACIÓN MES': 'Meta de utilización %'
    }, inplace=True)

    df_socio_utilizacion = df_socio_utilizacion.drop_duplicates(subset=['Socio'], keep='first')

    return df_socio_utilizacion

def create_socio_data_resumen(json_path):
    """Crea el DataFrame `df_socio_data_resumen` directamente desde un JSON."""
    df_combined_merge = load_json_to_dataframe(json_path)

    if 'Fecha' in df_combined_merge.columns:
        df_combined_merge['Fecha'] = pd.to_datetime(df_combined_merge['Fecha'])
        # df_combined_merge['Semana'] = df_combined_merge['Fecha'].apply(get_week_label)

    # df_socio_data_resumen = df_combined_merge.groupby(['PROFESIONAL_y', 'Mes', 'Semana']).agg(
    #     reportes_no_entregados=('PROFESIONAL_y', 'count'),
    #     profesionales_sin_reporte=('PROFESIONAL_y', 'nunique')
    # ).reset_index()

    df_socio_data_resumen = df_combined_merge

    # all_weeks = []
    # for year_month in df_combined_merge['Fecha'].dt.to_period('M').unique():
    #     all_weeks.extend(generate_all_weeks())

    # all_combinations = pd.MultiIndex.from_product(
    #     [df_socio_data_resumen['Socio'].unique(), df_socio_data_resumen['Mes'].unique(), all_weeks],
    #     names=['Socio', 'Mes', 'Semana']
    # )

    weekly_ranges = get_weekly_ranges()
    filas_finales = []
    for start_date, end_date in weekly_ranges:
        # Filtrar las filas del DataFrame original dentro del rango de fechas
        mask = (df_socio_data_resumen['Fecha'] >= start_date) & (df_socio_data_resumen['Fecha'] <= end_date)
        filtered_df = df_socio_data_resumen.loc[mask]
        
         # Agrupar por 'Socio' (PROFESIONAL_y) y calcular el conteo y número único de 'SAP_Profesional'
        grouped_df = filtered_df.groupby('PROFESIONAL_y').agg(
            Mes=('Mes', 'first'),
            reportes_no_entregados=('Empleado', 'count'),
            profesionales_sin_reporte=('Empleado', 'nunique')
        ).reset_index()

        grouped_df.rename(columns={
            'PROFESIONAL_y': 'Socio'}, inplace=True)
        # grouped_df['Mes'] = filtered_df['Mes'][0] #?
        grouped_df['Semana'] = f"{start_date} - {end_date}"

        # grouped_df = grouped_df.drop_duplicates(subset=['Socio'], keep='last')
        # Agregar las filas al resultado final
        filas_finales.append(grouped_df)

    # Concatenar todos los DataFrames en uno solo
    df_socio_data_resumen = pd.concat(filas_finales, ignore_index=True)

    columnas_requeridas = [
        'Socio',
        'Mes',
        'Semana',
        'reportes_no_entregados',
        'profesionales_sin_reporte'
    ]

    df_socio_data_resumen = df_socio_data_resumen[columnas_requeridas].copy()
    df_socio_data_resumen.rename(columns={
        'reportes_no_entregados': 'Reportes no entregados',
        'profesionales_sin_reporte': 'Profesionales sin reporte'
    }, inplace=True)

    # df_socio_data_resumen = df_socio_data_resumen.set_index(['Socio', 'Mes', 'Semana']).reindex(all_combinations).reset_index()
    
    # Convierto los 'NaN' a 0
    df_socio_data_resumen['Reportes no entregados'] = df_socio_data_resumen['Reportes no entregados'].fillna(0)
    df_socio_data_resumen['Profesionales sin reporte'] = df_socio_data_resumen['Profesionales sin reporte'].fillna(0)
    # Convierto a int los campos numéricos
    df_socio_data_resumen['Reportes no entregados'] = df_socio_data_resumen['Reportes no entregados'].astype(int)
    df_socio_data_resumen['Profesionales sin reporte'] = df_socio_data_resumen['Profesionales sin reporte'].astype(int)
    df_socio_data_resumen['Mes'] = pd.to_numeric(df_socio_data_resumen['Mes'], errors='coerce').fillna(0).astype(int)

    return df_socio_data_resumen

def create_socio_data_detalle(json_path):
    """Crea el DataFrame `socio_data_detalle` directamente desde un JSON."""
    df_combined_merge = load_json_to_dataframe(json_path)

    columnas_requeridas = ['PROFESIONAL_y', 'Empleado', 'Fecha']
    for columna in columnas_requeridas:
        if columna not in df_combined_merge.columns:
            raise ValueError(f"La columna {columna} no está presente en el JSON.")

    df_socio_data_detalle = df_combined_merge[columnas_requeridas].copy()
    
    # Saco la hora de la fecha
    df_socio_data_detalle['Fecha'] = pd.to_datetime(df_socio_data_detalle['Fecha'])
    df_socio_data_detalle['Fecha'] = df_socio_data_detalle['Fecha'].dt.date

    df_socio_data_detalle.rename(columns={
        'PROFESIONAL_y': 'Socio',
        'Empleado': 'Profesional'
        # 'Fecha': 'Día'
    }, inplace=True)

    return df_socio_data_detalle

def create_socio_data_agrupado(json_path):
    """Crea el DataFrame `socio_data_agrupado` directamente desde un JSON."""
    df_combined_merge = load_json_to_dataframe(json_path)

    columnas_requeridas = ['PROFESIONAL_y', 'Empleado', 'Mes']
    for columna in columnas_requeridas:
        if columna not in df_combined_merge.columns:
            raise ValueError(f"La columna {columna} no está presente en el JSON.")

    df_socio_data_agrupado = (
        df_combined_merge.groupby(['PROFESIONAL_y', 'Empleado', 'Mes'])
        .size()
        .reset_index(name='Cantidad de apariciones')
    )

    df_socio_data_agrupado.rename(columns={
        'PROFESIONAL_y': 'Socio',
        'Empleado': 'Profesional'
    }, inplace=True)

    return df_socio_data_agrupado

def main():
    """Función principal que coordina todas las operaciones."""

    json_path = os.path.join(os.getcwd(), "combined_data.json")

    # Crear el JSON una sola vez
    if not os.path.exists(json_path):
        print("Generando el archivo JSON por primera vez...")
        generate_combined_json(json_path)
    else:
        print(f"Archivo JSON encontrado: {json_path}")
    

    # Obtener el mes actual
    lista_meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    mes_actual = datetime.datetime.now().month
    mes = lista_meses[mes_actual - 1]

    df_socio_utilizacion = create_socio_utilizacion(json_path) # Crear DataFrames desde el JSON
    df_socio_data_resumen = create_socio_data_resumen(json_path)
    df_socio_data_detalle = create_socio_data_detalle(json_path)
    df_socio_data_agrupado = create_socio_data_agrupado(json_path)

    for index, row in df_socio_utilizacion.iterrows():
        email = row.get('e-mail-socio', None)
        if pd.isna(email):
            print(f"No se encontró correo electrónico para el Socio: {row['Socio']}")
        else:
            socio = row.get('Socio', None)

            # Datatable resumen filtrado por el socio de la fila
            datatable_socio = df_socio_data_resumen[(df_socio_data_resumen['Socio']==row.get('Socio', None)) & (df_socio_data_resumen['Mes']==mes_actual -3)] #! sacar el -3

            html_content = read_and_modify_html(socio, plantilla='socio', datatable=datatable_socio)
            subject = f'IMPORTANTE - PROFESIONALES ASIGNADOS - BLUE TAX & CARGABILIDAD - {mes}'

            # Filtro el df_socio_data_detalle por el socio especifico
            df_socio_data_detalle_unique = df_socio_data_detalle[(df_socio_data_detalle['Socio']==row.get('Socio', None))]
            # Filtro el df_socio_data_agrupado por el socio especifico y el mes
            df_socio_data_agrupado_unique = df_socio_data_agrupado[(df_socio_data_agrupado['Socio']==row.get('Socio', None)) & (df_socio_data_agrupado['Mes']==mes_actual -3)] #! sacar el -3

            socio_excel = data_paths["file_archivo_adjunto_socio"]
            create_excel_with_sheets(datatable_socio, df_socio_data_detalle_unique, df_socio_data_agrupado_unique,
                                    nombres = ['socio_data_resumen', 'socio_data_detalle', 'socio_data_agrupado'],
                                    output_path=socio_excel)
            
            # send_email(email, html_content, subject) #! Descomentar en producción
            send_email("amiriarte@deloitte.com", html_content, subject, archivo_adjunto=socio_excel) #? Prueba
            # send_email("lecaracciolo@deloitte.com", html_content, subject, archivo_adjunto=socio_excel) #? Prueba
            print(f"{socio} - {email}") #! Quitar


if __name__ == "__main__":
    main()