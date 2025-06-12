import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

from config import TOKEN, ADMIN_ID, ADMIN_USERNAME, BACKUP_CHAT_ID, LOG_DIR, BACKUP_INTERVAL, FILE_CLEANUP_INTERVAL, TEMP_DIR
from database import db
from translations import TRANSLATIONS, LANG_KEYBOARD, LANG_MAP, get_menu_keyboard, get_admin_keyboard
from downloader import VideoDownloader

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = str(message.from_user.id)
    
    if user_id in db.user_data["banned"]:
        return await message.answer(TRANSLATIONS["ru"]["banned"])
    
    if user_id not in db.user_data["users"]:
        db.user_data["users"][user_id] = {
            "language": None,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.save_data()
        await message.answer(TRANSLATIONS["ru"]["choose_language"], reply_markup=LANG_KEYBOARD)
    else:
        db.user_data["users"][user_id]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.save_data()
        
        lang = db.user_data["users"].get(user_id, {}).get("language", "ru")
        is_premium = user_id in db.user_data.get("premium", [])
        await message.answer(
            TRANSLATIONS[lang]["send_link"], 
            reply_markup=get_menu_keyboard(lang, is_premium)
        )

@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id != ADMIN_ID:
        return
    
    await message.answer("Панель администратора:", reply_markup=get_admin_keyboard())

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        return await callback.answer("Доступ запрещен")
    
    if callback.data == "stats":
        stats = db.get_global_stats()
        stats_text = (
            f"📊 Статистика:\n\n"
            f"Всего загрузок: {stats['total_downloads']}\n"
            f"TikTok загрузок: {stats['platforms']['tiktok']}\n"
            f"Instagram загрузок: {stats['platforms']['instagram']}\n"
            f"Всего пользователей: {stats['total_users']}\n"
            f"Premium: {stats['premium_users']}\n"
            f"Заблокировано: {stats['banned_users']}"
        )
        await callback.message.answer(stats_text)
    
    elif callback.data == "users":
        sorted_users = sorted(
            db.user_data["users"].items(),
            key=lambda x: datetime.strptime(x[1].get("last_activity", "2000-01-01"), "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        user_list = "👥 Недавно активные пользователи:\n\n"
        for uid, udata in sorted_users[:10]:
            username = udata.get("username", "Нет")
            first_name = udata.get("first_name", "Неизвестно")
            last_activity = udata.get("last_activity", "Неизвестно")
            downloads = db.get_user_stats(uid)["downloads"]
            premium = "⭐️ " if db.is_user_premium(uid) else ""
            user_list += f"ID: {uid}\nИмя: {first_name}\nUsername: @{username}\nАктивность: {last_activity}\nЗагрузок: {downloads}\n{premium}\n\n"
        
        await callback.message.answer(user_list)
    
    elif callback.data == "ban":
        await callback.message.answer("Ответьте на это сообщение с ID пользователя для блокировки:")
    
    elif callback.data == "unban":
        if not db.user_data["banned"]:
            return await callback.message.answer("Нет заблокированных пользователей")
        
        unban_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=uid, callback_data=f"unban_{uid}")] 
            for uid in db.user_data["banned"][:10]
        ])
        
        await callback.message.answer("Выберите пользователя для разблокировки:", reply_markup=unban_keyboard)
    
    elif callback.data.startswith("unban_"):
        uid = callback.data.split("_")[1]
        if db.unban_user(uid):
            await callback.message.answer(f"Пользователь {uid} разблокирован")
        else:
            await callback.message.answer(f"Пользователь {uid} не заблокирован")
    
    elif callback.data == "add_premium":
        await callback.message.answer("Ответьте на это сообщение с ID пользователя для добавления Premium:")
    
    elif callback.data == "broadcast":
        await callback.message.answer("Ответьте на это сообщение с текстом для рассылки:")
    
    await callback.answer()

@dp.message()
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)
    
    if user_id in db.user_data["users"]:
        db.user_data["users"][user_id]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.save_data()
    
    if user_id in db.user_data["banned"]:
        lang = db.user_data["users"].get(user_id, {}).get("language", "ru")
        return await message.answer(TRANSLATIONS[lang]["banned"])
    
    if message.text in LANG_MAP:
        db.user_data["users"][user_id]["language"] = LANG_MAP[message.text]
        db.save_data()
        is_premium = user_id in db.user_data.get("premium", [])
        await message.answer(
            TRANSLATIONS[LANG_MAP[message.text]]["saved_language"], 
            reply_markup=get_menu_keyboard(LANG_MAP[message.text], is_premium)
        )
        return
    
    if user_id not in db.user_data["users"] or db.user_data["users"][user_id]["language"] is None:
        await message.answer(TRANSLATIONS["ru"]["choose_language"], reply_markup=LANG_KEYBOARD)
        return
    
    lang = db.user_data["users"].get(user_id, {}).get("language", "ru")
    is_premium = user_id in db.user_data.get("premium", [])
    
    if message.text == "ℹ️ Help" or message.text == "ℹ️ Помощь" or message.text == "ℹ️ Օգնություն":
        return await message.answer(TRANSLATIONS[lang]["help"])
    
    if message.text == "🔄 Change language" or message.text == "🔄 Сменить язык" or message.text == "🔄 Փոխել լեզուն":
        return await message.answer(TRANSLATIONS[lang]["change_language"], reply_markup=LANG_KEYBOARD)
    
    if message.text == "⭐️ Premium":
        admin_contact = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(
                text=TRANSLATIONS[lang]["contact_admin"], 
                url=f"https://t.me/{ADMIN_USERNAME}?start=admin_{user_id}"   
            )]]
        )
        return await message.answer(TRANSLATIONS[lang]["premium_info"], reply_markup=admin_contact)
    
    if VideoDownloader.is_valid_url(message.text):
        url = message.text.strip()
        
        if not is_premium and db.get_user_stats(user_id)["downloads"] >= 5:
            return await message.answer(TRANSLATIONS[lang]["rate_limit"])
        
        await message.answer(TRANSLATIONS[lang]["downloading"])
        
        success, result, platform = await VideoDownloader.download_video(url, user_id, is_premium)
        
        if success:
            await message.answer_video(FSInputFile(result))
            db.update_stats(user_id, success=True, platform=platform)
        else:
            await message.answer(TRANSLATIONS[lang]["download_error"])
            db.update_stats(user_id, success=False)
        
        VideoDownloader.cleanup_file(result)
    else:
        await message.answer(TRANSLATIONS[lang]["unsupported_link"], 
                          reply_markup=get_menu_keyboard(lang, is_premium))

async def periodic_tasks():
    """Run periodic tasks like cleanup and backup."""
    while True:
        try:
            # Clean up old files
            for filename in os.listdir(TEMP_DIR):
                file_path = os.path.join(TEMP_DIR, filename)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < time.time() - FILE_CLEANUP_INTERVAL:
                    os.remove(file_path)
            
            # Backup data
            if datetime.now().weekday() == 0 and datetime.now().hour == 0:
                backup_time = datetime.now().strftime("%Y%m%d")
                backup_data = {
                    "user_data": db.user_data,
                    "stats": db.stats
                }
                backup_file = f"backup_{backup_time}.json"
                
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(backup_data, f, indent=4, ensure_ascii=False)
                    
                if os.path.exists(backup_file):
                    try:
                        await bot.send_document(
                            ADMIN_ID, 
                            FSInputFile(backup_file),
                            caption=f"Weekly backup {backup_time}"
                        )
                        await bot.send_document(
                            BACKUP_CHAT_ID, 
                            FSInputFile(backup_file),
                            caption=f"Weekly backup {backup_time}"
                        )
                        os.remove(backup_file)
                    except Exception as e:
                        logging.error(f"Error sending backup: {e}")
            
            await asyncio.sleep(BACKUP_INTERVAL)
        except Exception as e:
            logging.error(f"Error in periodic tasks: {e}")
            await asyncio.sleep(60)

async def main():
    """Main function to start the bot."""
    try:
        # Delete webhook and stop any existing sessions
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
        
        # Start periodic tasks
        asyncio.create_task(periodic_tasks())
        
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Bot stopped due to error: {e}") 
