import asyncio
from aiogram import Bot, Dispatcher, html
from aiogram.types import Message
from aiogram.filters import CommandStart
from google import genai

# Вставьте ваши токены строго в кавычках
TELEGRAM_TOKEN = "8968323117:AAH90T4QOxyendjOvwTzUMq9heMgvzKy_bk"
GEMINI_API_KEY = "AQ.Ab8RN6KdCAAIsr8bWr0AsCCBGNy5PAOSpbT1rpxDpukjMAVjuQ"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Новый официальный клиент Google ИИ
ai_client = genai.Client(api_key=GEMINI_API_KEY)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Я бот на базе Gemini. Задай мне любой вопрос!")

@dp.message()
async def echo_handler(message: Message) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        # Используем быструю и бесплатную модель gemini-2.5-flash
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Произошла ошибка при обращении к Gemini. Проверьте настройки сети или API-ключ.")
        print(f"Ошибка в консоли: {e}")

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
