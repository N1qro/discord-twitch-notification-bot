from tortoise.models import Model
from tortoise import fields
from tortoise.signals import Signals, post_save
from tortoise.fields import IntField, BigIntField, CharField, ForeignKeyField, BooleanField, SmallIntField


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
    async def update_linked_count(sender, instance, wasCreated, *a):
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


Role.register_listener(Signals.post_delete, Role.update_linked_count)
Role.register_listener(Signals.post_save, Role.update_linked_count)
