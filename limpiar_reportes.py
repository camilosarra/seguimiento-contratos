from database import SessionLocal
from models import ReporteMensual

db = SessionLocal()

db.query(ReporteMensual).delete()

db.commit()
db.close()

print("Reportes eliminados")