import asyncio
from aiogram import Bot, Dispatcher, html
from aiogram.types import Message
from aiogram.filters import CommandStart
from google import genai

# Вставьте ваши токены сюда


# Инициализируем бота Telegram и диспетчер
bot = Bot(token='8968323117:AAH90T4QOxyendjOvwTzUMq9heMgvzKy_bk')
dp = Dispatcher()

# Инициализируем официального клиента Gemini
ai_client = genai.Client(api_key='AQ.Ab8RN6KdCAAIsr8bWr0AsCCBGNy5PAOSpbT1rpxDpukjMAVjuQ')

# Обработка команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Я бот на базе ИИ Gemini. Задай мне любой вопрос!")

# Обработка всех текстовых сообщений
@dp.message()
async def echo_handler(message: Message) -> None:
    # Отправляем в чат статус "печатает...", пока ИИ думает над ответом
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем запрос в модель gemini-2.5-flash (она быстрая и бесплатная)
        response = ai_client.models.generate_content(
            model='gemini-3.7-flash',
            contents=message.text,
        )
        # Отправляем текстовый ответ пользователю
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Произошла ошибка при обращении к Gemini. Проверьте настройки сети или API-ключ.")
        print(f"Ошибка: {e}")

# Запуск процесса опроса Telegram (Polling)
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
