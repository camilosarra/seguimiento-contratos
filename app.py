from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from database import SessionLocal, engine, Base
import models
from models import Contrato, ReporteMensual

# crear tablas automáticamente si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------
# NORMALIZAR NUMERO DE CONTRATO
# -----------------------------------------
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


# -----------------------------------------
# PAGINA PRINCIPAL
# -----------------------------------------
@app.get("/")
async def inicio(request: Request):

    return templates.TemplateResponse(
        "supervisor.html",
        {"request": request}
    )


# -----------------------------------------
# BUSCAR CONTRATO
# -----------------------------------------
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
            {
                "request": request,
                "error": "Contrato no encontrado"
            }
        )

    # buscar último reporte
    ultimo_reporte = db.query(ReporteMensual).filter(
        ReporteMensual.contrato_id == contrato_db.id
    ).order_by(
        ReporteMensual.anio.desc(),
        ReporteMensual.mes.desc()
    ).first()

    ejecucion = ""

    if ultimo_reporte:
        ejecucion = f"{ultimo_reporte.porcentaje_ejecucion}%"

    db.close()

    return templates.TemplateResponse(
        "supervisor.html",
        {
            "request": request,

            "contrato": contrato_db.numero_contrato,
            "linea": contrato_db.linea,
            "contratista": contrato_db.contratista,
            "identificacion_contratista": contrato_db.identificacion_contratista,
            "subcuenta": contrato_db.subcuenta,

            "supervisor": contrato_db.supervisor,
            "cedula": contrato_db.cedula,
            "correo": contrato_db.correo,
            "telefono": contrato_db.telefono,
            "direccion": contrato_db.direccion,

            "departamento": contrato_db.departamento,
            "ciudad": contrato_db.ciudad,

            "ejecucion": ejecucion
        }
    )


# -----------------------------------------
# GUARDAR REPORTE
# -----------------------------------------
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

    mes = hoy.month
    anio = hoy.year

    db = SessionLocal()

    contrato_db = db.query(Contrato).filter(
        Contrato.numero_contrato == contrato
    ).first()

    if not contrato_db:

        db.close()

        return templates.TemplateResponse(
            "supervisor.html",
            {
                "request": request,
                "error": "Contrato no encontrado"
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


# -----------------------------------------
# VER REPORTES (API)
# -----------------------------------------
@app.get("/ver-reportes")
async def ver_reportes():

    db = SessionLocal()

    reportes = db.query(ReporteMensual).all()

    resultado = []

    for r in reportes:

        resultado.append({
            "contrato_id": r.contrato_id,
            "mes": r.mes,
            "anio": r.anio,
            "porcentaje": r.porcentaje_ejecucion,
            "observaciones": r.observaciones
        })

    db.close()

    return resultado