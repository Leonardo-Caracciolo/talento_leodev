import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

# Asegúrate de que la ruta sea relativa al directorio raíz del proyecto
# DATABASE_URL = "sqlite:///./data/data.db"
DATABASE_URL = "sqlite:///./database.db" #! CAMBIO DB
engine = create_engine(DATABASE_URL)


def init_db():
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(DATABASE_URL.split("///")[1]), exist_ok=True)
    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


def create_table_aggregated_seun_data():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_seun_data"))
        connection.execute(
            text(
                """
        CREATE TABLE aggregated_seun_data AS
        SELECT
            IFNULL (Mes, 0) AS Mes,
            marketplace_x AS Market_Place,
            linea_servicio_x AS Linea_de_Servicios,
            pais_soc AS Pais,
            oficina_fisica AS Oficina_fisica,
            codigo_ceco AS Codigo_CeCo,
            descripcion_ceco AS Descripcion_CeCo,
            COUNT(no_personal_validacion) AS reportes_no_entregados,
            COUNT(DISTINCT(no_personal_validacion)) AS profesionales_no_entregaron,
            sap AS No_SAP,
            nombre_completo AS Nombre_completo,
            email
        FROM
            combined_table
        GROUP BY
            Mes,
            No_SAP,
            Nombre_completo,
            email,
            Market_Place
        ORDER BY
            reportes_no_entregados DESC,
            profesionales_no_entregaron DESC;
        """
            )
        )
        connection.commit()


def create_table_aggregated_pais_count_data():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_pais_count_data"))
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS aggregated_pais_count_data AS
                SELECT 
                    v.Mes,
                    s.Pais,
                    COUNT(v.Empleado) AS Cantidad_Registros,
                    p.email
                FROM
                    dfvalidacion v
                    LEFT JOIN dfseun s ON v.CeCo_emisor = s.No_CeCo
                    LEFT JOIN dfpersonal p ON s.SEUN_Lider_Pais = p.Nombre_completo
                GROUP BY
                    v.Mes, s.Pais, s.SEUN_Lider_Pais;
        """
            )
        )
        connection.commit()


def create_table_aggregated_pais_distinct_data():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_pais_distinct_data"))
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS aggregated_pais_distinct_data AS
                SELECT 
                    v.Mes,
                    s.Pais,
                    COUNT(DISTINCT v.Empleado) AS Cantidad_Empleados,
                    p.email
                FROM
                    dfvalidacion v
                    LEFT JOIN dfseun s ON v.CeCo_emisor = s.No_CeCo
                    LEFT JOIN dfpersonal p ON s.SEUN_Lider_Pais = p.Nombre_completo
                GROUP BY
                    v.Mes, s.Pais, s.SEUN_Lider_Pais;
            """
            )
        )
        connection.commit()


def create_table_aggregated_pais_data():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_pais_data"))
        connection.execute(
            text("""
                CREATE TABLE IF NOT EXISTS aggregated_pais_data AS
                SELECT
                    d.Mes, d.Pais, d.Cantidad_Empleados, c.Cantidad_Registros, d.email 
                FROM
                    aggregated_pais_distinct_data d
                    LEFT JOIN aggregated_pais_count_data c ON d.MES = c.Mes;
            """)
        )
        connection.commit()


def create_table_aggregated_oficina_count_data():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_oficina_count_data"))
        connection.execute(
            text(
                """
                    CREATE TABLE IF NOT EXISTS aggregated_oficina_count_data AS
                    SELECT
                        p.Oficina,
                        p.Oficina_fisica,
                        s.Pais,
                        COUNT(v.Empleado) AS Cantidad_Registros,
                        p.Nombre_completo,
                        p.email
                    FROM
                        dfvalidacion v
                        LEFT JOIN dfseun s ON v.CeCo_emisor = s.No_CeCo
                        LEFT JOIN dfpersonal p ON s.SEUN_Lider_Pais = p.Nombre_completo
                    GROUP BY
                        v.Mes,
                        p.Oficina,
                        p.Oficina_fisica,
                        s.Pais;
                                """
            )
        )
        connection.commit()


def create_table_aggregated_oficina_distinct_data():
    with engine.connect() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS aggregated_oficina_distinct_data")
        )
        connection.execute(
            text(
                """
                    CREATE TABLE IF NOT EXISTS aggregated_oficina_distinct_data AS
                    SELECT
                        v.Mes,
                        p.Oficina,
                        p.Oficina_fisica,
                        s.Pais,
                        COUNT(DISTINCT(v.Empleado)) AS Cantidad_Empleados,
                        p.Nombre_completo,
                        p.email
                    FROM
                        dfvalidacion v
                        LEFT JOIN dfseun s ON v.CeCo_emisor = s.No_CeCo
                        LEFT JOIN dfpersonal p ON s.SEUN_Lider_Pais = p.Nombre_completo
                    GROUP BY
                        v.Mes,
                        p.Oficina,
                        p.Oficina_fisica,
                        s.Pais,
                        p.Nombre_completo,
                        p.email

                        """
            )
        )
        connection.commit()
        
        
        
def create_table_aggregated_socio_data_resumen():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_socio_data_resumen"))
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS aggregated_socio_data_resumen AS
                SELECT
                    IFNULL(c.Mes, 0) as Mes,
                    c.SAP as SAP_Socio,
                    c.Profesional as Socio,
                    c.linea_servicio_x as Linea,
                    c.pais_x as Pais,
                    c.Oficina as Oficina,
                    count(c.no_personal_validacion) as reportes_no_entregados,
                    count(distinct (c.no_personal_validacion)) as profesionales_no_entregaron,
                    s.Tiene_Grupo_Asignado
                FROM
                    combined_table c
                    LEFT JOIN dftotalsocios s ON s.SAP = c.sap_socio
                GROUP BY
                    c.sap_socio,
                    c.socio_responsable,
                    c.Mes
                ORDER BY
                    Mes DESC,
                    profesionales_no_entregaron DESC;
                """
            )
        )
        connection.commit()
        

def create_table_aggregated_socio_data_agrupado():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_socio_data_agrupado"))
        connection.execute(
            text(
                """
                    CREATE TABLE IF NOT EXISTS aggregated_socio_data_agrupado AS
                    WITH EmpleadoCount AS (
                        SELECT 
                            r.SAP_Socio, 
                            r.SAP AS Empleado
                        FROM dfreporteempleados r
                    )
                    SELECT 
                        ec.SAP_Socio, 
                        s.Profesional AS Socio, 
                        v.Empleado,
                        COUNT(*) AS veces_aparece,
                        SUM(v.Hras_fact) AS total_Hras_fact,
                        v.Descrip_CeCo_Emisor,
                        v.Descrip_Funcion,
                        v.CeCo_emisor,
                        v.No_personal,
                        v.Mes,
                        SUM(v.Hras_no_fact) AS total_Hras_no_fact,
                        SUM(v.HonB_CancPlan) AS total_HonB_CancPlan,
                        AVG(v.Porc_Canc) AS promedio_Porc_Canc,
                        v.Texto_Explicativo_PT1
                    FROM EmpleadoCount ec
                    INNER JOIN dftotalsocios s 
                        ON ec.SAP_Socio = s.SAP
                    INNER JOIN dfvalidacion v
                        ON ec.Empleado = v.No_personal
                    GROUP BY 
                        ec.SAP_Socio, 
                        s.Profesional, 
                        v.Empleado,
                        v.Descrip_CeCo_Emisor,
                        v.Descrip_Funcion,
                        v.CeCo_emisor,
                        v.No_personal,
                        v.Mes,
                        v.Texto_Explicativo_PT1
                    ORDER BY 
                        ec.SAP_Socio, 
                        v.Empleado;
        """
            )
        )
        connection.commit()



def create_table_aggregated_socio_data_detalle():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_socio_data_detalle"))
        connection.execute(
            text(
                """
                    CREATE TABLE IF NOT EXISTS aggregated_socio_data_detalle AS
                            WITH EmpleadoCount AS (
                                SELECT 
                                    r.SAP_Socio, 
                                    r.SAP AS SAP_Empleado 
                                FROM dfreporteempleados r
                            )
                            SELECT 
                                ec.SAP_Socio, 
                                s.Profesional AS Socio, 
                                ec.SAP_Empleado, 
                                v.Hras_fact,
                                v.Descrip_CeCo_Emisor,
                                v.Descrip_Funcion,
                                v.CeCo_emisor,
                                v.No_personal,
                                v.Empleado,
                                v.Fecha,
                                v.Mes,
                                v.Hras_no_fact,
                                v.HonB_CancPlan,
                                v.Porc_Canc,
                                v.Texto_Explicativo_PT1
                            FROM EmpleadoCount ec
                            INNER JOIN dftotalsocios s 
                                ON ec.SAP_Socio = s.SAP
                            INNER JOIN dfvalidacion v
                                ON ec.SAP_Empleado = v.No_personal;
                """
            )
        )
        connection.commit()


def create_table_market_place_data_resumen():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS market_place_data_resumen"))
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS market_place_data_resumen AS
                SELECT
                    IFNULL (v.Mes, 0) as Mes,
                    CASE
                        WHEN s.Market_Place = "MX & CA" AND s.Pais = "MÉXICO" THEN "MX"
                        WHEN s.Market_Place = "MX & CA" AND s.Pais != "MÉXICO" THEN "CA"
                        ELSE s.Market_Place
                    END AS Market_Place_Filtrado,
                    COUNT(DISTINCT(s.Pais)) as Cantidad_Paises,
                    count(v.No_personal) as reportes_no_entregados,
                    count(DISTINCT (v.No_personal)) as profesionales_no_entregaron,
                    count(DISTINCT (s.SAP_Seun)) as cantidad_seunes
                FROM
                    dfseun s
                    left join dfvalidacion v on TRIM(s.Codigo_CeCo) = TRIM(v.CeCo_emisor)
                GROUP BY
                    Market_Place_Filtrado;
                """
            )
        )
        connection.commit()


def create_table_aggregated_seun():
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS aggregated_socio_data_resumen"))
        connection.execute(
            text(
                """
                    SELECT
                    IFNULL(v.Mes,0) as Mes,
                        s.Market_Place,
                        s.Linea_de_Servicios,
                        s.Pais,
                        p.Oficina_fisica,
                        s.Codigo_CeCo,
                        s.Descripcion_CeCo,
                        COUNT(v.No_personal) AS reportes_no_entregados,
                        COUNT(DISTINCT v.No_personal) AS profesionales_no_entregaron,
                        p.No_SAP,
                        p.Nombre_completo,
                        p.email
                    FROM
                        dfseun s
                        LEFT JOIN dfpersonal p ON p.No_SAP = s.SAP_Seun
                        LEFT JOIN dfvalidacion v ON s.Codigo_CeCo = v.CeCo_emisor
                        -- WHERE 
                        --     v.Mes IS NOT NULL
                    GROUP BY
                        v.Mes,
                        p.No_SAP,
                        p.Nombre_completo,
                        p.email,
                        s.Market_Place
                    ORDER BY
                        reportes_no_entregados DESC,
                        profesionales_no_entregaron DESC;
                """
            )
        )
        connection.commit()

if __name__ == "__main__":
    init_db()
    create_table_aggregated_seun_data()
    create_table_aggregated_pais_count_data()
    create_table_aggregated_pais_distinct_data()
    create_table_aggregated_oficina_count_data()
    create_table_aggregated_oficina_distinct_data()
    
    print("Database and new tables initialized")
