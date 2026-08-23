import os
import asyncio
import json

from aiohttp import web, ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart


# =========================================================
# НАСТРОЙКИ
# =========================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

MODEL = "gemini-3.7-flash"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com"
    "/v1beta/interactions"
)


# =========================================================
# TELEGRAM
# =========================================================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


# =========================================================
# ПАМЯТЬ ДИАЛОГОВ
# =========================================================

user_interactions = {}


# =========================================================
# GEMINI API
# =========================================================

async def ask_gemini(user_id, text):

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "input": text
    }

    previous_id = user_interactions.get(user_id)

    if previous_id:
        data["previous_interaction_id"] = previous_id

    async with ClientSession() as session:

        async with session.post(
            GEMINI_URL,
            headers=headers,
            json=data
        ) as response:

            response_text = await response.text()

            if response.status != 200:

                raise Exception(
                    f"Gemini HTTP {response.status}: "
                    f"{response_text}"
                )

            result = json.loads(response_text)

            interaction_id = result.get("id")

            if interaction_id:
                user_interactions[user_id] = interaction_id

            # Ищем текстовый ответ
            output_text = result.get("output_text")

            if output_text:
                return output_text

            # Запасной вариант — разбираем output
            output = result.get("output", [])

            texts = []

            for item in output:

                if item.get("type") == "text":

                    text_value = item.get("text")

                    if text_value:
                        texts.append(text_value)

            if texts:
                return "\n".join(texts)

            return "Gemini не вернул текстовый ответ."


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start_command(message: types.Message):

    user_interactions.pop(
        message.from_user.id,
        None
    )

    await message.answer(
        "Привет! 🤖\n\n"
        "Я работаю на Gemini 3.7 Flash.\n\n"
        "Напиши мне любой вопрос."
    )


# =========================================================
# RESET
# =========================================================

@dp.message()
async def handle_message(message: types.Message):

    if not message.text:
        return

    if message.text == "/reset":

        user_interactions.pop(
            message.from_user.id,
            None
        )

        await message.answer(
            "🧠 Память диалога очищена."
        )

        return

    user_id = message.from_user.id

    try:

        answer = await ask_gemini(
            user_id,
            message.text
        )

        # Telegram max message length
        max_length = 4000

        for i in range(
            0,
            len(answer),
            max_length
        ):

            await message.answer(
                answer[i:i + max_length]
            )

    except Exception as e:

        error_text = repr(e)

        print("=" * 70)
        print("GEMINI ERROR")
        print(error_text)
        print("=" * 70)

        await message.answer(
            "❌ Gemini error:\n\n"
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
# MAIN
# =========================================================

async def main():

    await start_web_server()

    print("=" * 70)
    print("TELEGRAM BOT STARTED")
    print("MODEL:", MODEL)
    print("GEMINI API: DIRECT REST")
    print("=" * 70)

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
