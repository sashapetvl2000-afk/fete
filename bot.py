import os
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai


# =========================================================
# НАСТРОЙКИ
# =========================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

MODEL = "gemini-3.7-flash"


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={
        "api_version": "v1"
    }
)


# =========================================================
# TELEGRAM
# =========================================================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


# =========================================================
# ПАМЯТЬ ДИАЛОГОВ
# =========================================================

# user_id -> ID последнего взаимодействия Gemini
user_interactions = {}


# =========================================================
# /start
# =========================================================

@dp.message(CommandStart())
async def start_command(message: types.Message):

    # Сбрасываем предыдущую память пользователя
    user_interactions.pop(message.from_user.id, None)

    await message.answer(
        "Привет! 🤖\n\n"
        "Я работаю на Gemini 3.7 Flash.\n"
        "Можешь просто написать мне сообщение."
    )


# =========================================================
# /reset
# =========================================================

@dp.message(lambda message: message.text == "/reset")
async def reset_command(message: types.Message):

    user_interactions.pop(message.from_user.id, None)

    await message.answer(
        "🧠 Память диалога очищена."
    )


# =========================================================
# СООБЩЕНИЯ
# =========================================================

@dp.message()
async def handle_message(message: types.Message):

    if not message.text:
        return

    user_id = message.from_user.id
    user_text = message.text

    try:

        # -------------------------------------------------
        # Если у пользователя уже есть предыдущий диалог
        # -------------------------------------------------

        previous_id = user_interactions.get(user_id)

        if previous_id:

            interaction = client.interactions.create(
                model=MODEL,
                input=user_text,
                previous_interaction_id=previous_id
            )

        # -------------------------------------------------
        # Первое сообщение пользователя
        # -------------------------------------------------

        else:

            interaction = client.interactions.create(
                model=MODEL,
                input=user_text
            )

        # -------------------------------------------------
        # Сохраняем ID взаимодействия
        # -------------------------------------------------

        user_interactions[user_id] = interaction.id

        # -------------------------------------------------
        # Получаем текст ответа
        # -------------------------------------------------

        answer = interaction.output_text

        if not answer:
            answer = "Gemini не вернул текстовый ответ."

        # -------------------------------------------------
        # Telegram имеет ограничение на длину сообщения
        # -------------------------------------------------

        max_length = 4000

        for i in range(0, len(answer), max_length):

            chunk = answer[i:i + max_length]

            await message.answer(chunk)

    except Exception as e:

        error_text = repr(e)

        print("=" * 70)
        print("GEMINI ERROR")
        print(error_text)
        print("=" * 70)

        await message.answer(
            "❌ Ошибка Gemini:\n\n"
            + error_text[:3000]
        )


# =========================================================
# RENDER HEALTH CHECK
# =========================================================

async def health_check(request):

    return web.Response(
        text="Gemini Telegram Bot is alive!"
    )


async def start_web_server():

    app = web.Application()

    app.router.add_get(
        "/",
        health_check
    )

    app.router.add_get(
        "/health",
        health_check
    )

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(
        f"HTTP server started on port {port}"
    )


# =========================================================
# ЗАПУСК
# =========================================================

async def main():

    await start_web_server()

    print("======================================")
    print("Telegram bot started")
    print("Model:", MODEL)
    print("Gemini API: Interactions API")
    print("======================================")

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
