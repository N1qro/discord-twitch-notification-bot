import discord

from utils.autocomplete import getSubbedStreamers, getUnsubbedStreamers


class SubCog(discord.Cog):
    @discord.command(
        name="sub",
        description="Give yourself a notification role of a linked streamer")
    async def sub(
        self,
        ctx: discord.ApplicationContext,
        username: discord.Option(
            str,
            "Enter a twitch streamer login",
            autocomplete=getUnsubbedStreamers)
    ):
        """Подписывает пользователя на стримера"""
        for role in ctx.guild.roles:
            if role.name == f"t.tv/{username}":
                await ctx.author.add_roles(
                    role,
                    reason="Subscribed to streamer")
                return await ctx.respond(
                    f"Successfully subscribed to **{username}**")
        await ctx.respond(
            f"Couldn't find **{username}** in linked slots")

    @discord.command(
        name="unsub",
        description="Removes a notification role of given streamer from you")
    async def unsub(
        self,
        ctx: discord.ApplicationContext,
        username: discord.Option(
            str,
            "Enter a twitch streamer login",
            autocomplete=getSubbedStreamers)
    ):
        """Отписывает пользователя от стримера"""
        for role in ctx.author.roles:
            if role.name == f"t.tv/{username}":
                await ctx.author.remove_roles(role, reason="Unsubscribed")
                return await ctx.respond(
                    f"Successfully unsubscribed from **{username}**!")
        await ctx.respond(f"You are not subscribed to **{username}**")
