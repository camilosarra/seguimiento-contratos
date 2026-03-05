from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from datetime import datetime
import re

app = FastAPI()

templates = Jinja2Templates(directory="templates")

excel_file = "contratos.xlsx"

contratos = pd.read_excel(excel_file)

def normalizar_contrato(contrato):
    
    contrato = contrato.replace(" ", "")
    
    if "-" not in contrato:
        return contrato
    
    numero, año = contrato.split("-")
    
    numero = str(int(numero))
    
    return f"{numero}-{año}"

def ventana_abierta():
    
    dia = datetime.now().day
    
    if dia <= 9:
        return True
    
    return False

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    
    abierta = ventana_abierta()
    
    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,
            "ventana": abierta,
            "contrato": None
        }
    )

@app.post("/buscar", response_class=HTMLResponse)
async def buscar(
    request: Request,
    contrato: str = Form(...)
):
    
    contrato = normalizar_contrato(contrato)
    
    fila = contratos[
        contratos["CONTRATO Y AÑO"] == contrato
    ]
    
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
            "ventana": ventana_abierta(),
            "contrato": contrato,
            "contratista": datos["CONTRATISTA"],
            "supervisor": datos["SUPERVISOR"],
            "correo": datos["CORREO SUPERVISOR"],
            "departamento": datos["DEPARTAMENTO"],
            "ciudad": datos["CIUDAD"]
        }
    )

@app.post("/guardar")
async def guardar(
    porcentaje: str = Form(...),
    observaciones: str = Form(""),
    contrato: str = Form(...)
):

    porcentaje = porcentaje.replace(",", ".")
    porcentaje = float(porcentaje)

    hoy = datetime.now()

    mes = hoy.month - 1
    año = hoy.year
    
    data = {
        "contrato": contrato,
        "porcentaje": porcentaje,
        "observaciones": observaciones,
        "mes": mes,
        "año": año,
        "fecha": hoy
    }
    
    df = pd.DataFrame([data])
    
    try:
        
        existente = pd.read_excel("reportes.xlsx")
        
        existente = existente[
            ~(
                (existente["contrato"] == contrato)
                &
                (existente["mes"] == mes)
                &
                (existente["año"] == año)
            )
        ]
        
        final = pd.concat([existente, df])
        
    except:
        
        final = df
    
    final.to_excel("reportes.xlsx", index=False)
    
    return templates.TemplateResponse(
    "supervisor.html",
    {
        "request": Request,
        "mensaje": "Reporte guardado correctamente",
        "ventana": ventana_abierta()
    }
)