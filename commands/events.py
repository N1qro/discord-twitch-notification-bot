import discord
from database.models import Server, Streamer, Role
from ui.embeds import DefaultEmbed
from scripts.twitchapi import TwitchRequests
from commands.tasks import Tasks
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
        pass
        # if role.id not in await self.db.get_all_guild_roles(role.guild.id):
        #     return

        # await self.db.unlink_role(role.id)
        # await self.db.increment_linked_data(role.guild.id, -1)

        # if role.guild.system_channel:
        #     return await role.guild.system_channel.send(
        #         f"Role **{role.name}** was unexpectedly deleted, "
        #         "streamer corresponding to it was unlinked!")

        # await role.guild.owner.send(
        #     f"Role **{role.name}** was deleted in **'{role.guild.name}'**. "
        #     "Streamer, corresponding to it, was unlinked.\n"
        #     "You received this message because this guild does not "
        #     f"have a system channel set. {role.guild.owner.mention}")

    # async def cog_command_error(self, ctx: discord.ApplicationContext, error: Exception):
    #     # if isinstance(error, discord.ApplicationCommandInvokeError):
    #     #     raise errorz
    #     if isinstance(error, discord.errors.Forbidden):
    #         print(ctx.command)
    #     else:
    #         raise error

    async def init(self):
        DefaultEmbed.bot_name = self.bot.user.name
        DefaultEmbed.bot_thumnail_url = self.bot.user.avatar.url
        TwitchRequests.init()
