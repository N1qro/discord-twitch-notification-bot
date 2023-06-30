import discord
from discord.ext import tasks
from ui.embeds import StreamOnlineEmbed
from database.models import Streamer, Role
from utils.logger import Log
from api.twitch import Request


bot: discord.Bot = None


@tasks.loop(seconds=10)
async def notification_task():
    onlinemap = dict()  # Id -> online_status
    ids = set()

    # Наполняем хранилища
    async for streamer in Streamer.all():
        onlinemap[streamer.id] = streamer.is_online
        ids.add(streamer.id)

    # Получаем информацию о тех стримерах, которые онлайн
    data = await Request.getOnlineInfo(*ids)
    for entry in data:
        streamerId = int(entry["user_id"])
        ids.remove(streamerId)
        if onlinemap[streamerId] is False:
            embed = StreamOnlineEmbed(
                    entry["user_login"],
                    entry["game_name"],
                    entry["title"],
                    entry["thumbnail_url"])
            async for role in Role.filter(streamer_id=streamerId):
                guild = await role.belongs_to
                channel = bot.get_channel(guild.channel_id)
                if channel is None:
                    Log.warning(f"Channel {guild.channel_id} is None! Cannot send the message!")

                await channel.send(
                    content=f"<@&{role.id}>",
                    embed=embed)

    # Обновляем бд (Ставим онлайн = да)
    await Streamer.filter(id__in=tuple(int(entry["user_id"]) for entry in data)).update(is_online=True)

    # К этому времени здесь осталисть только аккаунты не в сети
    setToFalse = []
    for offlineId in ids:
        if onlinemap[offlineId] is True:
            setToFalse.append(offlineId)

    # Обновляем им статус
    if setToFalse:
        await Streamer.filter(id__in=setToFalse).update(is_online=False)
