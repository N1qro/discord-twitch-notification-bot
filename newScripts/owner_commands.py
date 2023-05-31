from logger import Log
import discord
from discord.ext import commands


class OwnerCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Yes", hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx: discord.ApplicationContext):
        await ctx.respond("Shutting down..")
        # await ctx.send("Shutting down...")
        Log.info(f"Manual shutdown initiated by {ctx.author.name}")
        await self.bot.close()
