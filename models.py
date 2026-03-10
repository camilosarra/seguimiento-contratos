from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)

    numero_contrato = Column(String, index=True)

    linea = Column(String)
    contratista = Column(String)
    identificacion_contratista = Column(String)
    subcuenta = Column(String)

    supervisor = Column(String)
    cedula = Column(String)
    correo = Column(String)
    telefono = Column(String)
    direccion = Column(String)

    departamento = Column(String)
    ciudad = Column(String)


class ReporteMensual(Base):
    __tablename__ = "reportes_mensuales"

    id = Column(Integer, primary_key=True, index=True)

    contrato_id = Column(Integer, ForeignKey("contratos.id"))

    porcentaje_ejecucion = Column(Float)
    observaciones = Column(String)

    mes = Column(Integer)
    anio = Column(Integer)

    contrato = relationship("Contrato")