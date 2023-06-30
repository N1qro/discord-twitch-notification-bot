import discord
from discord.ext import commands

from commands.link import LinkCog
from commands.sub import SubCog
from utils.exceptions import NoAlertChannelSet, NoLinkedSlotsLeft


class TwitchCog(SubCog, LinkCog):
    @discord.command()
    @commands.has_permissions(administrator=True)
    async def set_alert_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel
    ):
        """Устанавливает канал для оповещений о начале стримов"""
        everyone_role = ctx.guild.get_role(ctx.guild_id)
        permissions = channel.permissions_for(everyone_role)
        if permissions.view_channel:
            await self.db.update_channel(ctx.guild_id, channel.id)
            await ctx.respond("Successfully updated the alert channel!")
        else:
            await ctx.respond("This channel does not have permission for everyone to read it")

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.respond("Only server administators can run this command!")
        elif isinstance(error, NoAlertChannelSet):
            await ctx.respond(str(error))
        elif isinstance(error, NoLinkedSlotsLeft):
            await ctx.respond(str(error))
        else:
            raise error
