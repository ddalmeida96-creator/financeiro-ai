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


class Cofrinho(Base):
    __tablename__ = "cofrinhos"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    meta = Column(Float, default=0.0)      # objetivo; 0 = sem meta
    emoji = Column(String, default="🏦")
    ativo = Column(Boolean, default=True)


class CofrinhoMov(Base):
    __tablename__ = "cofrinho_movs"
    id = Column(Integer, primary_key=True)
    cofrinho_id = Column(Integer)
    tipo = Column(String)          # Aporte / Resgate / Rendimento
    valor = Column(Float)
    data = Column(DateTime, default=datetime.now)
    obs = Column(String)
    lanc_id = Column(Integer)      # Lancamento espelhado (aporte=despesa, resgate=receita)


class Bem(Base):
    __tablename__ = "bens"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    categoria = Column(String)     # Imóvel, Veículo, ...
    valor = Column(Float)          # valor atual
    ativo = Column(Boolean, default=True)


class BemSnapshot(Base):
    __tablename__ = "bem_snapshots"
    id = Column(Integer, primary_key=True)
    bem_id = Column(Integer)
    mes = Column(Integer)
    ano = Column(Integer)
    valor = Column(Float)


class Inflacao(Base):
    __tablename__ = "inflacao"
    id = Column(Integer, primary_key=True)
    mes = Column(Integer)
    ano = Column(Integer)
    pct = Column(Float)            # variação IPCA do mês (%)


class Compra(Base):
    __tablename__ = "compras"
    id = Column(Integer, primary_key=True)
    item = Column(String)
    comprado = Column(Boolean, default=False)
    usuario = Column(String)
    data = Column(DateTime, default=datetime.now)


# IPCA mensal (%) — semente inicial; editável no dashboard
_IPCA_SEED = [
    (2025, 12, 0.33),
    (2026, 1, 0.33), (2026, 2, 0.70), (2026, 3, 0.88),
    (2026, 4, 0.67), (2026, 5, 0.58), (2026, 6, 0.16),
]


def _migrate():
    # adiciona colunas novas em bancos já existentes (SQLite)
    with engine.begin() as c:
        cols = [r[1] for r in c.execute(text("PRAGMA table_info(lancamentos)"))]
        if "fixa_id" not in cols:
            c.execute(text("ALTER TABLE lancamentos ADD COLUMN fixa_id INTEGER"))


def _seed_inflacao():
    db = SessionLocal()
    if db.query(Inflacao).count() == 0:
        for ano, mes, pct in _IPCA_SEED:
            db.add(Inflacao(ano=ano, mes=mes, pct=pct))
        db.commit()
    db.close()


def _seed_historico():
    import hist_seed
    db = SessionLocal()
    # Importa o histórico da planilha como lançamentos reais (datados).
    # Guard: só importa se ainda não houver nada antes de jul/2025.
    ja_tem = db.query(Lancamento).filter(Lancamento.data < datetime(2025, 7, 1)).count()
    if ja_tem == 0:
        for (ano, mes), valor in hist_seed.RENDA.items():
            db.add(Lancamento(
                data=datetime(ano, mes, 15), usuario="Casal", tipo="Receita",
                descricao="Renda líquida", categoria="Renda",
                subcategoria="Renda líquida", valor=valor))
        for ano, mes, grupo, nome, valor in hist_seed.GASTOS:
            db.add(Lancamento(
                data=datetime(ano, mes, 15), usuario="Casal", tipo="Despesa",
                descricao=nome, categoria=grupo, subcategoria=nome, valor=valor))
        db.commit()
    # Fixas recorrentes (idempotente: só cria se não existir a descrição)
    existentes = {f.descricao for f in db.query(Fixa).all()}
    for descricao, categoria, valor, dia in hist_seed.FIXAS:
        if descricao not in existentes:
            db.add(Fixa(tipo="Despesa", descricao=descricao, categoria=categoria,
                        subcategoria=descricao, valor=valor, dia=dia,
                        usuario="Casal", ativo=True))
    db.commit()
    db.close()


def init_db():
    Base.metadata.create_all(engine)
    _migrate()
    _seed_inflacao()
    _seed_historico()
