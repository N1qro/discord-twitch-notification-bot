import asyncio
import os
import sys

import discord
from database import Database
from embeds import DefaultEmbed, LinkEmbed
from environ_loader import load_env
from logger import Log
from owner_commands import OwnerCog
from asyncpg.exceptions import PostgresConnectionError
from discord.ext import commands
from discord.utils import basic_autocomplete
from twitch import TwitchRequests
from ui import LinkView


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


loop = asyncio.events.new_event_loop()
asyncio.events.set_event_loop(loop)
perms = discord.Permissions()
intents = discord.Intents()
perms.manage_roles = True
intents.guilds = True
bot = discord.Bot(permissions=perms, intents=intents, debug_guilds=[696434683730329713], loop=loop)


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def link(
    ctx: discord.ApplicationContext,
    twitch_url: discord.Option(str, "Enter the twitch streamer link")
):
    try:
        data = await TwitchRequests.getChannelInfo(twitch_url)
        if not data:
            return await ctx.respond("Couldn't find anyone with those credentials")
    except Exception as e:
        Log.failure(str(e))
    else:
        # Проверка на существование
        if await bot.db.is_already_linked(ctx.guild_id, int(data["id"])):
            return await ctx.respond(
                "This streamer is already linked to this server!"
            )

        await ctx.respond(embed=LinkEmbed(
            twitch_name=data["login"],
            twitch_description=data["description"],
            twitch_thumbnail=data["profile_image_url"],
            creation_date=data["created_at"][:data["created_at"].index("T")],
            is_partner=data["broadcaster_type"] == "partner"
        ), view=LinkView(bot.db.add_role, data["login"], int(data["id"])))


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def unlink(
    ctx: discord.ApplicationContext,
    twitch_login: discord.commands.Option(str, autocomplete=basic_autocomplete(("yes")))
):
    role_id = await bot.db.get_role_from_streamer(ctx.guild_id, twitch_login)
    role = ctx.guild.get_role(role_id)

    if role is not None:
        await role.delete(reason="Alert unlink")
        await bot.db.unlink_role(role_id)
        await ctx.respond(f"Successfully unlinked **{twitch_login}** streamer")
    else:
        await ctx.respond("Couldn't find any streamer with that login!")


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def set_alert_channel(
    ctx: discord.ApplicationContext,
    channel: discord.TextChannel
):
    everyone_role = ctx.guild.get_role(ctx.guild_id)
    permissions = channel.permissions_for(everyone_role)
    if permissions.view_channel:
        await bot.db.update_channel(ctx.guild_id, channel.id)
        await ctx.respond("Successfully updated the alert channel!")
    else:
        await ctx.respond("This channel does not have permission for everyone to read it")


async def main():
    events = EventCog(bot)
    ownerCommands = OwnerCog(bot)
    bot.add_cog(events)
    bot.add_cog(ownerCommands)

    try:
        bot.db = await Database.connect()
    except ConnectionRefusedError as e:
        return Log.failure(str(e))

    await bot.login(os.getenv("BOT_TOKEN"))
    await bot.application_info()
    DefaultEmbed.bot_name = bot.user.name
    DefaultEmbed.bot_thumnail_url = bot.user.avatar.url
    await bot.connect()


if __name__ == "__main__":
    load_env()
    TwitchRequests.init()
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop.run_until_complete(main())
    Log.info("Launching discord bot")
    asyncio.run(main())
