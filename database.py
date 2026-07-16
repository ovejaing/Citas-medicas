from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///./citas.db"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Creamos una sesión para realizar consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#base de datos
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()