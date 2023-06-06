import asyncio
import os

import discord
from discord.ext import commands
from discord.utils import basic_autocomplete

from commands.owner import OwnerCog
from commands.events import EventCog
from commands.twitch import TwitchCog
from scripts.database import Database
from scripts.twitchapi import TwitchRequests
from ui.embeds import DefaultEmbed, LinkEmbed
from ui.ui import LinkView
from utils.environ_loader import load_env
from utils.logger import Log


loop = asyncio.events.new_event_loop()
asyncio.events.set_event_loop(loop)
perms = discord.Permissions()
intents = discord.Intents()
perms.manage_roles = True
intents.guilds = True
bot = discord.Bot(permissions=perms, intents=intents, debug_guilds=[696434683730329713], loop=loop)


async def get_linked_streamers(ctx: discord.AutocompleteContext):
    data = await ctx.bot.db.get_linked_streamers(ctx.interaction.guild_id)
    return (record.get("streamer_login") for record in data)


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


@link.error
async def error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.respond("Only the server administrators can run this command")


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def unlink(
    ctx: discord.ApplicationContext,
    twitch_login: discord.commands.Option(str, autocomplete=basic_autocomplete(get_linked_streamers))
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


@bot.slash_command()
async def sub(
    ctx: discord.ApplicationContext,
    streamer_login: discord.Option(str, autocomplete=basic_autocomplete(get_linked_streamers))
):
    pass


async def main():
    events = EventCog(bot)
    ownerCommands = OwnerCog(bot)
    twitchCommands = TwitchCog(bot)
    bot.add_cog(events)
    bot.add_cog(ownerCommands)
    bot.add_cog(twitchCommands)

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

    Log.info("Launching discord bot")
    loop.run_until_complete(main())
