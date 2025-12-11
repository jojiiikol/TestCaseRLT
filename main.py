from aiogram import Bot, Dispatcher, types
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BotConfig
from db import Database
from llm import LLM

dp = Dispatcher()
llm = LLM()
db = Database()


@dp.message()
async def result(message: types.Message):
    try:
        query = await llm.get_answer(message.text)
        print(query)
        result = await db.get_data(query)
        await message.answer(result)
    except Exception as e:
        await message.answer(f"Этот запрос не может быть обработан:\n{str(e)[:100]}")


async def main():
    res = await db.init_database()
    bot = Bot(token=BotConfig().bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
