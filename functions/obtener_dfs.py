"""
Este módulo proporciona funciones para cargar, transformar y almacenar datos en la base de datos.

Funciones:
- get_file_hashes: Obtiene los hashes de los archivos de datos.
- create_hashes_table_if_not_exists: Crea la tabla de hashes si no existe.
- save_dataframe_to_db: Guarda un DataFrame en la base de datos.
- rename_and_convert_columns: Renombra y convierte las columnas de un DataFrame según un diccionario de mapeo.
- verify_and_update_data: Verifica y actualiza los datos en la base de datos si los archivos han cambiado.

Mapeos:
- personal_mapping: Diccionario de mapeo para el DataFrame de personal.
- seun_mapping: Diccionario de mapeo para el DataFrame de SEUN.
- utilizacion_mapping: Diccionario de mapeo para el DataFrame de utilización.
- validacion_mapping: Diccionario de mapeo para el DataFrame de validación.

Uso:
1. Cargar los datos desde archivos Excel.
2. Renombrar y convertir las columnas utilizando rename_and_convert_columns.
3. Guardar los DataFrames en la base de datos utilizando save_dataframe_to_db.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib

import pandas as pd
from sqlmodel import Session, SQLModel, delete, select
import sqlite3

from app.database import (
    engine,
    get_session,
    create_table_aggregated_seun_data,
    create_table_aggregated_pais_count_data,
    create_table_aggregated_pais_distinct_data,
    create_table_aggregated_pais_data,
    create_table_aggregated_oficina_count_data,
    create_table_aggregated_oficina_distinct_data,
    create_table_aggregated_socio_data_resumen,
    create_table_aggregated_socio_data_agrupado,
    create_table_aggregated_socio_data_detalle,
    create_table_market_place_data_resumen
)

from app.models import DFPersonal, DFSeun, DFUtilizacion, DFValidacion, Hash, DFTotalSocios, DFReporteEmpleados, DFUtilizacionActual
from functions.utils import load_config
# Configurar el módulo logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

config = load_config()
data_paths = config["data_paths"]


def get_file_hashes() -> Dict[str, str]:
    files = [
        data_paths["file_personal"],
        data_paths["file_seun"],
        data_paths["file_utilizacion"],
        data_paths["file_validacion"],
        data_paths["file_total_socios"],
        data_paths["file_utilizacion_actual"]
        # "data/inputs/test/personal.xlsx",
        # "data/inputs/test/seun.xlsx",
        # "data/inputs/test/utilizacion.xlsx",
        # "data/inputs/test/validacion.xlsx",
    ]
    hashes = {}
    for file in files:
        with open(file, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
            hashes[file] = file_hash
    return hashes


def create_hashes_table_if_not_exists(engine) -> None:
    SQLModel.metadata.create_all(engine)


def save_dataframe_to_db(df: pd.DataFrame, model):
    # Verificar que todas las columnas necesarias estén presentes
    required_columns = [
        col.name for col in model.__table__.columns if col.nullable is False
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Obtener la fecha de mañana
    tomorrow = datetime.now() + timedelta(days=1)

    records = df.to_dict(orient="records")
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, pd.Timestamp):
                record[key] = value.to_pydatetime()
            elif isinstance(value, int) and key in [
                "Fecha_Baja",
                "Fecha_Alta_CeCo",
                "Fecha_Ingreso",
            ]:  # Add all datetime columns here
                record[key] = None  # Set invalid datetime values to None
            elif (
                key == "Fecha_Baja"
                and isinstance(value, datetime)
                and value >= tomorrow
            ):
                record[key] = None  # Set future dates to None

    with get_session() as session:
        session.exec(delete(model))
        session.bulk_insert_mappings(model, records)
        session.commit()


# Diccionarios de mapeo: nombre original -> (nombre nuevo, tipo de dato)
personal_mapping = {
    "No. SAP": ("No_SAP", "int"),
    "Nombre completo": ("Nombre_completo", "str"),
    "Sociedad": ("Sociedad", "str"),
    "Desc Soc": ("Desc_Soc", "str"),
    "Pais Soc": ("Pais_Soc", "str"),
    "Marketplace": ("Marketplace", "str"),
    "Negocio": ("Negocio", "str"),
    "Ce.Co.": ("Ce_Co", "str"),
    "Descripc.Ce.Co.": ("Descripc_Ce_Co", "str"),
    "Descripc.area organi": ("Descripc_area_organi", "str"),
    "Especialización": ("Especializacion", "str"),
    "Descripc.larga Func.": ("Descripc_larga_Func", "str"),
    "Categoria Global": ("Categoria_Global", "str"),
    "Desc.Subdiv.pers.": ("Desc_Subdiv_pers", "str"),
    "Oficina": ("Oficina", "str"),
    "Oficina física": ("Oficina_fisica", "str"),
    "Fec.ingres": ("Fec_ingres", "datetime"),
    "e-mail": ("email", "str"),
}

seun_mapping = {
    "CÓDIGO CeCo": ("Codigo_CeCo", "str"),
    "DESCRIPCIÓN CeCo": ("Descripcion_CeCo", "str"),
    "MARKETPLACE": ("Market_Place", "str"),
    "PAÍS": ("Pais", "str"),
    "OFICINA ADMIN": ("Oficina_Admin", "str"),
    "LÍNEA DE SERVICIO": ("Linea_de_Servicios", "str"),
    "SAP SEUN": ("SAP_Seun", "int"),
    "SEUN": ("Seun", "str"),
}

utilizacion_mapping = {
    "No. de personal": ("No_personal", "int"),
    "Centro coste emisor": ("Centro_coste_emisor", "str"),
    "Nombre empl./cand.": ("Nombre_empl_cand", "str"),
    "DenomFunc": ("DenomFunc", "str"),
    "Hrs. Real Per.": ("Hrs_Real_Per", "float"),
    "Hrs. Est. Per.": ("Hrs_Est_Per", "float"),
    "% Real Ut. Per.": ("Porc_Real_Ut_Per", "float"),
    "Hrs. Prespto. Per.": ("Hrs_Prespto_Per", "float"),
    "Txt.breve un.org.": ("Txt_breve_un_org", "str"),
    "Área pers.": ("Area_pers", "str"),
    "DenAr.per.": ("DenAr_per", "str"),
    "% Meta Util.": ("Porc_Meta_Util", "float"),
    "Cuota": ("Cuota", "float"),
    "Fecha Alta CeCo": ("Fecha_Alta_CeCo", "datetime"),
    "% Real Ut. Acu.": ("Porc_Real_Ut_Acu", "float"),
    "Fecha Baja Ceco": ("Fecha_Baja_Ceco", "datetime"),
    "Ing. Acu.": ("Ing_Acu", "float"),
    "Unid.org.": ("Unid_org", "str"),
    "Hrs. Programadas": ("Hrs_Programadas", "float"),
    "SDiv.pers.": ("SDiv_pers", "str"),
    "Ing. Per.": ("Ing_Per", "float"),
    "Ing. Prespto. Per.": ("Ing_Prespto_Per", "float"),
    "Clave de función": ("Clave_de_funcion", "str"),
    "% Util. Programado": ("Porc_Util_Programado", "float"),
    "Categoria RPI": ("Categoria_RPI", "str"),
    "Dif. Prespto. vs Real Per.": ("Dif_Prespto_vs_Real_Per", "float"),
    "Hrs. Est. Acu.": ("Hrs_Est_Acu", "float"),
    "% Prespto. Ut. Per.": ("Porc_Prespto_Ut_Per", "float"),
    "Hrs. Real Acu.": ("Hrs_Real_Acu", "float"),
    "Hrs. Prespto. Acu.": ("Hrs_Prespto_Acu", "float"),
    "Hrs. Var. Per.": ("Hrs_Var_Per", "float"),
    "% Prespto. Ut. Acu.": ("Porc_Prespto_Ut_Acu", "float"),
    "% Var. Ut. Per.": ("Porc_Var_Ut_Per", "float"),
    "Hrs. Var. Acu.": ("Hrs_Var_Acu", "float"),
    "% Var. Ut. Acu.": ("Porc_Var_Ut_Acu", "float"),
    "Ing. Prespto. Acu.": ("Ing_Prespto_Acu", "float"),
    "Dif. Prespto. vs Real Acu.": ("Dif_Prespto_vs_Real_Acu", "float"),
    "Moneda": ("Moneda", "str"),
    "Agrp.área personal": ("Agrp_area_personal", "str"),
    "ID calend.días fest.": ("ID_calend_dias_fest", "str"),
    "Agrp.subdiv.personal": ("Agrp_subdiv_personal", "str"),
    "Regla p.plan h.tbjo.": ("Regla_p_plan_h_tbjo", "str"),
    "Cantidad de Empleados": ("Cantidad_de_Empleados", "int"),
    "Número de Días": ("Numero_de_Dias", "int"),
    "Hrs. Trabajo por día": ("Hrs_Trabajo_por_dia", "float"),
    "H E Programadas": ("HE_Programadas", "float"),
    "H Dif. vs Ppto.": ("HDif_vs_Ppto", "float"),
    "Hrs. Ppto EO": ("Hrs_Ppto_EO", "float"),
    "Fec Ini CeCo": ("Fec_Ini_CeCo", "datetime"),
    "Fec Fin Ceco": ("Fec_Fin_Ceco", "datetime"),
    "Fecha Ingreso": ("Fecha_Ingreso", "datetime"),
    "Fecha Baja": ("Fecha_Baja", "datetime"),
    "Categoría HC": ("Categoria_HC", "str"),
}

validacion_mapping = {
    "Hras fact.": ("Hras_fact", "float"),
    "Socio Responsable": ("Socio_Responsable", "str"),
    "Descrip. Ce.Co. Emisor": ("Descrip_CeCo_Emisor", "str"),
    "CPT Std.": ("CPT_Std", "str"),
    "Descrip. Función": ("Descrip_Funcion", "str"),
    "Ce.Co. Emisor": ("CeCo_emisor", "str"),
    "Ce.plan.PM": ("Ce_plan_PM", "str"),
    "IdsocioR": ("IdsocioR", "str"),
    "Gerente": ("Gerente", "str"),
    "Cuota": ("Cuota", "float"),
    "No. Personal": ("No_personal", "int"),
    "Counter": ("Counter", "int"),
    "Empleado": ("Empleado", "str"),
    "No cliente": ("No_cliente", "int"),
    "Fecha mod.": ("Fecha_mod", "datetime"),
    "Función": ("Funcion", "str"),
    "Razón social": ("Razon_social", "str"),
    "Orden": ("Orden", "int"),
    "Hra mod.": ("Hra_mod", "str"),
    "Descrip. Orden": ("Descrip_Orden", "str"),
    "Id Oportunidad": ("Id_Oportunidad", "int"),
    "Mon.": ("Moneda", "str"),
    "CeCo Orden": ("CeCo_Orden", "str"),
    "Oficina": ("Oficina", "str"),
    "Fecha": ("Fecha", "datetime"),
    "Mes": ("Mes", "int"),
    "IdGerente": ("IdGerente", "int"),
    "Status tratamiento": ("Status_tratamiento", "str"),
    "Hon Bruto": ("Hon_Bruto", "float"),
    "Hras no fact.": ("Hras_no_fact", "float"),
    "Importe hras no fact.": ("Importe_hras_no_fact", "float"),
    "Texto Explicativo PT.1": ("Texto_Explicativo_PT1", "str"),
    "Texto Explicativo PT.2": ("Texto_Explicativo_PT2", "str"),
    "Texto Explicativo PT.3": ("Texto_Explicativo_PT3", "str"),
    "HonB-CancPlan (HONORARIO NETO)": ("HonB_CancPlan", "float"),
    "Modificado Por": ("Modificado_Por", "str"),
    "Unidad Org.": ("Unidad_Org", "str"),
    "Ope.": ("Ope", "str"),
    "Creado por": ("Creado_por", "str"),
    "% Canc.": ("Porc_Canc", "float"),
    "Descrip. Unidad Org.": ("Descrip_Unidad_Org", "str"),
    "Cl. Pres./abs.": ("Cl_Pres_abs", "str"),
    "Descrip. Operación/Cl. Pres./abs.": ("Descrip_Operacion_Cl_Pres_abs", "str"),
}

total_socios_maping = {
    "SAP" : ("SAP", "int"), 
    "PROFESIONAL": ("Profesional", "str"),
    "PAÍS": ("Pais","str"),
    "OFICINA": ("Oficina","str"),
    "LÍNEA": ("Linea","str"),
    "TIENE GRUPO ASIGNADO": ("Tiene_Grupo_Asignado","str")
}

reporte_empleados_maping = {
    "SAP" : ("SAP", "int"), 
    "PROFESIONAL": ("Profesional", "str"),
    "MARKETPLACE": ("Marketplace","str"),
    "PAÍS": ("Pais","str"),
    "OFICINA ADMIN": ("Oficina_Admin","str"),
    "LÍNEA DE SERVICIO": ("Linea_De_Servicio","str"),
    "CATEGORÍA": ("Categoria","str"),
    "CECO": ("CeCo","str"),
    "FECHA DE INGRESO": ("Fecha_De_Ingreso","int"),
    "SAP SOCIO": ("SAP_Socio","int"),
    "ASIGNACIÓN FY25": ("Asignacion_FY25","str")
}


utilizacion_mapping_actualizado = {
    "SAP": ("SAP", "int"),
    "PROFESIONAL": ("Profesional", "str"),
    "MARKETPLACE": ("Marketplace", "str"),
    "PAÍS": ("Pais", "str"),
    "OFICINA": ("Oficina", "str"),
    "LÍNEA DE SERVICIO": ("Linea_de_Servicio", "str"),
    "CATEGORÍA": ("Categoria", "str"),
    "CECO": ("CeCo", "str"),
    "HRS. FACTURABLES MES": ("Horas_Facturables_Mes", "float"),
    "HRS. TEÓRICAS MES": ("Horas_Teoricas_Mes", "float"),
    "% UTILIZACIÓN MES": ("Porcentaje_Utilizacion_Mes", "str"),
    "HRS. FACTURABLES (JUN - OCT)": ("Horas_Facturables_Periodo", "float"),
    "HRS. TEÓRICAS (JUN - OCT)": ("Horas_Teoricas_Periodo", "float"),
    "% UTILIZACIÓN (JUN - OCT)": ("Porcentaje_Utilizacion_Periodo", "str"),
    
}


def rename_and_convert_columns(
    df: pd.DataFrame, mapping: Dict[str, Tuple[str, str]]
) -> pd.DataFrame:
    # Renombrar las columnas primero
    df = df.rename(columns={orig: new for orig, (new, _) in mapping.items()})

    # Convertir los tipos de datos
    for orig, (new, dtype) in mapping.items():
        if new in df.columns:
            if dtype == "datetime":
                df[new] = pd.to_datetime(df[new], errors="coerce")
            else:
                df[new] = df[new].astype(dtype, errors="ignore")
        else:
            print(f"Warning: Column '{new}' not found in DataFrame.")
    return df


def get_merged_dataframes() -> (
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
):
    fecha_actual = datetime.now()
    df_personal = pd.read_excel(data_paths["file_personal"])
    df_seun = pd.read_excel(data_paths["file_seun"])
    df_utilizacion = pd.read_excel(data_paths["file_utilizacion"], sheet_name = 'Sheet1')
    # df_utilizacion = pd.read_excel(r"C:\Users\lecaracciolo\OneDrive - Deloitte (O365D)\Desktop\Leonardo\Tasks\20 - Talento\talento_sqlmodel\data\inputs\test\utilizacion.xlsx", sheet_name = 'Sheet1')
    # df_utilizacion = pd.read_excel(r"C:\Users\lecaracciolo\OneDrive - Deloitte (O365D)\Desktop\Leonardo\Tasks\20 - Talento\talento_sqlmodel\data\inputs\produccion\utilizacion.xlsx", sheet_name = 'Sheet1')
    df_validacion = pd.read_excel(data_paths["file_validacion"])

    df_utilizacion_actual = pd.read_excel(data_paths['file_utilizacion_actual'])
    
    # Renombrar y convertir las columnas de cada DataFrame
    df_personal = rename_and_convert_columns(df_personal, personal_mapping)
    
    df_seun = rename_and_convert_columns(df_seun, seun_mapping)
    
    df_utilizacion_actual = rename_and_convert_columns(df_utilizacion_actual, utilizacion_mapping_actualizado)
    
    #Elimina espacios del Codigo_Ceco
    # df_seun['Codigo_CeCo'] = df_seun['Codigo_CeCo'].str.strip()
    
    df_utilizacion = rename_and_convert_columns(df_utilizacion, utilizacion_mapping)
    df_validacion = rename_and_convert_columns(df_validacion, validacion_mapping)
    
    #Elimina espacios del CeCo_emisor
    # df_validacion['CeCo_emisor'] = df_validacion['CeCo_emisor'].str.strip()

    # Filtrar registros donde 'Texto_Explicativo_PT1' sea 'No entregó reporte'
    df_validacion = df_validacion[
        df_validacion["Texto_Explicativo_PT1"] == "No entregó reporte"
    ]

    # Eliminar filas con valores nulos en las columnas especificadas
    df_utilizacion.dropna(subset=["No_personal"], inplace=True)
    df_seun.dropna(inplace=True)

    # Reemplazar todos los valores NaN por 0 en los DataFrames
    df_personal.fillna({"No_SAP": 0}, inplace=True)
    df_seun.fillna(0, inplace=True)
    df_utilizacion.fillna(0, inplace=True)
    df_validacion.fillna(0, inplace=True)
    
    #Desconsiderar personas con fecha baja menor a fecha actual en df_utilizacion    
    
    df_utilizacion['Fecha_Baja'] = pd.to_datetime(df_utilizacion['Fecha_Baja'], format='%Y-%m-%d %H:%M:%S', errors= 'coerce')
    df_utilizacion = df_utilizacion[df_utilizacion['Fecha_Baja'] >= fecha_actual]
    
    # Agregar columna 'id' única a cada DataFrame
    df_personal["id"] = range(1, len(df_personal) + 1)
    df_seun["id"] = range(1, len(df_seun) + 1)
    df_utilizacion["id"] = range(1, len(df_utilizacion) + 1)
    df_validacion["id"] = range(1, len(df_validacion) + 1)
    df_utilizacion_actual["id"] = range(1, len(df_utilizacion_actual) + 1)
    
    
    #Df Total Socios
    df_total_socios = pd.read_excel(data_paths["file_total_socios"], sheet_name='Total Socios') 
    df_total_socios = rename_and_convert_columns(df_total_socios, total_socios_maping)
    df_total_socios["id"] = range(1, len(df_total_socios) + 1)
    
    #DF Reporte Empleados
    df_reporte_empleados = pd.read_excel(data_paths["file_total_socios"], sheet_name = 'Reporte de empleados',skiprows=1) 
    
    df_reporte_empleados = rename_and_convert_columns(df_reporte_empleados, reporte_empleados_maping)    
    
    df_reporte_empleados["id"] = range(1, len(df_reporte_empleados) + 1)
    df_reporte_empleados = df_reporte_empleados.dropna(subset=['SAP_Socio'])


    print(f"---------------------------------------RETURN DF_VALIDACION--------------------------------------------------------------------")
    print(df_validacion)
    print(f"---------------------------------------------------------------------------------------------------------------------")
    return df_personal, df_seun, df_utilizacion, df_validacion, df_total_socios, df_reporte_empleados, df_utilizacion_actual


def listar_tablas(nombre_bd):
    # Función para listar todas las tablas en la base de datos SQLite
    conn = sqlite3.connect(nombre_bd)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tablas

def exportar_tablas_a_excel(nombre_bd, tablas, nombre_archivo_excel):
    """
    Exporta varias tablas de una base de datos SQLite a un archivo Excel,
    donde cada tabla es una hoja separada. Si el archivo no existe, se creará.

    :param nombre_bd: Nombre o ruta de la base de datos SQLite.
    :param tablas: Lista con los nombres de las tablas a exportar.
    :param nombre_archivo_excel: Nombre del archivo Excel de salida.
    """
    # Verificar que las tablas existen en la base de datos
    tablas_disponibles = listar_tablas(nombre_bd)
    tablas = [tabla for tabla in tablas if tabla in tablas_disponibles]

    if not tablas:
        print("No se encontraron tablas para exportar.")
        return

    # Verifica que el nombre del archivo de salida tenga la extensión correcta
    if not nombre_archivo_excel.endswith('.xlsx'):
        nombre_archivo_excel += '.xlsx'

    # Conecta a la base de datos SQLite
    conn = sqlite3.connect(nombre_bd)

    # Usa ExcelWriter para manejar múltiples hojas
    with pd.ExcelWriter(nombre_archivo_excel, engine='openpyxl') as writer:
        for tabla in tablas:
            # Lee cada tabla y exporta a una hoja separada en el archivo Excel
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            df.to_excel(writer, sheet_name=tabla, index=False)

    print(f"Datos exportados exitosamente a {nombre_archivo_excel}")

    # Cierra la conexión a la base de datos
    conn.close()


#Recibe 4 DF y crea una sheet por cada DF correspondiente
def guardar_dataframes_en_excel(df1, df2, df3, df4, archivo_salida='Excel_Resumen.xlsx'):
    # Crear un objeto de ExcelWriter usando openpyxl como motor
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        # Escribir cada dataframe en una hoja separada
        df1.to_excel(writer, sheet_name='Resumen', index=False)
        df2.to_excel(writer, sheet_name='Agrupado', index=False)
        df3.to_excel(writer, sheet_name='Detalle', index=False)
        df4.to_excel(writer, sheet_name='Utilizacion', index=False)

#Aplica strip a todas las columnas
def strip_all_columns(df):
    """
    Aplica el método strip() a todos los valores de todas las columnas en un DataFrame.
    """
    df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else x)
    return df

def verify_and_update_data():
    create_hashes_table_if_not_exists(engine)
    hashes_actuales = get_file_hashes()

    with get_session() as session:
        hashes_almacenados = {
            hash.file: hash.hash for hash in session.exec(select(Hash)).all()
        }

    #! Descomentar para que la función siempre recalcule los datos
    # recalcular = True
    recalcular = False
    for file, hash_actual in hashes_actuales.items():
        if hashes_almacenados.get(file) != hash_actual:
            recalcular = True
            break

    
    if recalcular:
        df_personal, df_seun, df_utilizacion, df_validacion, df_total_socios, df_reporte_empleados, df_utilizacion_actual = get_merged_dataframes()
        save_dataframe_to_db(df_personal, DFPersonal)
        save_dataframe_to_db(df_seun, DFSeun)
        save_dataframe_to_db(df_utilizacion, DFUtilizacion)
        save_dataframe_to_db(df_validacion, DFValidacion)
        save_dataframe_to_db(df_total_socios, DFTotalSocios)
        save_dataframe_to_db(df_reporte_empleados, DFReporteEmpleados)
        save_dataframe_to_db(df_utilizacion_actual,DFUtilizacionActual)

        with get_session() as session:
            session.exec(delete(Hash))
            for file, hash_actual in hashes_actuales.items():
                session.add(Hash(file=file, hash=hash_actual))
            session.commit()
        create_table_aggregated_seun_data() #!
        # create_table_aggregated_pais_count_data()
        # create_table_aggregated_pais_distinct_data()
        # create_table_aggregated_pais_data()
        # create_table_aggregated_oficina_count_data()
        # create_table_aggregated_oficina_distinct_data()

        #Socio
        create_table_aggregated_socio_data_resumen()
        create_table_aggregated_socio_data_agrupado()
        create_table_aggregated_socio_data_detalle()
        create_table_market_place_data_resumen()
        
        ruta_db = r"C:\Users\lecaracciolo\OneDrive - Deloitte (O365D)\Desktop\Leonardo\Tasks\20 - Talento\talento_sqlmodel\data\data.db"
        ruta_excel = r"C:\Users\lecaracciolo\OneDrive - Deloitte (O365D)\Desktop\Leonardo\Tasks\20 - Talento\talento_sqlmodel\data\inputs\test\Excel_Resumen"
        
        #!
        # exportar_tablas_a_excel(ruta_db, ['aggregated_socio_data_resumen','aggregated_socio_data_agrupado','aggregated_socio_data_detalle'],ruta_excel)
        
        logging.info("La base de datos ha sido actualizada con los nuevos datos.")
    else:
        logging.info(
            "Los archivos no han cambiado. No es necesario recalcular los datos."
        )
       


    

if __name__ == "__main__":
    verify_and_update_data()
