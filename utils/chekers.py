import discord
import os
from database.models import Server
from discord.ext import commands
from utils.exceptions import NoAlertChannelSet, NoLinkedSlotsLeft


def has_alert_channel_set():
    async def predicate(ctx: discord.ApplicationContext):
        server = await Server.get(id=ctx.guild_id)

        if server.channel_id is None:
            raise NoAlertChannelSet("The server does not have any alert channel set!")
        return True
    return commands.check(predicate)


def has_empty_link_slot():
    async def predicate(ctx: discord.ApplicationContext):
        server = await Server.get(id=ctx.guild_id)

        if server.linked_count >= int(os.getenv("LINK_SLOTS")):
            raise NoLinkedSlotsLeft(f"You already have **{int(os.getenv('LINK_SLOTS'))}** link slots set!")
        return True
    return commands.check(predicate)
