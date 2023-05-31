import asyncio
import os
import sys

import discord
from database import Database
from embeds import DefaultEmbed, LinkEmbed
from environ_loader import load_env
from logger import Log
from owner_commands import OwnerCog
from twitch import TwitchRequests
from ui import LinkView


class EventCog(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.db: Database = None

    @discord.Cog.listener()
    async def on_ready(self):
        self.db: Database = self.bot.db
        Log.success("Bot is ready!")

    @discord.Cog.listener()
    async def on_connect(self):
        await self.bot.sync_commands()
        Log.info("Connected to the servers")

    @discord.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = guild.system_channel
        if channel:
            channel = channel.id
        await self.db.add_guild(guild.id, channel)

    @discord.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        print(f"Should delete {guild.id}")
        print(await self.db.remove_guild(guild.id))

    async def setup_hook(self):
        bot.db = await Database.connect()


perms = discord.Permissions()
intents = discord.Intents()
perms.manage_roles = True
intents.guilds = True
bot = discord.Bot(permissions=perms, intents=intents, debug_guilds=[696434683730329713])


@bot.slash_command()
async def link(
    ctx: discord.ApplicationContext,
    twitch_url: discord.Option(str, "Enter the twitch streamer link")
):
    try:
        data = await TwitchRequests.getChannelInfo(twitch_url)
        if not data:
            return
    except Exception as e:
        Log.failure(str(e))
    else:
        # Проверка на существование
        if await bot.db.is_already_linked(ctx.guild_id, int(data["id"])):
            return await ctx.respond(
                "This streamer is already linked to this server!"
            )

        await ctx.respond(embed=LinkEmbed(
            twitch_name=data["login"],
            twitch_description=data["description"],
            twitch_thumbnail=data["profile_image_url"],
            creation_date=data["created_at"],
            is_partner=data["broadcaster_type"] == "partner"
        ), view=LinkView(bot.db.add_role, data["login"], int(data["id"])))


@bot.slash_command()
async def stats(ctx: discord.ApplicationContext):
    pass


@bot.slash_command()
async def subscribe(ctx: discord.ApplicationContext):
    pass


@bot.user_command(name="Show subscribed channels")
async def show_subscribed(ctx, member: discord.Member):
    print(type(ctx), type(member))
    pass


async def main():
    events = EventCog(bot)
    ownerCommands = OwnerCog(bot)
    bot.add_cog(events)
    bot.add_cog(ownerCommands)

    await bot.login(os.getenv("BOT_TOKEN"))
    await bot.application_info()
    DefaultEmbed.bot_name = bot.user.name
    DefaultEmbed.bot_thumnail_url = bot.user.avatar.url
    await events.setup_hook()
    await bot.connect()


if __name__ == "__main__":
    load_env()
    TwitchRequests.init()
    Log.info("Launching discord bot")

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
        print("COMPLETED")
    finally:
        if sys.exc_info()[0] is None:
            Log.info("Bot offline")
