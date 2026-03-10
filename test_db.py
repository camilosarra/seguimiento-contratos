from database import engine

try:
    connection = engine.connect()
    print("Conexión exitosa a PostgreSQL")
    connection.close()
except Exception as e:
    print("Error:", e)