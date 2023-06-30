import discord
import asyncio
from utils.logger import Log
from scripts.database import Database
from discord.ext import tasks, commands


class Tasks(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.cached_streamers_amount = -1

    def startall(self):
        self.get_online.start()
        self.update_presence_task.start()

    @staticmethod
    async def update_presence(bot: discord.Bot, amount=None):
        status = discord.Status.streaming
        activity = discord.Activity(
            name=f"{amount} streamers!",
            type=discord.ActivityType.watching,
            state="State of this",
            details="Some details!",
            application_id=bot.application_id,
            assets={
                "large_image": "python-logo"
            })
        print(activity.assets)
        print(activity.large_image_url)

        Log.info("Updating rich presence...")
        await bot.change_presence(activity=activity,
                                  status=status)

    @tasks.loop(minutes=1)
    async def get_online(self):
        pass

    @tasks.loop(minutes=5)
    async def update_presence_task(self):
        amount = await self.db.get_streamer_amount()
        if amount != self.cached_streamers_amount:
            self.cached_streamers_amount = amount
            await self.update_presence(self.bot, amount)

    @update_presence_task.before_loop
    async def setup(self):
        await self.bot.wait_until_ready()
