import asyncio
import os
import sys

import discord
import interactions
from aiohttp.client_exceptions import ClientConnectionError
from database import Database
from discord.ext import commands
from environ_loader import load_env
from events import EventCog, cleanup, setup_hook
from logger import Log
from owner_commands import OwnerCog

# Установка прав бота и, пока что, пустого префикса
permissions = discord.Intents()
permissions.message_content = True
permissions.messages = True
permissions.reactions = True
bot = commands.Bot(command_prefix=None, intents=permissions)
bot.db: Database = None


@bot.command()
async def test(ctx: commands.Context):
    data = await bot.db.test_query()
    print(data)
    await ctx.channel.send("Registered!")


async def main():
    try:
        # Подключаем модули бота
        await bot.add_cog(EventCog(bot))
        await bot.add_cog(OwnerCog(bot))

        # Выполняем вход и подключаемся к бд
        await bot.login(os.getenv("BOT_TOKEN"))
        await setup_hook(bot)
        Log.success("Logged in using discord token!")

        # Подключаемся к серверам Discord
        await bot.connect()
    except discord.LoginFailure as e:
        Log.failure(str(e))
        await bot.close()
    except ClientConnectionError:
        Log.failure("Check your internet connection!")
    except Exception as e:
        print('FUCK', e)
    finally:
        await cleanup(bot)


if __name__ == "__main__":
    # Загрузка переменных среды и установка префикса
    load_env()
    bot.command_prefix = os.getenv("BOT_PREFIX")

    # В случае, если бот будет запущен на Windows, без этого
    # asyncio будет выдавать множество ошибок после завершения программы
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        Log.warning("Pressing Ctrl+C will freeze the script for some time")

    # Главная часть
    Log.info("Launching the bot...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Ручной выход из приложения на Ctrl+C
        pass
    finally:
        # Вывод при отсутствии ошибок
        if sys.exc_info()[0] is None:
            Log.info("Bot offline.")
