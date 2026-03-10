from sqlalchemy import Column, Integer, String
from database import Base

class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True)

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