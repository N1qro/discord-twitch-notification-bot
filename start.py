import asyncio
import os

import discord

from commands.owner import OwnerCog
from commands.events import EventCog
from commands.twitch import TwitchCog
from scripts.database import Database
from utils.environ_loader import load_env
from utils.logger import Log


loop = asyncio.events.new_event_loop()
asyncio.events.set_event_loop(loop)
perms = discord.Permissions()
intents = discord.Intents()
perms.manage_roles = True
intents.guilds = True
bot = discord.Bot(permissions=perms, intents=intents, debug_guilds=[696434683730329713], loop=loop)


async def main():
    events = EventCog(bot)
    ownerCommands = OwnerCog(bot)
    twitchCommands = TwitchCog(bot)
    bot.add_cog(events)
    bot.add_cog(ownerCommands)
    bot.add_cog(twitchCommands)

    try:
        bot.db = await Database.connect()
    except ConnectionRefusedError as e:
        return Log.failure(str(e))

    await bot.login(os.getenv("BOT_TOKEN"))
    await bot.application_info()
    await events.init()
    await bot.connect()


if __name__ == "__main__":
    load_env()
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    Log.info("Launching discord bot")
    loop.run_until_complete(main())
