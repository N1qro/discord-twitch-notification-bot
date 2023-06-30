import asyncio
import tortoise
from tortoise import Tortoise
from database.models import Streamer, Role, Server
import os

import discord

from commands.owner import OwnerCog
from commands.events import EventCog
from commands.twitch import TwitchCog
from commands.tasks import Tasks

from scripts.database import Database
from utils.environ_loader import load_env
from utils.logger import Log


loop = asyncio.events.new_event_loop()
asyncio.events.set_event_loop(loop)
intents = discord.Intents()
intents.guilds = True
bot = discord.Bot(intents=intents, debug_guilds=[696434683730329713], loop=loop)


async def main():
    try:
        await Tortoise.init(config_file=os.path.join("database", "config.json"))
        await Tortoise.generate_schemas(safe=True)
    except ConnectionRefusedError as e:
        return Log.failure(str(e))
    else:
        events = EventCog(bot)
        ownerCommands = OwnerCog(bot)
        twitchCommands = TwitchCog(bot)
        tasks = Tasks(bot)
        # tasks.startall()
        bot.add_cog(events)
        bot.add_cog(ownerCommands)
        bot.add_cog(twitchCommands)

        await bot.login(os.getenv("BOT_TOKEN"))
        await bot.application_info()
        await events.init()
        await bot.connect()
    finally:
        await tortoise.connections.close_all()


if __name__ == "__main__":
    load_env()
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    Log.info("Launching discord bot")
    loop.run_until_complete(main())
