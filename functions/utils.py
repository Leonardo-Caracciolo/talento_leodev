import json
import os


def exportar_tipos_de_datos(df, file_path):
    """
    Exporta los tipos de datos de las columnas de un DataFrame a un archivo de texto.

    :param df: DataFrame de pandas.
    :param file_path: Ruta del archivo de texto donde se exportarán los tipos de datos.

    Ejemplo de uso:
        exportar_tipos_de_datos(df_final, "tipos_de_datos.txt")
    """
    with open(file_path, "w", encoding="utf-8") as f:
        for column, dtype in df.dtypes.items():
            f.write(f"{column}: {dtype}\n")


def load_config():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    return config
