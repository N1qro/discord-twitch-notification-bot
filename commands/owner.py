import discord
from discord.ext import commands

from utils.logger import Log


class OwnerCog(discord.Cog):
    @discord.slash_command(
        name="shutdown",
        description="Shuts down the bot. For bot owner only",
        hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx: discord.ApplicationContext):
        await ctx.respond("Shutting down..")
        Log.info(f"Manual shutdown initiated by {ctx.author.name}")
        await ctx.bot.close()
