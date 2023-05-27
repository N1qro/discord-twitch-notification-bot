import asyncpg
import asyncio
import sys
import asyncio.exceptions
from accessify import private
from logger import Log
from queries import Query


class Database:
    @private
    def __init__(self, pool) -> None:
        """Чтобы создать обьект класса, используйте `Database.connect()`"""
        self.pool = pool

    @classmethod
    async def connect(cls):
        status = await cls.check_connection()
        if status is True:
            pool = await asyncpg.create_pool()
            return cls(pool)
        return status

    @staticmethod
    async def check_connection():
        """Проверяет возможность подключения к базе данных."""
        try:
            Log.info("Cheking the PostgreSQL connection possibility...")
            conn = await asyncpg.connect(timeout=5)
            await conn.close()
        except asyncio.exceptions.TimeoutError:
            raise Exception("Check your PostgreSQL connection, timeout error")
        except ConnectionRefusedError:
            raise Exception("Is your PostgreSQL port correct? Connection refused")
        else:
            Log.success("Connection possible. Can proceed further!")
            return True

    async def init_tables(self) -> None:
        """Создаёт pool соединений и все нужные таблицы, если они не существуют"""
        async with self.pool.acquire() as conn:
            await conn.execute(Query.CREATE_ALL.value)

    async def test_query(self) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch("SELECT * FROM person LIMIT 5")
