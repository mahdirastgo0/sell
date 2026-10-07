import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
import uvicorn
from sqlalchemy import text
from app.config import settings
from app.bot.handlers import router
from app.db.session import engine

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format='%(asctime)s %(levelname)s %(name)s %(message)s')
log = logging.getLogger(__name__)
app = FastAPI(title='VPN Sales Bot - Foreign VPS', version='2.0.0')

@app.get('/health')
async def health():
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        pass
    return {'ok': db_ok, 'role': 'foreign-bot-server', 'panel': settings.panel_base_url}

async def run_bot():
    bot = Bot(settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    log.info('Starting Telegram bot on FOREIGN VPS. It will connect only to Telegram and the Iran 3x-ui API.')
    try:
        # Polling is intentional: no public HTTPS certificate/domain is required on the bot VPS.
        # Telegram traffic terminates on this foreign VPS, not on the Iran server.
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

async def run_api():
    server = uvicorn.Server(uvicorn.Config(app, host='0.0.0.0', port=settings.api_port, log_level=settings.log_level.lower()))
    await server.serve()

async def main():
    await asyncio.gather(run_bot(), run_api())

if __name__ == '__main__':
    asyncio.run(main())
