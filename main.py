import asyncio
import os
import uvicorn
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from database import init_db
from bot import handle_message, ultimos, apagar, fixas, pagar, cofrinho, aportar
from dashboard import app

load_dotenv()
init_db()


async def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise SystemExit("Defina TELEGRAM_TOKEN no arquivo .env")

    tg = Application.builder().token(token).build()
    tg.add_handler(CommandHandler("ultimos", ultimos))
    tg.add_handler(CommandHandler("apagar", apagar))
    tg.add_handler(CommandHandler("fixas", fixas))
    tg.add_handler(CommandHandler("pagar", pagar))
    tg.add_handler(CommandHandler("cofrinho", cofrinho))
    tg.add_handler(CommandHandler("aportar", aportar))
    tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="warning")
    )

    async with tg:
        await tg.start()
        await tg.updater.start_polling()
        print("Bot rodando. Dashboard em http://localhost:8000")
        await server.serve()
        await tg.updater.stop()
        await tg.stop()


if __name__ == "__main__":
    asyncio.run(main())
