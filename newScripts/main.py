import os
import discord
import environ_loader
import asyncio
import sys
import signal
from database import Database
from aiohttp.client_exceptions import ClientConnectionError
from logger import Log
import asyncpg
from discord.ext import commands

permissions = discord.Intents()
permissions.message_content = True
permissions.messages = True
permissions.reactions = True
bot = commands.Bot(command_prefix=os.getenv("BOT_PREFIX"), intents=permissions)
disconnect_fired = asyncio.Event()


@bot.event
async def on_ready():
    Log.success("Bot started!")


@bot.command()
async def test(ctx: commands.Context):
    data = await bot.db.test_query()
    print(data)
    await ctx.channel.send("Registered!")


@bot.command()
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    Log.info("Manual shutdown initiated. Closing the connection")
    await bot.close()


@bot.event
async def on_disconnect():
    Log.info("Closing the database connection pool")
    await bot.pool.close()
    Log.info("Database connection pool closed!")
    disconnect_fired.set()


@bot.event
async def setup_hook():
    Log.info("Preparing bot setup...")
    bot.db = await Database.connect()
    Log.success("Successfully connected to the db!")


async def main():
    try:
        await bot.login(os.getenv("BOT_TOKEN"))
        Log.success("Logged in using discord token!")
        await bot.connect()
        await disconnect_fired.wait()
    except discord.LoginFailure as e:
        Log.failure(str(e))
    except ClientConnectionError:
        Log.failure("Check your internet connection!")


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    Log.info("Launching the bot...")
    asyncio.run(main())
