import os
from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, extract, or_
from datetime import datetime
from database import SessionLocal, Lancamento
import catstore

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
_INDEX = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def row(l):
    return {
        "id": l.id,
        "data": l.data.isoformat() if l.data else None,
        "usuario": l.usuario,
        "tipo": l.tipo,
        "descricao": l.descricao,
        "categoria": l.categoria,
        "subcategoria": l.subcategoria,
        "valor": round(l.valor or 0.0, 2),
    }


@app.get("/", response_class=HTMLResponse)
def index():
    with open(_INDEX, encoding="utf-8") as f:
        return HTMLResponse(f.read())


# ---------- OVERVIEW ----------
@app.get("/api/overview")
def overview():
    db = SessionLocal()
    agora = datetime.now()
    mes, ano = agora.month, agora.year

    def soma(tipo, m=mes, y=ano):
        return db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(
            Lancamento.tipo == tipo,
            extract("month", Lancamento.data) == m,
            extract("year", Lancamento.data) == y,
        ).scalar()

    receitas = soma("Receita")
    despesas = soma("Despesa")
    saldo = receitas - despesas

    # Patrimônio acumulado (todo o histórico)
    tot_rec = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(Lancamento.tipo == "Receita").scalar()
    tot_desp = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(Lancamento.tipo == "Despesa").scalar()
    patrimonio = tot_rec - tot_desp

    # Por usuário (mês)
    por_usuario = {}
    q = db.query(Lancamento.usuario, Lancamento.tipo, func.sum(Lancamento.valor)).filter(
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).group_by(Lancamento.usuario, Lancamento.tipo).all()
    for user, tipo, total in q:
        por_usuario.setdefault(user, {"Receita": 0.0, "Despesa": 0.0})
        por_usuario[user][tipo] = total or 0.0

    membros = []
    for u, v in por_usuario.items():
        membros.append({
            "nome": u,
            "receita": round(v["Receita"], 2),
            "despesa": round(v["Despesa"], 2),
            "saldo": round(v["Receita"] - v["Despesa"], 2),
        })
    membros.sort(key=lambda m: m["nome"].lower())

    mais_gastou = max(membros, key=lambda m: m["despesa"], default=None)
    mais_recebeu = max(membros, key=lambda m: m["receita"], default=None)

    ultimos = [row(l) for l in db.query(Lancamento).order_by(Lancamento.id.desc()).limit(8).all()]
    db.close()

    return {
        "mes_ref": f"{mes:02d}/{ano}",
        "receitas": round(receitas, 2),
        "despesas": round(despesas, 2),
        "saldo": round(saldo, 2),
        "patrimonio": round(patrimonio, 2),
        "membros": membros,
        "mais_gastou": mais_gastou if (mais_gastou and mais_gastou["despesa"] > 0) else None,
        "mais_recebeu": mais_recebeu if (mais_recebeu and mais_recebeu["receita"] > 0) else None,
        "ultimos": ultimos,
    }


# ---------- CHARTS ----------
@app.get("/api/charts")
def charts():
    db = SessionLocal()
    agora = datetime.now()
    mes, ano = agora.month, agora.year

    cat = db.query(Lancamento.categoria, func.sum(Lancamento.valor)).filter(
        Lancamento.tipo == "Despesa",
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).group_by(Lancamento.categoria).all()
    cat = sorted(cat, key=lambda c: c[1] or 0, reverse=True)
    cat_labels = [c[0] for c in cat]
    cat_values = [round(c[1] or 0, 2) for c in cat]

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

    # Comparação por usuário (mês)
    comp = {}
    q = db.query(Lancamento.usuario, Lancamento.tipo, func.sum(Lancamento.valor)).filter(
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).group_by(Lancamento.usuario, Lancamento.tipo).all()
    for user, tipo, total in q:
        comp.setdefault(user, {"Receita": 0.0, "Despesa": 0.0})
        comp[user][tipo] = round(total or 0.0, 2)
    comp_labels = list(comp.keys())
    comp_rec = [comp[u]["Receita"] for u in comp_labels]
    comp_desp = [comp[u]["Despesa"] for u in comp_labels]

    rec_mes = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(
        Lancamento.tipo == "Receita", extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano).scalar()
    desp_mes = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(
        Lancamento.tipo == "Despesa", extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano).scalar()
    db.close()

    return {
        "categoria": {"labels": cat_labels, "values": cat_values},
        "mensal": {"labels": labels_m, "receitas": rec_m, "despesas": desp_m},
        "usuarios": {"labels": comp_labels, "receitas": comp_rec, "despesas": comp_desp},
        "rec_x_desp": {"receitas": round(rec_mes, 2), "despesas": round(desp_mes, 2)},
    }


# ---------- LANÇAMENTOS ----------
@app.get("/api/meta")
def meta():
    db = SessionLocal()
    usuarios = [u[0] for u in db.query(Lancamento.usuario).distinct().all() if u[0]]
    categorias = [c[0] for c in db.query(Lancamento.categoria).distinct().all() if c[0]]
    db.close()
    return {"usuarios": sorted(usuarios), "categorias": sorted(categorias)}


@app.get("/api/lancamentos")
def lista(search: str = "", tipo: str = "", usuario: str = "", categoria: str = "",
          start: str = "", end: str = "", sort: str = "data", order: str = "desc"):
    db = SessionLocal()
    q = db.query(Lancamento)
    if search:
        s = f"%{search.lower()}%"
        q = q.filter(or_(func.lower(Lancamento.descricao).like(s),
                         func.lower(Lancamento.categoria).like(s),
                         func.lower(Lancamento.subcategoria).like(s)))
    if tipo:
        q = q.filter(Lancamento.tipo == tipo)
    if usuario:
        q = q.filter(Lancamento.usuario == usuario)
    if categoria:
        q = q.filter(Lancamento.categoria == categoria)
    if start:
        try:
            q = q.filter(Lancamento.data >= datetime.fromisoformat(start))
        except Exception:
            pass
    if end:
        try:
            q = q.filter(Lancamento.data <= datetime.fromisoformat(end + "T23:59:59"))
        except Exception:
            pass
    col = {"data": Lancamento.data, "valor": Lancamento.valor, "descricao": Lancamento.descricao,
           "categoria": Lancamento.categoria, "usuario": Lancamento.usuario, "tipo": Lancamento.tipo}.get(sort, Lancamento.data)
    q = q.order_by(col.asc() if order == "asc" else col.desc())
    rows = [row(l) for l in q.limit(500).all()]
    db.close()
    return {"lancamentos": rows}


@app.post("/api/lancamentos")
def criar(data: dict = Body(...)):
    db = SessionLocal()
    dt = datetime.now()
    if data.get("data"):
        try:
            dt = datetime.fromisoformat(data["data"])
        except Exception:
            pass
    l = Lancamento(
        usuario=data.get("usuario") or "—",
        tipo=data.get("tipo") or "Despesa",
        descricao=data.get("descricao") or "Lançamento",
        categoria=data.get("categoria") or "Outros",
        subcategoria=data.get("subcategoria") or "Outros",
        valor=float(data.get("valor") or 0),
        data=dt,
    )
    db.add(l)
    db.commit()
    r = row(l)
    db.close()
    return r


@app.put("/api/lancamentos/{lid}")
def editar(lid: int, data: dict = Body(...)):
    db = SessionLocal()
    l = db.get(Lancamento, lid)
    if not l:
        db.close()
        return JSONResponse({"erro": "não encontrado"}, status_code=404)
    for campo in ("usuario", "tipo", "descricao", "categoria", "subcategoria"):
        if campo in data and data[campo] is not None:
            setattr(l, campo, data[campo])
    if "valor" in data and data["valor"] is not None:
        l.valor = float(data["valor"])
    if data.get("data"):
        try:
            l.data = datetime.fromisoformat(data["data"])
        except Exception:
            pass
    db.commit()
    r = row(l)
    db.close()
    return r


@app.post("/api/lancamentos/{lid}/duplicate")
def duplicar(lid: int, data: dict = Body(default={})):
    db = SessionLocal()
    o = db.get(Lancamento, lid)
    if not o:
        db.close()
        return JSONResponse({"erro": "não encontrado"}, status_code=404)
    novo = Lancamento(
        usuario=o.usuario, tipo=o.tipo, descricao=o.descricao,
        categoria=o.categoria, subcategoria=o.subcategoria,
        valor=float(data.get("valor", o.valor)), data=datetime.now(),
    )
    db.add(novo)
    db.commit()
    r = row(novo)
    db.close()
    return r


@app.delete("/api/lancamentos/{lid}")
def excluir(lid: int):
    db = SessionLocal()
    l = db.get(Lancamento, lid)
    if l:
        db.delete(l)
        db.commit()
    db.close()
    return {"ok": True}


# ---------- CATEGORIAS ----------
@app.get("/api/categorias")
def cats():
    d = catstore.load()
    despesas = [{"kw": k, "categoria": v[0], "subcategoria": v[1]} for k, v in d["despesas"].items()]
    receitas = [{"kw": k, "subcategoria": v} for k, v in d["receitas"].items()]
    despesas.sort(key=lambda x: (x["categoria"], x["kw"]))
    receitas.sort(key=lambda x: x["kw"])
    return {"despesas": despesas, "receitas": receitas}


@app.post("/api/categorias/despesa")
def cat_desp_add(data: dict = Body(...)):
    d = catstore.load()
    kws = [k.strip().lower() for k in (data.get("kw") or "").split(",") if k.strip()]
    if not kws:
        return JSONResponse({"erro": "palavra-chave vazia"}, status_code=400)
    if data.get("kw_old") and data["kw_old"] not in kws:
        d["despesas"].pop(data["kw_old"], None)
    cat = data.get("categoria") or "Outros"
    sub = data.get("subcategoria") or "Outros"
    for kw in kws:
        d["despesas"][kw] = [cat, sub]
    catstore.save(d)
    return {"ok": True}


@app.delete("/api/categorias/despesa/{kw}")
def cat_desp_del(kw: str):
    d = catstore.load()
    d["despesas"].pop(kw, None)
    catstore.save(d)
    return {"ok": True}


@app.post("/api/categorias/receita")
def cat_rec_add(data: dict = Body(...)):
    d = catstore.load()
    kws = [k.strip().lower() for k in (data.get("kw") or "").split(",") if k.strip()]
    if not kws:
        return JSONResponse({"erro": "palavra-chave vazia"}, status_code=400)
    if data.get("kw_old") and data["kw_old"] not in kws:
        d["receitas"].pop(data["kw_old"], None)
    sub = data.get("subcategoria") or "Outros"
    for kw in kws:
        d["receitas"][kw] = sub
    catstore.save(d)
    return {"ok": True}


@app.delete("/api/categorias/receita/{kw}")
def cat_rec_del(kw: str):
    d = catstore.load()
    d["receitas"].pop(kw, None)
    catstore.save(d)
    return {"ok": True}
