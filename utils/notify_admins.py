from aiogram import Bot
from utils.db import SessionLocal
from models import User, UserRole

async def notify_admins(message: str, bot: Bot):
    session = SessionLocal()
    admins = session.query(User).filter(User.role==UserRole.ADMIN).all() 
    for admin in admins:
        try:
            await bot.send_message(chat_id=admin.id, text=message)
        except:
            pass