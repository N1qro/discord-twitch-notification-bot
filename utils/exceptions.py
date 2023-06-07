from discord.ext import commands


class NoAlertChannelSet(commands.CheckFailure):
    pass


class NoLinkedSlotsLeft(commands.CheckFailure):
    pass
