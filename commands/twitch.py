import discord
from utils.logger import Log


class TwitchCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.command()
    async def testing_command_2(self, ctx: discord.ApplicationContext):
        Log.success("Recognized!")
        await ctx.respond("Great.")
