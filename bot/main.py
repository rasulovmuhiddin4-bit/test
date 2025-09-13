import os
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Joriy papkani yo'lga qo'shamiz (bot papkasi)
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Local importlar
from utils.config import BOT_TOKEN
from utils.db import Database
from utils.logger import logger
from handlers.start import start_router
from handlers.user import user_router
from handlers.admin import admin_router

# Environment variables ni yuklash
load_dotenv()

async def on_startup(db: Database):
    """Bot ishga tushganda"""
    logger.info("🤖 Bot ishga tushmoqda...")
    await db.create_tables()
 # ✅ Yangi qo'shildi
    logger.info("✅ Database jadvallari yaratildi va yangilandi")
    
    try:
        # Stats chiqarish
        stats = await db.get_stats()
        logger.info(f"📊 Stats: {stats['users']['total']} foydalanuvchi, {stats['listings']['total']} e'lon")
    except Exception as e:
        logger.warning(f"⚠️ Stats olishda xatolik: {e}")

async def on_shutdown(db: Database):
    """Bot to'xtaganda"""
    logger.info("🛑 Bot to'xtamoqda...")
    await db.close()
    logger.info("✅ Database connection yopildi")

async def main():
    db = None
    bot = None
    try:
        # Database yaratish
        db = Database()
        
        # Startup
        await on_startup(db)
        
        # Bot yaratish
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Dispatcher yaratish
        dp = Dispatcher(storage=MemoryStorage())
        
        # Dependency injection
        dp.workflow_data.update({
            'db': db,
            'logger': logger
        })
        
        # Handlerlarni ro'yxatdan o'tkazish (barcha routerlarni qo'shish)
        dp.include_router(start_router)
        dp.include_router(user_router)
        dp.include_router(admin_router)

        logger.info("✅ Bot muvaffaqiyatli ishga tushdi")
        logger.info("📍 Polling rejimida ishlayapdi...")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Xatolik yuz berdi: {e}", exc_info=True)
    finally:
        if db:
            await on_shutdown(db)
        if bot:
            await bot.session.close()
            logger.info("✅ Bot session yopildi")

if __name__ == "__main__":
    asyncio.run(main())