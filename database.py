from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://contratos_user:FZJWn6wylUHjBKeRCvY68SKtywB5C5UO@dpg-d6o43kua2pns73fu7sbg-a.oregon-postgres.render.com/contratos_a7u1"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()