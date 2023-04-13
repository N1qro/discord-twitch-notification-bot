import os
import sys

# magic spell right here
sys.path.append(os.getcwd())

from sqlite3 import IntegrityError
from typing import Literal, Union
from embeds import getCheckEmbed

import discord
from discord.ext import commands
from dotenv import load_dotenv
from enums import Status

assert load_dotenv(), "No .env file configured"
from scripts.db import Database

permissions = discord.Intents.default()
permissions.guilds = True
permissions.message_content = True
permissions.members = True
bot = commands.Bot(os.getenv("PREFIX"), intents=permissions)
db = Database()


@bot.event
async def on_ready():
    print("Bot started")


@bot.event
async def on_guild_join(guild: discord.guild.Guild):
    try:
        db.execute("INSERT INTO general VALUES (?, Null, Null)", (guild.id,))
    except IntegrityError:
        pass
    else:
        db.commit()


@bot.event
async def on_guild_remove(guild: discord.guild.Guild):
    db.execute("DELETE FROM general WHERE guild_id == ?", (guild.id,))
    db.commit()


@bot.group(name="set")
@commands.has_permissions(administrator=True)
async def set(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        return await ctx.send("❓ Usage: **/twitch set <role|channel> <@role|#channel>**")


@set.command(name="role")
async def set_role(ctx: commands.Context, role: Union[discord.Role, str] = None):
    if role is None:
        return await ctx.send("❓ Usage: **/twitch set role <#role>**")

    if isinstance(role, str):
        return await ctx.send(f"Unresolved role: {role}")

    db.set_role(role.id, ctx.guild.id)
    await ctx.send(f"You selected {role.mention} as your alert role!", silent=True)


@set.command(name="channel")
async def set_channel(ctx: commands.Context, channel: Union[discord.TextChannel, str] = None):
    if channel is None:
        return await ctx.send("❓ Usage: **/twitch set role <@role>**")

    if isinstance(channel, str):
        return await ctx.send(f"Unresolved channel: {channel}")

    db.set_channel(channel.id, ctx.guild.id)
    await ctx.send(f"You selected {channel.mention} as your alert channel!", silent=True)


@bot.group(name="reset")
@commands.has_permissions(administrator=True)
async def reset(ctx: commands.Context):
    if not ctx.invoked_subcommand:
        await ctx.send("❓ Usage: **/twitch reset <role|channel>**")


@reset.command(name="role")
async def reset_role(ctx: commands.Context):
    data = db.get_guild_data(ctx.guild.id)
    print(data)
    if data.roleId is not None:
        db.reset_role(ctx.guild.id)
        return await ctx.send(f"Role <@&{data.roleId}> will no longer be alerted.", silent=True)
    await ctx.send("You haven't setup any notification role yet")


@reset.command(name="channel")
async def reset_channel(ctx: commands.Context):
    data = db.get_guild_data(ctx.guild.id)
    if data.channelId is not None:
        db.reset_channel(ctx.guild.id)
        return await ctx.send(f"Channel <#{data.channelId}> will no longer be messaged", silent=True)


@bot.command()
@commands.has_permissions(administrator=True)
async def check(ctx: commands.Context):
    embed = getCheckEmbed(bot, db, ctx.guild.id)
    await ctx.send(embed=embed, silent=True, reference=ctx.message)


@bot.command()
@commands.has_permissions(administrator=True)
async def setup(
    ctx: commands.Context,
    role: Union[discord.Role, str] = None,
    channel: Union[discord.TextChannel, str] = None
):
    if role is None:
        return await ctx.send("❓ Usage: **/twitch setup <@ROLE> <#channel>**")

    if channel is None:
        return await ctx.send("❓ Usage: **/twitch setup <@role> <#CHANNEL>**")

    if isinstance(role, str):
        return await ctx.send(f"Unresolved role: {role}")

    if isinstance(channel, str):
        return await ctx.send(f"Unresolved channel: {channel}")

    db.set_role(role.id, ctx.guild.id)
    db.set_channel(channel.id, ctx.guild.id)
    await ctx.send(f"You've setup the bot with {role.mention} role and {channel.mention} channel", silent=True)

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
