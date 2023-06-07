import discord
import os
from discord.ext import commands
from utils.exceptions import NoAlertChannelSet, NoLinkedSlotsLeft
from scripts.database import Database


def has_alert_channel_set():
    async def predicate(ctx: discord.ApplicationContext):
        db = Database()
        if await db.get_command_channel(ctx.guild_id) is None:
            raise NoAlertChannelSet("The server does not have any alert channel set!")
        return True
    return commands.check(predicate)


def has_empty_link_slot():
    async def predicate(ctx: discord.ApplicationContext):
        db = Database()
        if await db.get_linked_data(ctx.guild_id) >= int(os.getenv("LINK_SLOTS")):
            raise NoLinkedSlotsLeft(f"You already have **{os.getenv('LINK_SLOTS')}** link slots set!")
        return True
    return commands.check(predicate)
