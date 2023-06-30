import discord
from utils.autocomplete import getUserSubbedStreamers


class LinkCog(discord.Cog):

    @discord.user_command(name="Get subscribed")
    async def get_linked(self, ctx: discord.ApplicationContext, member):
        streamerList = await getUserSubbedStreamers(member)
        if not streamerList:
            return await ctx.respond(
                f"**{member.display_name}** is not yet subbed to anyone!")
        text = ", ".join(map(lambda x: f"**{x}**", streamerList))
        await ctx.respond(f"**{member.display_name}** is subscribed to {text}")
