from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.config import MENU_TEXTS

# keyboards.py ga qo'shimchalar

def get_main_menu_keyboard(language: str):
    if language == 'uz':
        buttons = [
            ["📝 E'lon joylash"],
            ["📋 Mavjud e'lonlar", "📁 Mening e'lonlarim"],
            ["⚙️ Sozlamalar", "🤝 Qo'llab-quvvatlash"]
        ]
    elif language == 'ru':
        buttons = [
            ["📝 Разместить объявление"],
            ["📋 Доступные объявления", "📁 Мои объявления"],
            ["⚙️ Настройки", "🤝 Поддержка"]
        ]
    else:
        buttons = [
            ["📝 Post an ad"],
            ["📋 Available ads", "📁 My ads"],
            ["⚙️ Settings", "🤝 Support"]
        ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b) for b in row] for row in buttons],
        resize_keyboard=True
    )



# Oilaviy kategoriyalar uchun inline keyboard
def get_category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍👩‍👧‍👦 Oilaga", callback_data="category_family")],
        [InlineKeyboardButton(text="👩 Qizlarga", callback_data="category_girls")],
        [InlineKeyboardButton(text="👶 Bollarga", callback_data="category_kids")],
        [InlineKeyboardButton(text="👥 Hammaga", callback_data="category_everyone")]
    ])


# Qavatlar uchun inline tugmalar
def get_floor_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1-qavat", callback_data="floor_1"),
             InlineKeyboardButton(text="2-qavat", callback_data="floor_2"),
             InlineKeyboardButton(text="3-qavat", callback_data="floor_3")],
            [InlineKeyboardButton(text="4-qavat", callback_data="floor_4"),
             InlineKeyboardButton(text="5-qavat", callback_data="floor_5"),
             InlineKeyboardButton(text="6+ qavat", callback_data="floor_6plus")]
        ]
    )

# Xonalar soni uchun inline keyboard
def get_rooms_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 xona", callback_data="rooms_1"),
         InlineKeyboardButton(text="2 xona", callback_data="rooms_2")],
        [InlineKeyboardButton(text="3 xona", callback_data="rooms_3"),
         InlineKeyboardButton(text="4 xona", callback_data="rooms_4")],
        [InlineKeyboardButton(text="5 xona va ko'p", callback_data="rooms_5+")]
    ])

# Til tanlash tugmachalari
def get_language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha")],
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇺🇸 English")]
        ],
        resize_keyboard=True
    )

# Telefon raqamini yuborish tugmasi
def get_phone_keyboard(language: str):
    text = {
        'uz': "📞 Telefon raqamini yuborish",
        'ru': "📞 Отправить номер телефона",
        'en': "📞 Send phone number"
    }
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text[language], request_contact=True)]],
        resize_keyboard=True
    )



# Joylashuv yuborish tugmasi
def get_location_keyboard(language: str):
    text = {
        'uz': "📍 Joylashuvni yuborish",
        'ru': "📍 Отправить местоположение",
        'en': "📍 Send location"
    }
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text.get(language, "📍 Send location"), request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )



# Valyuta tanlash tugmachalari
def get_currency_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💵 USD"), KeyboardButton(text="💵 UZS")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )

# Orqaga tugma
def get_back_button(language: str):
    text = {
        'uz': "🔙 Orqaga",
        'ru': "🔙 Назад",
        'en': "🔙 Back"
    }
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text.get(language, "🔙 Back"))]],
        resize_keyboard=True
    )



# Tasdiqlash tugmasi
def get_confirmation_keyboard(language: str = "uz"):
    texts = {
        'uz': ["✅ Tasdiqlash", "❌ Bekor qilish"],
        'ru': ["✅ Подтвердить", "❌ Отменить"],
        'en': ["✅ Confirm", "❌ Cancel"]
    }
    buttons = texts[language]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=buttons[0]), KeyboardButton(text=buttons[1])]],
        resize_keyboard=True
    )


# Hudud tanlash tugmachalari
def get_region_keyboard(language: str):
    regions = ["Toshkent", "Samarqand", "Buxoro", "Farg‘ona"]
    back_text = get_back_button(language).keyboard[0][0].text
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=r)] for r in regions] + [[KeyboardButton(text=back_text)]],
        resize_keyboard=True
    )

# Rasm yuklash davomida ishlatiladigan keyboard
def get_photo_confirm_keyboard(language: str):
    texts = {
        'uz': ["✅ Tasdiqlash", "🔙 Orqaga"],
        'ru': ["✅ Подтвердить", "🔙 Назад"],
        'en': ["✅ Confirm", "🔙 Back"]
    }
    buttons = texts.get(language, ["✅ Confirm", "🔙 Back"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=buttons[0]), KeyboardButton(text=buttons[1])]],
        resize_keyboard=True
    )

# Yakuniy tasdiqlash uchun keyboard
def get_final_confirm_keyboard(language: str):
    texts = {
        'uz': ["✅ Ha", "❌ Yo'q"],
        'ru': ["✅ Да", "❌ Нет"],
        'en': ["✅ Yes", "❌ No"]
    }
    buttons = texts.get(language, ["✅ Yes", "❌ No"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=buttons[0]), KeyboardButton(text=buttons[1])]],
        resize_keyboard=True
    )

# Narx valyutasi tugmachalari
def get_price_currency_keyboard(language: str):
    texts = {
        'uz': ["💵 USD", "💵 So'm", "🔙 Orqaga"],
        'ru': ["💵 USD", "💵 Сум", "🔙 Назад"],
        'en': ["💵 USD", "💵 UZS", "🔙 Back"]
    }
    buttons = texts.get(language, ["💵 USD", "💵 UZS", "🔙 Back"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=buttons[0]), KeyboardButton(text=buttons[1])], [KeyboardButton(text=buttons[2])]],
        resize_keyboard=True
    )



# Har bir qadamda asosiy menyu va orqaga tugmalari
def get_step_navigation_keyboard(language: str):
    back_text = {
        'uz': "🔙 Orqaga",
        'ru': "🔙 Назад", 
        'en': "🔙 Back"
    }
    main_menu_text = {
        'uz': "🏠 Asosiy menyu",
        'ru': "🏠 Главное меню",
        'en': "🏠 Main menu"
    }
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=back_text[language])],
            [KeyboardButton(text=main_menu_text[language])]
        ],
        resize_keyboard=True
    )