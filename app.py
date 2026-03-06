from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from datetime import datetime
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

archivo_contratos = os.path.join(BASE_DIR, "contratos.xlsx")
archivo_reportes = os.path.join(BASE_DIR, "reportes.xlsx")


def normalizar_contrato(numero):

    numero = numero.strip()

    if "-" not in numero:
        return numero

    parte, año = numero.split("-")

    parte = str(int(parte))

    return f"{parte}-{año}"


@app.get("/")
async def inicio(request: Request):

    return templates.TemplateResponse(
        "supervisor.html",
        {"request": request}
    )


@app.post("/buscar")
async def buscar(request: Request, contrato: str = Form(...)):

    contrato = normalizar_contrato(contrato)

    df = pd.read_excel(archivo_contratos)

    # CONTRATO Y AÑO está en la columna E (índice 4)
    fila = df[df.iloc[:,4].astype(str).str.strip() == contrato]

    if fila.empty:

        return templates.TemplateResponse(
            "supervisor.html",
            {
                "request": request,
                "error": "El contrato no se encuentra en la base de datos"
            }
        )

    datos = fila.iloc[0]

    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,
            "contrato": datos.iloc[4],

            "linea": datos.iloc[0],
            "id": datos.iloc[1],
            "contratista": datos.iloc[2],
            "identificacion_contratista": datos.iloc[3],
            "subcuenta": datos.iloc[5],
            "ejecucion": datos.iloc[6],

            "supervisor": datos.iloc[7],
            "cedula": datos.iloc[8],
            "correo": datos.iloc[9],
            "telefono": datos.iloc[10],
            "direccion": datos.iloc[11],
            "departamento": datos.iloc[12],
            "ciudad": datos.iloc[13]
        }
    )


@app.post("/guardar")
async def guardar(
    request: Request,
    contrato: str = Form(...),
    porcentaje: str = Form(...),
    observaciones: str = Form("")
):

    porcentaje = porcentaje.replace(",", ".")
    porcentaje = float(porcentaje)

    hoy = datetime.now()

    mes = hoy.month - 1
    año = hoy.year

    nuevo = pd.DataFrame([{
        "contrato": contrato,
        "porcentaje": porcentaje,
        "observaciones": observaciones,
        "mes": mes,
        "año": año,
        "fecha": hoy
    }])

    if os.path.exists(archivo_reportes):

        df = pd.read_excel(archivo_reportes)
        df = pd.concat([df, nuevo], ignore_index=True)

    else:

        df = nuevo

    df.to_excel(archivo_reportes, index=False)

    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,
            "mensaje": "Reporte guardado correctamente"
        }
    )