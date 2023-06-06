import discord
from discord.ext import commands
from discord.utils import basic_autocomplete
from ui.ui import LinkView
from ui.embeds import LinkEmbed
from scripts.twitchapi import TwitchRequests
from utils.logger import Log


async def get_linked_streamers(ctx: discord.AutocompleteContext):
    data = await ctx.bot.db.get_linked_streamers(ctx.interaction.guild_id)
    return (record.get("streamer_login") for record in data)


class TwitchCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.command()
    async def testing_command_2(self, ctx: discord.ApplicationContext):
        Log.success("Recognized!")
        await ctx.respond("Great.")

    @discord.command()
    @commands.has_permissions(administrator=True)
    async def link(
        self,
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
            if await self.bot.db.is_already_linked(ctx.guild_id, int(data["id"])):
                return await ctx.respond(
                    "This streamer is already linked to this server!"
                )

            await ctx.respond(embed=LinkEmbed(
                twitch_name=data["login"],
                twitch_description=data["description"],
                twitch_thumbnail=data["profile_image_url"],
                creation_date=data["created_at"][:data["created_at"].index("T")],
                is_partner=data["broadcaster_type"] == "partner"
            ), view=LinkView(self.bot.db.add_role, data["login"], int(data["id"])))

    @discord.command()
    @commands.has_permissions(administrator=True)
    async def unlink(
        self,
        ctx: discord.ApplicationContext,
        twitch_login: discord.commands.Option(str, autocomplete=basic_autocomplete(get_linked_streamers))
    ):
        role_id = await self.bot.db.get_role_from_streamer(ctx.guild_id, twitch_login)
        role = ctx.guild.get_role(role_id)

        if role is not None:
            await role.delete(reason="Alert unlink")
            await self.bot.db.unlink_role(role_id)
            await ctx.respond(f"Successfully unlinked **{twitch_login}** streamer")
        else:
            await ctx.respond("Couldn't find any streamer with that login!")

    @discord.command()
    @commands.has_permissions(administrator=True)
    async def set_alert_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel
    ):
        everyone_role = ctx.guild.get_role(ctx.guild_id)
        permissions = channel.permissions_for(everyone_role)
        if permissions.view_channel:
            await self.bot.db.update_channel(ctx.guild_id, channel.id)
            await ctx.respond("Successfully updated the alert channel!")
        else:
            await ctx.respond("This channel does not have permission for everyone to read it")

    @discord.command()
    async def sub(
        self,
        ctx: discord.ApplicationContext,
        streamer_login: discord.Option(str, autocomplete=basic_autocomplete(get_linked_streamers))
    ):
        pass


# @link.error
# async def error(ctx: discord.ApplicationContext, error: discord.DiscordException):
#     if isinstance(error, commands.errors.MissingPermissions):
#         await ctx.respond("Only the server administrators can run this command")