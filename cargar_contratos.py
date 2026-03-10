import pandas as pd
from database import SessionLocal
from models import Contrato

# leer excel
df = pd.read_excel("contratos.xlsx")

db = SessionLocal()

for _, row in df.iterrows():

    contrato = str(row.iloc[4]).strip()

    nuevo = Contrato(
        numero_contrato=contrato,
        contratista=str(row.iloc[2]),
        supervisor=str(row.iloc[7])
    )

    db.add(nuevo)

db.commit()
db.close()

print("Contratos cargados correctamente")