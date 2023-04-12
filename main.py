import os
import discord
from discord.ext import commands
from typing import Union

from dotenv import load_dotenv
assert load_dotenv(), "No .env file configured"

permissions = discord.Intents.default()
permissions.message_content = True
permissions.members = True
bot = commands.Bot(os.getenv("PREFIX"), intents=permissions)


def get_channel(
    ctx: commands.context.Context,
    channel: discord.channel.TextChannel
) -> Union[discord.channel.TextChannel, None]:
    """Retrieves channel name by it's NAME or the CHANNEL, mentioned by #<channel_name>"""
    return channel


@bot.event
async def on_ready():
    print("Bot started")


@bot.command()
@commands.has_permissions(administrator=True)
async def set_command_channel(
    ctx: commands.context.Context,
    channel: Union[discord.channel.TextChannel, str]
):
    if isinstance(channel, discord.channel.TextChannel):
        await ctx.send(f"You selected {channel} as your command channel! Id is {channel.id}")
    else:
        await ctx.send("Nothing found.")


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
