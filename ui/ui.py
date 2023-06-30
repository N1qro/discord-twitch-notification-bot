from database.models import Server, Streamer, Role

import discord
from tortoise.transactions import in_transaction
from tortoise.exceptions import OperationalError
from discord.ui import Button, View


class LinkView(View):
    def __init__(
        self,
        streamer: Streamer,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.streamer = streamer
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

        try:
            async with in_transaction():
                createdRole = await interaction.guild.create_role(
                    reason="Linked new streamer for alerts",
                    name="t.tv/" + self.streamer.login,
                    color=0x7123e7)

                await Role.create(id=createdRole.id,
                                  streamer=self.streamer,
                                  belongs_to_id=interaction.guild_id)
        except discord.Forbidden:
            await interaction.response.send_message(
                "Bot does not have **\"Manage roles\"** permissions!")
        except OperationalError:
            await createdRole.delete(reason="Link operation failed")
            await interaction.response.send_message(
                "Something went wrong with the database. Contact the developer")
        else:
            await interaction.edit_original_response(view=self)
        # await interaction.response.edit_message(view=self)

    async def cancelCallback(self, interaction: discord.Interaction):
        self.remove_item(self.subscribeButton)
        self.cancelButton.label = "Cancelled"
        self.cancelButton.emoji = "💥"
        self.cancelButton.disabled = True
        if not await self.streamer.roles:
            await self.streamer.delete()
        await interaction.response.edit_message(view=self)
