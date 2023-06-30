from http import HTTPStatus
from os import getenv

import discord
from discord.ext import commands

from api.twitch import Request
from database.models import Server, Streamer
from ui.embeds import LinkEmbed
from ui.ui import LinkView
from utils.autocomplete import getLinkedStreamers
from utils.chekers import hasAlertChannelSet, hasEmptyLinkSlot


class LinkCog(discord.Cog):
    @discord.command(
        name="link",
        description="Creates a streamer role and begins notifications")
    @commands.has_permissions(administrator=True)
    @hasAlertChannelSet()
    @hasEmptyLinkSlot()
    async def link(
        self,
        ctx: discord.ApplicationContext,
        username: discord.Option(str, "Enter a twitch streamer username or URL")
    ):
        """Привязывает стримера к серверу"""
        response = await Request.getChannelInfo(username)

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
            isOnline = await Request.checkIfOnline(streamer.id)
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

    @discord.command(
        name="unlink",
        description="Deletes a streamer alert role and stops notifications")
    @commands.has_permissions(administrator=True)
    async def unlink(
        self,
        ctx: discord.ApplicationContext,
        username: discord.commands.Option(
            str,
            "Enter a twitch streamer login",
            autocomplete=getLinkedStreamers)
    ):
        """Отвязывает стримера от сервера"""
        server = await Server.get(id=ctx.guild_id) \
                             .prefetch_related("roles__streamer")

        for role in server.roles:
            if role.streamer.login == username:
                discordRole = ctx.guild.get_role(role.id)
                await role.delete()
                await discordRole.delete(reason="Role unlinked")
                return await ctx.respond(
                    f"Successfully unlinked **{username}**!")

        await ctx.respond(
            f"Streamer **{username}** is not linked on this server.")

    @discord.command(
        name="unlink_all",
        description="Deletes all streamer alert roles and stops notifications")
    @commands.has_permissions(administrator=True)
    async def unlink_all(
        self,
        ctx: discord.ApplicationContext
    ):
        """Отвязывает всех стримеров от сервера"""
        server = await Server.get(id=ctx.guild_id).prefetch_related("roles")

        for role in server.roles:
            discordRole = ctx.guild.get_role(role.id)
            await discordRole.delete(reason="Role unlinked")

        await server.roles.all().delete()
        await ctx.respond("Successfully unlinked!")

    @discord.command(
        name="get_linked",
        description="Returns a list of currently linked to this guild streamers")
    async def get_linked(
        self,
        ctx: discord.ApplicationContext
    ):
        streamers = await getLinkedStreamers(ctx)

        if len(streamers) == 0:
            return await ctx.respond("This server does not have anyone linked to it! Use **/link**")

        text = f"This server currently has **{len(streamers)}** linked people\n\n"
        for i, streamer in enumerate(streamers, start=1):
            text += f"{i}: *{streamer}*\n"

        text += f"\nYou can link **{int(getenv('LINK_SLOTS')) - len(streamers)}** more streamers"

        await ctx.respond(text)
