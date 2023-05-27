from logger import Log
from discord.ext import commands


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context):
        Log.info(f"Manual shutdown initiated by {ctx.author.name}")
        await self.bot.close()
