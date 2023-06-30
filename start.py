import asyncio
import os

import discord
import tortoise
from tortoise import Tortoise

import utils.tasks
from commands.events import EventCog
from commands.main import TwitchCog
from commands.owner import OwnerCog
from utils.environ_loader import load_env
from utils.logger import Log

loop = asyncio.events.new_event_loop()
asyncio.events.set_event_loop(loop)
intents = discord.Intents()
intents.guilds = True
bot = discord.Bot(intents=intents, debug_guilds=[696434683730329713], loop=loop)
utils.tasks.bot = bot


async def init(bot):
    """Инициализация перед включеним бота"""
    import utils.chekers
    from api.twitch import Request
    from ui.embeds import DefaultEmbed
    DefaultEmbed.bot_name = bot.user.name
    DefaultEmbed.bot_thumnail_url = bot.user.avatar.url
    utils.chekers.LINK_SLOTS = int(os.getenv("LINK_SLOTS"))
    await Tortoise.init(config_file=os.path.join("database", "config.json"))
    await Tortoise.generate_schemas(safe=True)
    Request.init()
    del Request, DefaultEmbed, utils.chekers


async def main():
    try:
        await bot.login(os.getenv("BOT_TOKEN"))
        await bot.application_info()
        Log.info("Called init()")
        await init(bot)
        Log.success("No errors during init")
    except ConnectionRefusedError as e:
        return Log.failure(str(e))
    else:
        events = EventCog(bot)
        ownerCommands = OwnerCog()
        twitchCommands = TwitchCog()
        bot.add_cog(events)
        bot.add_cog(ownerCommands)
        bot.add_cog(twitchCommands)
        utils.tasks.notification_task.start()

        await bot.connect()
    finally:
        Log.info("Closing the connections")
        await tortoise.connections.close_all()
        Log.info("DB connections closed")


if __name__ == "__main__":
    load_env()
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    Log.info("Launching discord bot")
    loop.run_until_complete(main())
