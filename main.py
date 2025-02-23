import logging
import json
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '7756712835:AAFGks726IMI7OCMLrCrXSmsaQ2Q3t_y-Sw'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

USERS_FILE = "users.json"

# Функции для работы с пользователями
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

registered_users = load_users()

# Главное меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("📅 Расписание", "🗺 Карта", "🎤 Артисты")
main_menu.add("🏕 Проживание", "📞 Контакты", "✉ Обратная связь")
main_menu.add("✅ Подписаться на напоминания", "❌ Отписаться")

# Inline-клавиатура для выбора расписания
schedule_menu = InlineKeyboardMarkup()
schedule_menu.add(InlineKeyboardButton("Концерты", callback_data='filter_concerts'))
schedule_menu.add(InlineKeyboardButton("Мастер-классы", callback_data='filter_workshops'))
schedule_menu.add(InlineKeyboardButton("Лекции", callback_data='filter_lectures'))
schedule_menu.add(InlineKeyboardButton("Все события", callback_data='filter_all'))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Это бот фестиваля 🎉\nВыберите раздел ниже:", reply_markup=main_menu)

@dp.message_handler(lambda message: message.text == "✅ Подписаться на напоминания")
async def register_user(message: types.Message):
    user_id = message.from_user.id
    if user_id not in registered_users:
        registered_users.append(user_id)
        save_users(registered_users)
        await message.answer("✅ Вы подписались на напоминания!")
    else:
        await message.answer("Вы уже подписаны.")

@dp.message_handler(lambda message: message.text == "❌ Отписаться")
async def unregister_user(message: types.Message):
    user_id = message.from_user.id
    if user_id in registered_users:
        registered_users.remove(user_id)
        save_users(registered_users)
        await message.answer("❌ Вы отписались от напоминаний.")
    else:
        await message.answer("Вы не были подписаны.")

@dp.message_handler(lambda message: message.text == "📅 Расписание")
async def schedule(message: types.Message):
    await message.answer("Выберите категорию событий:", reply_markup=schedule_menu)

@dp.callback_query_handler(lambda call: call.data.startswith('filter_'))
async def filter_schedule(call: types.CallbackQuery):
    filter_type = call.data.split('_')[1]
    events = {
        "concerts": "🎵 Концерты: https://mintmusic.ru/line-up-2025",
        "workshops": "🛠 Мастер-классы: https://mintmusic.ru/workshops",
        "lectures": "📖 Лекции: https://mintmusic.ru/lectures",
        "all": "📅 Полное расписание: https://mintmusic.ru/schedule"
    }
    await call.message.answer(events[filter_type])
    await call.answer()

@dp.message_handler(lambda message: message.text == "🗺 Карта")
async def festival_map(message: types.Message):
    await message.answer("🗺 Карта фестиваля: https://mintmusic.ru/map")

@dp.message_handler(lambda message: message.text == "🎤 Артисты")
async def artists(message: types.Message):
    await message.answer("🎤 Список артистов: https://mintmusic.ru/line-up-2025")

@dp.message_handler(lambda message: message.text == "🏕 Проживание")
async def accommodation(message: types.Message):
    await message.answer("🏕 Проживание и кемпинг: https://mintmusic.ru/accommodation")

@dp.message_handler(lambda message: message.text == "📞 Контакты")
async def contacts(message: types.Message):
    await message.answer("📞 Контакты: https://mintmusic.ru/contacts")

@dp.message_handler(lambda message: message.text == "✉ Обратная связь")
async def feedback(message: types.Message):
    await message.answer("Напишите ваш вопрос или предложение, и мы ответим вам!")

async def send_reminders():
    if registered_users:
        for user_id in registered_users:
            try:
                await bot.send_message(user_id, "🔔 Напоминание: через 30 минут начнется главное событие!")
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения {user_id}: {e}")

scheduler.add_job(send_reminders, 'interval', hours=2)
scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
