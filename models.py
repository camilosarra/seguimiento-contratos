from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    numero_contrato = Column(String, index=True)
    contratista = Column(String)
    objeto = Column(Text)
    valor = Column(Numeric)
    supervisor = Column(String)

    reportes = relationship("ReporteMensual", back_populates="contrato")


class ReporteMensual(Base):
    __tablename__ = "reportes_mensuales"

    id = Column(Integer, primary_key=True, index=True)

    contrato_id = Column(Integer, ForeignKey("contratos.id"))

    anio = Column(Integer)
    mes = Column(Integer)

    porcentaje_ejecucion = Column(Numeric)
    observaciones = Column(Text)

    contrato = relationship("Contrato", back_populates="reportes")