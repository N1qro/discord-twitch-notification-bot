import discord

from database.models import Server
from utils.logger import Log


class EventCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        Log.success("Bot is ready!")

    @discord.Cog.listener()
    async def on_connect(self):
        await self.bot.sync_commands()
        Log.info("Connected to the servers")

    @discord.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = guild.system_channel
        if channel:
            channel = channel.id
        await Server.create(guild_id=guild.id, channel_id=channel)

    @discord.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        entry = await Server.get_or_none(guild_id=guild.id)
        if entry:
            await entry.delete()

    @discord.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """TODO"""
