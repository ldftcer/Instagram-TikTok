from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Language selection keyboard
LANG_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇦🇲 Հայերեն")],
        [KeyboardButton(text="🇬🇧 English")],
        [KeyboardButton(text="🇷🇺 Русский")]
    ],
    resize_keyboard=True
)

# Language mapping
LANG_MAP = {
    "🇦🇲 Հայերեն": "hy",
    "🇬🇧 English": "en",
    "🇷🇺 Русский": "ru"
}

# Translations dictionary
TRANSLATIONS = {
    "hy": {
        "choose_language": "Ընտրեք լեզուն:",
        "saved_language": "Լեզուն պահպանված է: Այժմ ուղարկեք տեսանյութի հղումը:",
        "send_link": "Ուղարկեք տեսանյութի հղումը TikTok կամ Instagram-ից:",
        "downloading": "⏳ Խնդրում ենք սպասել...",
        "download_error": "❌ Սխալ վիդեո ներբեռնելիս: Հնարավոր է հղումը սխալ է կամ տեսանյութը անհասանելի է:",
        "banned": "⛔ Դուք արգելափակված եք այս բոտում:",
        "help": "🔹 Ուղարկեք տեսանյութի հղումը TikTok կամ Instagram-ից։\n🔹 Սպասեք մի քանի վայրկյան\n🔹 Ստացեք տեսանյութը առանց ջրանշան",
        "change_language": "Կրկին ընտրեք լեզուն:",
        "unsupported_link": "⚠️ Չաջակցվող հղում: Խնդրում ենք օգտագործել միայն TikTok կամ Instagram-ի հղումներ:",
        "premium_info": "⭐️ Premium հաշիվը տալիս է հետևյալ առավելությունները.\n✅ Ավելի արագ ներբեռնում\n✅ Բարձր որակ\n✅ Գովազդ չկա\n✅ Առաջնահերթ աջակցություն\n\nԳինը: $5/ամիս",
        "contact_admin": "💬 Կապվեք ադմինի հետ",
        "rate_limit": "⚠️ Դուք հասել եք օրական սահմանին: Սպասեք 24 ժամ կամ բարելավեք Premium-ի համար"
    },
    "en": {
        "choose_language": "Choose language:",
        "saved_language": "Language saved! Now send a video link.",
        "send_link": "Send a video link from TikTok or Instagram.",
        "downloading": "⏳ Please wait...",
        "download_error": "❌ Error downloading video. The link may be invalid or the video is unavailable.",
        "banned": "⛔ You are banned from this bot.",
        "help": "🔹 Send a TikTok or Instagram video link\n🔹 Wait a few seconds\n🔹 Get your video without watermarks",
        "change_language": "Choose your language again:",
        "unsupported_link": "⚠️ Unsupported link. Please use only TikTok or Instagram links.",
        "premium_info": "⭐️ Premium account gives you these benefits:\n✅ Faster downloads\n✅ Higher quality\n✅ No ads\n✅ Priority support\n\nPrice: $5/month",
        "contact_admin": "💬 Contact Admin",
        "rate_limit": "⚠️ You've reached your daily limit. Wait 24 hours or upgrade to Premium"
    },
    "ru": {
        "choose_language": "Выберите язык:",
        "saved_language": "Язык сохранён! Теперь отправьте ссылку на видео.",
        "send_link": "Отправьте ссылку на видео из TikTok или Instagram.",
        "downloading": "⏳ Загружаю видео...",
        "download_error": "❌ Ошибка при скачивании видео. Возможно ссылка неверна или видео недоступно.",
        "banned": "⛔ Вы заблокированы в этом боте.",
        "help": "🔹 Отправьте ссылку на видео из TikTok или Instagram\n🔹 Подождите несколько секунд\n🔹 Получите видео без водяных знаков",
        "change_language": "Выберите язык снова:",
        "unsupported_link": "⚠️ Неподдерживаемая ссылка. Пожалуйста, используйте только ссылки TikTok или Instagram.",
        "premium_info": "⭐️ Премиум аккаунт даёт следующие преимущества:\n✅ Быстрая загрузка\n✅ Высокое качество\n✅ Без рекламы\n✅ Приоритетная поддержка\n\nЦена: $5/месяц",
        "contact_admin": "💬 Связаться с администратором",
        "rate_limit": "⚠️ Вы достигли дневного лимита. Подождите 24 часа или обновитесь до Premium"
    }
}

def get_menu_keyboard(lang: str, is_premium: bool = False) -> ReplyKeyboardMarkup:
    """Generate menu keyboard based on language and premium status."""
    premium_button = []
    if not is_premium:
        premium_button = [KeyboardButton(text="⭐️ Premium")]
        
    if lang == "hy":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="ℹ️ Օգնություն"), KeyboardButton(text="🔄 Փոխել լեզուն")],
                premium_button
            ],
            resize_keyboard=True
        )
    elif lang == "en":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="ℹ️ Help"), KeyboardButton(text="🔄 Change language")],
                premium_button
            ],
            resize_keyboard=True
        )
    else:  # ru
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="ℹ️ Помощь"), KeyboardButton(text="🔄 Сменить язык")],
                premium_button
            ],
            resize_keyboard=True
        )

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Generate admin panel keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton(text="👥 Пользователи", callback_data="users")],
            [InlineKeyboardButton(text="🚫 Блокировать", callback_data="ban"), 
             InlineKeyboardButton(text="✅ Разблокировать", callback_data="unban")],
            [InlineKeyboardButton(text="⭐️ Premium", callback_data="add_premium"),
             InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")],
            [InlineKeyboardButton(text="🗄️ Резервная копия", callback_data="backup")]
        ]
    ) 