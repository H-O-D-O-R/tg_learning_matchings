import asyncio
import logging

from aiogram.client.session.aiohttp import AiohttpSession

from aiogram import Bot, Dispatcher

from config import TOKEN

from app.handlers import router
from app.database.models import async_main


async def main():
    await async_main()
#    session = AiohttpSession(proxy='http://proxy.server:3128')
#    bot = Bot(token=TOKEN, session=session)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')