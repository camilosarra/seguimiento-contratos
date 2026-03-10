import pandas as pd
from database import SessionLocal
from models import Contrato

df = pd.read_excel("contratos.xlsx")

db = SessionLocal()

for _, row in df.iterrows():

    contrato = Contrato(

        linea = str(row.iloc[0]),
        numero_contrato = str(row.iloc[4]),
        contratista = str(row.iloc[2]),
        identificacion_contratista = str(row.iloc[3]),
        subcuenta = str(row.iloc[5]),

        supervisor = str(row.iloc[7]),
        cedula = str(row.iloc[8]),
        correo = str(row.iloc[9]),
        telefono = str(row.iloc[10]),
        direccion = str(row.iloc[11]),

        departamento = str(row.iloc[12]),
        ciudad = str(row.iloc[13])
    )

    db.add(contrato)

db.commit()
db.close()

print("Contratos cargados correctamente")