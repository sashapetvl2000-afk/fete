import os
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai


# =========================
# НАСТРОЙКИ
# =========================

TELEGRAM_TOKEN = os.environ[8819225995:AAGt-ITWWc2BNukP8OPg23HjvD5UFdDEj9I"]
GEMINI_API_KEY = os.environ["AQ.Ab8RN6L66m-m-ro00XU8qVksXCbJPTE69IdhuJ-AidzEVqgRzA"]

# Модель Gemini
GEMINI_MODEL = "gemini-3.7-flash"


# =========================
# GEMINI
# =========================

client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# TELEGRAM
# =========================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я Gemini-бот 🤖\n\n"
        "Напиши мне любой вопрос."
    )


@dp.message()
async def handle_message(message: types.Message):

    if not message.text:
        return

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=message.text
        )

        answer = response.text

        if not answer:
            answer = "Gemini не вернул текстовый ответ."

        await message.answer(answer)

    except Exception as e:
        print("GEMINI ERROR:", repr(e))

        await message.answer(
            "Произошла ошибка при обращении к Gemini.\n"
            "Посмотри логи Render."
        )


# =========================
# HTTP SERVER
# =========================

async def health_check(request):
    return web.Response(text="Bot is alive!")


async def start_web_server():

    app = web.Application()

    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    port = int(os.environ.get("PORT", 10000))

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(f"HTTP server started on port {port}")


# =========================
# ЗАПУСК
# =========================

async def main():

    await start_web_server()

    print("Telegram bot started!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
