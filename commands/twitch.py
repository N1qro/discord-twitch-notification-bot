import discord
import time
import asyncio
from discord.ext import commands
from discord.utils import basic_autocomplete
from ui.ui import LinkView
from http import HTTPStatus
from database.models import Server, Role, Streamer
from utils.chekers import has_alert_channel_set, has_empty_link_slot
from utils.exceptions import NoAlertChannelSet, NoLinkedSlotsLeft
from ui.embeds import LinkEmbed
from scripts.twitchapi import TwitchRequests
from utils.logger import Log


async def get_linked_streamers(ctx: discord.AutocompleteContext):
    guild = await Server.get(id=ctx.interaction.guild_id)

    autocomplete = []
    async for role in guild.roles:
        streamer = await role.streamer
        autocomplete.append(streamer.login)

    return autocomplete


async def get_subbed_streamers(ctx: discord.AutocompleteContext):
    logins = []
    for role in ctx.interaction.user.roles:
        if role.name.startswith("t.tv/"):
            logins.append(role.name[5:])
    return sorted(logins)


async def get_unsubbed_streamers(ctx: discord.AutocompleteContext):
    allRoles = set(r.name[5:] for r in ctx.interaction.guild.roles
                   if r.name.startswith("t.tv/"))
    userRoles = set(r.name[5:] for r in ctx.interaction.user.roles
                    if r.name.startswith("t.tv"))

    return sorted(allRoles.difference(userRoles))


class TwitchCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

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

        # Обработка HTTP кодов ошибки
        if response == HTTPStatus.BAD_REQUEST:
            return await ctx.respond("This is not a valid URL")
        if response == HTTPStatus.UNAUTHORIZED:
            return await ctx.respond("Contact the developer. API key expired")

        # Проверка на существование аккаунта
        if response is None:
            return await ctx.respond("Couldn't find anyone with those credentials")

        guild = await Server.get(id=ctx.guild_id)
        streamer, wasCreated = await Streamer.get_or_create(
            id=int(response["id"]),
            login=response["login"])

        # Если стример был только что создан, то мы проверяем
        # стримит он в текущий момент, или нет. Если да, то сохраняем это
        if wasCreated:
            isOnline = await TwitchRequests.checkIfOnline(streamer.id)
            if streamer.is_online != isOnline:
                streamer.is_online = isOnline
                await streamer.save()

        # Проверка на привязанность стримера к текущему серверу
        async for role in guild.roles:
            if role.streamer_id == streamer.id:
                return await ctx.respond("This streamer is already linked!")

        # Вывод интерфейса
        await ctx.respond(embed=LinkEmbed(
            twitch_name=response["login"],
            twitch_description=response["description"],
            twitch_thumbnail=response["profile_image_url"],
            creation_date=response["created_at"][:response["created_at"].index("T")],
            is_partner=response["broadcaster_type"] == "partner"
        ), view=LinkView(streamer))

    @discord.command()
    @commands.has_permissions(administrator=True)
    async def unlink(
        self,
        ctx: discord.ApplicationContext,
        twitch_login: discord.commands.Option(str, autocomplete=get_linked_streamers)
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
    async def unlink_all(
        self,
        ctx: discord.ApplicationContext
    ):
        server = await Server.get(id=ctx.guild_id).prefetch_related("roles")

        for role in server.roles:
            discordRole = ctx.guild.get_role(role.id)
            await discordRole.delete(reason="Role unlinked")

        await server.roles.all().delete()
        await ctx.respond("Successfully unlinked!")

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
        username: discord.Option(str, autocomplete=get_unsubbed_streamers)
    ):
        for role in ctx.guild.roles:
            if role.name == f"t.tv/{username}":
                await ctx.author.add_roles(
                    role,
                    reason="Subscribed to streamer")
                return await ctx.respond(
                    f"Successfully subscribed to **{username}**")
        await ctx.respond(
            f"Couldn't find **{username}** in linked slots")

    @discord.command()
    async def unsub(
        self,
        ctx: discord.ApplicationContext,
        username: discord.Option(str, autocomplete=get_subbed_streamers)
    ):
        for role in ctx.author.roles:
            if role.name == f"t.tv/{username}":
                await ctx.author.remove_roles(role, reason="Unsubscribed")
                return await ctx.respond(
                    f"Successfully unsubscribed from **{username}**!")
        await ctx.respond(f"You are not subscribed to **{username}**")

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
