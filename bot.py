import calendar
from datetime import datetime
from sqlalchemy import extract, func
from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, Lancamento, Fixa, Cofrinho, CofrinhoMov, Bem
from parser import parse


def _brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _cofre_saldo(db, cid):
    def s(tipo):
        return db.query(func.coalesce(func.sum(CofrinhoMov.valor), 0.0)).filter(
            CofrinhoMov.cofrinho_id == cid, CofrinhoMov.tipo == tipo).scalar()
    return round(s("Aporte") - s("Resgate") + s("Rendimento"), 2)


def _lanc_do_mes(db, fid, mes, ano):
    return db.query(Lancamento).filter(
        Lancamento.fixa_id == fid,
        extract("month", Lancamento.data) == mes,
        extract("year", Lancamento.data) == ano,
    ).first()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    r = parse(texto)
    if not r:
        await update.message.reply_text("❌ Não entendi. Envie algo como: Pizza 89")
        return

    usuario = update.effective_user.first_name or str(update.effective_user.id)

    db = SessionLocal()
    lanc = Lancamento(
        usuario=usuario,
        tipo=r["tipo"],
        descricao=r["descricao"],
        categoria=r["categoria"],
        subcategoria=r["subcategoria"],
        valor=r["valor"],
    )
    db.add(lanc)
    db.commit()
    lid = lanc.id
    db.close()

    await update.message.reply_text(
        "✅ Lançamento registrado\n"
        f"Tipo: {r['tipo']}\n"
        f"Descrição: {r['descricao']}\n"
        f"Categoria: {r['categoria']}\n"
        f"Subcategoria: {r['subcategoria']}\n"
        f"Valor: {_brl(r['valor'])}\n"
        f"Nº: {lid}  (apagar: /apagar {lid})"
    )


async def ultimos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    rows = db.query(Lancamento).order_by(Lancamento.id.desc()).limit(8).all()
    db.close()
    if not rows:
        await update.message.reply_text("Nenhum lançamento ainda.")
        return
    linhas = [
        f"#{l.id} {l.descricao} — {_brl(l.valor)} ({l.tipo}, {l.usuario})"
        for l in rows
    ]
    await update.message.reply_text(
        "Últimos lançamentos:\n" + "\n".join(linhas) + "\n\nPara apagar: /apagar <número>"
    )


async def apagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: /apagar 12")
        return
    lid = int(context.args[0])
    db = SessionLocal()
    l = db.get(Lancamento, lid)
    if not l:
        db.close()
        await update.message.reply_text(f"#{lid} não encontrado.")
        return
    desc = l.descricao
    db.delete(l)
    db.commit()
    db.close()
    await update.message.reply_text(f"🗑️ #{lid} ({desc}) apagado.")


async def fixas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agora = datetime.now()
    mes, ano = agora.month, agora.year
    db = SessionLocal()
    rows = db.query(Fixa).filter(Fixa.ativo == True).order_by(Fixa.dia.asc()).all()
    itens = [(f, _lanc_do_mes(db, f.id, mes, ano) is not None) for f in rows]
    db.close()
    if not itens:
        await update.message.reply_text("Nenhuma conta fixa cadastrada.")
        return
    pend = [(f, pago) for f, pago in itens if not pago]
    ok = [(f, pago) for f, pago in itens if pago]
    linhas = ["📌 *Fixas do mês*", ""]
    if pend:
        linhas.append("⏳ Pendentes:")
        for f, _ in pend:
            marca = "recebi" if f.tipo == "Receita" else "paguei"
            linhas.append(f"#{f.id} dia {f.dia} · {f.descricao} — {_brl(f.valor)}  (/pagar {f.id})")
        linhas.append("")
    if ok:
        linhas.append("✅ Já lançadas:")
        for f, _ in ok:
            linhas.append(f"#{f.id} {f.descricao} — {_brl(f.valor)}")
    await update.message.reply_text("\n".join(linhas), parse_mode="Markdown")


async def pagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: /pagar 3  (o número da fixa em /fixas)")
        return
    fid = int(context.args[0])
    agora = datetime.now()
    mes, ano = agora.month, agora.year
    db = SessionLocal()
    f = db.get(Fixa, fid)
    if not f:
        db.close()
        await update.message.reply_text(f"Fixa #{fid} não encontrada. Veja /fixas")
        return
    if _lanc_do_mes(db, fid, mes, ano):
        db.close()
        await update.message.reply_text(f"#{fid} ({f.descricao}) já estava lançada neste mês.")
        return
    dia = min(int(f.dia or 1), calendar.monthrange(ano, mes)[1])
    l = Lancamento(
        usuario=f.usuario, tipo=f.tipo, descricao=f.descricao,
        categoria=f.categoria, subcategoria=f.subcategoria,
        valor=float(f.valor or 0), data=datetime(ano, mes, dia), fixa_id=fid,
    )
    db.add(l)
    db.commit()
    db.close()
    verbo = "Receita registrada" if f.tipo == "Receita" else "Conta paga"
    await update.message.reply_text(f"✅ {verbo}: {f.descricao} — {_brl(f.valor)}")


async def cofrinho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    cofres = db.query(Cofrinho).filter(Cofrinho.ativo == True).order_by(Cofrinho.id.asc()).all()
    linhas = ["🏦 *Cofrinhos*", ""]
    total_c = 0.0
    for c in cofres:
        saldo = _cofre_saldo(db, c.id)
        total_c += saldo
        linhas.append(f"#{c.id} {c.emoji or ''} {c.nome} — {_brl(saldo)}  (/aportar {c.id} <valor>)")
    if not cofres:
        linhas.append("_Nenhum cofrinho cadastrado._")
    rec = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(Lancamento.tipo == "Receita").scalar()
    desp = db.query(func.coalesce(func.sum(Lancamento.valor), 0.0)).filter(Lancamento.tipo == "Despesa").scalar()
    bens = db.query(func.coalesce(func.sum(Bem.valor), 0.0)).filter(Bem.ativo == True).scalar()
    db.close()
    conta = rec - desp
    total = conta + total_c + bens
    linhas += ["", f"💰 Conta: {_brl(conta)}", f"◈ Cofrinhos: {_brl(total_c)}", f"⌂ Bens: {_brl(bens)}",
               f"*Patrimônio total: {_brl(total)}*"]
    await update.message.reply_text("\n".join(linhas), parse_mode="Markdown")


async def aportar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("Use: /aportar 1 500  (nº do cofrinho e valor)")
        return
    cid = int(context.args[0])
    try:
        valor = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("Valor inválido. Ex.: /aportar 1 500")
        return
    db = SessionLocal()
    c = db.get(Cofrinho, cid)
    if not c:
        db.close()
        await update.message.reply_text(f"Cofrinho #{cid} não encontrado. Veja /cofrinho")
        return
    usuario = update.effective_user.first_name or "Casal"
    l = Lancamento(usuario=usuario, tipo="Despesa", descricao=f"Aporte · {c.nome}",
                   categoria="Investimento", subcategoria=c.nome, valor=valor)
    db.add(l)
    db.commit()
    db.add(CofrinhoMov(cofrinho_id=cid, tipo="Aporte", valor=valor, lanc_id=l.id))
    db.commit()
    saldo = _cofre_saldo(db, cid)
    db.close()
    await update.message.reply_text(f"✅ Aporte de {_brl(valor)} em {c.nome}.\nSaldo do cofrinho: {_brl(saldo)}")
