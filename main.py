import logging
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = 'YOUR_BOT_TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Клавиатура главного меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("📅 Расписание", "🗺 Карта", "🎤 Артисты")
main_menu.add("🏕 Проживание", "📞 Контакты", "✉ Обратная связь")

# Inline-кнопки для фильтрации расписания
schedule_menu = InlineKeyboardMarkup()
schedule_menu.add(InlineKeyboardButton("Концерты", callback_data='filter_concerts'))
schedule_menu.add(InlineKeyboardButton("Мастер-классы", callback_data='filter_workshops'))
schedule_menu.add(InlineKeyboardButton("Все события", callback_data='filter_all'))

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Это официальный бот фестиваля «Дикая Мята» 🎉\n"
        "Выберите интересующий раздел ниже:",
        reply_markup=main_menu
    )

# Обработка кнопок главного меню
@dp.message_handler(lambda message: message.text == "📅 Расписание")
async def show_schedule(message: types.Message):
    await message.answer("Выберите категорию событий:", reply_markup=schedule_menu)

@dp.callback_query_handler(lambda call: call.data.startswith('filter_'))
async def filter_schedule(call: types.CallbackQuery):
    filter_type = call.data.split('_')[1]
    if filter_type == 'concerts':
        await call.message.answer("🎵 Расписание концертов доступно по ссылке: https://mintmusic.ru/line-up-2025")
    elif filter_type == 'workshops':
        await call.message.answer("🛠 Расписание мастер-классов будет опубликовано ближе к дате фестиваля.")
    else:
        await call.message.answer("📅 Полное расписание доступно по ссылке: https://mintmusic.ru/line-up-2025")
    await call.answer()

@dp.message_handler(lambda message: message.text == "🗺 Карта")
async def show_map(message: types.Message):
    await message.answer("🗺 Карта фестиваля доступна по ссылке: https://mintmusic.ru/map")

@dp.message_handler(lambda message: message.text == "🎤 Артисты")
async def show_artists(message: types.Message):
    await message.answer("🎤 Список артистов доступен по ссылке: https://mintmusic.ru/line-up-2025")

@dp.message_handler(lambda message: message.text == "🏕 Проживание")
async def show_accommodation(message: types.Message):
    await message.answer(
        "🏕 Информация о проживании:\n"
        "- Кемпинг «Семейный»\n"
        "- Кемпинг «Маяк»\n"
        "- Кемпинг «Меломан»\n"
        "Подробнее: https://mintmusic.ru/accommodation"
    )

@dp.message_handler(lambda message: message.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    await message.answer(
        "📞 Контакты организаторов:\n"
        "Email: support@mintmusic.ru\n"
        "Телефон: +7 (XXX) XXX-XX-XX\n"
        "Полный список контактов: https://mintmusic.ru/contacts"
    )

@dp.message_handler(lambda message: message.text == "✉ Обратная связь")
async def feedback(message: types.Message):
    await message.answer("Пожалуйста, отправьте ваш вопрос или предложение, и мы свяжемся с вами в ближайшее время.")

# Автоматическое напоминание о событиях
async def send_reminder():
    await bot.send_message(chat_id='USER_ID', text="🔔 Напоминание: через 30 минут начнется главное событие дня!")

scheduler.add_job(send_reminder, 'interval', hours=2)  # Напоминания каждые 2 часа
scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
