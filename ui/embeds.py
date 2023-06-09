from datetime import datetime

from discord import Embed


class DefaultEmbed(Embed):
    """Базовый класс, интерфейс для вложений"""
    bot_name = bot_thumnail_url = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, color=0x7123e7)
        self.set_author(
            name=self.bot_name,
            icon_url=self.bot_thumnail_url
        )
        self.description = "Нет описания"


class LinkEmbed(DefaultEmbed):
    """Вложение привязки стримера"""
    def __init__(
        self,
        twitch_name: str,
        twitch_description: str,
        twitch_thumbnail: str,
        creation_date: datetime,
        is_partner: bool
    ):
        super().__init__()
        self.title = twitch_name
        self.description = twitch_description
        self.set_thumbnail(url=twitch_thumbnail)
        self.add_field(name="Аккаунт создан", value=creation_date, inline=True)
        self.add_field(name="Партнёр", value="Да" if is_partner else "Нет", inline=True)


class StreamOnlineEmbed(DefaultEmbed):
    """Вложение оповещения о начале стрима"""
    def __init__(
        self,
        username: str,
        game: str,
        title: str,
        thumbnail: str
    ):
        super().__init__()
        self.title = f"{username} is online!"
        self.description = f"Streaming **{game}**\nhttps://www.twitch.tv/{username}"
        self.set_image(url=thumbnail)
        self.add_field(name="Title", value=title, inline=True)
