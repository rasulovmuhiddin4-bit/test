import os
from dotenv import load_dotenv

# config.py fayliga qo'shing
load_dotenv()

ADMIN_IDS = [606226674]
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = int(os.getenv("BACKUP_CHANNEL_ID", "0"))  # int qilib olish kerak!


LANGUAGES = {
    'uz': "O'zbekcha",
    'ru': "Русский", 
    'en': "English"
}

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
DB_URL = os.getenv('DATABASE_URL')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Valyuta kurslari (namuna, haqiqiy kursni API dan olishingiz mumkin)
CURRENCY_RATES = {
    'USD': 1.0,
    'UZS': 12500.0  # 1 USD = 12500 UZS
}

MENU_TEXTS = {
    'uz': {
        'main_menu': "🏠 Asosiy menyu",
        'post_ad': "📝 E'lon joylash",
        'view_ads': "📋 Mavjud e'lonlar",
        'my_ads': "📁 Mening e'lonlarim",
        'settings': "⚙️ Sozlamalar",
        'support': "🆘 Qo'llab-quvvatlash"
    },
    'ru': {
        'main_menu': "🏠 Главное меню", 
        'post_ad': "📝 Разместить объявление",
        'view_ads': "📋 Доступные объявления",
        'my_ads': "📁 Мои объявления",
        'settings': "⚙️ Настройки",
        'support': "🆘 Поддержка"
    },
    'en': {
        'main_menu': "🏠 Main menu",
        'post_ad': "📝 Post an ad", 
        'view_ads': "📋 Available ads",
        'my_ads': "📁 My ads",
        'settings': "⚙️ Settings",
        'support': "🆘 Support"
    }
}



class Texts:
    # ... existing code ...
    
    MY_ADS = {
        'no_ads': "📭 Sizda hali e'lonlar mavjud emas.",
        'title': "📁 Mening e'lonlarim",
        'list': "Sizning e'lonlaringiz ({} ta):\n\nHar bir e'lonni boshqarish uchun ustiga bosing:",
        'ad_detail': "🏠 <b>E'lon ma'lumotlari</b>\n\n📌 <b>Sarlavha:</b> {}\n📝 <b>Tavsif:</b> {}...\n💰 <b>Narx:</b> {} {}\n📞 <b>Telefon:</b> {}\n📊 <b>Holat:</b> {}\n👁️ <b>Ko'rishlar:</b> {}\n📅 <b>Yaratilgan:</b> {}",
        'delete_confirm': "🗑️ <b>E'lonni o'chirish</b>\n\n\"{}\" e'lonini rostdan ham o'chirmoqchimisiz?\n\n⚠️ Bu amalni ortga qaytarib bo'lmaydi!",
        'deleted': "✅ E'lon muvaffaqiyatli o'chirildi!",
        'delete_error': "❌ E'lonni o'chirishda xatolik yuz berdi"
    }