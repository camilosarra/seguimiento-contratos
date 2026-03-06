from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from datetime import datetime
import os
import io

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

archivo_contratos = os.path.join(BASE_DIR, "contratos.xlsx")
archivo_reportes = os.path.join(BASE_DIR, "reportes.xlsx")

ADMIN_USER = "planeacion"
ADMIN_PASS = "ART2026!"


def ventana_abierta():
    hoy = datetime.now()
    return hoy.day <= 9


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
        {"request": request, "ventana": ventana_abierta()}
    )


@app.post("/buscar")
async def buscar(request: Request, contrato: str = Form(...)):

    contrato = normalizar_contrato(contrato)

    df = pd.read_excel(archivo_contratos)

    fila = df[df["CONTRATO Y AÑO"].astype(str).str.strip() == contrato]

    if fila.empty:
        return templates.TemplateResponse(
            "supervisor.html",
            {
                "request": request,
                "error": "El contrato no se encuentra en la base de datos",
                "ventana": ventana_abierta()
            }
        )

    datos = fila.iloc[0]

    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,
            "contrato": contrato,
            "contratista": datos["CONTRATISTA"],
            "supervisor": datos["SUPERVISOR"],
            "correo": datos["CORREO SUPERVISOR"],
            "departamento": datos["DEPARTAMENTO"],
            "ciudad": datos["CIUDAD"],
            "ventana": ventana_abierta()
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
            "mensaje": "Reporte guardado correctamente",
            "ventana": ventana_abierta()
        }
    )


# ---------------------------
# ADMIN LOGIN
# ---------------------------

@app.get("/admin")
async def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin")
async def admin_auth(
    request: Request,
    usuario: str = Form(...),
    password: str = Form(...)
):

    if usuario == ADMIN_USER and password == ADMIN_PASS:
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Credenciales incorrectas"}
    )


# ---------------------------
# DASHBOARD
# ---------------------------

@app.get("/dashboard")
async def dashboard(request: Request):

    df_contratos = pd.read_excel(archivo_contratos)

    total_contratos = len(df_contratos)

    if os.path.exists(archivo_reportes):

        df_reportes = pd.read_excel(archivo_reportes)

        mes_actual = datetime.now().month - 1

        reportes_mes = df_reportes[df_reportes["mes"] == mes_actual]

        total_reportados = len(reportes_mes)

        tabla = reportes_mes.tail(50).to_dict(orient="records")

    else:

        total_reportados = 0
        tabla = []

    pendientes = total_contratos - total_reportados

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_contratos": total_contratos,
            "reportados": total_reportados,
            "pendientes": pendientes,
            "tabla": tabla
        }
    )


# ---------------------------
# DESCARGAR EXCEL
# ---------------------------

@app.get("/descargar")
async def descargar():

    if not os.path.exists(archivo_reportes):
        return {"error": "No hay reportes"}

    df = pd.read_excel(archivo_reportes)

    stream = io.BytesIO()
    df.to_excel(stream, index=False)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=reporte_consolidado.xlsx"}
    )