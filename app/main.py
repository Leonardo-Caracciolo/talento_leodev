import io
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, text
from sqlmodel import Session, SQLModel, create_engine, select


from app.models import (
    AggregatedPaisData,
    AggregatedSeunData,
    AggregatedSocioData,
    AggregatedValidationData,
    DFCombined,
    DFPersonal,
    DFSeun,
    DFTotalSocios,
    DFUtilizacion,
    DFValidacion,
    MarketPlaceData,
)
from functions import enviar_correo, verify_and_update_data
from sqlalchemy import create_engine, text
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
# Configurar la carpeta de plantillas


# Ruta a tu base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
# # engine = create_engine("sqlite:///data/data.db")
# engine = create_engine("sqlite:///./database.db")

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)
# engine = create_engine("sqlite:///./database.db") #! CAMBIO DB

SQLModel.metadata.create_all(engine)

# Verificar y actualizar datos, incluyendo la creación de la tabla aggregated_seun_data si no existe
verify_and_update_data()


@app.post("/send_email")
async def send_email(
    filter_type: str = Query(..., description="Tipo de filtro: 'socio', 'seun', 'marketplace'"),
    email: str = Query(...),
    slider_value_count_min: Optional[int] = Query(None),
    slider_value_count_max: Optional[int] = Query(None),
    slider_value_unique_min: Optional[int] = Query(None),
    slider_value_unique_max: Optional[int] = Query(None),
    selected_month: Optional[str] = Query(None),
    selected_serviceline: Optional[str] = Query(None),
    selected_country: Optional[str] = Query(None),
    selected_office: Optional[str] = Query(None),
    selected_market_place: Optional[str] = Query(None),
    subject: str = Query("Reporte de I&SL"),
):
    with Session(engine) as session:
        base_query = "SELECT * FROM combined_table WHERE 1=1"
        params = {}

        # Aplicar filtros según el tipo
        if filter_type in ["socio", "seun"]:
            if selected_month and selected_month != "all":
                base_query += " AND Mes = :mes"
                params["mes"] = selected_month
            if selected_serviceline and selected_serviceline != "all":
                base_query += " AND Linea_de_Servicios = :linea_de_servicios"
                params["linea_de_servicios"] = selected_serviceline
            if selected_country and selected_country != "all":
                base_query += " AND Pais = :pais"
                params["pais"] = selected_country
            if selected_office and selected_office != "all":
                base_query += " AND Oficina_fisica = :oficina"
                params["oficina"] = selected_office

        elif filter_type == "marketplace":
            if selected_month and selected_month != "all":
                base_query += " AND Mes = :mes"
                params["mes"] = selected_month
            if selected_market_place and selected_market_place != "all":
                base_query += " AND Market_Place = :market_place"
                params["market_place"] = selected_market_place

        # Aplicar sliders
        if slider_value_count_min is not None:
            base_query += " AND reportes_no_entregados >= :min_reportes_no_entregados"
            params["min_reportes_no_entregados"] = slider_value_count_min
        if slider_value_count_max is not None:
            base_query += " AND reportes_no_entregados <= :max_reportes_no_entregados"
            params["max_reportes_no_entregados"] = slider_value_count_max
        if slider_value_unique_min is not None:
            base_query += " AND profesionales_no_entregaron >= :min_profesionales_no_entregaron"
            params["min_profesionales_no_entregaron"] = slider_value_unique_min
        if slider_value_unique_max is not None:
            base_query += " AND profesionales_no_entregaron <= :max_profesionales_no_entregaron"
            params["max_profesionales_no_entregaron"] = slider_value_unique_max

        query = text(base_query)
        result = session.execute(query, params)
        column_names = result.keys()
        results = result.fetchall()

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para los parámetros proporcionados",
            )

        # Convertir a DataFrame
        df = pd.DataFrame(results, columns=column_names)

        # Agrupar según el tipo
        if filter_type == "socio":
            group_by_columns = ["nombre_socio", "pais_x"]
        elif filter_type == "seun":
            group_by_columns = ["seun", "pais_x"]
        elif filter_type == "marketplace":
            group_by_columns = ["marketplace"]
        else:
            raise HTTPException(status_code=400, detail="Tipo de filtro inválido")

        df_grouped = df.groupby(group_by_columns).sum().reset_index()

        # Generar DataFrames
        df1 = df_grouped.iloc[:, : int(df_grouped.shape[1] / 3)]
        df2 = df_grouped.iloc[
            :, int(df_grouped.shape[1] / 3) : int(2 * df_grouped.shape[1] / 3)
        ]
        df3 = df_grouped.iloc[:, int(2 * df_grouped.shape[1] / 3) :]

        # Convertir a Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df1.to_excel(writer, sheet_name="Reporte 1", index=False)
            df2.to_excel(writer, sheet_name="Reporte 2", index=False)
            df3.to_excel(writer, sheet_name="Reporte 3", index=False)
        excel_data = output.getvalue()

        # Enviar correo
        try:
            enviar_correo(
                destinatario=email,
                asunto=subject,
                contenido="Adjunto encontrarás los reportes solicitados.",
                adjunto=excel_data,
                nombre_archivo="reportes.xlsx",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al enviar el correo: {str(e)}"
            )

        return {"detail": "Correo enviado exitosamente"}


@app.get("/get_all_data")
def get_all_data():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM combined_table"))
            data = [dict(row) for row in result.mappings()]
            return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/market-place", response_class=HTMLResponse)
async def read_market_place(request: Request):
    return templates.TemplateResponse("market-place.html", {"request": request})


@app.get("/seun", response_class=HTMLResponse)
async def read_seun(request: Request):
    return templates.TemplateResponse("seun.html", {"request": request})


@app.get("/socio", response_class=HTMLResponse)
async def read_socio(request: Request):
    return templates.TemplateResponse("socio.html", {"request": request})


# @app.get("/pais", response_class=HTMLResponse)
# async def read_pais(request: Request):
#     return templates.TemplateResponse("pais.html", {"request": request})


@app.get(
    "/df_personal/",
    response_model=List[DFPersonal],
    summary="Get Personal Data",
    description="Retrieve personal data with optional filters.",
    tags=["Personal Data"],
)
async def get_personal(
    sap: Optional[str] = Query(None, description="SAP number of the person"),
    negocio: Optional[str] = Query(None, description="Business unit"),
    pais_soc: Optional[str] = Query(None, description="Country of the society"),
    marketplace: Optional[str] = Query(None, description="Marketplace"),
    ce_co: Optional[str] = Query(None, description="Cost center"),
    especializacion: Optional[str] = Query(None, description="Specialization"),
    categoria_global: Optional[str] = Query(None, description="Global category"),
    desc_subdiv_pers: Optional[str] = Query(
        None, description="Description of the personnel subdivision"
    ),
    oficina: Optional[str] = Query(None, description="Office"),
    oficina_fisica: Optional[str] = Query(None, description="Physical office"),
    fec_ingres: Optional[datetime] = Query(None, description="Date of entry"),
    email: Optional[str] = Query(None, description="Email address"),
):
    """
    Retrieve personal data with optional filters.
    """
    with Session(engine) as session:
        statement = select(DFPersonal)

        if sap:
            statement = statement.where(DFPersonal.No_SAP == sap)
        if negocio:
            statement = statement.where(DFPersonal.Negocio == negocio)
        if pais_soc:
            statement = statement.where(DFPersonal.Pais_Soc == pais_soc)
        if marketplace:
            statement = statement.where(DFPersonal.Marketplace == marketplace)
        if ce_co:
            statement = statement.where(DFPersonal.Ce_Co == ce_co)
        if especializacion:
            statement = statement.where(DFPersonal.Especializacion == especializacion)
        if categoria_global:
            statement = statement.where(DFPersonal.Categoria_Global == categoria_global)
        if desc_subdiv_pers:
            statement = statement.where(DFPersonal.Desc_Subdiv_pers == desc_subdiv_pers)
        if oficina:
            statement = statement.where(DFPersonal.Oficina == oficina)
        if oficina_fisica:
            statement = statement.where(DFPersonal.Oficina_fisica == oficina_fisica)
        if fec_ingres:
            statement = statement.where(DFPersonal.Fec_ingres == fec_ingres)
        if email:
            statement = statement.where(DFPersonal.email == email)

        results = session.exec(statement)
        personal = results.all()
        return personal


@app.get(
    "/df_seun/",
    response_model=List[DFSeun],
    summary="Get SEUN Data",
    description="Retrieve SEUN data with optional filters.",
    tags=["SEUN Data"],
)
async def get_seun(
    market_place: Optional[str] = Query(None, description="Market Place"),
    pais: Optional[str] = Query(None, description="Country"),
    no_ceco: Optional[str] = Query(None, description="Cost Center Number"),
    descripcion_ceco: Optional[str] = Query(
        None, description="Cost Center Description"
    ),
    seun_lider_pais: Optional[str] = Query(None, description="SEUN Leader Country"),
    linea_de_servicios: Optional[str] = Query(None, description="Service Line"),
):
    with Session(engine) as session:
        statement = select(DFSeun)

        if market_place:
            statement = statement.where(DFSeun.Market_Place == market_place)
        if pais:
            statement = statement.where(DFSeun.Pais == pais)
        if no_ceco:
            statement = statement.where(DFSeun.No_CeCo == no_ceco)
        if descripcion_ceco:
            statement = statement.where(DFSeun.Descripcion_CeCo == descripcion_ceco)
        if seun_lider_pais:
            statement = statement.where(DFSeun.SEUN_Lider_Pais == seun_lider_pais)
        if linea_de_servicios:
            statement = statement.where(DFSeun.Linea_de_Servicios == linea_de_servicios)

        results = session.exec(statement)
        seun = results.all()
        return seun


@app.get(
    "/df_utilizacion/",
    response_model=List[DFUtilizacion],
    summary="Get Utilization Data",
    description="Retrieve utilization data with optional filters.",
    tags=["Utilization Data"],
)
async def get_utilizacion(
    no_personal: Optional[float] = Query(None, description="Personal Number"),
    hrs_real_per: Optional[float] = Query(None, description="Real Hours Performed"),
    hrs_est_per: Optional[int] = Query(None, description="Estimated Hours Performed"),
    porc_meta_util: Optional[float] = Query(
        None, description="Utilization Goal Percentage"
    ),
    porc_real_ut_acu: Optional[float] = Query(
        None, description="Accumulated Real Utilization Percentage"
    ),
    fecha_baja: Optional[datetime] = Query(None, description="Date of Discharge"),
):
    with Session(engine) as session:
        statement = select(DFUtilizacion)

        if no_personal:
            statement = statement.where(DFUtilizacion.No_personal == no_personal)
        if hrs_real_per:
            statement = statement.where(DFUtilizacion.Hrs_Real_Per == hrs_real_per)
        if hrs_est_per:
            statement = statement.where(DFUtilizacion.Hrs_Est_Per == hrs_est_per)
        if porc_meta_util:
            statement = statement.where(DFUtilizacion.Porc_Meta_Util == porc_meta_util)
        if porc_real_ut_acu:
            statement = statement.where(
                DFUtilizacion.Porc_Real_Ut_Acu == porc_real_ut_acu
            )
        if fecha_baja:
            statement = statement.where(DFUtilizacion.Fecha_Baja == fecha_baja)

        results = session.exec(statement)
        utilizacion = results.all()
        return utilizacion


@app.get(
    "/df_validacion/",
    response_model=List[DFValidacion],
    summary="Get Validation Data",
    description="Retrieve validation data with optional filters.",
    tags=["Validation Data"],
)
async def get_validacion(
    hras_fact: Optional[float] = Query(None, description="Billed Hours"),
    descrip_ceco_emisor: Optional[str] = Query(
        None, description="Emitter Cost Center Description"
    ),
    descrip_funcion: Optional[str] = Query(None, description="Function Description"),
    ceco_emisor: Optional[str] = Query(None, description="Emitter Cost Center"),
    no_personal: Optional[int] = Query(None, description="Personal Number"),
    empleado: Optional[str] = Query(None, description="Employee"),
    fecha: Optional[datetime] = Query(None, description="Date"),
    hras_no_fact: Optional[float] = Query(None, description="Non-billed Hours"),
    honb_cancplan: Optional[float] = Query(None, description="Cancelled Planned Hours"),
    porc_canc: Optional[float] = Query(None, description="Cancellation Percentage"),
):
    with Session(engine) as session:
        statement = select(DFValidacion)

        if hras_fact:
            statement = statement.where(DFValidacion.Hras_fact == hras_fact)
        if descrip_ceco_emisor:
            statement = statement.where(
                DFValidacion.Descrip_CeCo_Emisor == descrip_ceco_emisor
            )
        if descrip_funcion:
            statement = statement.where(DFValidacion.Descrip_Funcion == descrip_funcion)
        if ceco_emisor:
            statement = statement.where(DFValidacion.CeCo_emisor == ceco_emisor)
        if no_personal:
            statement = statement.where(DFValidacion.No_personal == no_personal)
        if empleado:
            statement = statement.where(DFValidacion.Empleado == empleado)
        if fecha:
            statement = statement.where(DFValidacion.Fecha == fecha)
        if hras_no_fact:
            statement = statement.where(DFValidacion.Hras_no_fact == hras_no_fact)
        if honb_cancplan:
            statement = statement.where(DFValidacion.HonB_CancPlan == honb_cancplan)
        if porc_canc:
            statement = statement.where(DFValidacion.Porc_Canc == porc_canc)

        results = session.exec(statement)
        validacion = results.all()
        return validacion


@app.get(
    "/validacion/agrupado/",
    summary="Get Aggregated Validation Data",
    description="Retrieve aggregated validation data grouped by Emitter Cost Center Description.",
    tags=["Validation Data"],
    response_model=List[AggregatedValidationData],
)
async def get_aggregated_validacion(
    descrip_ceco_emisor: Optional[str] = Query(
        None, description="Emitter Cost Center Description"
    ),
    total_hras_fact: Optional[float] = Query(None, description="Total Billed Hours"),
):
    with Session(engine) as session:
        statement = select(
            DFValidacion.Descrip_CeCo_Emisor,
            func.sum(DFValidacion.Hras_fact).label("total_hras_fact"),
        ).group_by(DFValidacion.Descrip_CeCo_Emisor)

        if descrip_ceco_emisor:
            statement = statement.where(
                DFValidacion.Descrip_CeCo_Emisor == descrip_ceco_emisor
            )
        if total_hras_fact:
            statement = statement.having(
                func.sum(DFValidacion.Hras_fact) >= total_hras_fact
            )

        results = session.exec(statement)
        aggregated_data = results.all()

        # Convertir los resultados a una lista de diccionarios
        response_data = [
            {
                "Descrip_CeCo_Emisor": row.Descrip_CeCo_Emisor,
                "total_hras_fact": row.total_hras_fact,
            }
            for row in aggregated_data
        ]

        return response_data


@app.get("/market_place_data_resumen/", response_model=List[MarketPlaceData])  #!!
async def get_market_place_data_resumen(
    mes: Optional[int] = Query(None, description="Filter by Mes"),
    min_reportes_no_entregados: Optional[int] = Query(
        None, description="Minimum value for reportes_no_entregados"
    ),
    max_reportes_no_entregados: Optional[int] = Query(
        None, description="Maximum value for reportes_no_entregados"
    ),
    min_profesionales_no_entregaron: Optional[int] = Query(
        None, description="Minimum value for profesionales_no_entregaron"
    ),
    max_profesionales_no_entregaron: Optional[int] = Query(
        None, description="Maximum value for profesionales_no_entregaron"
    ),
    market_place: Optional[str] = Query(None, description="Filter by Market_Place"),
):
    with Session(engine) as session:
        query = """
            SELECT
                Mes,
                Market_Place_Filtrado,
                Cantidad_Paises,
                reportes_no_entregados,
                profesionales_no_entregaron,
                cantidad_seunes
            FROM market_place_data_resumen
            WHERE 1=1
        """

        if mes is not None:
            query += " AND Mes = :mes"
        if min_reportes_no_entregados is not None:
            query += " AND reportes_no_entregados >= :min_reportes_no_entregados"
        if max_reportes_no_entregados is not None:
            query += " AND reportes_no_entregados <= :max_reportes_no_entregados"
        if min_profesionales_no_entregaron is not None:
            query += (
                " AND profesionales_no_entregaron >= :min_profesionales_no_entregaron"
            )
        if max_profesionales_no_entregaron is not None:
            query += (
                " AND profesionales_no_entregaron <= :max_profesionales_no_entregaron"
            )
        if market_place is not None:
            query += " AND Market_Place = :market_place"

        statement = text(query)
        params = {
            "mes": mes,
            "min_reportes_no_entregados": min_reportes_no_entregados,
            "max_reportes_no_entregados": max_reportes_no_entregados,
            "min_profesionales_no_entregaron": min_profesionales_no_entregaron,
            "max_profesionales_no_entregaron": max_profesionales_no_entregaron,
            "market_place": market_place,
        }

        results = session.execute(statement, params).fetchall()
        aggregated_data = [MarketPlaceData(**row._mapping) for row in results]
        return aggregated_data


@app.get("/aggregated_seun_data/", response_model=List[AggregatedSeunData])
async def get_aggregated_seun_data(
    mes: Optional[int] = Query(None, description="Filter by Mes"),
    min_reportes_no_entregados: Optional[int] = Query(
        None, description="Minimum value for reportes_no_entregados"
    ),
    max_reportes_no_entregados: Optional[int] = Query(
        None, description="Maximum value for reportes_no_entregados"
    ),
    min_profesionales_no_entregaron: Optional[int] = Query(
        None, description="Minimum value for profesionales_no_entregaron"
    ),
    max_profesionales_no_entregaron: Optional[int] = Query(
        None, description="Maximum value for profesionales_no_entregaron"
    ),
    market_place: Optional[str] = Query(None, description="Filter by Market_Place"),
):
    with Session(engine) as session:
        query = """
            SELECT
                Mes,
                Market_Place,
                Linea_De_Servicios,
                Pais,
                Oficina_fisica,
                Codigo_CeCo,
                Descripcion_CeCo,
                reportes_no_entregados,
                profesionales_no_entregaron,
                No_SAP,
                Nombre_completo,
                email
            FROM
                aggregated_seun_data
            WHERE 1=1
        """

        if mes is not None:
            query += " AND Mes = :mes"
        if min_reportes_no_entregados is not None:
            query += " AND reportes_no_entregados >= :min_reportes_no_entregados"
        if max_reportes_no_entregados is not None:
            query += " AND reportes_no_entregados <= :max_reportes_no_entregados"
        if min_profesionales_no_entregaron is not None:
            query += (
                " AND profesionales_no_entregaron >= :min_profesionales_no_entregaron"
            )
        if max_profesionales_no_entregaron is not None:
            query += (
                " AND profesionales_no_entregaron <= :max_profesionales_no_entregaron"
            )
        if market_place is not None:
            query += " AND Market_Place = :market_place"

        statement = text(query)
        params = {
            "mes": mes,
            "min_reportes_no_entregados": min_reportes_no_entregados,
            "max_reportes_no_entregados": max_reportes_no_entregados,
            "min_profesionales_no_entregaron": min_profesionales_no_entregaron,
            "max_profesionales_no_entregaron": max_profesionales_no_entregaron,
            "market_place": market_place,
        }

        results = session.execute(statement, params).fetchall()
        aggregated_data = [AggregatedSeunData(**row._mapping) for row in results]
        return aggregated_data


@app.get(
    "/aggregated_socio_data_resumen/", response_model=List[AggregatedSocioData]
)  #!!
async def get_aggregated_socio_data_resumen(
    mes: Optional[int] = Query(None, description="Filter by Mes"),
    min_reportes_no_entregados: Optional[int] = Query(
        None, description="Minimum value for reportes_no_entregados"
    ),
    max_reportes_no_entregados: Optional[int] = Query(
        None, description="Maximum value for reportes_no_entregados"
    ),
    min_profesionales_no_entregaron: Optional[int] = Query(
        None, description="Minimum value for profesionales_no_entregaron"
    ),
    max_profesionales_no_entregaron: Optional[int] = Query(
        None, description="Maximum value for profesionales_no_entregaron"
    ),
    market_place: Optional[str] = Query(None, description="Filter by Market_Place"),
):
    with Session(engine) as session:
        query = """
            SELECT
                Mes,
                SAP_Socio,
                Socio,
                Linea,
                Pais,
                Oficina,
                reportes_no_entregados,
                profesionales_no_entregaron,
                Tiene_Grupo_Asignado
            FROM aggregated_socio_data_resumen
            WHERE 1=1
        """

        if mes is not None:
            query += " AND Mes = :mes"
        if min_reportes_no_entregados is not None:
            query += " AND reportes_no_entregados >= :min_reportes_no_entregados"
        if max_reportes_no_entregados is not None:
            query += " AND reportes_no_entregados <= :max_reportes_no_entregados"
        if min_profesionales_no_entregaron is not None:
            query += (
                " AND profesionales_no_entregaron >= :min_profesionales_no_entregaron"
            )
        if max_profesionales_no_entregaron is not None:
            query += (
                " AND profesionales_no_entregaron <= :max_profesionales_no_entregaron"
            )
        # if market_place is not None:
        #     query += " AND Market_Place = :market_place"

        statement = text(query)
        params = {
            "mes": mes,
            "min_reportes_no_entregados": min_reportes_no_entregados,
            "max_reportes_no_entregados": max_reportes_no_entregados,
            "min_profesionales_no_entregaron": min_profesionales_no_entregaron,
            "max_profesionales_no_entregaron": max_profesionales_no_entregaron,
            "market_place": market_place,
        }

        results = session.execute(statement, params).fetchall()
        aggregated_data = [AggregatedSocioData(**row._mapping) for row in results]
        return aggregated_data


@app.get("/aggregated_pais_data/", response_model=List[AggregatedPaisData])
async def get_aggregated_pais_data(
    mes: Optional[int] = Query(None, description="Filter by Mes"),
    pais: Optional[str] = Query(None, description="Filter by Pais"),
    max_cantidad_empleados: Optional[int] = Query(
        None,
        description="Maximum value for Cantidad_Empleados (aggregated_pais_distinct_data)",
    ),
    min_cantidad_empleados: Optional[int] = Query(
        None,
        description="Minimum value for Cantidad_Empleados (aggregated_pais_distinct_data)",
    ),
    max_cantidad_registros: Optional[int] = Query(
        None,
        description="Maximum value for Cantidad_Registros (aggregated_pais_count_data)",
    ),
    min_cantidad_registros: Optional[int] = Query(
        None,
        description="Minimum value for Cantidad_Registros (aggregated_pais_count_data)",
    ),
):
    with Session(engine) as session:
        query = """
            SELECT 
                Mes,
                Pais,
                Cantidad_Empleados,
                Cantidad_Registros,
                email
            FROM aggregated_pais_data
            WHERE 1=1
        """

        if mes is not None:
            query += " AND Mes = :mes"
        if pais is not None:
            query += " AND Pais = :pais"
        if max_cantidad_empleados is not None:
            query += " AND Cantidad_Empleados >= :max_cantidad_empleados"
        if min_cantidad_empleados is not None:
            query += " AND Cantidad_Empleados <= :min_cantidad_empleados"
        if max_cantidad_registros is not None:
            query += " AND Cantidad_Registros >= :max_cantidad_registros"
        if min_cantidad_registros is not None:
            query += " AND Cantidad_Registros <= :min_cantidad_registros"

        statement = text(query)
        params = {
            "mes": mes,
            "pais": pais,
            "max_cantidad_empleados": max_cantidad_empleados,
            "min_cantidad_empleados": min_cantidad_empleados,
            "max_cantidad_registros": max_cantidad_registros,
            "min_cantidad_registros": min_cantidad_registros,
        }

        results = session.execute(statement, params).fetchall()
        aggregated_data = [AggregatedPaisData(**row._mapping) for row in results]
        return aggregated_data


@app.get(
    "/df_total_socios/",
    response_model=List[DFTotalSocios],
    summary="Get List Of Partners",
    description="Retrieve partner data with optional filters.",
    tags=["Get List Of Partners"],
)
async def get_partners(
    sap: Optional[str] = Query(None, description="SAP number of the partner"),
    profesional: Optional[str] = Query(None, description="Professional"),
    pais_soc: Optional[str] = Query(None, description="Country of the Partner"),
    oficina: Optional[str] = Query(None, description="Office"),
    linea: Optional[str] = Query(None, description="Services Line"),
    tiene_grupo_asociado: Optional[str] = Query(None, description="Has group assigned"),
):
    """
    Retrieve personal data with optional filters.
    """
    with Session(engine) as session:
        statement = select(DFTotalSocios)

        if sap:
            statement = statement.where(DFTotalSocios.SAP == sap)
        if profesional:
            statement = statement.where(DFTotalSocios.Profesional == profesional)
        if pais_soc:
            statement = statement.where(DFTotalSocios.Pais == pais_soc)
        if oficina:
            statement = statement.where(DFTotalSocios.Oficina == oficina)
        if linea:
            statement = statement.where(DFTotalSocios.Linea == linea)
        if tiene_grupo_asociado:
            statement = statement.where(
                DFTotalSocios.Tiene_Grupo_Asignado == tiene_grupo_asociado
            )

        results = session.exec(statement)
        partners = results.all()
        return partners


# -------------------------------------------------


@app.post("/send_email_seun")
async def send_email_seun(
    slider_value_count_min: int = Form(...),
    slider_value_count_max: int = Form(...),
    slider_value_unique_min: int = Form(...),
    slider_value_unique_max: int = Form(...),
    selected_month: str = Form(...),
    selected_serviceline: str = Form(...),
    selected_country: str = Form(...),
    selected_office: str = Form(...),
):
    with Session(engine) as session:
        query1 = """
            SELECT
                Mes,
                Market_Place,
                Linea_de_Servicios,
                Pais,
                Oficina_fisica,
                No_CeCo,
                Descripcion_CeCo,
                reportes_no_entregados,
                profesionales_no_entregaron,
                No_SAP,
                Nombre_completo,
                email
            FROM aggregated_seun_data
            WHERE 1=1
        """

        query2 = """
            SELECT
                v.Mes,
                v.CeCo_emisor,
                v.No_personal,
                v.Empleado,
                strftime('%d/%m/%Y', v.Fecha) AS Fecha,
                v.Hras_no_fact,
                v.Texto_Explicativo_PT1,
                s.Market_Place,
                s.No_CeCo,
                s.Descripcion_CeCo,
                p.No_SAP,
                p.Nombre_completo,
                p.email
            FROM
                dfseun s
                LEFT JOIN dfpersonal p ON p.Nombre_completo = s.SEUN_Lider_Pais
                LEFT JOIN dfvalidacion v ON s.No_CeCo = v.CeCo_emisor
            WHERE 
                v.Mes IS NOT NULL
        """

        if selected_month != "all":
            query1 += " AND Mes = :mes"
            query2 += " AND v.Mes = :mes"
        if selected_serviceline != "all":
            query1 += " AND Linea_de_Servicios = :linea_de_servicios"
            query2 += " AND s.Linea_de_Servicios = :linea_de_servicios"
        if selected_country != "all":
            query1 += " AND Pais = :pais"
            query2 += " AND s.Pais = :pais"
        if selected_office != "all":
            query1 += " AND Oficina_fisica = :oficina"
            query2 += " AND p.Oficina_fisica = :oficina"
        if slider_value_unique_min is not None:
            query1 += (
                " AND profesionales_no_entregaron >= :min_profesionales_no_entregaron"
            )
        if slider_value_unique_max is not None:
            query1 += (
                " AND profesionales_no_entregaron <= :max_profesionales_no_entregaron"
            )
        if slider_value_count_min is not None:
            query1 += " AND reportes_no_entregados >= :min_reportes_no_entregados"
        if slider_value_count_max is not None:
            query1 += " AND reportes_no_entregados <= :max_reportes_no_entregados"

        statement1 = text(query1)
        statement2 = text(query2)
        params = {
            "mes": selected_month if selected_month != "all" else None,
            "linea_de_servicios": (
                selected_serviceline if selected_serviceline != "all" else None
            ),
            "pais": selected_country if selected_country != "all" else None,
            "oficina": selected_office if selected_office != "all" else None,
            "min_profesionales_no_entregaron": slider_value_unique_min,
            "max_profesionales_no_entregaron": slider_value_unique_max,
            "min_reportes_no_entregados": slider_value_count_min,
            "max_reportes_no_entregados": slider_value_count_max,
        }

        results1 = session.execute(statement1, params).fetchall()
        results2 = session.execute(statement2, params).fetchall()
        if not results1 and not results2:
            raise HTTPException(
                status_code=404, detail="No data found with the given filters"
            )

        # Convert results to DataFrames
        df_resumen = pd.DataFrame([row._mapping for row in results1])
        df_detalle = pd.DataFrame([row._mapping for row in results2])

        # Group by email
        grouped1 = df_resumen.groupby("email")
        grouped2 = df_detalle.groupby("email")

        for email, group1 in grouped1:
            group2 = (
                grouped2.get_group(email)
                if email in grouped2.groups
                else pd.DataFrame()
            )

            # Convert DataFrames to CSV
            csv_buffer1 = io.StringIO()
            group1.to_csv(csv_buffer1, index=False)
            csv_buffer1.seek(0)

            csv_buffer2 = io.StringIO()
            group2.to_csv(csv_buffer2, index=False)
            csv_buffer2.seek(0)

            # Send email with both CSV attachments
            enviar_correo(
                # receptor=email,
                # receptor="lmarinaro@deloitte.com",
                receptor="amiriarte@deloitte.com",
                cliente=email,
                dataframes=[csv_buffer1, csv_buffer2],
                nombres_adjuntos=["resumen_por_seun.csv", "detalle_por_seun.csv"],
            )

        return {
            "message": f"Emails enviados con el filtro de: Reportes no entregados >= {slider_value_count_min} y <= {slider_value_count_max}, "
            f"Profesionales que no entregaron reportes >= {slider_value_count_min} y <= {slider_value_unique_max}, Mes = {selected_month}, "
            f"Linea de Servicio = {selected_serviceline}, Pais = {selected_country}, Oficina = {selected_office}"
        }


@app.post("/send_email_socio")  #! en desarrollo
async def send_email_socio(
    slider_value_count_min: int = Form(...),
    slider_value_count_max: int = Form(...),
    slider_value_unique_min: int = Form(...),
    slider_value_unique_max: int = Form(...),
    selected_month: str = Form(...),
    selected_serviceline: str = Form(...),
    selected_country: str = Form(...),
    selected_office: str = Form(...),
):
    with Session(engine) as session:
        query_resumen = """ #? Tabla resumen
            SELECT
                Mes,
                SAP_Socio,
                Socio,
                Linea,
                Pais,
                Oficina,
                reportes_no_entregados,
                profesionales_no_entregaron,
                Tiene_Grupo_Asignado
            FROM
                aggregated_socio_data_resumen
            WHERE
                1 = 1
        """

        query_agrupados = """ #? Tabla agrupados
            SELECT
                mes,
                sap_socio,
                nombre_socio,
                empleado,
                COUNT(*) AS veces_aparece,
                SUM(hras_fact) AS total_Hras_fact,
                descrip_ceco_x,
                descrip_funcion,
                ceco_emisor,
                no_sap,
                -- mes,
                SUM(hras_no_fact) AS total_Hras_no_fact,
                SUM(honb_cancplan) AS total_HonB_CancPlan,
                AVG(porc_canc) AS promedio_Porc_Canc,
                texto_explicativo_pt1
            FROM
                combined_table
            GROUP BY
                sap_socio,
                nombre_socio,
                empleado,
                descrip_ceco_x,
                descrip_funcion,
                ceco_emisor,
                no_sap,
                mes,
                texto_explicativo_pt1
            ORDER BY
                sap_socio,
                empleado
            WHERE
                1 = 1
        """

        query_detalle = """ #? Tabla detalle
            SELECT
                sap_socio,
                nombre_socio,
                no_sap,
                hras_fact,
                descrip_ceco_x,
                descrip_funcion,
                ceco_emisor,
                nombre_completo,
                fecha,
                mes,
                hras_no_fact,
                honb_cancplan,
                porc_canc,
                texto_explicativo_pt1
            FROM
                combined_table
            WHERE
                1 = 1
        """

        query_socio_utilizacion = """
        SELECT
            dfutilizacionactual.*,
            combined_table.sap_socio,
            combined_table.nombre_socio
        FROM
            dfutilizacionactual
            LEFT JOIN combined_table ON dfutilizacionactual.SAP = combined_table.no_sap
        ORDER BY
            nombre_socio DESC
        WHERE
            1 = 1
        """

        query_mail_socio = """ #! Matchea con dfpersonal para obtener los mail de los socios
            SELECT
                s.*,
                s.SAP_Socio,
                c.descrip_funcion,
                c.email
            FROM
                aggregated_socio_data_resumen s
                LEFT JOIN combined_table c ON c.no_sap = s.SAP_Socio
            WHERE
                c.Mes IS NOT NULL
        """

        query_mail_seun = """ #! Matchea con dfpersonal para obtener los mail del seun
            SELECT
                v.Mes,
                v.CeCo_emisor,
                v.No_personal,
                v.Empleado,
                strftime('%d/%m/%Y', v.Fecha) AS Fecha,
                v.Hras_no_fact,
                v.Texto_Explicativo_PT1,
                s.Market_Place,
                s.No_CeCo,
                s.Descripcion_CeCo,
                p.No_SAP,
                p.Nombre_completo,
                p.email
            FROM
                dfseun s
                LEFT JOIN dfpersonal p ON p.Nombre_completo = s.SEUN_Lider_Pais
                LEFT JOIN dfvalidacion v ON s.No_CeCo = v.CeCo_emisor
                LEFT JOIN aggregated_socio_data_resumen sr ON s.Pais = sr.Pais AND p.No_SAP = sr.SAP_Socio
            WHERE 
                v.Mes IS NOT NULL
        """

        # ? Por ahora, sin filtros
        # if selected_month != "all":
        #     query_resumen += " AND Mes = :mes"
        #     # query2 += " AND v.Mes = :mes"
        # if selected_serviceline != "all":
        #     query_resumen += " AND Linea_de_Servicios = :linea_de_servicios"
        #     # query2 += " AND s.Linea_de_Servicios = :linea_de_servicios"
        # if selected_country != "all":
        #     query_resumen += " AND Pais = :pais"
        #     # query2 += " AND s.Pais = :pais"
        # if selected_office != "all":
        #     query_resumen += " AND Oficina_fisica = :oficina"
        #     # query2 += " AND p.Oficina_fisica = :oficina"
        # if slider_value_unique_min is not None:
        #     query_resumen += " AND profesionales_no_entregaron >= :min_profesionales_no_entregaron"
        # if slider_value_unique_max is not None:
        #     query_resumen += " AND profesionales_no_entregaron <= :max_profesionales_no_entregaron"
        # if slider_value_count_min is not None:
        #     query_resumen += " AND reportes_no_entregados >= :min_reportes_no_entregados"
        # if slider_value_count_max is not None:
        #     query_resumen += " AND reportes_no_entregados <= :max_reportes_no_entregados"

        statement1 = text(query_resumen)
        statement2 = text(query_agrupados)
        statement3 = text(query_detalle)
        statement4 = text(query_mail_socio)
        # statement5 = text(query_mail_seun)
        params = {
            "mes": selected_month if selected_month != "all" else None,
            "linea_de_servicios": (
                selected_serviceline if selected_serviceline != "all" else None
            ),
            "pais": selected_country if selected_country != "all" else None,
            "oficina": selected_office if selected_office != "all" else None,
            "min_profesionales_no_entregaron": slider_value_unique_min,
            "max_profesionales_no_entregaron": slider_value_unique_max,
            "min_reportes_no_entregados": slider_value_count_min,
            "max_reportes_no_entregados": slider_value_count_max,
        }

        results1 = session.execute(statement1, params).fetchall()
        results2 = session.execute(statement2, params).fetchall()
        results3 = session.execute(statement3, params).fetchall()
        results4 = session.execute(statement4, params).fetchall()
        # results5 = session.execute(statement5, params).fetchall()

        if (
            not results1
            and not results2
            and not results3
            and not results4
            # and not results5
        ):
            raise HTTPException(
                status_code=404, detail="No data found with the given filters"
            )

        # Convert results to DataFrames
        df_resumen = pd.DataFrame([row._mapping for row in results1])
        df_agrupado = pd.DataFrame([row._mapping for row in results2])
        df_detalle = pd.DataFrame([row._mapping for row in results3])
        df_emails_socio = pd.DataFrame([row._mapping for row in results4])
        # df_emails_seun = pd.DataFrame([row._mapping for row in results5])

        # Group by email
        grouped_emails_socio = df_emails_socio.groupby("email")
        # grouped_emails_seun = df_emails_seun.groupby("email")

        for email_socio in grouped_emails_socio['email']:
            # Send email with both CSV attachments
            enviar_correo(
                # receptor="lmarinaro@deloitte.com",
                receptor="amiriarte@deloitte.com, leocaracciolo@deloitte.com, rtolaba@deloitte.com",
                cliente=email_socio,
                dataframes=[],  #!
                #! Adjuntar el excel con las 3 sheets
                nombres_adjuntos=["excel"] #!
            )

        return {
            "message": f"Emails enviados con el filtro de: Reportes no entregados >= {slider_value_count_min} y <= {slider_value_count_max}, "
            f"Profesionales que no entregaron reportes >= {slider_value_count_min} y <= {slider_value_unique_max}, Mes = {selected_month}, "
            f"Linea de Servicio = {selected_serviceline}, Pais = {selected_country}, Oficina = {selected_office}"
        }


@app.post("/send_email_pais")  #! cambiarlo para Market Place
async def send_email_pais(
    slider_value_empleados: int = Form(...),
    slider_value_registros: int = Form(...),
    selected_month: str = Form(...),
    selected_country: str = Form(...),
):
    with Session(engine) as session:
        query1 = """
            SELECT
                Mes,
                Pais,
                Cantidad_Empleados,
                Cantidad_Registros,
                email
            FROM aggregated_pais_data
            WHERE 1=1
        """

        query2 = """
            SELECT
                v.Mes,
                s.Pais,
                v.CeCo_emisor,
                v.No_personal,
                v.Empleado,
                strftime('%d/%m/%Y', v.Fecha) AS Fecha,
                v.Hras_no_fact,
                v.Texto_Explicativo_PT1,
                s.Market_Place,
                s.No_CeCo,
                s.Descripcion_CeCo,
                p.No_SAP,
                p.Nombre_completo,
                p.email
            FROM
                dfseun s
                LEFT JOIN dfpersonal p ON p.Nombre_completo = s.SEUN_Lider_Pais
                LEFT JOIN dfvalidacion v ON s.No_CeCo = v.CeCo_emisor
            WHERE 
                v.Mes IS NOT NULL;
        """

        if selected_month != "all":
            query1 += " AND Mes = :mes"
            query2 += " AND v.Mes = :mes"
        if selected_country != "all":
            query1 += " AND Pais = :pais"
        if slider_value_empleados is not None:
            query1 += " AND Cantidad_Empleados >= :min_cantidad_empleados"
        if slider_value_registros is not None:
            query1 += " AND Cantidad_Registros >= :min_cantidad_registros"

        statement1 = text(query1)
        statement2 = text(query2)
        params = {
            "mes": selected_month if selected_month != "all" else None,
            "pais": selected_country if selected_country != "all" else None,
            "min_cantidad_empleados": slider_value_empleados,
            "min_cantidad_registros": slider_value_registros,
        }

        results1 = session.execute(statement1, params).fetchall()
        results2 = session.execute(statement2, params).fetchall()
        if not results1 and not results2:
            raise HTTPException(
                status_code=404, detail="No data found with the given filters"
            )

        # Convert results to DataFrames
        df_resumen = pd.DataFrame([row._mapping for row in results1])
        df_detalle = pd.DataFrame([row._mapping for row in results2])

        # Group by email
        grouped1 = df_resumen.groupby("email")
        grouped2 = df_detalle.groupby("email")

        for email, group1 in grouped1:
            group2 = (
                grouped2.get_group(email)
                if email in grouped2.groups
                else pd.DataFrame()
            )

            # Convert DataFrames to CSV
            csv_buffer1 = io.StringIO()
            group1.to_csv(csv_buffer1, index=False)
            csv_buffer1.seek(0)

            csv_buffer2 = io.StringIO()
            group2.to_csv(csv_buffer2, index=False)
            csv_buffer2.seek(0)

            # Send email with both CSV attachments
            enviar_correo(
                # receptor=email,
                # receptor="lmarinaro@deloitte.com",
                receptor="amiriarte@deloitte.com",
                cliente=email,
                dataframes=[csv_buffer1, csv_buffer2],
                nombres_adjuntos=["resumen_por_pais.csv", "detalle_por_pais.csv"],
            )

        return {
            "message": f"Emails enviados con el filtro de: Cantidad Empleados >= {slider_value_empleados}, Cantidad Registros >= {slider_value_registros}, Mes = {selected_month}, Pais = {selected_country}"
        }
