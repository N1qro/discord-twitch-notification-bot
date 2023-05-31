import asyncpg
from asyncio.exceptions import TimeoutError
from accessify import private
from logger import Log
from functools import wraps
from typing import Optional, Coroutine
from queries import Query


class Database:
    @private
    def __init__(self, pool) -> None:
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
        except TimeoutError:
            raise Exception("Check your PostgreSQL connection, timeout error")
        except ConnectionRefusedError:
            raise Exception("Is your PostgreSQL port correct? Connection refused")
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
        connection: asyncpg.Connection
    ) -> None:
        """Добавляет роль к `roles`, стримера в `streamers` и соединяет их"""
        queryArgs = ((roleId, guildId),
                     (streamerId,),
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


async def main():
    db = await Database.connect()
    await db.init_tables()
    await db.pool.close()
    print("all good")


if __name__ == "__main__":
    from environ_loader import load_env
    load_env()
    import asyncio
    asyncio.run(main())
