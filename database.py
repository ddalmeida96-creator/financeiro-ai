import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, text
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
    fixa_id = Column(Integer)  # se veio de uma conta fixa, referência dela


class Fixa(Base):
    __tablename__ = "fixas"
    id = Column(Integer, primary_key=True)
    tipo = Column(String)          # Receita / Despesa
    descricao = Column(String)
    categoria = Column(String)
    subcategoria = Column(String)
    valor = Column(Float)
    dia = Column(Integer)          # dia do vencimento (1-31)
    usuario = Column(String)
    ativo = Column(Boolean, default=True)


def _migrate():
    # adiciona colunas novas em bancos já existentes (SQLite)
    with engine.begin() as c:
        cols = [r[1] for r in c.execute(text("PRAGMA table_info(lancamentos)"))]
        if "fixa_id" not in cols:
            c.execute(text("ALTER TABLE lancamentos ADD COLUMN fixa_id INTEGER"))


def init_db():
    Base.metadata.create_all(engine)
    _migrate()
