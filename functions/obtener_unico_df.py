import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Union, get_args, get_origin

import numpy as np
import pandas as pd
from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.types import TypeDecorator
from sqlmodel import Field, Session, SQLModel, create_engine, delete
from utils import load_config

config = load_config()
data_paths = config["data_paths"]
engine = create_engine("sqlite:///database.db", echo=True)


# Diccionarios de mapeo: nombre original -> (nombre nuevo, tipo de dato)
personal_mapping = {  #
    "No. SAP": ("no_sap", "int"),
    "Nombre completo": ("nombre_completo", "str"),
    "Sociedad": ("sociedad", "str"),
    "Desc Soc": ("desc_soc", "str"),
    "Pais Soc": ("pais_soc", "str"),
    "Marketplace": ("marketplace", "str"),
    "Negocio": ("negocio", "str"),
    "Ce.Co.": ("ceco_personal", "str"),
    "Descripc.Ce.Co.": ("descrip_ceco", "str"),
    "Descripc.area organi": ("descrip_area", "str"),
    "Especialización": ("especializacion", "str"),
    "Descripc.larga Func.": ("descrip_larga_func", "str"),
    "Categoria Global": ("categoria_global", "str"),
    "Desc.Subdiv.pers.": ("desc_subdiv_pers", "str"),
    "Oficina": ("oficina_personal", "str"),
    "Oficina física": ("oficina_fisica", "str"),
    "Fec.ingres": ("fec_ingreso", "datetime"),
    "e-mail": ("email", "str"),
}

seunes_mapping = {  #
    "CÓDIGO CeCo": ("codigo_ceco", "str"),  #
    "DESCRIPCIÓN CeCo": ("descripcion_ceco", "str"),  #
    "MARKETPLACE": ("marketplace", "str"),  #
    "PAÍS": ("pais", "str"),  #
    "OFICINA ADMIN": ("oficina_seun", "str"),  #
    "LÍNEA DE SERVICIO": ("linea_servicio", "str"),  #
    "SAP SEUN": ("sap_seun", "int"),  #
    "SEUN": ("seun", "str"),  #
}

utilizaciones_mapping = {  #
    "No. de personal": ("no_personal_utilizacion", "int"),  #
    # "Centro coste emisor": ("Centro_coste_emisor", "str"),
    # "Nombre empl./cand.": ("Nombre_empl_cand", "str"),
    # "DenomFunc": ("DenomFunc", "str"),
    "Hrs. Real Per.": ("hrs_real_per", "float"),  #
    "Hrs. Est. Per.": ("hrs_est_per", "float"),  #
    # "% Real Ut. Per.": ("Porc_Real_Ut_Per", "float"),
    # "Hrs. Prespto. Per.": ("Hrs_Prespto_Per", "float"),
    # "Txt.breve un.org.": ("Txt_breve_un_org", "str"),
    # "Área pers.": ("Area_pers", "str"),
    # "DenAr.per.": ("DenAr_per", "str"),
    "% Meta Util.": ("porc_meta_util", "float"),  #
    # "Cuota": ("Cuota", "float"),
    # "Fecha Alta CeCo": ("Fecha_Alta_CeCo", "datetime"),
    "% Real Ut. Acu.": ("porc_real_ut_acu", "float"),  #
    # "Fecha Baja Ceco": ("Fecha_Baja_Ceco", "datetime"),
    # "Ing. Acu.": ("Ing_Acu", "float"),
    # "Unid.org.": ("Unid_org", "str"),
    # "Hrs. Programadas": ("Hrs_Programadas", "float"),
    # "SDiv.pers.": ("SDiv_pers", "str"),
    # "Ing. Per.": ("Ing_Per", "float"),
    # "Ing. Prespto. Per.": ("Ing_Prespto_Per", "float"),
    # "Clave de función": ("Clave_de_funcion", "str"),
    # "% Util. Programado": ("Porc_Util_Programado", "float"),
    # "Categoria RPI": ("Categoria_RPI", "str"),
    # "Dif. Prespto. vs Real Per.": ("Dif_Prespto_vs_Real_Per", "float"),
    # "Hrs. Est. Acu.": ("Hrs_Est_Acu", "float"),
    # "% Prespto. Ut. Per.": ("Porc_Prespto_Ut_Per", "float"),
    # "Hrs. Real Acu.": ("Hrs_Real_Acu", "float"),
    # "Hrs. Prespto. Acu.": ("Hrs_Prespto_Acu", "float"),
    # "Hrs. Var. Per.": ("Hrs_Var_Per", "float"),
    # "% Prespto. Ut. Acu.": ("Porc_Prespto_Ut_Acu", "float"),
    # "% Var. Ut. Per.": ("Porc_Var_Ut_Per", "float"),
    # "Hrs. Var. Acu.": ("Hrs_Var_Acu", "float"),
    # "% Var. Ut. Acu.": ("Porc_Var_Ut_Acu", "float"),
    # "Ing. Prespto. Acu.": ("Ing_Prespto_Acu", "float"),
    # "Dif. Prespto. vs Real Acu.": ("Dif_Prespto_vs_Real_Acu", "float"),
    # "Moneda": ("Moneda", "str"),
    # "Agrp.área personal": ("Agrp_area_personal", "str"),
    # "ID calend.días fest.": ("ID_calend_dias_fest", "str"),
    # "Agrp.subdiv.personal": ("Agrp_subdiv_personal", "str"),
    # "Regla p.plan h.tbjo.": ("Regla_p_plan_h_tbjo", "str"),
    # "Cantidad de Empleados": ("Cantidad_de_Empleados", "int"),
    # "Número de Días": ("Numero_de_Dias", "int"),
    # "Hrs. Trabajo por día": ("Hrs_Trabajo_por_dia", "float"),
    # "H E Programadas": ("HE_Programadas", "float"),
    # "H Dif. vs Ppto.": ("HDif_vs_Ppto", "float"),
    # "Hrs. Ppto EO": ("Hrs_Ppto_EO", "float"),
    # "Fec Ini CeCo": ("Fec_Ini_CeCo", "datetime"),
    # "Fec Fin Ceco": ("Fec_Fin_Ceco", "datetime"),
    # "Fecha Ingreso": ("Fecha_Ingreso", "datetime"),
    "Fecha Baja": ("fecha_baja", "datetime"),  #
    # "Categoría HC": ("Categoria_HC", "str"),
}

validaciones_mapping = {  #
    "Hras fact.": ("hras_fact", "float"),  #
    "Socio Responsable": ("Socio_Responsable", "str"),
    "Descrip. Ce.Co. Emisor": ("descrip_ceco", "str"),  #
    # "CPT Std.": ("CPT_Std", "str"),
    "Descrip. Función": ("descrip_funcion", "str"),  #
    "Ce.Co. Emisor": ("ceco_emisor", "str"),  #
    # "Ce.plan.PM": ("Ce_plan_PM", "str"),
    "IdsocioR": ("id_socio_r", "str"),
    "Gerente": ("Gerente", "str"),
    "Cuota": ("Cuota", "float"),
    "No. Personal": ("no_personal_validacion", "int"),  #
    "Counter": ("Counter", "int"),
    "Empleado": ("empleado", "str"),  #
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
    "Fecha": ("fecha", "datetime"),  #
    "Mes": ("mes", "int"),  #
    "IdGerente": ("IdGerente", "int"),
    "Status tratamiento": ("Status_tratamiento", "str"),
    "Hon Bruto": ("Hon_Bruto", "float"),
    "Hras no fact.": ("hras_no_fact", "float"),  #
    "Importe hras no fact.": ("Importe_hras_no_fact", "float"),
    "Texto Explicativo PT.1": ("texto_explicativo_pt1", "str"),  #
    # "Texto Explicativo PT.2": ("Texto_Explicativo_PT2", "str"),
    # "Texto Explicativo PT.3": ("Texto_Explicativo_PT3", "str"),
    "HonB-CancPlan (HONORARIO NETO)": ("honb_cancplan", "float"),  #
    # "Modificado Por": ("Modificado_Por", "str"),
    # "Unidad Org.": ("Unidad_Org", "str"),
    # "Ope.": ("Ope", "str"),
    # "Creado por": ("Creado_por", "str"),
    "% Canc.": ("porc_canc", "float"),  #
    # "Descrip. Unidad Org.": ("Descrip_Unidad_Org", "str"),
    # "Cl. Pres./abs.": ("Cl_Pres_abs", "str"),
    # "Descrip. Operación/Cl. Pres./abs.": ("Descrip_Operacion_Cl_Pres_abs", "str"),
}

socios_mapping = {  #
    "SAP": ("sap", "int"),
    "PROFESIONAL": ("profesional", "str"),
    "PAÍS": ("pais", "str"),
    "OFICINA": ("oficina", "str"),
    "LÍNEA": ("linea", "str"),
    "TIENE GRUPO ASIGNADO": ("tiene_grupo_asignado", "str"),
}

empleado_socio_mapping = {  #
    "SAP": ("sap", "int"),  #
    "PROFESIONAL": ("profesional", "str"),  #
    "MARKETPLACE": ("marketplace", "str"),  #
    "PAÍS": ("pais", "str"),  #
    "OFICINA ADMIN": ("oficina", "str"),  #
    "LÍNEA DE SERVICIO": ("linea_servicio", "str"),  #
    "CATEGORÍA": ("categoria", "str"),
    "CECO": ("ceco", "str"),
    "FECHA DE INGRESO": ("fecha_ingreso", "int"),
    "SAP SOCIO": ("sap_socio", "int"),
    "ASIGNACIÓN FY25": ("nombre_socio", "str"),
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


def strip_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Aplicar strip a todas las columnas de tipo string
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def get_combined_dataframe() -> pd.DataFrame:
    # Load dataframes
    df_personal = pd.read_excel(data_paths["file_personal"])
    df_seun = pd.read_excel(data_paths["file_seun"])
    df_utilizacion = pd.read_excel(data_paths["file_utilizacion"], sheet_name="Sheet1")
    df_validacion = pd.read_excel(data_paths["file_validacion"])
    # df_total_socios = pd.read_excel(
    #     data_paths["file_total_socios"], sheet_name="Total Socios"
    # )
    df_reporte_empleados = pd.read_excel(
        data_paths["file_total_socios"], sheet_name="Reporte de empleados", skiprows=1
    )

    df_validacion = df_validacion[
        df_validacion["Texto Explicativo PT.1"] == "No entregó reporte"
    ]

    # Rename and convert columns
    df_personal = rename_and_convert_columns(df_personal, personal_mapping)
    df_seun = rename_and_convert_columns(df_seun, seunes_mapping)
    df_utilizacion = rename_and_convert_columns(df_utilizacion, utilizaciones_mapping)
    df_validacion = rename_and_convert_columns(df_validacion, validaciones_mapping)
    # df_total_socios = rename_and_convert_columns(df_total_socios, socios_mapping)
    df_reporte_empleados = rename_and_convert_columns(
        df_reporte_empleados, empleado_socio_mapping
    )

    # Strip all columns
    df_personal = strip_all_columns(df_personal)
    df_seun = strip_all_columns(df_seun)
    df_utilizacion = strip_all_columns(df_utilizacion)
    df_validacion = strip_all_columns(df_validacion)
    # df_reporte_empleados = strip_all_columns(df_reporte_empleados)

    # Merge dataframes based on the keys specified
    df_merged = (
        df_validacion.merge(
            df_personal, left_on="no_personal_validacion", right_on="no_sap", how="left"
        )
        .merge(
            df_utilizacion,
            left_on="no_personal_validacion",
            right_on="no_personal_utilizacion",
            how="left",
        )
        .merge(
            df_reporte_empleados,
            left_on="no_personal_validacion",
            right_on="sap",
            how="left",
        )
        .merge(df_seun, left_on="ceco_personal", right_on="codigo_ceco", how="left")
    )

    # # Select the columns you want to keep
    # columns_to_keep = [
    #     "no_personal", "nombre_completo", "sociedad", "desc_soc", "pais_soc",
    #     "marketplace", "negocio", "ceco", "descrip_ceco", "descrip_area",
    #     "especializacion", "descrip_larga_func", "categoria_global", "desc_subdiv_pers",
    #     "oficina", "oficina_fisica", "fec_ingreso", "email", "hras_fact", "ceco_emisor",
    #     "descrip_ceco", "descrip_funcion", "fecha", "mes", "hras_no_fact", "honb_cancplan",
    #     "porc_canc", "texto_explicativo_pt1"
    # ]
    # df_merged = df_merged[columns_to_keep]

    # Drop duplicate columns if any
    df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]

    # Identify and drop columns with all null values
    all_null_columns = df_merged.columns[df_merged.isnull().all()]
    df_merged = df_merged.drop(columns=all_null_columns)

    all_null_columns_list = (
        all_null_columns.tolist()
    )  # Store the names of columns with all null values
    print("Columns with all null values:", all_null_columns_list)
    df_merged = df_merged.dropna(axis=1, how="all")  # Drop columns with all null values
    
    # Agregar la columna 'id'
    df_merged.insert(0, 'id', range(1, len(df_merged) + 1))

    return df_merged, all_null_columns_list


def save_combined_dataframe_to_db(df: pd.DataFrame):

    # Create SQLAlchemy engine
    engine = create_engine("sqlite:///database.db", echo=True)

    # Replace NaN values with None
    # Ensure column names are unique (case-insensitive)
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespaces
    df.columns = df.columns.str.lower()  # Convert to lowercase

    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Proceed with replacing NaN values and defining data types
    df = df.where(pd.notnull(df), None)

    # Define SQL data types for your columns
    dtype_mapping = {}
    for col in df.columns:
        if df[col].dtype.kind in ("i", "u"):  # integer types
            dtype_mapping[col] = Integer()
        elif df[col].dtype.kind == "f":  # float types
            dtype_mapping[col] = Float()
        elif df[col].dtype.kind == "M":  # datetime types
            dtype_mapping[col] = DateTime()
        else:
            dtype_mapping[col] = String()

    # Write DataFrame to SQL
    df.to_sql(
        "combined_table",
        con=engine,
        if_exists="replace",
        index=False,
        dtype=dtype_mapping,
    )


def get_df_combined():
    df_combined, all_null_columns_list = get_combined_dataframe()
    save_combined_dataframe_to_db(df_combined)

    # # Agrupar por 'seun' y contar el número de ocurrencias
    # seun_df = df_combined.groupby("seun").size().reset_index(name="counts")
    # print(seun_df)
    # seun_df_empleado = df_combined.groupby(["seun", "no_sap", "nombre_empleado"]).size().reset_index(name="counts")
    # seun_df_validacion = df_combined.groupby(["seun"]).size().reset_index(name="counts")
    # seun_df_utilizacion = df_combined.groupby(["seun"]).size().reset_index(name="counts")

    # # Agrupar por 'seun' y contar el número de ocurrencias
    # socio_df = df_combined.groupby("nombre_socio").size().reset_index(name="counts")
    # print(socio_df)

    # marketplace_df = (
    #     df_combined.groupby(["marketplace_x", "marketplace_y"])
    #     .size()
    #     .reset_index(name="counts")
    # )
    # print(marketplace_df)


if __name__ == "__main__":
    get_df_combined()
