from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, extract
from datetime import datetime
from database import SessionLocal, Lancamento

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    agora = datetime.now()
    mes, ano = agora.month, agora.year

    def soma(tipo):
        return db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(
            Lancamento.tipo == tipo,
            extract("month", Lancamento.data) == mes,
            extract("year", Lancamento.data) == ano,
        ).scalar()

    receitas = soma("Receita")
    despesas = soma("Despesa")
    saldo = receitas - despesas

    # Por usuário (mês atual)
    por_usuario = {}
    q = db.query(
        Lancamento.usuario, Lancamento.tipo, func.sum(Lancamento.valor)
    ).filter(
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).group_by(Lancamento.usuario, Lancamento.tipo).all()
    for user, tipo, total in q:
        por_usuario.setdefault(user, {"Receita": 0.0, "Despesa": 0.0})
        por_usuario[user][tipo] = total

    # Últimos lançamentos
    ultimos = db.query(Lancamento).order_by(Lancamento.id.desc()).limit(10).all()

    # Gráfico por categoria (despesas do mês)
    cat = db.query(
        Lancamento.categoria, func.sum(Lancamento.valor)
    ).filter(
        Lancamento.tipo == "Despesa",
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).group_by(Lancamento.categoria).all()
    cat_labels = [c[0] for c in cat]
    cat_values = [round(c[1], 2) for c in cat]

    # Gráfico mensal (6 meses)
    labels_m, rec_m, desp_m = [], [], []
    for i in range(5, -1, -1):
        m = (mes - i - 1) % 12 + 1
        y = ano + ((mes - i - 1) // 12)
        r = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(
            Lancamento.tipo == "Receita",
            extract("month", Lancamento.data) == m,
            extract("year", Lancamento.data) == y,
        ).scalar()
        d = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(
            Lancamento.tipo == "Despesa",
            extract("month", Lancamento.data) == m,
            extract("year", Lancamento.data) == y,
        ).scalar()
        labels_m.append(f"{m:02d}/{y}")
        rec_m.append(round(r, 2))
        desp_m.append(round(d, 2))

    db.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "receitas": brl(receitas),
            "despesas": brl(despesas),
            "saldo": brl(saldo),
            "saldo_positivo": saldo >= 0,
            "por_usuario": {u: {"Receita": brl(v["Receita"]), "Despesa": brl(v["Despesa"])} for u, v in por_usuario.items()},
            "ultimos": ultimos,
            "brl": brl,
            "cat_labels": cat_labels,
            "cat_values": cat_values,
            "labels_m": labels_m,
            "rec_m": rec_m,
            "desp_m": desp_m,
        },
    )
