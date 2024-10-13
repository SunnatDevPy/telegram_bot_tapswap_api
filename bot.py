import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.utils.i18n import FSMI18nMiddleware, I18n

from bot.handlers.add_channels import channels_router
from bot.handlers.admin import admin_router
from bot.handlers.game import game_router
from bot.handlers.start import start_router
from bot.language import language_router
from config import conf
from db import database


async def on_start(bot: Bot):
    await database.create_all()
    commands_admin = [
        BotCommand(command='start', description="Bo'tni ishga tushirish")
    ]
    text = "Assalomu alaykum STOCKFOOTBALL botga xush kelibsiz. Siz bu bot orqali sovg'alarga ega bolishingiz, futbol uchrashuvlarini jonli ko'rishingiz va o'yinlar haqida ma'lumotlar olishingiz mumkin"
    await bot.set_my_description(text)
    await bot.set_my_commands(commands=commands_admin)


async def on_shutdown(bot: Bot):
    await bot.delete_my_commands()


async def main():
    dp = Dispatcher()
    i18n = I18n(path="locales", default_locale='uz')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.include_routers(start_router, game_router, admin_router, channels_router, language_router)
    dp.startup.register(on_start)
    dp.shutdown.register(on_shutdown)
    # dp.callback_query.outer_middleware(ConfirmChannelMiddleware())
    # dp.message.outer_middleware(Middleware())
    bot = Bot(token=conf.bot.BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

# 1065  docker login
# 1068  docker build -t nickname/name .
# 1071  docker push nickname/name

# docker run --name db_mysql -e MYSQL_ROOT_PASSWORD=1 -d mysql
