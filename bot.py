import os
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google import genai


TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

MODEL = "gemini-3.7-flash"


client = genai.Client(
    api_key=GEMINI_API_KEY
)


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: types.Message):

    await message.answer(
        "Привет! 🤖\n\n"
        "Gemini 3.7 Flash подключён."
    )


@dp.message()
async def handle_message(message: types.Message):

    if not message.text:
        return

    try:

        interaction = client.interactions.create(
            model=MODEL,
            input=message.text
        )

        answer = interaction.output_text

        await message.answer(answer)

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        await message.answer(
            "❌ Gemini error:\n\n"
            + repr(e)[:3000]
        )


async def health_check(request):

    return web.Response(
        text="Bot is alive!"
    )


async def start_web_server():

    app = web.Application()

    app.router.add_get("/", health_check)

    app.router.add_get("/health", health_check)

    port = int(
        os.environ.get("PORT", 10000)
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()


async def main():

    await start_web_server()

    print("Telegram bot started!")
    print("Gemini model:", MODEL)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
