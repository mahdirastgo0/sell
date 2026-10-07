import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
import uvicorn
from app.config import settings
from app.bot.handlers import router

logging.basicConfig(level=getattr(logging,settings.log_level.upper(),logging.INFO),format='%(asctime)s %(levelname)s %(name)s %(message)s')
app=FastAPI(title='VPN Bot API',version='1.0.0')
@app.get('/health')
async def health(): return {'ok':True}

async def run_bot():
    bot=Bot(settings.bot_token)
    dp=Dispatcher(storage=MemoryStorage());dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    try: await dp.start_polling(bot)
    finally: await bot.session.close()

async def run_api():
    server=uvicorn.Server(uvicorn.Config(app,host='0.0.0.0',port=8000,log_level=settings.log_level.lower()))
    await server.serve()

async def main(): await asyncio.gather(run_bot(),run_api())
if __name__=='__main__': asyncio.run(main())
