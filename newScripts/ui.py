import discord
from typing import Coroutine
from discord.ui import View, Button


class LinkView(View):
    def __init__(
        self,
        db_query_function: Coroutine,
        streamer_login: str,
        streamer_id: int,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.queryFunction = db_query_function
        self.streamerLogin = streamer_login
        self.streamerId = streamer_id
        self.subscribeButton = Button(
            label="Subscribe", style=discord.ButtonStyle.green, emoji="🔔")
        self.cancelButton = Button(
            label="Cancel", style=discord.ButtonStyle.red, emoji="⛔")
        self.subscribeButton.callback = self.subscribeCallback
        self.cancelButton.callback = self.cancelCallback
        self.add_item(self.subscribeButton)
        self.add_item(self.cancelButton)

    async def subscribeCallback(self, interaction: discord.Interaction):
        self.remove_item(self.cancelButton)
        self.subscribeButton.label = "Subscribed!"
        self.subscribeButton.emoji = "✨"
        self.subscribeButton.disabled = True
        await interaction.response.defer()
        role = await interaction.guild.create_role(name=self.streamerLogin, color=0x7123e7)
        await self.queryFunction(role.id, interaction.guild_id, self.streamerId, self.streamerLogin)
        await interaction.edit_original_response(view=self)
        # await interaction.response.edit_message(view=self)

    async def cancelCallback(self, interaction: discord.Interaction):
        self.remove_item(self.subscribeButton)
        self.cancelButton.label = "Cancelled"
        self.cancelButton.emoji = "💥"
        self.cancelButton.disabled = True
        await interaction.response.edit_message(view=self)
