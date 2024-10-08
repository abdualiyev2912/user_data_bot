import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import user_router
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from utils.notify_admins import notify_admins
from handlers import user_handlers
from dotenv import load_dotenv


load_dotenv()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Botni boshlash"),
        BotCommand(command="/add", description="Yangi dacha qo'shish"),
        BotCommand(command="/mydachas", description="Mening dachalarim"),
        BotCommand(command="/help", description="Yordam")
    ]
    await bot.set_my_commands(commands)

async def onstartup(bot: Bot):
    await notify_admins("Bot ishga tushdi!", bot)

async def shutdown(bot: Bot):
    await notify_admins("Bot ishdan to'xtatildi!", bot)

async def bot_task():
    bot = Bot(token=str(os.getenv("BOT_TOKEN")))
    
    dp.startup.register(onstartup)
    user_handlers.register_handlers(dp)
    dp.shutdown.register(shutdown)

    await set_commands(bot)
    await dp.start_polling(bot)

app = FastAPI(docs_url="/api/v1/docs")

origins = ["http://localhost:8000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(user_router, prefix="/api/v1/users")

# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(bot_task()) 

