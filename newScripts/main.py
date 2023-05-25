import os
import discord
import environ_loader
import asyncio
import sys
from logger import Log
import asyncpg
from discord.ext import commands

permissions = discord.Intents()
permissions.message_content = True
permissions.messages = True
permissions.reactions = True
bot = commands.Bot(command_prefix=os.getenv("BOT_PREFIX"), intents=permissions)


@bot.event
async def on_connect():
    Log.success("Connected to the discord bot!")
    Log.info("Connecting to the PostgreSQL database...")
    bot.pool = await asyncpg.create_pool()
    Log.success("Successfully connected to the db!")


@bot.event
async def on_ready():
    Log.success("Bot started!")


@bot.command()
async def test(ctx: commands.Context):
    async with bot.pool.acquire() as conn:
        data = await conn.fetch("SELECT * FROM person LIMIT 4")
        print(data)
    await ctx.channel.send("Registered!")


@bot.command()
@commands.is_owner()
async def shutdown(ctx: commands.Context):
    try:
        sys.exit(0)
    except Exception:  # До сих пор не блочит все asyncio исключения
        pass
    finally:
        Log.info("Bot offline")


if __name__ == "__main__":
    # if os.name == "nt":
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        Log.info("Launching discord bot...")
        bot.run(os.getenv("BOT_TOKEN"))
    except discord.errors.LoginFailure as e:
        Log.failure(str(e)), sys.exit(1)
    finally:
        if getattr(bot, "pool", None):
            Log.info("Closing the database connection pool")
            asyncio.new_event_loop().run_until_complete(bot.pool.close())
            Log.success("Database connection pool closed!")
