from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

# ✅ 'bot.' ni olib tashlash
from utils.db import Database
from utils.config import ADMIN_ID

admin_router = Router()

# ... (qolgan kod o'zgarmaydi)

# Export qilish
router = admin_router

# Admin holatlari
class AdminStates(StatesGroup):
    waiting_for_advert = State()
    waiting_for_user_id = State()
    waiting_for_message = State()

# Asosiy admin panel
def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='📊 Statistika'), KeyboardButton(text='📣 Reklama yuborish')],
            [KeyboardButton(text='👥 Foydalanuvchilar'), KeyboardButton(text='🏠 E\'lonlar')],
            [KeyboardButton(text='🔍 Foydalanuvchi qidirish'), KeyboardButton(text='🚫 Bloklash')],
            [KeyboardButton(text='⚙️ Sozlamalar'), KeyboardButton(text='◀️ Asosiy menyu')]
        ],
        resize_keyboard=True
    )

# Admin panel
@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Siz admin emassiz!")
        return
        
    await message.answer(
        "👨‍💻 Admin panelga xush kelibsiz!\n\n"
        "Quyidagi imkoniyatlardan foydalanishingiz mumkin:",
        reply_markup=get_admin_keyboard()
    )

# Statistika
@admin_router.message(F.text == '📊 Statistika')
async def show_stats(message: Message, db: Database):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        stats = await db.get_stats()
        
        stats_text = (
            "📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 <b>Foydalanuvchilar:</b>\n"
            f"• Jami: {stats['users']['total']}\n"
            f"• Kunlik: {stats['users']['daily']}\n"
            f"• Haftalik: {stats['users']['weekly']}\n"
            f"• Oylik: {stats['users']['monthly']}\n"
            f"• E'lon joylagan: {stats['users']['with_listings']}\n\n"
            f"🏠 <b>E'lonlar:</b>\n"
            f"• Jami: {stats['listings']['total']}\n"
            f"• Kunlik: {stats['listings']['daily']}\n"
            f"• Haftalik: {stats['listings']['weekly']}\n"
            f"• Oylik: {stats['listings']['monthly']}\n"
            f"• Faol: {stats['listings']['active']}\n"
            f"• Nofaol: {stats['listings']['inactive']}"
        )
        
        await message.answer(stats_text, parse_mode='HTML')
        
    except Exception as e:
        await message.answer(f"❌ Statistika olishda xatolik: {str(e)}")

# Foydalanuvchilar ro'yxati
@admin_router.message(F.text == '👥 Foydalanuvchilar')
async def show_users(message: Message, db: Database):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        users = await db.get_all_users()
        
        if not users:
            await message.answer("❌ Hozircha foydalanuvchilar mavjud emas")
            return
            
        users_text = "👥 <b>Oxirgi 10 foydalanuvchi:</b>\n\n"
        
        for i, user in enumerate(users[:10], 1):
            username = f"@{user['username']}" if user['username'] else "Yo'q"
            users_text += (
                f"{i}. <b>ID:</b> {user['user_id']}\n"
                f"   <b>Ism:</b> {user['first_name']} {user['last_name'] or ''}\n"
                f"   <b>Username:</b> {username}\n"
                f"   <b>Qo'shilgan:</b> {user['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
                f"   ─────────────────\n"
            )
            
        await message.answer(users_text, parse_mode='HTML')
        
    except Exception as e:
        await message.answer(f"❌ Foydalanuvchilarni olishda xatolik: {str(e)}")

# Reklama yuborish
@admin_router.message(F.text == '📣 Reklama yuborish')
async def send_advert(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
        
    await message.answer(
        "📣 Reklama matnini yuboring yoki forward qiling:\n\n"
        "⚠️ Eslatma: Barcha foydalanuvchilarga yuboriladi",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='🔙 Bekor qilish')]],
            resize_keyboard=True
        )
    )
    await state.set_state(AdminStates.waiting_for_advert)

@admin_router.message(AdminStates.waiting_for_advert, F.text == '🔙 Bekor qilish')
async def cancel_advert(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Reklama yuborish bekor qilindi", reply_markup=get_admin_keyboard())

@admin_router.message(AdminStates.waiting_for_advert)
async def process_advert(message: Message, state: FSMContext, db: Database, bot):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        users = await db.get_all_users()
        total = len(users)
        success = 0
        failed = 0
        
        # Progress xabari
        progress_msg = await message.answer(f"📤 Reklama yuborilmoqda... 0/{total}")
        
        for i, user in enumerate(users, 1):
            try:
                if message.text:
                    await bot.send_message(user['user_id'], message.text)
                elif message.photo:
                    await bot.send_photo(user['user_id'], message.photo[-1].file_id, caption=message.caption)
                elif message.video:
                    await bot.send_video(user['user_id'], message.video.file_id, caption=message.caption)
                else:
                    await message.send_copy(chat_id=user['user_id'])
                
                success += 1
                
                # Har 10ta yuborilganda progress yangilash
                if i % 10 == 0:
                    await progress_msg.edit_text(f"📤 Reklama yuborilmoqda... {i}/{total}")
                    
                # Spamdan saqlash uchun kichik kutish
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed += 1
                print(f"Xatolik user {user['user_id']}: {e}")
                
        await progress_msg.delete()
        await message.answer(
            f"✅ Reklama yuborish tugallandi!\n\n"
            f"• Jami: {total}\n"
            f"• Muvaffaqiyatli: {success}\n"
            f"• Xatolik: {failed}",
            reply_markup=get_admin_keyboard()
        )
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_admin_keyboard())
    
    await state.clear()

# Foydalanuvchi qidirish
@admin_router.message(F.text == '🔍 Foydalanuvchi qidirish')
async def search_user(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
        
    await message.answer(
        "🔍 Foydalanuvchi ID sini yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='🔙 Bekor qilish')]],
            resize_keyboard=True
        )
    )
    await state.set_state(AdminStates.waiting_for_user_id)

@admin_router.message(AdminStates.waiting_for_user_id, F.text == '🔙 Bekor qilish')
async def cancel_search(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Qidiruv bekor qilindi", reply_markup=get_admin_keyboard())

@admin_router.message(AdminStates.waiting_for_user_id)
async def process_user_search(message: Message, state: FSMContext, db: Database):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        user_id = int(message.text)
        user = await db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi")
            return
            
        user_info = (
            "👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
            f"🆔 <b>ID:</b> {user['user_id']}\n"
            f"👤 <b>Ism:</b> {user['first_name']} {user['last_name'] or ''}\n"
            f"📧 <b>Username:</b> @{user['username'] or "Yo'q"}\n"
            f"📞 <b>Telefon:</b> {user['phone'] or "Yo'q"}\n"
            f"🌐 <b>Til:</b> {user['language']}\n"
            f"📅 <b>Qo'shilgan:</b> {user['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
            f"📊 <b>E'lonlar soni:</b> ..."
        )
        
        # Foydalanuvchi e'lonlarini olish
        listings = await db.get_user_listings(user_id)
        
        user_info += f"\n🏠 <b>E'lonlar soni:</b> {len(listings)}"
        
        if listings:
            user_info += "\n\n<b>Oxirgi e'lonlar:</b>"
            for i, listing in enumerate(listings[:3], 1):
                status = "✅ Faol" if listing['is_active'] else "❌ Nofaol"
                user_info += f"\n{i}. {listing['title']} - {listing['price']} so'm ({status})"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Xabar yuborish", callback_data=f"send_msg_{user_id}"),
             InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"block_{user_id}")],
            [InlineKeyboardButton(text="🏠 E'lonlarni ko'rish", callback_data=f"view_listings_{user_id}")]
        ])
        
        await message.answer(user_info, parse_mode='HTML', reply_markup=keyboard)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID format. Faqat raqam kiriting.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
    
    await state.clear()

# Asosiy menyuga qaytish
@admin_router.message(F.text == '◀️ Asosiy menyu')
async def back_to_main(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    await message.answer("🏠 Asosiy menyuga qaytingiz", reply_markup=ReplyKeyboardRemove())

# Callback handlerlar
@admin_router.callback_query(F.data.startswith('send_msg_'))
async def send_message_to_user(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[-1]
    await callback.message.answer(f"✉️ Foydalanuvchi {user_id} ga xabar yuboring:")
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_message)
    await callback.answer()

@admin_router.message(AdminStates.waiting_for_message)
async def process_user_message(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    try:
        await message.send_copy(chat_id=target_user_id)
        await message.answer("✅ Xabar muvaffaqiyatli yuborildi!", reply_markup=get_admin_keyboard())
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=get_admin_keyboard())
    
    await state.clear()

# E'lonlar boshqaruvi
@admin_router.message(F.text == '🏠 E\'lonlar')
async def manage_listings(message: Message, db: Database):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        stats = await db.get_stats()
        
        listings_text = (
            "🏠 <b>E'lonlar Boshqaruvi</b>\n\n"
            f"📊 <b>Umumiy statistikalar:</b>\n"
            f"• Jami e'lonlar: {stats['listings']['total']}\n"
            f"• Faol e'lonlar: {stats['listings']['active']}\n"
            f"• Nofaol e'lonlar: {stats['listings']['inactive']}\n\n"
            f"📈 <b>Oxirgi 24 soat:</b> {stats['listings']['daily']} ta yangi e'lon"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Barcha e'lonlar", callback_data="all_listings"),
            InlineKeyboardButton(text="✅ Faol e'lonlar", callback_data="active_listings")],
            [InlineKeyboardButton(text="❌ Nofaol e'lonlar", callback_data="inactive_listings"),
            InlineKeyboardButton(text="🔄 Yangilanishlar", callback_data="refresh_stats")]
        ])
        
        await message.answer(listings_text, parse_mode='HTML', reply_markup=keyboard)
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        
        
# Export qilish
router = admin_router        