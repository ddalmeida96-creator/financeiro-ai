from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, Lancamento
from parser import parse


def _brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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
