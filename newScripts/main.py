import os
import discord
import environ_loader
from database import Database
from discord.ext import commands

permissions = discord.Intents()
permissions.message_content = True
permissions.messages = True
permissions.reactions = True

db = Database()
bot = commands.Bot(command_prefix=os.getenv("BOT_PREFIX"), intents=permissions)


@bot.event
async def on_ready():
    print("Bot is ready!")


@bot.event
async def on_disconnect():
    await db.close()


@bot.command()
async def test(ctx: commands.Context):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            data = await conn.fetch("SELECT * FROM person LIMIT 5")

    await ctx.channel.send("Registered!")


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
