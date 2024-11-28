from df_socio import load_json_to_dataframe
import os
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.utils import load_config

config = load_config()
data_paths = config["data_paths"]


# def main():
    
#     json_path = os.path.join(os.getcwd(), "combined_data.json")
    
#     df_combined = load_json_to_dataframe(json_path)
    
#     print(df_combined)
# main()




# def created_seun_detalle():
#     """
#     Fusiona el DataFrame df_combined con df_mapeo_cecos_y_seunes usando la columna 'Ce.Co. Emisor'
#     de df_combined y la columna 'CÓDIGO CeCo' de df_mapeo_cecos_y_seunes.

#     Returns:
#     pd.DataFrame: DataFrame resultante de la fusión.
#     """

#     # Cargar el DataFrame desde el JSON
#     json_path = os.path.join(os.getcwd(), "combined_data.json")
#     df_combined = load_json_to_dataframe(json_path)

#     # Definir la ruta del archivo Excel
#     file_mapeo_cecos_y_seunes = data_paths["file_mapeo_cecos_y_seunes"]

#     # Cargar el DataFrame desde el archivo Excel
#     df_mapeo_cecos_y_seunes = pd.read_excel(file_mapeo_cecos_y_seunes).dropna(how='all')

#     # Renombrar la columna 'PAÍS' a 'PAÍS_CECO' en df_mapeo_cecos_y_seunes
#     df_mapeo_cecos_y_seunes.rename(columns={'PAÍS': 'PAÍS_CECO'}, inplace=True)

#     # Verificar que las columnas de unión no contengan valores faltantes
#     if df_combined['Ce.Co. Emisor'].isnull().any():
#         print("Advertencia: 'Ce.Co. Emisor' contiene valores faltantes.")
#     if df_mapeo_cecos_y_seunes['CÓDIGO CeCo'].isnull().any():
#         print("Advertencia: 'CÓDIGO CeCo' contiene valores faltantes.")

#     # Asegurarse de que las columnas de unión sean del mismo tipo
#     df_combined['Ce.Co. Emisor'] = df_combined['Ce.Co. Emisor'].astype(str).str.strip()
#     df_mapeo_cecos_y_seunes['CÓDIGO CeCo'] = df_mapeo_cecos_y_seunes['CÓDIGO CeCo'].astype(str).str.strip()

#     # Imprimimos las primeras filas de los DataFrames para verificar las columnas de unión
#     # print("Primeras filas de df_combined:")
#     # print(df_combined[['Ce.Co. Emisor']].head())
#     # print("Primeras filas de df_mapeo_cecos_y_seunes:")
#     # print(df_mapeo_cecos_y_seunes[['CÓDIGO CeCo']].head())

#     # Verificamos si hay valores únicos en las columnas de unión
#     # print("Valores únicos en 'Ce.Co. Emisor' en df_combined:")
#     # print(df_combined['Ce.Co. Emisor'].unique())
#     # print("Valores únicos en 'CÓDIGO CeCo' en df_mapeo_cecos_y_seunes:")
#     # print(df_mapeo_cecos_y_seunes['CÓDIGO CeCo'].unique())

#     # Comparamos los valores específicos de las columnas de unión
#     # print("Muestra de valores 'Ce.Co. Emisor' en df_combined:")
#     # print(df_combined['Ce.Co. Emisor'].sample(10, random_state=1))
#     # print("Muestra de valores 'CÓDIGO CeCo' en df_mapeo_cecos_y_seunes:")
#     # print(df_mapeo_cecos_y_seunes['CÓDIGO CeCo'].sample(10, random_state=1))

#     # Realizar el merge de los dos DataFrames
#     df_merged = pd.merge(df_combined, df_mapeo_cecos_y_seunes, how='left', left_on='Ce.Co. Emisor', right_on='CÓDIGO CeCo')

#     # Mostrar el resultado
#     print("Primeras filas del DataFrame resultante:")
#     print(df_merged.head())

#     # Mostrar las columnas nuevas agregadas y cuántos valores nulos tienen
#     new_columns = set(df_mapeo_cecos_y_seunes.columns) - set(df_combined.columns)
#     for col in new_columns:
#         print(f"Columna '{col}' agregada tiene {df_merged[col].isnull().sum()} valores nulos.")

#     return df_merged

# created_seun_detalle()



def created_seun_detalle():
    """
    Fusiona el DataFrame df_combined con df_mapeo_cecos_y_seunes usando la columna 'Ce.Co. Emisor'
    de df_combined y la columna 'CÓDIGO CeCo' de df_mapeo_cecos_y_seunes, y luego agrupa el
    DataFrame resultante por 'Empleado', 'Fecha' y 'SEUN', manteniendo solo estas columnas.
    Finalmente, ordena el DataFrame por la columna 'SEUN'.

    Returns:
    pd.DataFrame: DataFrame resultante de la fusión, agrupación y ordenación, con solo las columnas 'Empleado', 'Fecha' y 'SEUN'.
    """

    # Definir la ruta del archivo JSON
    json_path = os.path.join(os.getcwd(), "combined_data.json")

    # Cargar el DataFrame desde el JSON
    df_combined = load_json_to_dataframe(json_path)

    # Cargar el DataFrame desde el archivo Excel usando data_paths
    df_mapeo_cecos_y_seunes = pd.read_excel(data_paths["file_mapeo_cecos_y_seunes"]).dropna(how='all')

    # Renombrar la columna 'PAÍS' a 'PAÍS_CECO' en df_mapeo_cecos_y_seunes
    df_mapeo_cecos_y_seunes.rename(columns={'PAÍS': 'PAÍS_CECO'}, inplace=True)

    # Verificar que las columnas de unión no contengan valores faltantes
    if df_combined['Ce.Co. Emisor'].isnull().any():
        print("Advertencia: 'Ce.Co. Emisor' contiene valores faltantes.")
    if df_mapeo_cecos_y_seunes['CÓDIGO CeCo'].isnull().any():
        print("Advertencia: 'CÓDIGO CeCo' contiene valores faltantes.")

    # Asegurarse de que las columnas de unión sean del mismo tipo
    df_combined['Ce.Co. Emisor'] = df_combined['Ce.Co. Emisor'].astype(str).str.strip()
    df_mapeo_cecos_y_seunes['CÓDIGO CeCo'] = df_mapeo_cecos_y_seunes['CÓDIGO CeCo'].astype(str).str.strip()

    # Realizar el merge de los dos DataFrames
    df_merged = pd.merge(df_combined, df_mapeo_cecos_y_seunes, how='left', left_on='Ce.Co. Emisor', right_on='CÓDIGO CeCo')

    # Mostrar las columnas nuevas agregadas y cuántos valores nulos tienen
    new_columns = set(df_mapeo_cecos_y_seunes.columns) - set(df_combined.columns)
    for col in new_columns:
        print(f"Columna '{col}' agregada tiene {df_merged[col].isnull().sum()} valores nulos.")

    # Agrupar el DataFrame resultante por 'Empleado', 'Fecha' y 'SEUN'
    df_grouped = df_merged.groupby(['Empleado', 'Fecha', 'SEUN']).size().reset_index(name='count')

    # Mantener solo las columnas 'Empleado', 'Fecha' y 'SEUN'
    df_final = df_grouped[['Empleado', 'Fecha', 'SEUN']]

    # Ordenar el DataFrame por la columna 'SEUN'
    df_final_sorted = df_final.sort_values(by='SEUN').reset_index(drop=True)

    # Mostrar el DataFrame final ordenado
    print("DataFrame final ordenado:")
    print(df_final_sorted.head())

    return df_final_sorted
    
    
created_seun_detalle()