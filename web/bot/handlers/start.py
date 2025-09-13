from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ✅ 'bot.' ni olib tashlash
from utils.db import Database
from utils.config import LANGUAGES
from utils.keyboards import get_main_menu_keyboard, get_language_keyboard
import logging

start_router = Router()

class LanguageState(StatesGroup):
    choosing_language = State()

# Til tanlash keyboardi
def get_language_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇺🇸 English")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# Tilga qarab xabarlar
def get_welcome_message(language):
    messages = {
        'uz': "👋 Assalomu alaykum! Botimizga xush kelibsiz!\n\n"
             "📝 E'lon joylash yoki sotib olish uchun kerakli bo'limni tanlang.",
        'ru': "👋 Здравствуйте! Добро пожаловать в нашего бота!\n\n"
             "📝 Выберите нужный раздел для размещения или покупки объявлений.",
        'en': "👋 Hello! Welcome to our bot!\n\n"
             "📝 Choose the desired section to place or buy ads."
    }
    return messages.get(language, messages['uz'])

def get_language_request_message(language):
    messages = {
        'uz': "🌐 Iltimos, tilni tanlang:",
        'ru': "🌐 Пожалуйста, выберите язык:",
        'en': "🌐 Please choose a language:"
    }
    return messages.get(language, messages['uz'])

@start_router.message(Command("start"))
async def start_handler(message: Message, db: Database, logger: logging.Logger, state: FSMContext):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        
        logger.info(f"👤 Foydalanuvchi start bosdi: {user_id} - {username}")
        
        # Foydalanuvchini bazadan olish
        user = await db.get_user(user_id)
        
        if user and user['language']:
            # Agar til allaqachon tanlangan bo'lsa
            user_language = user['language']
            
            # Ma'lumotlarni yangilash (agar kerak bo'lsa)
            await db.add_user(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone=user.get('phone'),
                language=user_language
            )
            
            # ✅ TO'G'RI: Xabar BILAN keyboard yuborish
            await message.answer(
                get_welcome_message(user_language),
                reply_markup=get_main_menu_keyboard(user_language)  # ✅ MENYU QO'SHILDI
            )
            
            logger.info(f"✅ Foydalanuvchi {user_id} allaqachon {user_language} tilini tanlagan")
            
        else:
            # Agar til tanlanmagan bo'lsa
            # Foydalanuvchini bazaga qo'shish (dastlab til None)
            await db.add_user(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone=None,
                language=None
            )
            
            # Til tanlashni so'rash (dastlabki til uz deb hisoblaymiz)
            await message.answer(
                get_language_request_message('uz'),
                reply_markup=get_language_keyboard()
            )
            
            # Til tanlash holatiga o'tish
            await state.set_state(LanguageState.choosing_language)
            logger.info(f"🌐 Foydalanuvchi {user_id} til tanlaydi")
        
    except Exception as e:
        logger.error(f"Start handler xatosi: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

@start_router.message(LanguageState.choosing_language)
async def language_chosen_handler(message: Message, db: Database, logger: logging.Logger, state: FSMContext):
    try:
        user_id = message.from_user.id
        text = message.text
        
        # Tanlangan tilni aniqlash
        language_choice = None
        if text == "🇺🇿 O'zbekcha":
            language_choice = 'uz'
        elif text == "🇷🇺 Русский":
            language_choice = 'ru' 
        elif text == "🇺🇸 English":
            language_choice = 'en'
        
        if language_choice:
            # Tilni bazaga saqlash
            await db.add_user(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                phone=None,
                language=language_choice
            )
            
            # ✅ Asosiy menyuni ko'rsatish
            await message.answer(
                get_welcome_message(language_choice),
                reply_markup=get_main_menu_keyboard(language_choice)
            )
            
            logger.info(f"✅ Foydalanuvchi {user_id} {language_choice} tilini tanladi")
            await state.clear()
            
    except Exception as e:
        logger.error(f"Language choice error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# Export qilish
router = start_router