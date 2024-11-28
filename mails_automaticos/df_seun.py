import pandas as pd
import os
from send_email import send_email, read_and_modify_html
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.utils import load_config

config = load_config()
data_paths = config["data_paths"]
from dataframe_utils import load_json_to_dataframe


def load_json_to_dataframe(json_path):
    """Carga un archivo JSON y lo convierte en un DataFrame."""
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return pd.DataFrame(data)
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo JSON no se encontró en la ruta: {json_path}")
    
    
def create_seun_utilizacion(df_combined_seun):
    """Extrae y renombra columnas específicas de un DataFrame para crear el DataFrame `df_seun_utilizacion`.

    Args:
        df_combined_seun (pd.DataFrame): DataFrame combinado que contiene los datos necesarios.

    Returns:
        pd.DataFrame: DataFrame resultante con las columnas seleccionadas y renombradas.
    """

    # Columnas requeridas
    columnas_requeridas = [
        'CÓDIGO CeCo',  # Código CeCo
        'SEUN', #SEUN
        'Empleado',     # Empleado asociado
        '% UTILIZACIÓN (JUN - OCT)',  # Utilización acumulada
        '% UTILIZACIÓN MES'  # Meta de utilización %
    ]

    # Verificar si las columnas están presentes en el DataFrame
    for columna in columnas_requeridas:
        if columna not in df_combined_seun.columns:
            raise ValueError(f"La columna {columna} no está presente en el DataFrame.")

    # Extraer y renombrar las columnas
    df_seun_utilizacion = df_combined_seun[columnas_requeridas].copy()
    df_seun_utilizacion.rename(columns={
        '% UTILIZACIÓN (JUN - OCT)': 'Utilización acumulada',
        '% UTILIZACIÓN MES': 'Meta de utilización %'
    }, inplace=True)

    return df_seun_utilizacion

def concatenar_json_to_dataframe(dataframe, json_path, columna_df, columna_json):
    """_Lee un archivo JSON y combina sus datos con los datos de un DF existente
    matcheando por la columna Ceco Emisor_

    Args:
        dataframe (_type_): _DataFrame existente_
        json_path (_type_): _Ruta del JSON_
        columna_df (_type_): _columna específica del DataFrame_
        columna_json (_type_): _columna específica del JSON_

    Returns:
        _pd.DataFrame_: _Retorna el dataframe resultante_
    """

    try:
        df_json = load_json_to_dataframe(json_path)

        df_json_ajustado = df_json.rename(columns={columna_json: columna_df})

        # Especifica sufijos para manejar nombres duplicados
        df_matched = pd.merge(dataframe, df_json_ajustado, on=columna_df, how='outer', suffixes=('_df', '_json'))

        return df_matched

    except Exception as e:
        print(f"Error al intentar concatenar el archivo JSON: {e}")
        return dataframe


# ToDo hacer los mails
def get_seun_emails():
    df_personal = pd.read_excel(data_paths["file_personal"]).dropna(how='all')
    
    df_emails = pd.DataFrame(df_personal)
    return df_emails

def create_seun_data_detalle(json_path):
    """Crea el DataFrame `seun_data_detalle` directamente desde un JSON."""
    df_combined_merge = load_json_to_dataframe(json_path)

    columnas_requeridas = ['PROFESIONAL_y', 'Empleado', 'Fecha']
    for columna in columnas_requeridas:
        if columna not in df_combined_merge.columns:
            raise ValueError(f"La columna {columna} no está presente en el JSON.")

    df_seun_data_detalle = df_combined_merge[columnas_requeridas].copy()

    df_seun_data_detalle.rename(columns={
        'PROFESIONAL_y': 'Socio',
        'Empleado': 'Profesional',
        'Fecha': 'Día'
    }, inplace=True)

    return df_seun_data_detalle


# seun utilizacion : Empleado', similar al de socio

def main():
    json_path = os.path.join(os.getcwd(), "combined_data.json")
    # df_mapeo_ceco_seun = pd.read_excel(data_paths["file_mapeo_cecos_y_seunes"]).dropna(how='all')
    # df_mapeo_ceco_seun = df_mapeo_ceco_seun.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # # df_combined_seun = df_mapeo_ceco_seun  # Suponiendo que ya tienes df_combined_seun
    # df_combined_seun = concatenar_json_to_dataframe(df_mapeo_ceco_seun, json_path, 'CÓDIGO CeCo', 'Ce.Co. Emisor')
    # df_seun_utilizacion = create_seun_utilizacion(df_combined_seun)
    
    df_seun_detalle = create_seun_data_detalle(json_path)

    # Merge emails into df_seun_utilizacion
    # df_emails = get_seun_emails()
    # df_seun_utilizacion = df_seun_utilizacion.merge(df_emails, on='SEUN', how='left')
    
    df_seun_utilizacion = load_json_to_dataframe(json_path)

    for index, row in df_seun_utilizacion.iterrows():
        email = row.get('e-mail', None)
        if pd.isna(email):
            print(f"No se encontró correo electrónico para el SEUN: {row['SEUN']}")
        else:
            seun = row.get('SEUN', None)
            html_content = read_and_modify_html(seun, plantilla = 'seun')
            subject = 'Utilización SEUN | Talento'
            send_email(email, html_content, subject)
    
    
if __name__ == "__main__":
    main()