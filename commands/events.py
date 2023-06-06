import discord
from ui.embeds import DefaultEmbed
from scripts.twitchapi import TwitchRequests
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
        await self.db.add_guild(guild.id, channel)

    @discord.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await self.db.remove_guild(guild.id)

    async def init(self):
        DefaultEmbed.bot_name = self.bot.user.name
        DefaultEmbed.bot_thumnail_url = self.bot.user.avatar.url
        TwitchRequests.init()
