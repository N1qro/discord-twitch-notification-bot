import discord
from discord.ext import commands

from database.models import Server
from utils.exceptions import NoAlertChannelSet, NoLinkedSlotsLeft

LINK_SLOTS = None


def hasAlertChannelSet():
    """Проверка: Установлен ли канал для оповещений, или нет?"""
    async def predicate(ctx: discord.ApplicationContext):
        server = await Server.get(id=ctx.guild_id)

        if server.channel_id is None:
            raise NoAlertChannelSet("The server does not have any alert channel set!")
        return True
    return commands.check(predicate)


def hasEmptyLinkSlot():
    """Проверка: Есть ли свободный слот для привязки стримера?"""
    async def predicate(ctx: discord.ApplicationContext):
        server = await Server.get(id=ctx.guild_id)

        if server.linked_count >= LINK_SLOTS:
            raise NoLinkedSlotsLeft(f"You already have **{LINK_SLOTS}** link slots set!")
        return True
    return commands.check(predicate)
