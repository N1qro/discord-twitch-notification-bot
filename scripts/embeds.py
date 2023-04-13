from discord import Embed
from enums import Status


def getCheckEmbed(bot, db, guildId):
    guildData = db.get_guild_data(guildId)

    embed_role = f"<@&{guildData.roleId}>" if guildData.roleId else Status.bad.value
    embed_channel = f"<#{guildData.channelId}>" if guildData.channelId else Status.bad.value
    embed_guild = Status.good.value if guildData.guildId else Status.bad.value

    is_everything_correct = all(guildData)
    embed_color = 0x46f339 if is_everything_correct else 0xf50f0f

    embed = Embed(title="Status preview", description="Will help you determine what is missing or not", color=embed_color)
    embed.set_author(name=bot.user.display_name, icon_url=bot.user.display_avatar)
    embed.add_field(name="Guild setup", value=embed_guild, inline=True)
    embed.add_field(name="Permissions", value=Status.good.value, inline=True)
    embed.add_field(name="", value="", inline=True)
    embed.add_field(name="Alert role set", value=embed_role, inline=True)
    embed.add_field(name="Announcement channel set", value=embed_channel, inline=True)
    embed.set_footer(text="Use '/twitch link help' to see how to set missing information if needed")
    return embed
