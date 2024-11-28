from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import io
from functions import enviar_correo, verify_and_update_data
from app.models import get_df_seun
import sqlite3
import time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Variable global para almacenar el DataFrame
df_seun = None
df_seun_html = None
min_value_unique = None
max_value_unique = None
min_value_count = None
max_value_count = None
months = range(1, 13)

# Configurar la conexión a la base de datos
DATABASE_URL = "data.db"


def get_db_connection():
    return sqlite3.connect(DATABASE_URL, check_same_thread=False)


def load_dataframe():
    global df_seun, df_seun_html, min_value_unique, max_value_unique, min_value_count, max_value_count
    df_seun = get_df_seun()
    df_seun_html = df_seun.to_html(classes="dataframe", header="true", index=False)
    # Aquí puedes calcular los valores min_value_unique, max_value_unique, etc.


@app.on_event("startup")
async def startup_event():
    # Cargar el DataFrame en segundo plano al iniciar la aplicación
    background_tasks = BackgroundTasks()
    background_tasks.add_task(load_dataframe)
    await background_tasks()


@app.get("/")
def read_root(request: Request):
    if df_seun is None:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Talento SLATAM",
                "content": "<p>DataFrame is still loading. Please try again later.</p>",
            },
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Talento SLATAM",
            "content": df_seun_html,
            "min_value_unique": min_value_unique,
            "max_value_unique": max_value_unique,
            "min_value_count": min_value_count,
            "max_value_count": max_value_count,
            "months": months,
        },
    )


@app.get("/dataframe")
def show_dataframe():
    if df_seun is None:
        return JSONResponse(
            content={"message": "DataFrame is still loading. Please try again later."},
            status_code=503,
        )
    return JSONResponse(content=df_seun.to_dict(orient="records"))


@app.get("/dataframe_range")
def get_dataframe_range():
    if df_seun is None:
        return JSONResponse(
            content={"message": "DataFrame is still loading. Please try again later."},
            status_code=503,
        )
    return {
        "min_unique": min_value_unique,
        "max_unique": max_value_unique,
        "min_count": min_value_count,
        "max_count": max_value_count,
    }


@app.get("/download_csv")
def download_csv():
    if df_seun is None:
        return JSONResponse(
            content={"message": "DataFrame is still loading. Please try again later."},
            status_code=503,
        )
    stream = io.StringIO()
    df_seun.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=dataframe.csv"
    return response


@app.post("/send_email")
def send_email(
    slider_value_unique: int = Form(...),
    slider_value_count: int = Form(...),
    selected_month: str = Form(...),
):
    # Cargar df_final y df_por_seun desde la base de datos
    conn = get_db_connection()
    df_final = pd.read_sql("SELECT * FROM df_final", con=conn)
    df_por_seun = pd.read_sql("SELECT * FROM df_por_seun", con=conn)
    conn.close()

    # Check if the required columns exist in df_por_seun
    required_columns = [
        "No_Personal_Unique",
        "No_Personal_Count",
        "Mes",
        "e-mail",
        "SEUN/Líder País",
    ]
    for col in required_columns:
        if col not in df_por_seun.columns:
            return JSONResponse(
                content={"message": f"Column '{col}' not found in df_por_seun."},
                status_code=400,
            )

    # Aplicar los filtros al DataFrame df_por_seun
    filtered_df_por_seun = df_por_seun[
        (df_por_seun["No_Personal_Unique"] >= slider_value_unique)
        & (df_por_seun["No_Personal_Count"] >= slider_value_count)
    ]

    if selected_month != "all":
        filtered_df_por_seun = filtered_df_por_seun[
            filtered_df_por_seun["Mes"] == int(selected_month)
        ]

    # Agrupar por el campo SEUN/Líder País
    grouped_df_por_seun = filtered_df_por_seun.groupby("SEUN/Líder País")

    # Enviar un correo a cada grupo
    for seun_lider_pais, group in grouped_df_por_seun:
        # Obtener el email correspondiente al SEUN/Líder País
        email = group["e-mail"].iloc[0]

        # Filtrar df_final por el campo SEUN/Líder País y selected_month
        df_final_filtered = df_final[df_final["SEUN/Líder País"] == seun_lider_pais]
        if selected_month != "all":
            df_final_filtered = df_final_filtered[
                df_final_filtered["Mes"] == int(selected_month)
            ]

        # Convertir los DataFrames filtrados a CSV
        por_seun_csv = io.StringIO()
        group.to_csv(por_seun_csv, index=False)
        por_seun_csv.seek(0)

        final_csv = io.StringIO()
        df_final_filtered.to_csv(final_csv, index=False)
        final_csv.seek(0)

        # Enviar el correo con los archivos CSV adjuntos
        enviar_correo(
            #! receptor=email,
            receptor="LMARINARO@DELOITTE.COM",
            cliente=email,
            dataframes=[por_seun_csv, final_csv],
            nombres_adjuntos=[
                f"resumen_{seun_lider_pais}.csv",
                f"detalle_{seun_lider_pais}.csv",
            ],
        )

    return {
        "message": f"Emails enviados con el filtro de: Únicos >= {slider_value_unique}, Cantidad >= {slider_value_count}, Mes = {selected_month}"
    }


@app.get("/dataframe_html")
def show_dataframe_html(request: Request):
    if df_seun_html is None:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Talento SLATAM",
                "content": "<p>DataFrame is still loading. Please try again later.</p>",
            },
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Talento SLATAM",
            "content": df_seun_html,
            "min_value": min_value_unique,
            "max_value": max_value_unique,
        },
    )
