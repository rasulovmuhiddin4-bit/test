from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.media_group import MediaGroupBuilder
from utils.config import BACKUP_CHANNEL_ID
from utils.config import ADMIN_IDS
from utils.logger import logger
from aiogram.types import InputMediaPhoto
import logging

from utils.db import Database
from utils.keyboards import (
    get_main_menu_keyboard, 
    get_back_button,
    get_phone_keyboard,
    get_location_keyboard,
    get_confirmation_keyboard
)

user_router = Router()

class PostAdState(StatesGroup):
    choosing_category = State()
    choosing_floor = State()
    choosing_rooms = State()
    entering_title = State()
    entering_description = State()
    entering_price = State()
    requesting_phone = State()
    requesting_optional_phone = State()
    requesting_location = State()
    uploading_photos = State()
    confirmation = State()

# Inline keyboardlar
def get_category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍👩‍👧‍👦 Oilaga", callback_data="category_oilaga")],
        [InlineKeyboardButton(text="👩 Qizlarga", callback_data="category_qizlarga")],
        [InlineKeyboardButton(text="👶 Bollarga", callback_data="category_bollarga")],
        [InlineKeyboardButton(text="👥 Hammaga", callback_data="category_hammaga")]
    ])

def get_floor_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1-qavat", callback_data="floor_1"),
         InlineKeyboardButton(text="2-qavat", callback_data="floor_2"),
         InlineKeyboardButton(text="3-qavat", callback_data="floor_3")],
        [InlineKeyboardButton(text="4-qavat", callback_data="floor_4"),
         InlineKeyboardButton(text="5-qavat", callback_data="floor_5"),
         InlineKeyboardButton(text="6+ qavat", callback_data="floor_6plus")]
    ])

def get_rooms_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 xona", callback_data="rooms_1"),
         InlineKeyboardButton(text="2 xona", callback_data="rooms_2")],
        [InlineKeyboardButton(text="3 xona", callback_data="rooms_3"),
         InlineKeyboardButton(text="4 xona", callback_data="rooms_4")],
        [InlineKeyboardButton(text="5+ xona", callback_data="rooms_5plus")]
    ])


# user.py fayliga qo'shing

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# ... existing code ...

@user_router.message(F.text == "📁 Mening e'lonlarim")
async def my_ads_handler(message: Message, db: Database):
    """Foydalanuvchining e'lonlarini ko'rsatish"""
    try:
        listings = await db.get_user_listings(message.from_user.id)
        
        if not listings:
            await message.answer("📭 Sizda hali e'lonlar mavjud emas.")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for listing in listings[:10]:  # Oxirgi 10 ta e'lon
            status = "✅" if listing.get('status') == 'active' else "❌"
            btn_text = f"{status} {listing['title'][:30]}..."
            
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"myad_{listing['id']}"
                )
            ])
        
        # Sahifalash tugmalari (agar ko'p e'lon bo'lsa)
        if len(listings) > 10:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="⬅️ Oldingi", callback_data="myads_prev"),
                InlineKeyboardButton(text="Keyingi ➡️", callback_data="myads_next")
            ])
        
        await message.answer(
            f"📁 Sizning e'lonlaringiz ({len(listings)} ta):\n\n"
            "Har bir e'lonni boshqarish uchun ustiga bosing:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"My ads error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")

@user_router.callback_query(F.data.startswith("myad_"))
async def my_ad_detail_handler(callback: CallbackQuery, db: Database):
    """Ma'lum bir e'lonni boshqarish"""
    try:
        listing_id = int(callback.data.split("_")[1])
        listing = await db.get_listing(listing_id)
        
        if not listing or listing['user_id'] != callback.from_user.id:
            await callback.answer("❌ E'lon topilmadi yoki ruxsat yo'q")
            return
        
        status_text = "✅ Faol" if listing.get('status') == 'active' else "❌ Nofaol"
        views = listing.get('views', 0)
        
        ad_text = (
            f"🏠 <b>E'lon ma'lumotlari</b>\n\n"
            f"📌 <b>Sarlavha:</b> {listing['title']}\n"
            f"📝 <b>Tavsif:</b> {listing['description'][:100]}...\n"
            f"💰 <b>Narx:</b> {listing['price']} {listing.get('currency', 'UZS')}\n"
            f"📞 <b>Telefon:</b> {listing['phone']}\n"
            f"📊 <b>Holat:</b> {status_text}\n"
            f"👁️ <b>Ko'rishlar:</b> {views}\n"
            f"📅 <b>Yaratilgan:</b> {listing['created_at'].strftime('%Y-%m-%d %H:%M')}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Faollashtirish" if listing.get('status') != 'active' else "❌ Nofaollashtirish",
                    callback_data=f"toggle_{listing_id}"
                )
            ],
            [
                InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_{listing_id}"),
                InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_{listing_id}")
            ],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_myads")]
        ])
        
        # Agar rasm bor bo'lsa, rasm bilan jo'natish
        if listing.get('photos'):
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=listing['photos'][0],
                caption=ad_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await callback.message.edit_text(ad_text, reply_markup=keyboard, parse_mode='HTML')
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"My ad detail error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")

@user_router.callback_query(F.data.startswith("toggle_"))
async def toggle_ad_status_handler(callback: CallbackQuery, db: Database):
    """E'lon holatini o'zgartirish"""
    try:
        listing_id = int(callback.data.split("_")[1])
        listing = await db.get_listing(listing_id)
        
        if not listing or listing['user_id'] != callback.from_user.id:
            await callback.answer("❌ E'lon topilmadi")
            return
        
        new_status = 'inactive' if listing.get('status') == 'active' else 'active'
        success = await db.update_listing_status(listing_id, new_status)
        
        if success:
            status_text = "✅ Faol" if new_status == 'active' else "❌ Nofaol"
            await callback.answer(f"E'lon holati: {status_text}")
            
            # Yangilangan ma'lumotlarni ko'rsatish
            listing['status'] = new_status
            status_text = "✅ Faol" if new_status == 'active' else "❌ Nofaol"
            
            ad_text = (
                f"🏠 <b>E'lon ma'lumotlari</b>\n\n"
                f"📌 <b>Sarlavha:</b> {listing['title']}\n"
                f"📝 <b>Tavsif:</b> {listing['description'][:100]}...\n"
                f"💰 <b>Narx:</b> {listing['price']} {listing.get('currency', 'UZS')}\n"
                f"📞 <b>Telefon:</b> {listing['phone']}\n"
                f"📊 <b>Holat:</b> {status_text}\n"
                f"👁️ <b>Ko'rishlar:</b> {listing.get('views', 0)}\n"
                f"📅 <b>Yaratilgan:</b> {listing['created_at'].strftime('%Y-%m-%d %H:%M')}"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Faollashtirish" if new_status != 'active' else "❌ Nofaollashtirish",
                        callback_data=f"toggle_{listing_id}"
                    )
                ],
                [
                    InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_{listing_id}"),
                    InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_{listing_id}")
                ],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_myads")]
            ])
            
            if callback.message.photo:
                await callback.message.edit_caption(caption=ad_text, reply_markup=keyboard)
            else:
                await callback.message.edit_text(ad_text, reply_markup=keyboard, parse_mode='HTML')
        else:
            await callback.answer("❌ Xatolik yuz berdi")
            
    except Exception as e:
        logger.error(f"Toggle status error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")

@user_router.callback_query(F.data.startswith("delete_"))
async def delete_ad_handler(callback: CallbackQuery, db: Database):
    """E'lonni o'chirish (foydalanuvchi yoki admin)"""
    try:
        listing_id = int(callback.data.split("_")[1])
        listing = await db.get_listing(listing_id)

        # Faqat admin yoki e'lon egasi o'chira oladi
        if not listing or (listing['user_id'] != callback.from_user.id and callback.from_user.id not in ADMIN_IDS):
            await callback.answer("❌ Siz bu e’loni o‘chira olmaysiz")
            return

        # Tasdiqlash keyboard
        confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_delete_{listing_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=f"cancel_delete_{listing_id}")
        ]])

        if callback.message.photo:
            await callback.message.edit_caption(
                caption=(f"🗑️ <b>E'lonni o'chirish</b>\n\n"
                         f"\"{listing['title']}\" e'lonini rostdan ham o'chirmoqchimisiz?\n\n"
                         f"⚠️ Bu amalni ortga qaytarib bo'lmaydi!"),
                reply_markup=confirm_keyboard,
                parse_mode='HTML'
            )
        else:
            await callback.message.edit_text(
                f"🗑️ <b>E'lonni o'chirish</b>\n\n"
                f"\"{listing['title']}\" e'lonini rostdan ham o'chirmoqchimisiz?\n\n"
                f"⚠️ Bu amalni ortga qaytarib bo'lmaydi!",
                reply_markup=confirm_keyboard,
                parse_mode='HTML'
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Delete ad error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")


@user_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_handler(callback: CallbackQuery, db: Database):
    """E'lonni o'chirishni tasdiqlash (faqat egasi yoki admin o'chira oladi)"""
    try:
        listing_id = int(callback.data.split("_")[2])

        # Faqat foydalanuvchi o'z e'lonini yoki admin o'chira oladi
        if callback.from_user.id in ADMIN_IDS:
            success = await db.delete_listing(listing_id, None, is_admin=True)  # Admin uchun
        else:
            success = await db.delete_listing(listing_id, callback.from_user.id, is_admin=False)

        if success:
            await callback.message.edit_text(
                "✅ E'lon muvaffaqiyatli o'chirildi!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📁 Mening e'lonlarim", callback_data="back_to_myads")]
                ])
            )
        else:
            await callback.message.edit_text("❌ E'lonni o'chirishda xatolik yuz berdi")

        await callback.answer()

    except Exception as e:
        logger.error(f"Confirm delete error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")


@user_router.callback_query(F.data.startswith("cancel_delete_"))
async def cancel_delete_handler(callback: CallbackQuery, db: Database):
    """E'lonni o'chirishni bekor qilish"""
    try:
        listing_id = int(callback.data.split("_")[2])
        listing = await db.get_listing(listing_id)
        
        if listing:
            status_text = "✅ Faol" if listing.get('status') == 'active' else "❌ Nofaol"
            
            ad_text = (
                f"🏠 <b>E'lon ma'lumotlari</b>\n\n"
                f"📌 <b>Sarlavha:</b> {listing['title']}\n"
                f"📝 <b>Tavsif:</b> {listing['description'][:100]}...\n"
                f"💰 <b>Narx:</b> {listing['price']} {listing.get('currency', 'UZS')}\n"
                f"📞 <b>Telefon:</b> {listing['phone']}\n"
                f"📊 <b>Holat:</b> {status_text}\n"
                f"👁️ <b>Ko'rishlar:</b> {listing.get('views', 0)}\n"
                f"📅 <b>Yaratilgan:</b> {listing['created_at'].strftime('%Y-%m-%d %H:%M')}"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Faollashtirish" if listing.get('status') != 'active' else "❌ Nofaollashtirish",
                        callback_data=f"toggle_{listing_id}"
                    )
                ],
                [
                    InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_{listing_id}"),
                    InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_{listing_id}")
                ],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_myads")]
            ])
            
            if callback.message.photo:
                await callback.message.edit_caption(caption=ad_text, reply_markup=keyboard)
            else:
                await callback.message.edit_text(ad_text, reply_markup=keyboard, parse_mode='HTML')
        
        await callback.answer("❌ O'chirish bekor qilindi")
        
    except Exception as e:
        logger.error(f"Cancel delete error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")



@user_router.callback_query(F.data.startswith("edit_"))
async def edit_ad_handler(callback: CallbackQuery, state: FSMContext):
    """E'lonni tahrirlash"""
    try:
        listing_id = int(callback.data.split("_")[1])
        
        await callback.message.edit_text(
            "✏️ Tahrirlash funksiyasi hozircha ishlamaydi.\n"
            "Tez orada qo'shiladi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"myad_{listing_id}")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Edit ad error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")


@user_router.callback_query(F.data == "back_to_myads")
async def back_to_my_ads_handler(callback: CallbackQuery, db: Database):
    """Mening e'lonlarim ro'yxatiga qaytish"""
    try:
        listings = await db.get_user_listings(callback.from_user.id)
        
        if not listings:
            await callback.message.edit_text("📭 Sizda hali e'lonlar mavjud emas.")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for listing in listings[:10]:
            status = "✅" if listing.get('status') == 'active' else "❌"
            btn_text = f"{status} {listing['title'][:30]}..."
            
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"myad_{listing['id']}"
                )
            ])
        
        if len(listings) > 10:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text="⬅️ Oldingi", callback_data="myads_prev"),
                InlineKeyboardButton(text="Keyingi ➡️", callback_data="myads_next")
            ])
        
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(
                f"📁 Sizning e'lonlaringiz ({len(listings)} ta):\n\n"
                "Har bir e'lonni boshqarish uchun ustiga bosing:",
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text(
                f"📁 Sizning e'lonlaringiz ({len(listings)} ta):\n\n"
                "Har bir e'lonni boshqarish uchun ustiga bosing:",
                reply_markup=keyboard
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Back to my ads error: {e}")
        await callback.answer("❌ Xatolik yuz berdi")



# E'lon joylash handler
@user_router.message(F.text == "📝 E'lon joylash")
async def post_ad_handler(message: Message, state: FSMContext):
    await message.answer(
        "🏠 E'lon kategoriyasini tanlang:",
        reply_markup=get_category_keyboard()
    )
    await state.set_state(PostAdState.choosing_category)

# Kategoriya tanlash callback
@user_router.callback_query(PostAdState.choosing_category, F.data.startswith("category_"))
async def category_chosen_handler(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    category_names = {
        "oilaga": "👨‍👩‍👧‍👦 Oilaga",
        "qizlarga": "👩 Qizlarga", 
        "bollarga": "👶 Bollarga",
        "hammaga": "👥 Hammaga"
    }
    
    await state.update_data(category=category_names[category])
    await callback.message.edit_text(
        f"✅ Kategoriya: {category_names[category]}\n\n"
        "🏢 Uyning qavatini tanlang:",
        reply_markup=get_floor_keyboard()
    )
    await state.set_state(PostAdState.choosing_floor)
    await callback.answer()

# Qavat tanlash callback
@user_router.callback_query(PostAdState.choosing_floor, F.data.startswith("floor_"))
async def floor_chosen_handler(callback: CallbackQuery, state: FSMContext):
    floor = callback.data.split("_")[1]
    await state.update_data(floor=floor)
    
    data = await state.get_data()
    await callback.message.edit_text(
        f"✅ Kategoriya: {data['category']}\n"
        f"✅ Qavat: {floor}-qavat\n\n"
        "🏠 Xonalar sonini tanlang:",
        reply_markup=get_rooms_keyboard()
    )
    await state.set_state(PostAdState.choosing_rooms)
    await callback.answer()

# Xonalar soni tanlash callback
@user_router.callback_query(PostAdState.choosing_rooms, F.data.startswith("rooms_"))
async def rooms_chosen_handler(callback: CallbackQuery, state: FSMContext):
    rooms = callback.data.split("_")[1]
    await state.update_data(rooms=rooms)
    
    data = await state.get_data()
    await callback.message.edit_text(
        f"✅ Kategoriya: {data['category']}\n"
        f"✅ Qavat: {data['floor']}-qavat\n"
        f"✅ Xonalar: {rooms} xona\n\n"
        "✏️ E'lon sarlavhasini kiriting:",
        reply_markup=None
    )
    await state.set_state(PostAdState.entering_title)
    await callback.answer()

# Sarlavha kiritish
@user_router.message(PostAdState.entering_title)
async def ad_title_handler(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer("❌ Sarlavha juda uzun. Iltimos, 200 ta belgidan kamroq kiriting.")
        return
        
    await state.update_data(title=message.text)
    
    data = await state.get_data()
    await message.answer(
        f"✅ Kategoriya: {data['category']}\n"
        f"✅ Qavat: {data['floor']}-qavat\n"
        f"✅ Xonalar: {data['rooms']} xona\n"
        f"✅ Sarlavha: {message.text}\n\n"
        "📝 E'lon tavsifini kiriting:",
        reply_markup=get_back_button('uz')
    )
    await state.set_state(PostAdState.entering_description)

# Tavsif kiritish
@user_router.message(PostAdState.entering_description)
async def ad_description_handler(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("✏️ E'lon sarlavhasini kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(PostAdState.entering_title)
        return
        
    await state.update_data(description=message.text)
    
    await message.answer(
        "💰 Narxni kiriting (so'mda):",
        reply_markup=get_back_button('uz')
    )
    await state.set_state(PostAdState.entering_price)

# Narx kiritish
@user_router.message(PostAdState.entering_price)
async def ad_price_handler(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("📝 E'lon tavsifini kiriting:", reply_markup=get_back_button('uz'))
        await state.set_state(PostAdState.entering_description)
        return
        
    try:
        price = float(message.text.replace(" ", "").replace(",", "."))
        if price <= 0:
            raise ValueError()
    except ValueError:
        await message.answer("❌ Noto'g'ri narx formati. Iltimos, raqam kiriting:")
        return
        
    await state.update_data(price=price)
    
    await message.answer(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=get_phone_keyboard('uz')
    )
    await state.set_state(PostAdState.requesting_phone)

# Telefon raqamini qabul qilish
@user_router.message(PostAdState.requesting_phone, F.contact)
async def phone_received_handler(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    await message.answer(
        f"✅ Telefon: {phone}\n\n"
        "📞 Zahira telefon raqami kiriting (ixtiyoriy):",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Orqaga"), KeyboardButton(text="⏭️ O'tkazib yuborish")]],
            resize_keyboard=True
        )
    )
    await state.set_state(PostAdState.requesting_optional_phone)

# Zahira telefon raqami
@user_router.message(PostAdState.requesting_optional_phone)
async def optional_phone_handler(message: Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=get_phone_keyboard('uz'))
        await state.set_state(PostAdState.requesting_phone)
        return
    elif message.text == "⏭️ O'tkazib yuborish":
        await state.update_data(optional_phone=None)
    else:
        await state.update_data(optional_phone=message.text)
    
    await message.answer(
        "📍 Joylashuvingizni yuboring:",
        reply_markup=get_location_keyboard('uz')
    )
    await state.set_state(PostAdState.requesting_location)

# Joylashuvni qabul qilish
@user_router.message(PostAdState.requesting_location, F.location)
async def location_received_handler(message: Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await state.update_data(location=f"{latitude},{longitude}")
    
    await message.answer(
        "📸 E'lon uchun rasmlar yuklang (1-10 ta):\n\n"
        "ℹ️ Bir nechta rasm yuborishingiz mumkin. Barcha rasmlarni yuborgach, "
        "'✅ Tasdiqlash' tugmasini bosing.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="✅ Tasdiqlash"), KeyboardButton(text="🔙 Orqaga")]],
            resize_keyboard=True
        )
    )
    await state.set_state(PostAdState.uploading_photos)

# Rasmlarni qabul qilish
@user_router.message(PostAdState.uploading_photos, F.photo | F.text)
async def photos_received_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    file_ids = data.get('file_ids', [])
    
    if message.text == "🔙 Orqaga":
        await message.answer("📍 Joylashuvingizni yuboring:", reply_markup=get_location_keyboard('uz'))
        await state.set_state(PostAdState.requesting_location)
        return
        
    if message.text == "✅ Tasdiqlash":
        if not file_ids:
            await message.answer("❖ Hech qanday rasm yuklanmadi. Iltimos, kamida bitta rasm yuklang.")
            return
            
        # E'lon ma'lumotlarini ko'rsatish
        data = await state.get_data()
        confirm_text = (
            "📋 E'lon ma'lumotlari:\n\n"
            f"🏠 Kategoriya: {data['category']}\n"
            f"🏢 Qavat: {data['floor']}-qavat\n"
            f"🏠 Xonalar: {data['rooms']} xona\n"
            f"📝 Sarlavha: {data['title']}\n"
            f"📄 Tavsif: {data['description']}\n"
            f"💰 Narx: {data['price']} so'm\n"
            f"📞 Telefon: {data['phone']}\n"
        )
        
        if data.get('optional_phone'):
            confirm_text += f"📞 Zahira: {data['optional_phone']}\n"
            
        confirm_text += f"📍 Joylashuv: Ko'rsatilgan\n"
        confirm_text += f"📸 Rasmlar: {len(file_ids)} ta\n\n"
        confirm_text += "✅ E'lonni joylashni tasdiqlaysizmi?"
        
        await message.answer(confirm_text, reply_markup=get_confirmation_keyboard('uz'))
        await state.set_state(PostAdState.confirmation)
        return
        
    if message.photo:
        file_id = message.photo[-1].file_id
        file_ids.append(file_id)
        await state.update_data(file_ids=file_ids)
        
        if len(file_ids) >= 10:
            await message.answer("✅ 10 ta rasm qabul qilindi. '✅ Tasdiqlash' tugmasini bosing.")
        else:
            await message.answer(f"✅ Rasm qabul qilindi ({len(file_ids)}/10). Yana rasm yuborishingiz mumkin.")
    else:
        await message.answer("❖ Iltimos, rasm yuboring yoki '✅ Tasdiqlash' tugmasini bosing.")

# Tasdiqlash
@user_router.message(PostAdState.confirmation)
async def confirmation_handler(message: Message, state: FSMContext, db: Database, bot: Bot):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        file_ids = data.get('file_ids', [])
        
        # E'lonni bazaga qo'shish
        listing_id = await db.add_listing(
            user_id=message.from_user.id,
            category=data['category'],
            floor=data['floor'],
            rooms=data['rooms'],
            title=data['title'],
            description=data['description'],
            price=data['price'],
            currency='UZS',
            phone=data['phone'],
            optional_phone=data.get('optional_phone'),
            location=data['location'],
            file_ids=file_ids
        )
        
        # Kanalga yuborish
        try:
            await send_listing_to_channel(bot, data, file_ids, listing_id, message.from_user.id)
        except Exception as e:
            logger.error(f"❌ Kanalga yuborishda xatolik: {e}")
        
        await message.answer(
            f"✅ E'lon muvaffaqiyatli joylandi! ID: #{listing_id}\n\n"
            "E'loningiz tekshiruvdan so'ng aktiv bo'ladi.",
            reply_markup=get_main_menu_keyboard('uz')
        )
        await state.clear()
        
    elif message.text == "❌ Bekor qilish":
        await message.answer(
            "❌ E'lon joylash bekor qilindi.",
            reply_markup=get_main_menu_keyboard('uz')
        )
        await state.clear()
    else:
        await message.answer("❖ Iltimos, '✅ Tasdiqlash' yoki '❌ Bekor qilish' tugmalaridan birini bosing.")


async def send_listing_to_channel(bot, data, file_ids, listing_id: int, user_id: int):
    """E'lonni maxfiy kanalga yuborish"""
    try:
        caption = (
            f"🆔 E'lon ID: {listing_id}\n"
            f"👤 User ID: {user_id}\n\n"
            f"🏠 Yangi e'lon!\n\n"
            f"📌 {data['title']}\n"
            f"📝 {data['description']}\n"
            f"💰 {data['price']} {data.get('currency', 'UZS')}\n"
            f"📞 {data['phone']}\n"
            f"📍 {data['location']}\n"
        )

        if file_ids and len(file_ids) > 1:
            media = [InputMediaPhoto(media=file_ids[0], caption=caption)]
            media += [InputMediaPhoto(media=pid) for pid in file_ids[1:]]
            await bot.send_media_group(chat_id=BACKUP_CHANNEL_ID, media=media)
        elif file_ids:
            await bot.send_photo(chat_id=BACKUP_CHANNEL_ID, photo=file_ids[0], caption=caption)
        else:
            await bot.send_message(chat_id=BACKUP_CHANNEL_ID, text=caption)

        logger.info(f"📤 E'lon kanalga yuborildi: {listing_id} | User: {user_id}")

    except Exception as e:
        logger.error(f"❌ Kanalga yuborishda xatolik: {e}")


# Asosiy menyuga qaytish
@user_router.message(F.text == "🏠 Asosiy menyu")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=get_main_menu_keyboard('uz')
    )

# Orqaga qaytish
@user_router.message(F.text == "🔙 Orqaga")
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == PostAdState.entering_description:
        await message.answer("✏️ E'lon sarlavhasini kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(PostAdState.entering_title)
    elif current_state == PostAdState.entering_price:
        await message.answer("📝 E'lon tavsifini kiriting:", reply_markup=get_back_button('uz'))
        await state.set_state(PostAdState.entering_description)
    # Boshqa holatlar uchun ham shunday qilish mumkin
    
    else:
        await message.answer(
            "🏠 Asosiy menyu:",
            reply_markup=get_main_menu_keyboard('uz')
        )
        await state.clear()

# Export qilish
router = user_router