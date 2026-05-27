from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()


""" Создание подключения к БД"""
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"   # fallback для тестов
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
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

from backend.database import models_db

Base.metadata.create_all(bind=engine)