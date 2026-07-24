import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "financeiro.db")
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class Lancamento(Base):
    __tablename__ = "lancamentos"
    id = Column(Integer, primary_key=True)
    data = Column(DateTime, default=datetime.now)
    usuario = Column(String)
    tipo = Column(String)
    descricao = Column(String)
    categoria = Column(String)
    subcategoria = Column(String)
    valor = Column(Float)


def init_db():
    Base.metadata.create_all(engine)
