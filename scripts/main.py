import os
import pickle
from sqlite3 import Connection, IntegrityError
from typing import Literal, Union

import discord
from discord.ext import commands
from dotenv import load_dotenv

assert load_dotenv(), "No .env file configured"
from db import db, set_channel, set_role

permissions = discord.Intents.default()
permissions.guilds = True
permissions.message_content = True
permissions.members = True
bot = commands.Bot(os.getenv("PREFIX"), intents=permissions)


@bot.event
async def on_ready():
    print("Bot started")
    print(bot.command_prefix)


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


@bot.command()
@commands.has_permissions(administrator=True)
async def check(ctx: commands.context.Context):
    good = "✅ Done"
    bad = "❌ Not given"
    guild_id, channel_id, role_id = db.cursor().execute("""
        SELECT *
        FROM general
        WHERE guild_id == ?
    """, (ctx.guild.id,)).fetchone()

    is_everything_correct = all(item is not None for item in (guild_id, channel_id, role_id))
    embed_color = 0x46f339 if is_everything_correct else 0xf50f0f

    embed=discord.Embed(title="Status preview", description="Will help you determine what is missing or not", color=embed_color)
    embed.set_author(name=bot.user.display_name, icon_url=bot.user.display_avatar)
    embed.add_field(name="Guild setup", value=good if guild_id else bad, inline=True)
    embed.add_field(name="Permissions", value="✅ Done", inline=True)
    embed.add_field(name="", value="", inline=True)
    embed.add_field(name="Alert role set", value=good if role_id else bad, inline=True)
    embed.add_field(name="Announcement channel set", value=good if channel_id else bad, inline=True)
    embed.set_footer(text="Use '/twitch link help' to see how to set missing information if needed")
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def set(
    ctx: commands.context.Context,
    mode: Literal["channel", "role", "help"] = "help",
    channel_or_role: Union[discord.channel.TextChannel, discord.role.Role, str] = None
):
    if mode == "help":
        return await ctx.send("TODO")

    try:
        assert mode in ("channel", "role", "help"), "Unrecognized command. Type /twitch set help"
        assert not isinstance(channel_or_role, str), f"Given {mode} not found"
        assert (mode == "channel" and isinstance(channel_or_role, discord.channel.TextChannel)) \
            or (mode == "role" and isinstance(channel_or_role, discord.role.Role)), \
            f"This command requires {mode} to be provided"
    except AssertionError as e:
        await ctx.send(str(e))
    else:
        if mode == "channel":
            set_channel(ctx.guild.id, channel_or_role.id)
            await ctx.send(f"You selected {channel_or_role} as your alert channel!")
        elif mode == "role":
            set_role(ctx.guild.id, channel_or_role.id)
            await ctx.send(f"You selected {channel_or_role} as your alert role!")


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
