
# ===============================
# app.py - Sistema de contratos
# ===============================

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from database import SessionLocal, engine, Base
from models import Contrato, ReporteMensual

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def normalizar_contrato(numero):
    numero = numero.strip()
    if "-" not in numero:
        return numero
    parte, anio = numero.split("-")
    try:
        parte = str(int(parte))
    except:
        pass
    return f"{parte}-{anio}"


def limpiar(valor):
    if valor is None:
        return ""
    texto = str(valor).strip().lower()
    if texto == "nan" or texto == "":
        return ""
    return valor


@app.get("/")
async def inicio(request: Request):
    return templates.TemplateResponse("supervisor.html", {"request": request})


@app.post("/buscar")
async def buscar(request: Request, contrato: str = Form(...)):

    contrato = normalizar_contrato(contrato)
    db = SessionLocal()

    contrato_db = db.query(Contrato).filter(
        Contrato.numero_contrato == contrato
    ).first()

    if not contrato_db:
        db.close()
        return templates.TemplateResponse(
            "supervisor.html",
            {"request": request, "error": "Contrato no encontrado"}
        )

    ultimo_reporte = db.query(ReporteMensual).filter(
        ReporteMensual.contrato_id == contrato_db.id
    ).order_by(
        ReporteMensual.anio.desc(),
        ReporteMensual.mes.desc()
    ).first()

    ejecucion = ""

    if ultimo_reporte:
        porcentaje = ultimo_reporte.porcentaje_ejecucion
        if porcentaje is not None:
            if porcentaje <= 1:
                porcentaje = porcentaje * 100
            ejecucion = f"{round(porcentaje,2)}%"

    ejecucion_anterior = ""

    if contrato_db.ejecucion_mes_anterior is not None:
        p = contrato_db.ejecucion_mes_anterior
        if p <= 1:
            p = p * 100
        ejecucion_anterior = f"{round(p,2)}%"

    db.close()

    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,
            "contrato": limpiar(contrato_db.numero_contrato),
            "supervisor": limpiar(contrato_db.supervisor),
            "cedula": limpiar(contrato_db.cedula),
            "correo": limpiar(contrato_db.correo),
            "telefono": limpiar(contrato_db.telefono),
            "direccion": limpiar(contrato_db.direccion),
            "departamento": limpiar(contrato_db.departamento),
            "ciudad": limpiar(contrato_db.ciudad),
            "ejecucion": ejecucion,
            "ejecucion_anterior": ejecucion_anterior
        }
    )


@app.post("/actualizar_datos")
async def actualizar_datos(
    contrato: str = Form(...),
    supervisor: str = Form(...),
    cedula: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    departamento: str = Form(...),
    ciudad: str = Form(...)
):

    db = SessionLocal()

    contrato_db = db.query(Contrato).filter(
        Contrato.numero_contrato == contrato
    ).first()

    contrato_db.supervisor = supervisor
    contrato_db.cedula = cedula
    contrato_db.correo = correo
    contrato_db.telefono = telefono
    contrato_db.direccion = direccion
    contrato_db.departamento = departamento
    contrato_db.ciudad = ciudad

    db.commit()
    db.close()

    return {"mensaje": "Datos actualizados correctamente"}


@app.post("/guardar")
async def guardar(
    request: Request,
    contrato: str = Form(...),
    porcentaje: str = Form(...),
    observaciones: str = Form("")
):

    porcentaje = porcentaje.replace(",", ".")
    porcentaje = float(porcentaje)

    if porcentaje > 1:
        porcentaje = porcentaje / 100

    hoy = datetime.now()
    mes = hoy.month
    anio = hoy.year

    db = SessionLocal()

    contrato_db = db.query(Contrato).filter(
        Contrato.numero_contrato == contrato
    ).first()

    campos = [
        contrato_db.supervisor,
        contrato_db.cedula,
        contrato_db.correo,
        contrato_db.telefono,
        contrato_db.direccion,
        contrato_db.departamento,
        contrato_db.ciudad
    ]

    if any(c is None or str(c).strip() == "" for c in campos):
        db.close()
        return templates.TemplateResponse(
            "supervisor.html",
            {
                "request": request,
                "error": "Para guardar, debe ingresar la información faltante"
            }
        )

    reporte = ReporteMensual(
        contrato_id=contrato_db.id,
        porcentaje_ejecucion=porcentaje,
        observaciones=observaciones,
        mes=mes,
        anio=anio
    )

    db.add(reporte)
    db.commit()
    db.close()

    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,
            "mensaje": "Reporte guardado correctamente"
        }
    )
