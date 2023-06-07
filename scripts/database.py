from asyncio.exceptions import TimeoutError
from functools import wraps
from typing import List, Optional, Union

import asyncpg

from utils.logger import Log
from utils.queries import Query


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=Singleton):
    connected_once = False

    def __init__(self, pool=None) -> None:
        assert self.connected_once
        """Чтобы создать обьект класса, используйте `Database.connect()`"""
        self.pool = pool

    def acquire_connection(function):
        """Выделяет канал `connection` с базой данных и передаёт его функции"""
        @wraps(function)
        async def wrapper(self, *args, **kwargs):
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    return await function(*args, **kwargs, connection=conn)
        return wrapper

    @classmethod
    async def connect(cls):
        """Возвращает обьект `Database` или вызывает исключения если бд недоступна"""
        assert not cls.connected_once
        cls.connected_once = True
        status = await cls.check_connection()
        if status is True:
            pool = await asyncpg.create_pool()
            db_object = cls(pool)
            await db_object.init_tables()
            return db_object
        return status

    @staticmethod
    async def check_connection() -> bool:
        """Проверяет возможность подключения к базе данных."""
        try:
            Log.info("Cheking the PostgreSQL connection possibility...")
            conn = await asyncpg.connect(timeout=5)
            await conn.close()
            asyncpg.PostgresConnectionError
        except TimeoutError:
            raise ConnectionRefusedError("Check your PostgreSQL connection, timeout error")
        except ConnectionRefusedError:
            raise ConnectionRefusedError("Is your PostgreSQL port correct? Connection refused")
        else:
            Log.success("Connection possible. Can proceed further!")
            return True

    @acquire_connection
    async def init_tables(connection: asyncpg.Connection) -> None:
        """Создаёт все необходимые таблицы, если они отсутствуют"""
        await connection.execute(Query.CREATE_ALL.value)

    @acquire_connection
    @staticmethod
    async def add_guild(
        guildId: int,
        channelId: Optional[int] = None,
        connection: asyncpg.Connection = None
    ) -> None:
        """Добавляет гильдию и канал оповещений в таблицу `guilds`"""
        await connection.execute(Query.GUILD_ADD.value, guildId, channelId)

    @acquire_connection
    @staticmethod
    async def remove_guild(
        guildId: int,
        connection: asyncpg.Connection
    ) -> None:
        """Удаляет гильдию, связанные с ней роли и чистит таблицу оповещений"""
        await connection.execute(Query.GUILD_REMOVE.value, guildId)

    @acquire_connection
    @staticmethod
    async def add_role(
        roleId: int,
        guildId: int,
        streamerId: int,
        streamerLogin: str,
        connection: asyncpg.Connection
    ) -> None:
        """Добавляет роль к `roles`, стримера в `streamers` и соединяет их"""
        queryArgs = ((roleId, guildId),
                     (streamerId, streamerLogin),
                     (streamerId, roleId))
        for query, args in zip(Query.ADD_ROLE.value, queryArgs):
            print(query, *args)
            await connection.execute(query, *args)

    @acquire_connection
    @staticmethod
    async def is_already_linked(
        guildId: int,
        streamerId: int,
        connection: asyncpg.Connection
    ) -> bool:
        row = await connection.fetchrow(Query.CHECK_IF_LINKED.value, guildId, streamerId)
        return row is not None

    @acquire_connection
    @staticmethod
    async def get_role_from_streamer(
        guildId: int,
        streamer_login: str,
        connection: asyncpg.Connection
    ) -> int:
        """Получает `id` роли, к которой привязан стример в текущей гильдии"""
        return await connection.fetchval(Query.GET_GUILD_ROLE_FROM_STREAMER.value,
                                         guildId,
                                         streamer_login)

    @acquire_connection
    @staticmethod
    async def unlink_role(
        roleId: int,
        connection: asyncpg.Connection
    ) -> None:
        await connection.execute(Query.DELETE_ROLE_FROM_ROLES.value, roleId)

    @acquire_connection
    @staticmethod
    async def update_channel(
        guildId: int,
        channelId: int,
        connection: asyncpg.Connection
    ) -> None:
        await connection.execute(Query.UPDATE_COMMAND_CHANNEL.value, guildId, channelId)

    @acquire_connection
    @staticmethod
    async def get_linked_streamers(
        guildId: int,
        connection: asyncpg.Connection
    ) -> List[asyncpg.Record]:
        return await connection.fetch(Query.GET_LINKED_STREAMERS.value, guildId)

    @acquire_connection
    @staticmethod
    async def get_command_channel(
        guildId: int,
        connection: asyncpg.Connection
    ) -> Union[int, None]:
        return await connection.fetchval(Query.GET_COMMAND_CHANNEL.value, guildId)

    @acquire_connection
    @staticmethod
    async def get_linked_data(
        guildId: int,
        connection: asyncpg.Connection
    ) -> int:
        return await connection.fetchval(Query.GET_LINKED_DATA.value, guildId)

    @acquire_connection
    @staticmethod
    async def get_all_guild_roles(
        guildId: int,
        connection: asyncpg.Connection
    ) -> List[int]:
        records = await connection.fetch(Query.GET_ALL_ROLES.value, guildId)
        return [record.get("role_id") for record in records]

    @acquire_connection
    @staticmethod
    async def increment_linked_data(
        guildId: int,
        amount: int,
        connection: asyncpg.Connection
    ) -> None:
        await connection.execute(Query.INCREMENT_LINKED_DATA.value, guildId, amount)

    @acquire_connection
    @staticmethod
    async def get_streamer_amount(connection: asyncpg.Connection) -> int:
        return await connection.fetchval(Query.GET_STREAMER_AMOUNT.value)


if __name__ == "__main__":
    import asyncio
    from utils.environ_loader import load_env

    async def main():
        db = await Database.connect()
        await db.init_tables()
        await db.pool.close()

    load_env()
    asyncio.run(main())
