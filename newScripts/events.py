from logger import Log
from database import Database
from discord.ext import commands


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        Log.success("Bot started!")


async def cleanup(bot):
    if hasattr(bot, "db"):
        Log.info("Closing the database connection pool...")
        await bot.db.pool.close()
        Log.info("Database connection pool closed!")


async def setup_hook(bot):
    Log.info("Preparing bot setup...")
    try:
        bot.db = await Database.connect()
    except Exception as e:
        Log.failure(str(e))
        await bot.close()
        exit(2)
    else:
        Log.success("Successfully connected to the db!")
