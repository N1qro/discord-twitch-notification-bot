from tortoise import fields
from tortoise.fields import (BigIntField, BooleanField, CharField,
                             ForeignKeyField, IntField, SmallIntField)
from tortoise.models import Model
from tortoise.signals import Signals


class Streamer(Model):
    id = IntField(pk=True)
    login = CharField(32)
    is_online = BooleanField(default=False)

    def __str__(self):
        return f"<Streamer: {self.login}>"


class Role(Model):
    id = BigIntField(pk=True)
    streamer = ForeignKeyField("discord.Streamer",
                               related_name="roles",
                               on_delete=fields.RESTRICT)
    belongs_to = ForeignKeyField("discord.Server",
                                 related_name="roles",
                                 on_delete=fields.CASCADE)

    @staticmethod
    async def update_linked_count(_, instance, wasCreated, *a):
        """Обновление `Server.linked_count`, при создании или удалении роли"""
        if not wasCreated:
            return

        server = await instance.belongs_to
        server.linked_count = await Role.filter(belongs_to=server).count()
        await server.save()

    def __str__(self):
        return f"<Role for {self.belongs_to_id} of {self.streamer_id}>"


class Server(Model):
    id = BigIntField(pk=True)
    channel_id = BigIntField(unique=True, null=True)
    linked_count = SmallIntField(default=0)

    def __str__(self):
        return f"<Server {self.id}>"


# Установка эвентов на сохранение/удаление роли
Role.register_listener(Signals.post_delete, Role.update_linked_count)
Role.register_listener(Signals.post_save, Role.update_linked_count)
