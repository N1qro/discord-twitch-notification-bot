import discord
from discord.ext import commands
from discord.utils import basic_autocomplete
from ui.ui import LinkView
from http import HTTPStatus
from scripts.database import Database
from utils.chekers import has_alert_channel_set, has_empty_link_slot
from utils.exceptions import NoAlertChannelSet, NoLinkedSlotsLeft
from ui.embeds import LinkEmbed
from scripts.twitchapi import TwitchRequests
from utils.logger import Log


async def get_linked_streamers(ctx: discord.AutocompleteContext):
    data = await ctx.cog.db.get_linked_streamers(ctx.interaction.guild_id)
    return (record.get("streamer_login") for record in data)


class TwitchCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = Database()

    # @property
    # def db(self):
    #     if getattr(self.__class__, "_db", None) is None:
    #         new_db = Database()
    #         self.__class__._db = new_db
    #     return self.__class__._db

    @discord.command()
    @commands.has_permissions(administrator=True)
    @has_alert_channel_set()
    @has_empty_link_slot()
    async def link(
        self,
        ctx: discord.ApplicationContext,
        twitch_url: discord.Option(str, "Enter the twitch streamer link")
    ):
        response = await TwitchRequests.getChannelInfo(twitch_url)

        # Обработка HTTP кодов
        match response:
            case HTTPStatus.BAD_REQUEST:
                return await ctx.respond("This is not a valid URL")
            case HTTPStatus.UNAUTHORIZED:
                return await ctx.respond("Contact the developer. API key expired")

        # Проверка на существование аккаунта
        if response is None:
            return await ctx.respond("Couldn't find anyone with those credentials")

        # Проверка на привязанность
        if await self.db.is_already_linked(ctx.guild_id, int(response["id"])):
            return await ctx.respond(
                "This streamer is already linked to this server!")

        await ctx.respond(embed=LinkEmbed(
            twitch_name=response["login"],
            twitch_description=response["description"],
            twitch_thumbnail=response["profile_image_url"],
            creation_date=response["created_at"][:response["created_at"].index("T")],
            is_partner=response["broadcaster_type"] == "partner"
        ), view=LinkView(response["login"], int(response["id"])))

    @discord.command()
    @commands.has_permissions(administrator=True)
    async def unlink(
        self,
        ctx: discord.ApplicationContext,
        twitch_login: discord.commands.Option(str, autocomplete=basic_autocomplete(get_linked_streamers))
    ):
        role_id = await self.db.get_role_from_streamer(ctx.guild_id, twitch_login)
        role = ctx.guild.get_role(role_id)

        if role is not None:
            await role.delete(reason="Alert unlink")
            await self.db.unlink_role(role_id)
            await self.db.increment_linked_data(ctx.guild_id, -1)
            await ctx.respond(f"Successfully unlinked **{twitch_login}** streamer")
        else:
            await ctx.respond("Couldn't find any streamer with that login!")

    @discord.command()
    @commands.has_permissions(administrator=True)
    async def set_alert_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel
    ):
        everyone_role = ctx.guild.get_role(ctx.guild_id)
        permissions = channel.permissions_for(everyone_role)
        if permissions.view_channel:
            await self.db.update_channel(ctx.guild_id, channel.id)
            await ctx.respond("Successfully updated the alert channel!")
        else:
            await ctx.respond("This channel does not have permission for everyone to read it")

    @discord.command()
    async def sub(
        self,
        ctx: discord.ApplicationContext,
        streamer_login: discord.Option(str, autocomplete=basic_autocomplete(get_linked_streamers))
    ):
        pass

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        # if isinstance(error, discord.ApplicationCommandInvokeError):
        #     raise error
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.respond("Only server administators can run this command!")
        elif isinstance(error, NoAlertChannelSet):
            await ctx.respond(str(error))
        elif isinstance(error, NoLinkedSlotsLeft):
            await ctx.respond(str(error))
        else:
            raise error


# @link.error
# async def error(ctx: discord.ApplicationContext, error: discord.DiscordException):
#     if isinstance(error, commands.errors.MissingPermissions):
#         await ctx.respond("Only the server administrators can run this command")